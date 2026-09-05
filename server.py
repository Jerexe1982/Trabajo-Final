import base64
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).parent
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MAX_BYTES = 10 * 1024 * 1024
API_URL = "https://api.openai.com/v1/responses"

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
    if mime_type == "application/pdf":
        content_part = {"type": "input_file", "filename": filename, "file_data": f"data:application/pdf;base64,{encoded}"}
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


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def do_GET(self):
        if self.path == "/api/health":
            return json_response(self, 200, {"ok": True, "model": MODEL, "api_key_configured": bool(os.getenv("OPENAI_API_KEY"))})
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
