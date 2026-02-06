from typing import Union
from database import get_db, DB_CONFIG
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import subprocess
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Voyage",
    description="API pour gérer les données de voyage en Europe",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Page d'accueil de l'API"""
    return {
        "message": "API Voyage - Gestion de données de voyages en Europe",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "Cette page",
            "GET /data": "Récupérer toutes les données",
            "GET /data/country/{pays}": "Récupérer les données par pays visité",
            "GET /data/person/{nom}": "Récupérer les données par personne",
            "GET /personnes": "Récupérer toutes les personnes avec leurs voyages",
            "GET /stats": "Récupérer les statistiques",
            "POST /import": "Importer les données depuis Google Sheets"
        }
    }

@app.get("/data")
async def get_all_data(limit: int = 1000, offset: int = 0):
    try:
        db = get_db()
        if not db:
            raise HTTPException(status_code=500, detail="Impossible de se connecter à la base de données")
        
        data = db.get_all_data(limit=limit, offset=offset)
        db.close()
        return data
    except Exception as e:
        logger.exception("Erreur lors de la récupération des données")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/personnes")
async def get_all_personnes():
    try:
        db = get_db()
        if not db:
            raise HTTPException(status_code=500, detail="Impossible de se connecter à la base de données")
        
        data = db.get_all_personnes()
        db.close()
        return {
            "status": "success",
            "count": len(data),
            "personnes": data
        }
    except Exception as e:
        logger.exception("Erreur lors de la récupération des personnes")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/person/{nom}")
async def get_data_by_person(nom: str):
    try:
        db = get_db()
        if not db:
            raise HTTPException(status_code=500, detail="Impossible de se connecter à la base de données")
        
        data = db.get_data_by_person(nom)
        db.close()
        
        if not data:
            raise HTTPException(status_code=404, detail=f"Aucune donnée trouvée pour {nom}")
        
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur lors de la récupération des données par personne")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/country/{pays}")
async def get_data_by_country(pays: str):
    try:
        db = get_db()
        if not db:
            raise HTTPException(status_code=500, detail="Impossible de se connecter à la base de données")
        
        data = db.get_data_by_country(pays)
        db.close()
        
        if not data:
            raise HTTPException(status_code=404, detail=f"Aucune donnée trouvée pour {pays}")
        
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur lors de la récupération des données par pays")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    try:
        db = get_db()
        if not db:
            raise HTTPException(status_code=500, detail="Impossible de se connecter à la base de données")
        
        stats = db.get_stats()
        db.close()
        
        if not stats:
            raise HTTPException(status_code=500, detail="Erreur lors de la récupération des statistiques")
        
        return {
            "status": "success",
            "stats": stats
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur lors de la récupération des statistiques")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/import")
async def import_google_sheet():
    try:
        logger.info("Démarrage de l'import Google Sheets...")
        
        # Exécuter le script googlesheet.py
        result = subprocess.run(
            [sys.executable, "googlesheet.py"],
            capture_output=True,
            text=True,
            timeout=60  # Timeout de 60 secondes
        )
        
        # Vérifier si l'exécution a réussi
        if result.returncode == 0:
            logger.info("Import Google Sheets terminé avec succès")
            return {
                "status": "success",
                "message": "Import depuis Google Sheets terminé avec succès",
                "output": result.stdout
            }
        else:
            logger.error(f"Erreur lors de l'import: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de l'import: {result.stderr}"
            )
    
    except subprocess.TimeoutExpired:
        logger.error("Timeout lors de l'import Google Sheets")
        raise HTTPException(
            status_code=500,
            detail="Timeout: L'import a pris trop de temps (> 60s)"
        )
    except FileNotFoundError:
        logger.error("Fichier googlesheet.py introuvable")
        raise HTTPException(
            status_code=500,
            detail="Le fichier googlesheet.py est introuvable"
        )
    except Exception as e:
        logger.exception("Erreur inattendue lors de l'import")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("DÉMARRAGE DE L'API VOYAGE")
    print("="*70)
    print(f"Base de données: {DB_CONFIG['database']}")
    print(f"URL: http://localhost:8000")
    print(f"Documentation: http://localhost:8000/docs")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)