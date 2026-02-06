from google.oauth2 import service_account
from googleapiclient.discovery import build
from database import get_db
import re

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'service_account.json'
SPREADSHEET_ID = '1I6z9wWzmEOVLL6ZQDErC0AppWo2_u2wa4u0zy0imPcE'

PAYS_EUROPENS = [
    'Allemagne', 'Autriche', 'Belgique', 'Bulgarie', 'Chypre', 'Croatie',
    'Danemark', 'Espagne', 'Estonie', 'Finlande', 'France', 'Grèce',
    'Hongrie', 'Irlande', 'Italie', 'Lettonie', 'Lituanie', 'Luxembourg',
    'Malte', 'Pays-Bas', 'Pologne', 'Portugal', 'Roumanie', 'Slovaquie',
    'Slovénie', 'Suède', 'Albanie', 'Andorre', 'Bosnie-Herzégovine',
    'Islande', 'Liechtenstein', 'Macédoine du Nord', 'Moldavie', 'Monaco',
    'Monténégro', 'Norvège', 'Royaume-Uni', 'Saint-Marin', 'Serbie',
    'Suisse', 'Ukraine', 'Vatican'
]

def parse_duree(duree_str):
    if not duree_str or duree_str.strip() == "":
        return 0
    
    duree_str = duree_str.strip().lower()
    
    # Extraire le nombre (le premier groupe de chiffres, avec support des décimales)
    match = re.search(r'(\d+(?:[.,]\d+)?)', duree_str)
    if not match:
        print(f"Pas de nombre trouvé dans: '{duree_str}' - valeur par défaut: 7 jours")
        return 7  # Valeur par défaut si pas de nombre trouvé
    
    # Convertir en float puis en int (pour gérer "1.5 semaine" par exemple)
    nombre_str = match.group(1).replace(',', '.')
    nombre = float(nombre_str)
    
    # Déterminer l'unité et convertir en jours
    if 'jour' in duree_str:
        resultat = int(nombre)
    elif 'semaine' in duree_str:
        resultat = int(nombre * 7)
    elif 'mois' in duree_str:
        resultat = int(nombre * 30)
    elif 'an' in duree_str or 'année' in duree_str:
        resultat = int(nombre * 365)
        # Afficher un avertissement si la durée semble anormalement longue
        if resultat > 730:  # Plus de 2 ans
            print(f"Durée très longue: {duree_str} = {resultat} jours")
    else:
        # Si pas d'unité reconnue, on suppose que ce sont des jours
        print(f"Unité non reconnue dans: '{duree_str}' - interprété comme {int(nombre)} jours")
        resultat = int(nombre)
    
    return resultat

print("Connexion à Google Sheets...")

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

result = sheet.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range='A1:ZZ100'
).execute()

values = result.get('values', [])

if not values:
    print("Aucune donnée trouvée")
    exit()

print(f"{len(values)-1} réponses trouvées\n")

headers = values[0]
data_rows = values[1:]

parsed = []

print("📄 Parsing des données...\n")

for idx, row in enumerate(data_rows, start=2):
    # Compléter la ligne si nécessaire
    row = row + [""] * (len(headers) - len(row))
    entry = dict(zip(headers, row))
    
    # Extraire les informations personnelles
    nom = entry.get("Quel est votre nom ?", "").strip() or entry.get("Quel est votre nom ? ", "").strip()
    prenom = entry.get("Quel est votre prénom ?", "").strip() or entry.get("  Quel est votre prénom ?  ", "").strip()
    pays_origine = entry.get("Quel est votre pays d'origine ?", "").strip() or entry.get("Quel est votre pays d'origine ?  ", "").strip()
    
    if not nom or not prenom or not pays_origine:
        print(f"Ligne {idx} ignorée (informations manquantes)")
        continue
    
    nom_complet = f"{prenom} {nom}".strip()
    
    # Parser les voyages
    voyages = []
    
    for pays in PAYS_EUROPENS:
        # Chercher les colonnes pour ce pays
        col_visite = f"Avez-vous visité {pays} ?"
        col_duree = f"Combien de temps êtes-vous resté(e) en {pays} ?"
        
        a_visite = entry.get(col_visite, "").strip()
        duree_str = entry.get(col_duree, "").strip()
        
        # Si la personne a visité ce pays
        if a_visite.lower() == "oui" and duree_str:
            jours = parse_duree(duree_str)
            
            if jours > 0:
                voyages.append({
                    'pays': pays,
                    'jours': jours,
                    'duree_originale': duree_str
                })
    
    if voyages:
        parsed.append({
            'nom': nom_complet,
            'pays_origine': pays_origine,
            'voyages': voyages
        })
        
        print(f"{nom_complet} ({pays_origine}) - {len(voyages)} pays visités")
    else:
        print(f"{nom_complet} - Aucun voyage enregistré")

print("\n" + "="*70)
print("DONNÉES PARSÉES")
print("="*70)

for e in parsed:
    print("\n" + "-"*70)
    print(f"{e['nom']}")
    print(f"Pays d'origine: {e['pays_origine']}")
    print(f"Voyages ({len(e['voyages'])}):")
    for voyage in e['voyages']:
        print(f"   - {voyage['pays']}: {voyage['jours']} jours ({voyage['duree_originale']})")

print("\n" + "="*70)
print(f"Total: {len(parsed)} personnes avec des voyages")
print("="*70 + "\n")

db = get_db()

if db:
    print("Début de l'importation en base de données...\n")
    
    total_personnes_traitees = 0
    total_personnes_nouvelles = 0
    total_voyages = 0
    
    for entry in parsed:
        personne_id = db.insert_personne(entry['nom'], entry['pays_origine'])
        
        if personne_id:
            total_personnes_traitees += 1
            
            for voyage in entry['voyages']:
                if db.insert_voyage(personne_id, voyage['pays'], voyage['jours']):
                    total_voyages += 1
    
    db.commit()
    
    print("\n" + "="*70)
    print("RÉSUMÉ DE L'IMPORTATION")
    print("="*70)
    print(f"Personnes traitées: {total_personnes_traitees}")
    print(f"Voyages ajoutés: {total_voyages}")
    print("="*70 + "\n")
    
    db.afficher_stats()
    
    db.close()
    
    print("Importation terminée avec succès!\n")
else:
    print("Impossible de se connecter à la base de données")