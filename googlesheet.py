from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'service_account.json'
SPREADSHEET_ID = '1I6z9wWzmEOVLL6ZQDErC0AppWo2_u2wa4u0zy0imPcE'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

service = build('sheets', 'v4', credentials=credentials)

sheet = service.spreadsheets()
result = sheet.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range='A1:Z100'
).execute()

values = result.get('values', [])

if not values:
    print("Aucune donnée trouvée")
    exit()


headers = values[0]
data_rows = values[1:]

parsed = []

for row in data_rows:
    row = row + [""] * (len(headers) - len(row))
    entry = dict(zip(headers, row))
    
    print("hearders : ",headers,"row : ",row)
    # pays = entry["Quel pays as tu visités ?"]
    # liste_pays = [p.strip() for p in pays.split(",")]
    pays = entry["Quels pays as tu visités ?"]
    entry["liste_pays"] = [p.strip() for p in pays.split(",")if p.strip()]
    parsed.append(entry)


for e in parsed:
    print("-----")
    print("Prénom :", e.get("Quel est votre prénom ?"))
    print("Pays d'origine :", e.get("Quel est votre pays d'origine ?"))
    print("Pays visités :", e["liste_pays"])
