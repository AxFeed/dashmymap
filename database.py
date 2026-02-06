"""
Gestionnaire de base de données pour le projet voyage
Toutes les opérations de base de données sont centralisées ici
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# ===========================
# CONFIGURATION CENTRALISÉE
# ===========================

DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'admin123',  # ⚠️ À MODIFIER
    'port': 5432
}


class DatabaseManager:
    """Gestionnaire de base de données pour le projet voyage"""

    def __init__(self, host=None, database=None, user=None, password=None, port=None):
        """
        Initialise la connexion à la base de données
        Si aucun paramètre n'est fourni, utilise la configuration par défaut

        Args:
            host: Hôte de la base de données (défaut: depuis DB_CONFIG)
            database: Nom de la base de données (défaut: depuis DB_CONFIG)
            user: Nom d'utilisateur (défaut: depuis DB_CONFIG)
            password: Mot de passe (défaut: depuis DB_CONFIG)
            port: Port de connexion (défaut: depuis DB_CONFIG)
        """
        self.config = {
            'host': host or DB_CONFIG['host'],
            'database': database or DB_CONFIG['database'],
            'user': user or DB_CONFIG['user'],
            'password': password or DB_CONFIG['password'],
            'port': port or DB_CONFIG['port'],
            'client_encoding': 'UTF8'
        }
        self.conn = None
        self.cursor = None

    def connect(self) -> bool:
        """
        Établit la connexion à la base de données

        Returns:
            True si connexion réussie, False sinon
        """
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor()
            self.cursor.execute("SET client_encoding TO 'UTF8';")
            logger.info(f"Connexion à la base de données '{self.config['database']}' réussie")
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion à la base de données: {e}")
            return False

    def close(self):
        """Ferme la connexion à la base de données"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Connexion fermée")

    # ============================================================
    # MÉTHODES D'INSERTION
    # ============================================================

    def insert_personne(self, nom: str, pays_origine: str) -> Optional[int]:
        """
        Insère ou récupère une personne

        Args:
            nom: Nom complet de la personne
            pays_origine: Pays d'origine

        Returns:
            ID de la personne (int) ou None en cas d'erreur
        """
        try:
            # Vérifier si la personne existe déjà
            self.cursor.execute(
                "SELECT id FROM personnes WHERE nom = %s AND pays_origine = %s",
                (nom, pays_origine)
            )
            existing = self.cursor.fetchone()

            if existing:
                logger.info(f"Personne existante: {nom}")
                return existing[0]
            else:
                # Insérer la nouvelle personne
                self.cursor.execute(
                    "INSERT INTO personnes (nom, pays_origine) VALUES (%s, %s) RETURNING id",
                    (nom, pays_origine)
                )
                personne_id = self.cursor.fetchone()[0]
                logger.info(f"Nouvelle personne créée: {nom} (ID: {personne_id})")
                return personne_id

        except Exception as e:
            logger.error(f"Erreur lors de l'insertion de la personne: {e}")
            return None

    def insert_voyage(self, personne_id: int, pays_visite: str, jours: int = 7) -> bool:
        """
        Insère un voyage

        Args:
            personne_id: ID de la personne
            pays_visite: Pays visité
            jours: Nombre de jours (défaut: 7)

        Returns:
            True si insertion réussie, False sinon
        """
        try:
            # Vérifier si ce voyage existe déjà
            self.cursor.execute(
                "SELECT id FROM voyages WHERE personne_id = %s AND pays_visite = %s",
                (personne_id, pays_visite)
            )

            if self.cursor.fetchone():
                logger.info(f"Voyage existant ignoré: {pays_visite}")
                return False

            # Insérer le voyage
            self.cursor.execute(
                "INSERT INTO voyages (personne_id, pays_visite, jours) VALUES (%s, %s, %s)",
                (personne_id, pays_visite, jours)
            )
            logger.info(f"Voyage ajouté: {pays_visite} ({jours} jours)")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'insertion du voyage: {e}")
            return False

    def insert_personne_avec_voyages(self, nom: str, pays_origine: str, liste_pays: List[str], jours: int = 7) -> Tuple[int, Optional[int]]:
        """
        Insère une personne et tous ses voyages

        Args:
            nom: Nom complet
            pays_origine: Pays d'origine
            liste_pays: Liste des pays visités
            jours: Nombre de jours par voyage (défaut: 7)

        Returns:
            Tuple (nombre_voyages_insérés, personne_id)
        """
        personne_id = self.insert_personne(nom, pays_origine)

        if not personne_id:
            return (0, None)

        voyages_inseres = 0
        for pays in liste_pays:
            if self.insert_voyage(personne_id, pays, jours):
                voyages_inseres += 1

        return (voyages_inseres, personne_id)

    # ============================================================
    # MÉTHODES DE RÉCUPÉRATION (POUR L'API)
    # ============================================================

    def get_all_data(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Récupère toutes les données avec pagination

        Args:
            limit: Nombre maximum d'enregistrements
            offset: Décalage pour la pagination

        Returns:
            Liste de dictionnaires avec les données
        """
        try:
            self.cursor.execute("""
                SELECT 
                    v.id,
                    p.nom,
                    p.pays_origine,
                    v.pays_visite,
                    v.jours
                FROM voyages v
                JOIN personnes p ON v.personne_id = p.id
                ORDER BY v.id
                LIMIT %s OFFSET %s
            """, (limit, offset))

            rows = self.cursor.fetchall()

            result = []
            for row in rows:
                result.append({
                    'id': row[0],
                    'nom': row[1],
                    'pays_origine': row[2],
                    'pays_visite': row[3],
                    'jours': row[4]
                })

            return result

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données: {e}")
            return []

    def get_data_by_country(self, pays: str) -> List[Dict]:
        """
        Récupère les données pour un pays visité spécifique

        Args:
            pays: Nom du pays visité

        Returns:
            Liste de dictionnaires avec les données
        """
        try:
            self.cursor.execute("""
                SELECT 
                    v.id,
                    p.nom,
                    p.pays_origine,
                    v.pays_visite,
                    v.jours
                FROM voyages v
                JOIN personnes p ON v.personne_id = p.id
                WHERE v.pays_visite = %s
                ORDER BY v.id
            """, (pays,))

            rows = self.cursor.fetchall()

            result = []
            for row in rows:
                result.append({
                    'id': row[0],
                    'nom': row[1],
                    'pays_origine': row[2],
                    'pays_visite': row[3],
                    'jours': row[4]
                })

            return result

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données par pays: {e}")
            return []

    def get_data_by_person(self, nom: str) -> List[Dict]:
        """
        Récupère les données pour une personne spécifique

        Args:
            nom: Nom de la personne

        Returns:
            Liste de dictionnaires avec les données
        """
        try:
            self.cursor.execute("""
                SELECT 
                    v.id,
                    p.nom,
                    p.pays_origine,
                    v.pays_visite,
                    v.jours
                FROM voyages v
                JOIN personnes p ON v.personne_id = p.id
                WHERE p.nom ILIKE %s
                ORDER BY v.id
            """, (f'%{nom}%',))

            rows = self.cursor.fetchall()

            result = []
            for row in rows:
                result.append({
                    'id': row[0],
                    'nom': row[1],
                    'pays_origine': row[2],
                    'pays_visite': row[3],
                    'jours': row[4]
                })

            return result

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données par personne: {e}")
            return []

    def get_all_personnes(self) -> List[Dict]:
        """
        Récupère toutes les personnes avec leurs voyages

        Returns:
            Liste de dictionnaires avec les personnes et leurs voyages
        """
        try:
            self.cursor.execute("""
                SELECT 
                    p.id, 
                    p.nom, 
                    p.pays_origine, 
                    v.pays_visite, 
                    v.jours
                FROM personnes p
                LEFT JOIN voyages v ON p.id = v.personne_id
                ORDER BY p.id
            """)

            rows = self.cursor.fetchall()

            # Regrouper les voyages par personne
            personnes = {}
            for row in rows:
                pid, nom, pays_origine, pays_visite, jours = row

                if pid not in personnes:
                    personnes[pid] = {
                        "id": pid,
                        "nom": nom,
                        "pays_origine": pays_origine,
                        "voyages": []
                    }

                if pays_visite:
                    personnes[pid]["voyages"].append({
                        "pays": pays_visite,
                        "jours": jours
                    })

            return list(personnes.values())

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des personnes: {e}")
            return []

    def get_stats(self) -> Optional[Dict]:
        """
        Récupère les statistiques de la base de données

        Returns:
            Dictionnaire avec les statistiques complètes
        """
        try:
            stats = {}

            # Nombre total de personnes
            self.cursor.execute("SELECT COUNT(*) FROM personnes")
            stats['nb_personnes'] = self.cursor.fetchone()[0]

            # Nombre total de voyages
            self.cursor.execute("SELECT COUNT(*) FROM voyages")
            stats['nb_voyages'] = self.cursor.fetchone()[0]

            # Nombre de pays différents visités
            self.cursor.execute("SELECT COUNT(DISTINCT pays_visite) FROM voyages")
            stats['nb_pays'] = self.cursor.fetchone()[0]

            # Pays le plus visité
            self.cursor.execute("""
                SELECT pays_visite, COUNT(*) as nb_visites
                FROM voyages
                GROUP BY pays_visite
                ORDER BY nb_visites DESC
                LIMIT 1
            """)
            pays_plus_visite = self.cursor.fetchone()
            if pays_plus_visite:
                stats['pays_plus_visite'] = {
                    'pays': pays_plus_visite[0],
                    'nombre_visites': pays_plus_visite[1]
                }

            # Personne ayant visité le plus de pays
            self.cursor.execute("""
                SELECT p.nom, COUNT(DISTINCT v.pays_visite) as nb_pays
                FROM personnes p
                JOIN voyages v ON p.id = v.personne_id
                GROUP BY p.id, p.nom
                ORDER BY nb_pays DESC
                LIMIT 1
            """)
            personne_plus_voyage = self.cursor.fetchone()
            if personne_plus_voyage:
                stats['personne_plus_voyage'] = {
                    'nom': personne_plus_voyage[0],
                    'nombre_pays': personne_plus_voyage[1]
                }

            # Durée moyenne des visites par pays
            self.cursor.execute("""
                SELECT pays_visite, AVG(jours) as duree_moyenne
                FROM voyages
                GROUP BY pays_visite
                ORDER BY duree_moyenne DESC
            """)
            duree_moyenne_par_pays = []
            for row in self.cursor.fetchall():
                duree_moyenne_par_pays.append({
                    'pays': row[0],
                    'duree_moyenne': float(row[1])
                })
            stats['duree_moyenne_par_pays'] = duree_moyenne_par_pays

            # Durée moyenne globale
            self.cursor.execute("SELECT AVG(jours) FROM voyages")
            duree_moy = self.cursor.fetchone()[0]
            stats['duree_moyenne_globale'] = float(duree_moy) if duree_moy else 0

            return stats

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return None

    # ============================================================
    # MÉTHODES DE TRANSACTION
    # ============================================================

    def commit(self) -> bool:
        """
        Valide les changements

        Returns:
            True si succès, False sinon
        """
        try:
            self.conn.commit()
            logger.info("Changements validés")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du commit: {e}")
            return False

    def rollback(self) -> bool:
        """
        Annule les changements

        Returns:
            True si succès, False sinon
        """
        try:
            self.conn.rollback()
            logger.warning("Changements annulés")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du rollback: {e}")
            return False

    # ============================================================
    # MÉTHODES UTILITAIRES
    # ============================================================

    def afficher_stats(self):
        """Affiche les statistiques de la base de données"""
        stats = self.get_stats()

        if stats:
            print("\n" + "="*60)
            print("STATISTIQUES DE LA BASE DE DONNÉES")
            print("="*60)
            print(f"👥 Personnes: {stats['nb_personnes']}")
            print(f"✈️  Voyages: {stats['nb_voyages']}")
            print(f"🌍 Pays différents: {stats['nb_pays']}")

            if 'pays_plus_visite' in stats:
                print(f"\n🏆 Pays le plus visité:")
                print(f"   {stats['pays_plus_visite']['pays']} ({stats['pays_plus_visite']['nombre_visites']} visites)")

            if 'personne_plus_voyage' in stats:
                print(f"\n✈️  Grand voyageur:")
                print(f"   {stats['personne_plus_voyage']['nom']} ({stats['personne_plus_voyage']['nombre_pays']} pays)")

            print(f"\n📅 Durée moyenne des voyages: {stats['duree_moyenne_globale']:.1f} jours")
            print("="*60 + "\n")


# ============================================================
# FONCTION UTILITAIRE POUR L'API
# ============================================================

def get_db() -> Optional[DatabaseManager]:
    """
    Crée et retourne une connexion à la base de données avec la config par défaut
    Fonction pratique pour l'API

    Returns:
        DatabaseManager connecté ou None si échec
    """
    db = DatabaseManager()
    if db.connect():
        return db
    return None


# ============================================================
# EXEMPLE D'UTILISATION
# ============================================================

if __name__ == "__main__":
    # Configuration pour les logs
    logging.basicConfig(level=logging.INFO)

    # Créer une instance du gestionnaire (utilise la config par défaut)
    db = DatabaseManager()

    # Se connecter
    if db.connect():
        # Test d'insertion
        nb_voyages, personne_id = db.insert_personne_avec_voyages(
            nom="Test User",
            pays_origine="France",
            liste_pays=["Espagne", "Italie", "Portugal"],
            jours=10
        )

        print(f"\n✅ {nb_voyages} voyages insérés pour la personne ID {personne_id}")

        # Valider
        db.commit()

        # Afficher les statistiques
        db.afficher_stats()

        # Fermer
        db.close()