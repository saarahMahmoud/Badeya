/**
 * بادية — Google Sheets: orders + product catalog
 *
 * Works with your EXISTING "badeya.order" spreadsheet.
 * Orders keep going to your current tab — we only ADD a "Products" tab.
 *
 * Setup (on your existing sheet):
 * 1. Open badeya.order → Extensions -> Apps Script
 * 2. Replace all code with this file
 * 3. Run setupProducts() once (creates Products tab + sample rows)
 * 4. Deploy -> Manage deployments -> Edit -> New version -> Deploy
 *    (same /exec URL — no change needed in index.html)
 *
 * Orders:  POST  <WEB_APP_URL>           (unchanged)
 * Products: GET   <WEB_APP_URL>?action=products
 */

// Leave blank to auto-use your first tab (existing orders). Or set exact tab name.
var ORDERS_SHEET = "";
var PRODUCTS_SHEET = "Products";

var PRODUCT_HEADERS = [
  "active", "id", "img", "name", "size", "desc", "price", "was", "tag", "sort"
];

function getOrdersSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  if (ORDERS_SHEET) {
    var named = ss.getSheetByName(ORDERS_SHEET);
    if (named) return named;
  }
  var sheets = ss.getSheets();
  for (var i = 0; i < sheets.length; i++) {
    if (sheets[i].getName() !== PRODUCTS_SHEET) return sheets[i];
  }
  return ss.getActiveSheet();
}

/** Run once — only creates the Products tab. Does NOT touch your orders tab. */
function setupProducts() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  var products = ss.getSheetByName(PRODUCTS_SHEET) || ss.insertSheet(PRODUCTS_SHEET);
  if (products.getLastRow() === 0) {
    products.appendRow(PRODUCT_HEADERS);
    products.appendRow([
      "yes", "fullpack", "images/hero.jpg", "الباكدج الكاملة", "عرض خاص",
      "لتر زيت زيتون + زيت شعر 200 مل + شامبو 300 مل + ٢ صابونة 120 جم — وفّر ٥١ ج.م",
      999, 1050, "عرض", 1
    ]);
    products.appendRow([
      "yes", "oil1l", "images/oil750.jpg", "زيت زيتون أورجانيك", "1 لتر",
      "عصرة أولى على البارد من زيتون مطروح البلدي. الحجم العائلي للسلطات والطبخ الصحي.",
      600, "", "", 2
    ]);
    products.appendRow([
      "yes", "oil500", "images/oil500.jpg", "زيت زيتون أورجانيك", "½ لتر",
      "نفس الجودة الممتازة في حجم مناسب للتجربة الأولى أو الهدايا.",
      350, "", "", 3
    ]);
    products.appendRow([
      "yes", "hairoil", "images/bodyoil.jpg", "زيت شعر طبيعي", "200 مل",
      "زيت زيتون نقي لتغذية الشعر وترطيبه من الجذور للأطراف.",
      175, "", "", 4
    ]);
    products.appendRow([
      "yes", "shampoo", "images/shampoo.jpg", "شامبو أورجانيك", "300 مل",
      "تنظيف لطيف وتغذية للشعر من غير سلفات أو مواد كيميائية قاسية.",
      165, "", "", 5
    ]);
    products.appendRow([
      "yes", "soap120", "images/soap.jpg", "صابون صلب طبيعي", "120 جم",
      "صابون زيت الزيتون المصنوع يدويًا. لطيف على البشرة الحساسة.",
      55, "", "", 6
    ]);
  }
}

function doGet(e) {
  if (e && e.parameter && e.parameter.action === "products") {
    return ContentService
      .createTextOutput(JSON.stringify({ products: getProducts() }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  return ContentService
    .createTextOutput(JSON.stringify({ status: "badeya endpoint is live", actions: ["products"] }))
    .setMimeType(ContentService.MimeType.JSON);
}

function getProducts() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(PRODUCTS_SHEET);
  if (!sheet || sheet.getLastRow() < 2) {
    return [];
  }

  var rows = sheet.getDataRange().getValues();
  var headers = rows[0].map(function(h) { return String(h).trim().toLowerCase(); });
  var products = [];

  for (var i = 1; i < rows.length; i++) {
    var row = rows[i];
    var item = {};
    for (var j = 0; j < headers.length; j++) {
      if (!headers[j]) continue;
      item[headers[j]] = row[j];
    }

    var active = String(item.active || "yes").toLowerCase();
    if (active === "no" || active === "false" || active === "0") continue;
    if (!item.id) continue;

    var product = {
      id: String(item.id).trim(),
      img: String(item.img || "").trim(),
      name: String(item.name || "").trim(),
      size: String(item.size || "").trim(),
      desc: String(item.desc || "").trim(),
      price: Number(item.price) || 0
    };

    if (item.was !== "" && item.was != null) product.was = Number(item.was);
    if (item.tag) product.tag = String(item.tag).trim();
    if (item.sort !== "" && item.sort != null) product.sort = Number(item.sort);

    products.push(product);
  }

  products.sort(function(a, b) {
    return (a.sort || 999) - (b.sort || 999);
  });

  return products;
}

function doPost(e) {
  if (!e || !e.postData) {
    return ContentService
      .createTextOutput(JSON.stringify({ result: "error", message: "No POST data received" }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = getOrdersSheet();

  if (sheet.getLastRow() === 0) {
    sheet.appendRow(["Timestamp", "Name", "Phone", "Address", "Notes", "Items", "Total (EGP)"]);
  }

  var data = JSON.parse(e.postData.contents);

  sheet.appendRow([
    new Date(),
    data.name || "",
    data.phone || "",
    data.address || "",
    data.notes || "",
    data.items || "",
    data.total || ""
  ]);

  return ContentService
    .createTextOutput(JSON.stringify({ result: "success" }))
    .setMimeType(ContentService.MimeType.JSON);
}

function testDoPost() {
  var fakeEvent = {
    postData: {
      contents: JSON.stringify({
        name: "عميل تجريبي",
        phone: "01016860556",
        address: "القاهرة - مدينة نصر - شارع تجريبي",
        notes: "طلب اختباري",
        items: "زيت زيتون أورجانيك (1 لتر) × 1 = 600 ج.م",
        total: 600
      })
    }
  };
  Logger.log(doPost(fakeEvent).getContent());
}

function testGetProducts() {
  Logger.log(JSON.stringify(getProducts()));
}
