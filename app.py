import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# Connexion à la base
conn = sqlite3.connect("hotel.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

st.set_page_config(page_title="Application Hôtel", layout="wide")
st.title("🏨 Application de gestion d'hôtel - Projet BD 2025")

# --- Fonctions utilitaires ---

def get_hotels():
    return pd.read_sql_query("SELECT * FROM Hotel", conn)

def get_clients():
    return pd.read_sql_query("SELECT * FROM Client", conn)

def get_types_chambre_by_hotel(id_hotel):
    query = """
    SELECT DISTINCT tc.id, tc.nom, tc.description, tc.prix
    FROM TypeChambre tc
    JOIN Chambre c ON c.id_type = tc.id
    WHERE c.id_hotel = ?
    """
    return pd.read_sql_query(query, conn, params=(id_hotel,))

def chambres_disponibles(date_debut, date_fin):
    query = """
    SELECT * FROM Chambre WHERE id NOT IN (
        SELECT c.id FROM Chambre c
        JOIN Reservation r ON c.id_hotel = r.id_hotel AND c.id_type = r.id_type_chambre
        WHERE NOT (r.date_fin <= ? OR r.date_debut >= ?)
    )
    """
    return pd.read_sql_query(query, conn, params=(date_debut, date_fin))

# --- Menu ---

menu = st.sidebar.selectbox("📋 Menu", [
    "Accueil",
    "Réservations",
    "Clients",
    "Chambres disponibles",
    "Ajouter un client",
    "Ajouter une réservation",
    "Évaluations",
    "Ajouter une évaluation",
    "Statistiques"
])

# --- Pages ---

if menu == "Accueil":
    st.header("📌 Bienvenue")
    st.markdown("Utilisez le menu à gauche pour naviguer entre les différentes fonctionnalités.")

elif menu == "Réservations":
    st.header("📅 Liste des réservations")
    
    clients = get_clients()
    noms = clients["nom"].tolist()
    noms.insert(0, "Tous")
    selected_client = st.selectbox("Filtrer par client :", noms)

    query = """
        SELECT r.id, c.nom AS client, h.ville || ', ' || h.pays AS hotel,
               tc.nom AS type_chambre,
               r.date_debut, r.date_fin, r.nb_chambres
        FROM Reservation r
        JOIN Client c ON r.id_client = c.id
        JOIN Hotel h ON r.id_hotel = h.id
        JOIN TypeChambre tc ON r.id_type_chambre = tc.id
        ORDER BY r.date_debut
    """
    df = pd.read_sql_query(query, conn)

    if selected_client != "Tous":
        df = df[df["client"] == selected_client]

    st.dataframe(df)

elif menu == "Clients":
    st.header("👥 Liste des clients")
    df = get_clients()
    st.dataframe(df)

elif menu == "Chambres disponibles":
    st.header("🛏️ Rechercher des chambres disponibles")
    date1 = st.date_input("Date d'arrivée", value=date.today())
    date2 = st.date_input("Date de départ", value=date.today())

    if date1 >= date2:
        st.warning("⚠️ La date d'arrivée doit être avant la date de départ.")
    else:
        df = chambres_disponibles(date1.isoformat(), date2.isoformat())
        if df.empty:
            st.info("Aucune chambre disponible pour cette période.")
        else:
            st.dataframe(df)

# 4. Ajouter un client
elif menu == "Ajouter un client":
    st.header("➕ Ajouter un client")

    with st.form("form_client"):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        adresse = st.text_input("Adresse")
        ville = st.text_input("Ville")
        code_postal = st.number_input("Code postal", step=1)
        email = st.text_input("Email")
        telephone = st.text_input("Téléphone")

        submit = st.form_submit_button("Ajouter")

        if submit:
            # Vérifier si le client existe déjà
            cursor.execute("""
                SELECT COUNT(*) FROM Client WHERE email = ? OR telephone = ?
            """, (email, telephone))
            client_existe = cursor.fetchone()[0]

            if client_existe > 0:
                st.warning("⚠️ Ce client est déjà enregistré. [Voir la liste des clients](#clients)")
            else:
                cursor.execute("""
                    INSERT INTO Client (adresse, ville, code_postal, email, telephone, nom, prenom)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (adresse, ville, code_postal, email, telephone, nom, prenom))
                conn.commit()
                st.success("Client ajouté avec succès ✅")

elif menu == "Ajouter une réservation":
    st.header("📆 Ajouter une réservation")

    clients = get_clients()
    client_dict = dict(zip(clients["nom"], clients["id"]))
    client_nom = st.selectbox("Client", list(client_dict.keys()))

    hotels = get_hotels()
    hotel_dict = dict(zip(hotels["ville"] + ", " + hotels["pays"], hotels["id"]))
    hotel_nom = st.selectbox("Hôtel", list(hotel_dict.keys()))

    if hotel_nom:
        types_chambres = get_types_chambre_by_hotel(hotel_dict[hotel_nom])
        if types_chambres.empty:
            st.warning("Pas de types de chambres disponibles pour cet hôtel.")
        else:
            tc_dict = dict(zip(types_chambres["nom"], types_chambres["id"]))
            tc_nom = st.selectbox("Type de chambre", list(tc_dict.keys()))

            # Ajouter une option pour choisir entre fumeur et non-fumeur
            fumeur = st.radio("Type de chambre :", ["Non-fumeur", "Fumeur"])
            fumeur_bool = True if fumeur == "Fumeur" else False

            date_debut = st.date_input("Date de début")
            date_fin = st.date_input("Date de fin")
            nb_chambres = st.number_input("Nombre de chambres", min_value=1, value=1, step=1)

            if st.button("Réserver"):
                if date_fin <= date_debut:
                    st.error("La date de fin doit être après la date de début.")
                else:
                    cursor.execute("""
                        INSERT INTO Reservation (date_debut, date_fin, id_client, id_hotel, id_type_chambre, nb_chambres)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (date_debut.isoformat(), date_fin.isoformat(), client_dict[client_nom], hotel_dict[hotel_nom], tc_dict[tc_nom], nb_chambres))
                    conn.commit()
                    st.success("✅ Réservation enregistrée.")
elif menu == "Évaluations":
    st.header("📝 Évaluations des clients")
    query = """
        SELECT e.id, c.nom AS client, h.ville || ', ' || h.pays AS hotel,
               e.date_arrivee, e.note, e.commentaire
        FROM Evaluation e
        JOIN Client c ON e.id_client = c.id
        JOIN Hotel h ON e.id_hotel = h.id
        ORDER BY e.date_arrivee DESC
    """
    df = pd.read_sql_query(query, conn)
    st.dataframe(df)

elif menu == "Ajouter une évaluation":
    st.header("💬 Ajouter une évaluation client")

    clients = get_clients()
    client_dict = dict(zip(clients["nom"], clients["id"]))
    hotels = get_hotels()
    hotel_dict = dict(zip(hotels["ville"] + ", " + hotels["pays"], hotels["id"]))

    with st.form("form_eval"):
        client_nom = st.selectbox("Client", list(client_dict.keys()))
        hotel_nom = st.selectbox("Hôtel", list(hotel_dict.keys()))
        date_eval = st.date_input("Date d'arrivée")
        note = st.slider("Note sur 5", 1, 5)
        commentaire = st.text_area("Commentaire")

        submit = st.form_submit_button("Enregistrer")

        if submit:
            cursor.execute("""
                INSERT INTO Evaluation (date_arrivee, note, commentaire, id_client, id_hotel)
                VALUES (?, ?, ?, ?, ?)""",
                (date_eval.isoformat(), note, commentaire, client_dict[client_nom], hotel_dict[hotel_nom])
            )
            conn.commit()
            st.success("✅ Évaluation enregistrée.")

elif menu == "Statistiques":
    st.header("📊 Statistiques générales")

    nb_clients = cursor.execute("SELECT COUNT(*) FROM Client").fetchone()[0]
    nb_reserv = cursor.execute("SELECT COUNT(*) FROM Reservation").fetchone()[0]
    nb_chambres = cursor.execute("SELECT COUNT(*) FROM Chambre").fetchone()[0]
    nb_hotels = cursor.execute("SELECT COUNT(*) FROM Hotel").fetchone()[0]

    st.metric("Nombre de clients", nb_clients)
    st.metric("Nombre de réservations", nb_reserv)
    st.metric("Nombre de chambres", nb_chambres)
    st.metric("Nombre d'hôtels", nb_hotels)
