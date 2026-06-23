# Y.M.I Roofing — Google Sheets Setup

## Sheet 1: "Leads" (for lead-capture.json)
Create these column headers in Row 1:

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| Timestamp | Name | Phone | Suburb | Service | Message | Source |

## Sheet 2: "Jobs" (for review-machine.json)
Create these column headers in Row 1:

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| Job Date | Customer Name | Customer Phone | Suburb | Review Requested | Review Received |

## Sheet 3: "Monthly Summary" (for reporting)
Create these column headers in Row 1:

| A | B | C | D | E |
|---|---|---|---|---|
| Month | Leads Received | Jobs Completed | Reviews Requested | Reviews Received |

---

## How to get your Sheet ID:
1. Open the Google Sheet
2. Look at the URL: https://docs.google.com/spreadsheets/d/SHEET_ID_IS_HERE/edit
3. Copy the long string between /d/ and /edit
4. Paste it into both n8n workflows where it says REPLACE_SHEET_ID
