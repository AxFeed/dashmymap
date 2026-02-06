from typing import Union
from database import get_db, DB_CONFIG
from fastapi import FastAPI

app = FastAPI()



@app.get("/")
def read_root():
    return {"Hello": "World"}

#! récupérer bdd 
#! 
#! 1️⃣ Import / synchro des données


@app.get("/readdata")
def read_data():
    db = get_db()
    data = db.get_all_data()
    db.close()
    return data

#! 2️⃣ Liste des personnes (pour Dash)
@app.get("/people")
def affiche_data():
    db = get_db()
    data = db.get_all_personnes()
    db.close()
    return data

#! 3️⃣ Pays visités par une personne (carte)
@app.get("/people/{name}/")

def peoplebyname():
    db =get_db()
    data = db.get_data_by_person()
    db.close()
    return data

#! 3️⃣ Pays visités par une personne (carte)
@app.get("/data/{country}/")
def countrybynamecountry():
    db = get_db()
    data = db.get_data_by_country()
    db.close()
    return


#? POST /sync/google-sheet
@app.post("/sync/google-sheet")
def updatedata():
    return

@app.get("/allcountry")
def all_country():
    return

#TODO Stat des gens 