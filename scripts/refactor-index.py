import re

INDEX = r"c:\Users\Sara\badeya\index.html"

with open(INDEX, "r", encoding="utf-8") as f:
    html = f.read()

new_script = r'''const WA_NUMBER = "201016860556";
// نفس رابط Apps Script — بيقرأ المنتجات بـ ?action=products وبيسجّل الطلبات بـ POST
const SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxpVhOSmdA30U1NmNxFPDxDXVB3RKiEt_FjvjrowdXAkBeHBHa1-zQLfLriYj6bxNxtEA/exec";
const HERO_IMG = "images/hero.jpg";
let PRODUCTS = [];

async function loadProducts(){
  if(SHEET_WEBAPP_URL && !SHEET_WEBAPP_URL.includes("PASTE_YOUR")){
    try{
      const r = await fetch(SHEET_WEBAPP_URL + "?action=products");
      const data = await r.json();
      if(Array.isArray(data.products) && data.products.length){
        return data.products.filter(p => p.active !== false && p.id);
      }
    }catch(e){ /* fallback to products.json */ }
  }
  const r = await fetch("products.json");
  if(!r.ok) throw new Error("products.json unavailable");
  return r.json();
}

document.getElementById("heroImg").src = HERO_IMG;

let cart = {};
try{ cart = JSON.parse(localStorage.getItem("badeya_cart")) || {}; }catch(e){ cart = {}; }
function saveCart(){ localStorage.setItem("badeya_cart", JSON.stringify(cart)); }

const grid = document.getElementById("prodGrid");

function renderProducts(){
  grid.innerHTML = "";
  PRODUCTS.forEach(p=>{
    const card = document.createElement("div");
    card.className = "prod-card reveal" + (p.tag ? " bundle" : "");
    const tagClass = p.tag ? "size-tag offer" : "size-tag";
    const priceHtml = p.was
      ? `<span class="price"><span class="price-was">${p.was} ج.م</span>${p.price} <small>ج.م</small></span>`
      : `<span class="price">${p.price} <small>ج.م</small></span>`;
    card.innerHTML = `
      <div class="prod-photo"><img src="${p.img}" alt="${p.name} — ${p.size}" loading="lazy"></div>
      <span class="${tagClass}">${p.tag || p.size}</span>
      <h3>${p.name}</h3>
      <p class="desc">${p.desc}</p>
      <div class="prod-meta">
        ${priceHtml}
        <button class="add-btn" data-id="${p.id}" onclick="addToCart('${p.id}', this)">أضف للسلة +</button>
      </div>`;
    grid.appendChild(card);
    io.observe(card);
  });
}

async function initProducts(){
  grid.innerHTML = `<div class="cart-empty" style="grid-column:1/-1"><span class="icon">🫒</span>جاري تحميل المنتجات...</div>`;
  try{
    PRODUCTS = await loadProducts();
    renderProducts();
    renderCart();
  }catch(e){
    grid.innerHTML = `<div class="cart-empty" style="grid-column:1/-1"><span class="icon">⚠️</span>تعذّر تحميل المنتجات — حدّث الصفحة</div>`;
  }
}

function addToCart(id, btn){
  cart[id] = (cart[id]||0)+1;
  saveCart();
  renderCart();
  if(btn){
    btn.classList.add("added"); btn.textContent = "اتضاف ✓";
    setTimeout(()=>{btn.classList.remove("added"); btn.textContent="أضف للسلة +";},1200);
  }
  showToast("اتضاف للسلة 🧺");
}
function changeQty(id, d){
  cart[id] = (cart[id]||0)+d;
  if(cart[id]<=0) delete cart[id];
  saveCart();
  renderCart();
}
function cartItems(){
  return Object.entries(cart).map(([id,q])=>{
    const p = PRODUCTS.find(x=>x.id===id);
    return p ? {...p, qty:q} : null;
  }).filter(Boolean);
}
function cartTotal(){ return cartItems().reduce((s,i)=>s+i.price*i.qty,0); }

function renderCart(){
  const items = cartItems();
  const body = document.getElementById("cartBody");
  const count = items.reduce((s,i)=>s+i.qty,0);
  document.getElementById("cartCount").textContent = count;
  document.getElementById("cartCountMobile").textContent = count;
  document.getElementById("cartTotal").textContent = cartTotal().toLocaleString("ar-EG") + " ج.م";
  if(!items.length){
    body.innerHTML = `<div class="cart-empty"><span class="icon">🫒</span>سلتك لسه فاضية —<br>اختار خيرك من المنتجات!</div>`;
    return;
  }
  body.innerHTML = items.map(i=>`
    <div class="cart-item">
      <img class="cart-thumb" src="${i.img}" alt="">

      <div class="info"><h4>${i.name} — ${i.size}</h4><span>${i.price} ج.م × ${i.qty} = <b>${i.price*i.qty} ج.م</b></span></div>
      <div class="qty">
        <button onclick="changeQty('${i.id}',1)" aria-label="زيادة">+</button>
        <span class="n">${i.qty}</span>
        <button onclick="changeQty('${i.id}',-1)" aria-label="نقصان">−</button>
      </div>
    </div>`).join("");
}

function toggleCart(open){
  document.getElementById("drawer").classList.toggle("open", open);
  document.getElementById("overlay").classList.toggle("open", open);
  document.body.style.overflow = open ? "hidden" : "";
}

function fieldError(inputId, errId, message){
  const input = document.getElementById(inputId);
  const err = document.getElementById(errId);
  if(message){
    input.classList.add("error");
    err.textContent = message; err.hidden = false;
  }else{
    input.classList.remove("error");
    err.hidden = true;
  }
}

function validOrderForm(name, phone, address){
  let ok = true;
  if(!name){ fieldError("fName","errName","اكتب الاسم بالكامل"); ok = false; }
  else fieldError("fName","errName","");

  const phoneDigits = phone.replace(/[^\d]/g,"").replace(/^20/,"0");
  const phoneOk = /^01[0125]\d{8}$/.test(phoneDigits);
  if(!phone || !phoneOk){ fieldError("fPhone","errPhone","اكتب رقم موبايل مصري صحيح (01xxxxxxxxx)"); ok = false; }
  else fieldError("fPhone","errPhone","");

  if(!address){ fieldError("fAddress","errAddress","اكتب العنوان بالتفصيل"); ok = false; }
  else fieldError("fAddress","errAddress","");

  return ok;
}

async function sendOrder(){
  const items = cartItems();
  if(!items.length){ showToast("أضف منتجات للسلة الأول 🫒"); return; }
  const name = document.getElementById("fName").value.trim();
  const phone = document.getElementById("fPhone").value.trim();
  const address = document.getElementById("fAddress").value.trim();
  const notes = document.getElementById("fNotes").value.trim();
  if(!validOrderForm(name, phone, address)){ showToast("راجع بيانات الطلب 🙏"); return; }

  const itemsLine = items.map(i=>`${i.name} (${i.size}) × ${i.qty} = ${i.price*i.qty} ج.م`).join(" | ");

  const btn = document.getElementById("waOrder");
  btn.disabled = true; btn.classList.add("loading");
  const originalLabel = btn.textContent;
  btn.textContent = "جاري إرسال الطلب...";

  if(SHEET_WEBAPP_URL && !SHEET_WEBAPP_URL.includes("PASTE_YOUR")){
    try{
      await fetch(SHEET_WEBAPP_URL, {
        method: "POST",
        mode: "no-cors",
        headers: {"Content-Type": "text/plain;charset=utf-8"},
        body: JSON.stringify({ name, phone, address, notes, items: itemsLine, total: cartTotal() })
      });
    }catch(e){}
  }

  let msg = "🫒 *طلب جديد من موقع بادية*\n\n";
  items.forEach(i=>{ msg += `• ${i.name} (${i.size}) × ${i.qty} = ${i.price*i.qty} ج.م\n`; });
  msg += `\n*الإجمالي: ${cartTotal()} ج.م*\n\n`;
  msg += `👤 الاسم: ${name}\n📱 الموبايل: ${phone}\n📍 العنوان: ${address}`;
  if(notes) msg += `\n📝 ملاحظات: ${notes}`;

  window.open(`https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(msg)}`, "_blank");

  btn.disabled = false; btn.classList.remove("loading"); btn.textContent = originalLabel;
  cart = {}; saveCart(); renderCart(); toggleCart(false);
  showToast("تم إرسال طلبك ✅");
}

document.getElementById("waFooter").href = `https://wa.me/${WA_NUMBER}`;
document.getElementById("waFloat").href = `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent("عايز أستفسر عن منتجات بادية 🫒")}`;

["fName","fPhone","fAddress"].forEach(id=>{
  const el = document.getElementById(id);
  const saved = localStorage.getItem("badeya_"+id);
  if(saved) el.value = saved;
  el.addEventListener("input", ()=> localStorage.setItem("badeya_"+id, el.value));
});

function showToast(t){
  const el = document.getElementById("toast");
  el.textContent = t; el.classList.add("show");
  clearTimeout(el._t); el._t = setTimeout(()=>el.classList.remove("show"), 2200);
}

const io = new IntersectionObserver(es=>es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add("in"); io.unobserve(e.target);} }),{threshold:.12});
document.querySelectorAll(".reveal").forEach(el=>io.observe(el));

initProducts();
renderCart();'''

pattern = re.compile(
    r"const WA_NUMBER = .*?renderCart\(\);\s*</script>",
    re.DOTALL,
)

match = pattern.search(html)
if not match:
    raise SystemExit("Script block not found")

html = html[: match.start()] + new_script + "\n</script>" + html[match.end() :]

with open(INDEX, "w", encoding="utf-8") as f:
    f.write(html)

print(f"index.html updated — removed inline IMGS/PRODUCTS ({len(html)} chars)")
