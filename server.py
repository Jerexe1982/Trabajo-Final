import base64
import json
import os
import re
import secrets
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).parent
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MAX_BYTES = 10 * 1024 * 1024
BATCH_MAX = 10
API_URL = "https://api.openai.com/v1/responses"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", f"http://{HOST}:{PORT}/oauth2callback")
GOOGLE_SCOPE = "https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/drive.file"
GOOGLE_FOLDER_NAME = os.getenv("GOOGLE_FOLDER_NAME", "Finanzas claras")
google_tokens = None
oauth_state = None

SYSTEM_PROMPT = (ROOT / "prompts" / "system_prompt.md").read_text(encoding="utf-8")
USER_PROMPT = (ROOT / "prompts" / "user_prompt.md").read_text(encoding="utf-8")


def json_response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def extract_output_text(payload):
    if payload.get("output_text"):
        return payload["output_text"]
    chunks = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in ("output_text", "text"):
                chunks.append(content.get("text", ""))
    return "".join(chunks)


def parse_model_json(text):
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return json.loads(cleaned.strip())


def analyze_receipt(payload):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta OPENAI_API_KEY en el entorno del servidor.")
    filename = payload.get("filename", "comprobante")
    mime_type = payload.get("mime_type", "application/octet-stream")
    encoded = payload.get("data", "")
    if not encoded:
        raise ValueError("El comprobante está vacío.")
    raw = base64.b64decode(encoded, validate=True)
    if len(raw) > MAX_BYTES:
        raise ValueError("El comprobante supera el límite de 10 MB.")
    is_pdf = mime_type == "application/pdf" or filename.lower().endswith(".pdf")
    if is_pdf:
        content_part = {"type": "input_file", "filename": filename, "file_data": encoded}
    elif mime_type.startswith("image/"):
        content_part = {"type": "input_image", "detail": "high", "image_url": f"data:{mime_type};base64,{encoded}"}
    else:
        raise ValueError("Formato no compatible. Usá una imagen o un PDF.")
    request_body = {
        "model": MODEL,
        "instructions": SYSTEM_PROMPT,
        "input": [{"role": "user", "content": [{"type": "input_text", "text": USER_PROMPT}, content_part]}],
        "temperature": 0,
    }
    request = Request(API_URL, data=json.dumps(request_body).encode("utf-8"), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=90) as response:
        result = json.loads(response.read().decode("utf-8"))
    return parse_model_json(extract_output_text(result))


def spreadsheet_id_from_url(value):
    match = re.search(r"docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)", value or "")
    if match:
        return match.group(1)
    if re.fullmatch(r"[a-zA-Z0-9_-]{20,}", value or ""):
        return value
    raise ValueError("Pegá una URL válida de Google Sheets.")


def google_auth_url():
    global oauth_state
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise RuntimeError("Faltan GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET en el entorno del servidor.")
    oauth_state = secrets.token_urlsafe(32)
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": GOOGLE_SCOPE,
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "select_account consent",
        "state": oauth_state,
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)


