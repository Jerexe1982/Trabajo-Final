const STORAGE_KEY = 'finanzas-claras-gastos-v1';
const seed = [
  {id:1, description:'Supermercado', amount:48250, category:'Alimentación', date:'2026-09-02', note:''},
  {id:2, description:'Carga SUBE', amount:12500, category:'Transporte', date:'2026-09-03', note:''},
  {id:3, description:'Alquiler', amount:310000, category:'Vivienda y servicios', date:'2026-09-01', note:'Septiembre'},
  {id:4, description:'Café y medialunas', amount:6800, category:'Alimentación', date:'2026-09-04', note:''},
  {id:5, description:'Farmacia', amount:18700, category:'Salud', date:'2026-09-05', note:''}
];
let expenses = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null') || seed;
let selectedReceipt = null;
const $ = id => document.getElementById(id);
const money = value => new Intl.NumberFormat('es-AR',{style:'currency',currency:'ARS',maximumFractionDigits:0}).format(value);
const dateLabel = value => new Intl.DateTimeFormat('es-AR',{day:'2-digit',month:'short'}).format(new Date(`${value}T12:00:00`)).replace('.','');
const currentMonth = () => $('month-picker').value || new Date().toISOString().slice(0,7);
function save(){localStorage.setItem(STORAGE_KEY, JSON.stringify(expenses));}
function render(){
  const month=currentMonth(), search=($('search').value||'').toLowerCase();
  const monthExpenses=expenses.filter(e=>e.date.startsWith(month));
  const visible=monthExpenses.filter(e=>`${e.description} ${e.category} ${e.note}`.toLowerCase().includes(search)).sort((a,b)=>b.date.localeCompare(a.date));
  const total=monthExpenses.reduce((s,e)=>s+Number(e.amount),0);
  $('total-spent').textContent=money(total); $('chart-total').textContent=money(total); $('movement-count').textContent=monthExpenses.length;
  const grouped=monthExpenses.reduce((acc,e)=>(acc[e.category]=(acc[e.category]||0)+Number(e.amount),acc),{});
  const categories=Object.entries(grouped).sort((a,b)=>b[1]-a[1]); const top=categories[0];
  $('top-category').textContent=top?top[0]:'—'; $('top-category-value').textContent=top?`${money(top[1])} en este período`:'Sin movimientos todavía';
  $('comparison').textContent=total?'Período seleccionado':'Agregá un gasto para comenzar';
  $('category-chart').innerHTML=categories.map(([name,value])=>`<div class="bar-line"><span>${name}</span><div class="bar-track"><div class="bar" style="width:${Math.max(4,(value/(top?.[1]||1))*100)}%"></div></div><span class="bar-value">${money(value)}</span></div>`).join('');
  $('chart-empty').style.display=categories.length?'none':'block';
  $('expense-table').innerHTML=visible.map(e=>`<tr><td>${escapeHtml(e.description)}${e.note?`<small class="muted"> · ${escapeHtml(e.note)}</small>`:''}${e.receipt?`<small class="muted"> · 📎 ${escapeHtml(e.receipt.name)}</small>`:''}</td><td><span class="category-pill">${escapeHtml(e.category)}</span></td><td>${dateLabel(e.date)}</td><td class="align-right">${money(e.amount)}</td><td class="align-right"><button class="delete-btn" data-id="${e.id}" title="Eliminar gasto" aria-label="Eliminar ${escapeHtml(e.description)}">×</button></td></tr>`).join('');
  $('table-empty').classList.toggle('hidden',visible.length>0);
}
function escapeHtml(text){return String(text).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}
function setDefaults(){const now=new Date(); $('month-picker').value=now.toISOString().slice(0,7); $('date').value=now.toISOString().slice(0,10);}
function handleReceipt(file){if(!file)return;selectedReceipt={name:file.name,type:file.type||'archivo',size:file.size};$('attachment-status').textContent=file.type==='application/pdf'?'PDF listo para analizar':'Imagen lista para analizar';$('attachment-preview').classList.remove('hidden');$('attachment-preview').innerHTML=`<span class="receipt-name">📎 ${escapeHtml(file.name)}<small>${file.type==='application/pdf'?'Documento PDF':'Imagen'} · ${(file.size/1024).toFixed(0)} KB</small></span><button type="button" id="remove-attachment" aria-label="Quitar comprobante">×</button>`;$('remove-attachment').addEventListener('click',clearReceipt);}
function clearReceipt(){selectedReceipt=null;$('receipt-file').value='';$('receipt-camera').value='';$('attachment-preview').classList.add('hidden');$('attachment-preview').innerHTML='';$('attachment-status').textContent='Podés adjuntar una foto o un PDF';}
$('receipt-file').addEventListener('change',event=>handleReceipt(event.target.files[0]));$('receipt-camera').addEventListener('change',event=>handleReceipt(event.target.files[0]));
$('expense-form').addEventListener('submit',event=>{event.preventDefault();const data=new FormData(event.target);expenses.push({id:Date.now(),description:data.get('description').trim(),amount:Number(data.get('amount')),category:data.get('category'),date:data.get('date'),note:data.get('note').trim(),receipt:selectedReceipt});save();event.target.reset();clearReceipt();$('date').value=$('month-picker').value+'-01';render();});
$('month-picker').addEventListener('change',render); $('search').addEventListener('input',render);
$('expense-table').addEventListener('click',event=>{const btn=event.target.closest('[data-id]');if(!btn)return;expenses=expenses.filter(e=>e.id!==Number(btn.dataset.id));save();render();});
$('export-btn').addEventListener('click',()=>{const blob=new Blob([JSON.stringify(expenses.filter(e=>e.date.startsWith(currentMonth())),null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=`gastos_${currentMonth()}.json`;a.click();URL.revokeObjectURL(url);});
setDefaults();render();
