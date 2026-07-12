/**
 * بادية — Google Sheets order logger.
 *
 * Setup:
 * 1. Go to https://sheet.new to create a fresh Google Sheet. Rename it "Badeya Orders".
 * 2. In the sheet, Extensions -> Apps Script.
 * 3. Delete any starter code and paste this whole file in.
 * 4. Click "Deploy" -> "New deployment" -> gear icon -> "Web app".
 *    - Description: badeya orders
 *    - Execute as: Me
 *    - Who has access: Anyone
 * 5. Click Deploy, authorize the permissions Google asks for (it's your own script).
 * 6. Copy the "Web app URL" it gives you (ends with /exec).
 * 7. Paste that URL into index.html as the value of SHEET_WEBAPP_URL.
 *
 * Every order submitted on the site will now also append a row to this sheet
 * (Timestamp, Name, Phone, Address, Notes, Items, Total) as a backup record,
 * independent of WhatsApp.
 */
function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

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

function doGet() {
  return ContentService
    .createTextOutput(JSON.stringify({ status: "badeya orders endpoint is live" }))
    .setMimeType(ContentService.MimeType.JSON);
}
