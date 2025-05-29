import sqlite3

# Connexion à la base de données (ou création)
conn = sqlite3.connect("hotel.db")
cursor = conn.cursor()

# Suppression des tables si elles existent (ordre inverse des dépendances)
tables = ["Evaluation", "Reservation", "HotelPrestation", "Prestation", "Chambre", "TypeChambre", "Client", "Hotel"]
for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table}")

# Création des tables

cursor.execute("""
CREATE TABLE Hotel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    ville TEXT NOT NULL,
    pays TEXT NOT NULL,
    code_postal INTEGER NOT NULL
)
""")

cursor.execute("""
CREATE TABLE Client (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prenom TEXT NOT NULL,
    nom TEXT NOT NULL,
    adresse TEXT,
    ville TEXT,
    code_postal INTEGER,
    email TEXT,
    telephone TEXT
)
""")

cursor.execute("""
CREATE TABLE Prestation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    description TEXT
)
""")

# Table associant les prestations à un hôtel avec un prix propre à l'hôtel
cursor.execute("""
CREATE TABLE HotelPrestation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_hotel INTEGER NOT NULL,
    id_prestation INTEGER NOT NULL,
    prix INTEGER NOT NULL,
    FOREIGN KEY (id_hotel) REFERENCES Hotel(id),
    FOREIGN KEY (id_prestation) REFERENCES Prestation(id),
    UNIQUE(id_hotel, id_prestation)
)
""")

cursor.execute("""
CREATE TABLE TypeChambre (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    description TEXT,
    prix INTEGER NOT NULL
)
""")

cursor.execute("""
CREATE TABLE Chambre (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero INTEGER NOT NULL,
    etage INTEGER NOT NULL,
    fumeur INTEGER NOT NULL CHECK (fumeur IN (0,1)),
    id_type INTEGER NOT NULL,
    id_hotel INTEGER NOT NULL,
    FOREIGN KEY (id_type) REFERENCES TypeChambre(id),
    FOREIGN KEY (id_hotel) REFERENCES Hotel(id),
    UNIQUE(id_hotel, numero) -- Un numéro unique par hôtel
)
""")

cursor.execute("""
CREATE TABLE Reservation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_client INTEGER NOT NULL,
    id_hotel INTEGER NOT NULL,
    id_type_chambre INTEGER NOT NULL,
    date_debut TEXT NOT NULL,
    date_fin TEXT NOT NULL,
    nb_chambres INTEGER NOT NULL CHECK(nb_chambres > 0),
    FOREIGN KEY (id_client) REFERENCES Client(id),
    FOREIGN KEY (id_hotel) REFERENCES Hotel(id),
    FOREIGN KEY (id_type_chambre) REFERENCES TypeChambre(id)
)
""")

cursor.execute("""
CREATE TABLE Evaluation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_client INTEGER NOT NULL,
    id_hotel INTEGER NOT NULL,
    date_arrivee TEXT NOT NULL,
    note INTEGER NOT NULL CHECK(note >= 0 AND note <= 5),
    commentaire TEXT,
    FOREIGN KEY (id_client) REFERENCES Client(id),
    FOREIGN KEY (id_hotel) REFERENCES Hotel(id)
)
""")

# Insertion des données

# Hôtels (ajout de noms)
hotels = [
    (1, 'Hôtel Paris Centre', 'Paris', 'France', 75001),
    (2, 'Hôtel Lyon Lumière', 'Lyon', 'France', 69002)
]

# Clients (prénom + nom)
clients = [
    (1, 'Jean', 'Dupont', '12 Rue de Paris', 'Paris', 75001, 'jean.dupont@email.fr', '0612345678'),
    (2, 'Marie', 'Leroy', '5 Avenue Victor Hugo', 'Lyon', 69002, 'marie.leroy@email.fr', '0623456789'),
    (3, 'Paul', 'Moreau', '8 Boulevard Saint-Michel', 'Marseille', 13005, 'paul.moreau@email.fr', '0634567890'),
    (4, 'Lucie', 'Martin', '27 Rue Nationale', 'Lille', 59800, 'lucie.martin@email.fr', '0645678901'),
    (5, 'Emma', 'Giraud', '3 Rue des Fleurs', 'Nice', 6000, 'emma.giraud@email.fr', '0656789012')
]