def exchange_google_code(code):
    global google_tokens
    form = urlencode({"code": code, "client_id": GOOGLE_CLIENT_ID, "client_secret": GOOGLE_CLIENT_SECRET, "redirect_uri": GOOGLE_REDIRECT_URI, "grant_type": "authorization_code"}).encode()
    request = Request("https://oauth2.googleapis.com/token", data=form, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urlopen(request, timeout=30) as response:
        token = json.loads(response.read().decode("utf-8"))
    token["expires_at"] = time.time() + int(token.get("expires_in", 3600)) - 60
    google_tokens = token


def google_access_token():
    global google_tokens
    if not google_tokens:
        return None
    if google_tokens.get("expires_at", 0) > time.time():
        return google_tokens.get("access_token")
    refresh_token = google_tokens.get("refresh_token")
    if not refresh_token:
        google_tokens = None
        return None
    form = urlencode({"client_id": GOOGLE_CLIENT_ID, "client_secret": GOOGLE_CLIENT_SECRET, "refresh_token": refresh_token, "grant_type": "refresh_token"}).encode()
    request = Request("https://oauth2.googleapis.com/token", data=form, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urlopen(request, timeout=30) as response:
        renewed = json.loads(response.read().decode("utf-8"))
    renewed["refresh_token"] = refresh_token
    renewed["expires_at"] = time.time() + int(renewed.get("expires_in", 3600)) - 60
    google_tokens = renewed
    return renewed.get("access_token")


def append_to_google_sheet(payload):
    token = google_access_token()
    if not token:
        return None
    spreadsheet_id = payload.get("spreadsheet_id") or spreadsheet_id_from_url(payload.get("sheet_url", ""))
    expenses = payload.get("expenses") or [payload.get("expense", {})]
    if not expenses or len(expenses) > BATCH_MAX:
        raise ValueError("El lote debe contener entre 1 y 10 registros.")
    row = [[expense.get("date", ""), expense.get("amount", ""), expense.get("currency", "ARS"), expense.get("description", ""), expense.get("cbu", "Sin dato"), expense.get("payment_method", "Sin dato"), expense.get("category", ""), expense.get("note", "")] for expense in expenses]
    endpoint = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/A:H:append?{urlencode({'valueInputOption':'USER_ENTERED','insertDataOption':'INSERT_ROWS'})}"
    request = Request(endpoint, data=json.dumps({"majorDimension": "ROWS", "values": row}).encode("utf-8"), headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def list_google_sheets():
    token = google_access_token()
    if not token:
        return None
    query = "mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
    params = urlencode({"q": query, "pageSize": "100", "orderBy": "modifiedTime desc", "fields": "files(id,name,mimeType,modifiedTime,webViewLink)"})
    request = Request(f"https://www.googleapis.com/drive/v3/files?{params}", headers={"Authorization": f"Bearer {token}"}, method="GET")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8")).get("files", [])


def google_request(method, endpoint, body=None):
    token = google_access_token()
    if not token:
        return None
    headers = {"Authorization": f"Bearer {token}"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    request = Request(endpoint, data=data, headers=headers, method=method)
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def create_google_workspace(spreadsheet_name):
    if not spreadsheet_name or len(spreadsheet_name.strip()) < 1:
        raise ValueError("Indicá un nombre para la planilla de gastos.")
    folder_query = f"name='{GOOGLE_FOLDER_NAME.replace(chr(39), chr(39) + chr(39))}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    folders = google_request("GET", "https://www.googleapis.com/drive/v3/files?" + urlencode({"q": folder_query, "spaces": "drive", "pageSize": "10", "fields": "files(id,name)"}))
    folder_id = folders.get("files", [])[0].get("id") if folders and folders.get("files") else None
    if not folder_id:
        folder = google_request("POST", "https://www.googleapis.com/drive/v3/files", {"name": GOOGLE_FOLDER_NAME, "mimeType": "application/vnd.google-apps.folder"})
        folder_id = folder["id"]
    sheet = google_request("POST", "https://sheets.googleapis.com/v4/spreadsheets", {"properties": {"title": spreadsheet_name.strip()}})
    spreadsheet_id = sheet["spreadsheetId"]
    current = google_request("GET", f"https://www.googleapis.com/drive/v3/files/{quote(spreadsheet_id)}?fields=parents") or {}
    remove_parents = ",".join(current.get("parents", []))
    move_params = {"addParents": folder_id, "fields": "id,name,parents,webViewLink"}
    if remove_parents:
        move_params["removeParents"] = remove_parents
    google_request("PATCH", f"https://www.googleapis.com/drive/v3/files/{quote(spreadsheet_id)}?{urlencode(move_params)}", {})
    return {"folder_id": folder_id, "folder_name": GOOGLE_FOLDER_NAME, "spreadsheet_id": spreadsheet_id, "spreadsheet_name": spreadsheet_name.strip()}


def read_google_sheet(spreadsheet_id):
    if not spreadsheet_id:
        raise ValueError("Falta el identificador de la planilla.")
    return google_request("GET", f"https://sheets.googleapis.com/v4/spreadsheets/{quote(spreadsheet_id)}/values/A:H")


def analyze_receipts(payload):
    documents = payload.get("documents", [])
    if not documents or len(documents) > BATCH_MAX:
        raise ValueError("El lote debe contener entre 1 y 10 comprobantes.")
    results = []
    for document in documents:
        result = analyze_receipt(document)
        result["archivo"] = document.get("filename", "comprobante")
        results.append(result)
    return results


def auth_popup_html(message):
    safe = json.dumps(message, ensure_ascii=False)
    return f"<!doctype html><html lang='es'><meta charset='utf-8'><title>Google autorizado</title><body><p>{message}</p><script>if(window.opener){{window.opener.postMessage({{type:'google-auth-complete',message:{safe}}},window.location.origin);window.close();}}</script></body></html>"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def do_GET(self):
        if self.path == "/api/health":
            return json_response(self, 200, {"ok": True, "model": MODEL, "api_key_configured": bool(os.getenv("OPENAI_API_KEY")), "google_configured": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)})
        if self.path.startswith("/api/google-auth-url"):
            try:
                return json_response(self, 200, {"ok": True, "auth_url": google_auth_url()})
            except Exception as exc:
                return json_response(self, 500, {"ok": False, "error": str(exc)})
        if self.path.startswith("/api/google-files"):
            try:
                files = list_google_sheets()
                if files is None:
                    return json_response(self, 401, {"ok": False, "auth_required": True, "auth_url": google_auth_url()})
                return json_response(self, 200, {"ok": True, "files": files})
            except HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                return json_response(self, 502, {"ok": False, "error": "Google Drive no pudo listar tus planillas.", "detail": detail[:500]})
            except Exception as exc:
                return json_response(self, 500, {"ok": False, "error": str(exc)})
        if self.path.startswith("/api/google-read"):
            try:
                query = parse_qs(urlparse(self.path).query)
                spreadsheet_id = query.get("spreadsheet_id", [""])[0]
                if not google_access_token():
                    return json_response(self, 401, {"ok": False, "auth_required": True, "auth_url": google_auth_url()})
                return json_response(self, 200, {"ok": True, "data": read_google_sheet(spreadsheet_id)})
            except HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                return json_response(self, 502, {"ok": False, "error": "Google Sheets no pudo leer la planilla.", "detail": detail[:500]})
            except Exception as exc:
                return json_response(self, 500, {"ok": False, "error": str(exc)})
        if self.path.startswith("/oauth2callback"):
            query = parse_qs(urlparse(self.path).query)
            state = query.get("state", [""])[0]
            code = query.get("code", [""])[0]
            if not code or state != oauth_state:
                body = auth_popup_html("No se pudo validar la autorización de Google.")
                self.send_response(400)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(body.encode("utf-8"))
                return
            try:
                exchange_google_code(code)
                body = auth_popup_html("Google autorizado. Esta ventana se cerrará.")
                self.send_response(200)
            except Exception as exc:
                body = auth_popup_html(f"Error de autorización: {exc}")
                self.send_response(502)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
            return
        relative = self.path.split("?", 1)[0].lstrip("/") or "index.html"
        path = (ROOT / relative).resolve()
        if ROOT not in path.parents and path != ROOT:
            return json_response(self, 403, {"error": "Ruta no permitida."})
        if not path.is_file():
            return json_response(self, 404, {"error": "Recurso no encontrado."})
        content_type = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8", ".md": "text/plain; charset=utf-8"}.get(path.suffix, "application/octet-stream")
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path == "/api/google-setup":
            length = int(self.headers.get("Content-Length", "0"))
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                if not google_access_token():
                    return json_response(self, 401, {"ok": False, "auth_required": True, "auth_url": google_auth_url()})
                return json_response(self, 200, {"ok": True, "workspace": create_google_workspace(payload.get("spreadsheet_name", ""))})
            except HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                return json_response(self, 502, {"ok": False, "error": "Google no pudo crear la carpeta o la planilla.", "detail": detail[:500]})
            except (ValueError, json.JSONDecodeError) as exc:
                return json_response(self, 400, {"ok": False, "error": str(exc)})
            except Exception as exc:
                return json_response(self, 500, {"ok": False, "error": str(exc)})
        if self.path == "/api/analyze-receipts":
            length = int(self.headers.get("Content-Length", "0"))
            if length > MAX_BYTES * BATCH_MAX * 2:
                return json_response(self, 413, {"ok": False, "error": "El lote supera el tamaño máximo permitido."})
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                result = analyze_receipts(payload)
                return json_response(self, 200, {"ok": True, "results": result, "count": len(result), "model": MODEL})
            except (ValueError, json.JSONDecodeError) as exc:
                return json_response(self, 400, {"ok": False, "error": str(exc)})
            except HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                return json_response(self, 502, {"ok": False, "error": "La API rechazó uno de los comprobantes.", "detail": detail[:500]})
            except Exception as exc:
                return json_response(self, 500, {"ok": False, "error": str(exc)})
        if self.path == "/api/google-save":
            length = int(self.headers.get("Content-Length", "0"))
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                if not google_access_token():
                    return json_response(self, 401, {"ok": False, "auth_required": True, "auth_url": google_auth_url()})
                result = append_to_google_sheet(payload)
                return json_response(self, 200, {"ok": True, "saved": True, "result": result})
            except HTTPError as exc:
                if exc.code == 401:
                    global google_tokens
                    google_tokens = None
                    return json_response(self, 401, {"ok": False, "auth_required": True, "auth_url": google_auth_url()})
                detail = exc.read().decode("utf-8", errors="replace")
                return json_response(self, 502, {"ok": False, "error": "Google Sheets rechazó el guardado.", "detail": detail[:500]})
            except (ValueError, json.JSONDecodeError) as exc:
                return json_response(self, 400, {"ok": False, "error": str(exc)})
            except Exception as exc:
                return json_response(self, 500, {"ok": False, "error": str(exc)})
        if self.path != "/api/analyze-receipt":
            return json_response(self, 404, {"error": "Endpoint no encontrado."})
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_BYTES * 2:
            return json_response(self, 413, {"error": "La solicitud es demasiado grande."})
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            result = analyze_receipt(payload)
            json_response(self, 200, {"ok": True, "result": result, "model": MODEL})
        except (ValueError, json.JSONDecodeError) as exc:
            json_response(self, 400, {"ok": False, "error": str(exc)})
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            json_response(self, 502, {"ok": False, "error": "La API rechazó el comprobante.", "detail": detail[:500]})
        except (URLError, TimeoutError) as exc:
            json_response(self, 502, {"ok": False, "error": f"No se pudo contactar al servicio de análisis: {exc}"})
        except Exception as exc:
            json_response(self, 500, {"ok": False, "error": str(exc)})


if __name__ == "__main__":
    print(f"Finanzas claras en http://{HOST}:{PORT} · modelo {MODEL}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