# Prestations (nom + description)
prestations = [
    (1, 'Petit-déjeuner', 'Petit-déjeuner continental servi tous les matins.'),
    (2, 'Navette aéroport', 'Service de navette entre l\'aéroport et l\'hôtel.'),
    (3, 'Wi-Fi gratuit', 'Accès internet sans fil dans tout l\'hôtel.'),
    (4, 'Spa et bien-être', 'Accès au spa et centre de bien-être.'),
    (5, 'Parking sécurisé', 'Parking privé et sécurisé pour les clients.')
]

# Prix des prestations par hôtel
hotel_prestations = [
    # id_hotel, id_prestation, prix
    (1, 1, 15),
    (1, 2, 30),
    (1, 3, 0),
    (1, 4, 50),
    (1, 5, 20),
    (2, 1, 10),
    (2, 2, 25),
    (2, 3, 0),
    (2, 4, 45),
    (2, 5, 18),
]

# Types de chambre (nom, description, prix)
type_chambres = [
    (1, 'Standard', 'Chambre standard avec les équipements de base.', 80),
    (2, 'Deluxe', 'Chambre plus spacieuse avec vue.', 120),
    (3, 'Suite', 'Suite luxueuse avec salon séparé.', 200)
]

# Chambres (numero, etage, fumeur, id_type, id_hotel)
chambres = [
    (1, 201, 2, 0, 1, 1),  # chambre fumeur=0 = non fumeur
    (2, 502, 5, 1, 1, 2),
    (3, 305, 3, 0, 2, 1),
    (4, 410, 4, 0, 2, 2),
    (5, 104, 1, 1, 2, 2),
    (6, 202, 2, 0, 1, 1),
    (7, 307, 3, 1, 1, 2),
    (8, 101, 1, 0, 1, 1)
]

# Réservations (id_client, id_hotel, id_type_chambre, date_debut, date_fin, nb_chambres)
reservations = [
    (1, 1, 1, '2025-06-15', '2025-06-18', 1),
    (2, 2, 1, '2025-07-01', '2025-07-05', 2),
    (2, 2, 2, '2025-11-12', '2025-11-14', 1),
    (2, 2, 3, '2026-02-01', '2026-02-05', 1),
    (3, 1, 2, '2025-08-10', '2025-08-14', 1),
    (4, 2, 3, '2025-09-05', '2025-09-07', 1),
    (4, 2, 1, '2026-01-15', '2026-01-18', 1),
    (5, 2, 2, '2025-09-20', '2025-09-25', 1)
]

# Évaluations (id_client, id_hotel, date_arrivee, note, commentaire)
evaluations = [
    (1, 1, '2025-06-15', 5, 'Excellent séjour, personnel très accueillant.'),
    (2, 2, '2025-07-01', 4, 'Chambre propre, bon rapport qualité/prix.'),
    (3, 1, '2025-08-10', 3, 'Séjour correct mais bruyant la nuit.'),
    (4, 2, '2025-09-05', 5, 'Service impeccable, je recommande.'),
    (5, 2, '2025-09-20', 4, 'Très bon petit-déjeuner, hôtel bien situé.')
]

# Insertion dans la base

cursor.executemany("INSERT INTO Hotel (id, nom, ville, pays, code_postal) VALUES (?, ?, ?, ?, ?)", hotels)
cursor.executemany("INSERT INTO Client (id, prenom, nom, adresse, ville, code_postal, email, telephone) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", clients)
cursor.executemany("INSERT INTO Prestation (id, nom, description) VALUES (?, ?, ?)", prestations)
cursor.executemany("INSERT INTO HotelPrestation (id_hotel, id_prestation, prix) VALUES (?, ?, ?)", hotel_prestations)
cursor.executemany("INSERT INTO TypeChambre (id, nom, description, prix) VALUES (?, ?, ?, ?)", type_chambres)
cursor.executemany("INSERT INTO Chambre (id, numero, etage, fumeur, id_type, id_hotel) VALUES (?, ?, ?, ?, ?, ?)", chambres)
cursor.executemany("INSERT INTO Reservation (id_client, id_hotel, id_type_chambre, date_debut, date_fin, nb_chambres) VALUES (?, ?, ?, ?, ?, ?)", reservations)
cursor.executemany("INSERT INTO Evaluation (id_client, id_hotel, date_arrivee, note, commentaire) VALUES (?, ?, ?, ?, ?)", evaluations)

conn.commit()
conn.close()
print("Base de données SQLite créée avec succès selon le cahier des charges.")
