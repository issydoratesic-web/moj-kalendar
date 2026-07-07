import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- KONFIGURACIJA I BAZA PODATAKA ---
# Koristimo jednostavnu CSV datoteku kao bazu podataka za spremanje termina
DB_FILE = "termini.csv"

def ucitaj_termine():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Status"])

def spremi_termin(ime, kontakt, datum, vrijeme):
    df = ucitaj_termine()
    novi_termin = pd.DataFrame([{
        "Ime": ime, 
        "Kontakt": kontakt, 
        "Datum": str(datum), 
        "Vrijeme": vrijeme, 
        "Status": "Na čekanju"
    }])
    df = pd.concat([df, novi_termin], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- GLAVNI PROGRAM ---
st.set_page_config(page_title="Rezervacija Termina", layout="centered")

# Jednostavna navigacija na vrhu (Klijent / Admin)
stranica = st.sidebar.radio("Navigacija", ["Rezerviraj Termin", "Admin Panel (Za tebe)"])

# --- 1. STRANICA ZA KLIJENTE ---
if stranica == "Rezerviraj Termin":
    st.title("📅 Rezervirajte svoj termin")
    st.write("Odaberite datum i vrijeme koji vam odgovaraju, a ja ću vam se javiti za potvrdu.")
    
    # Učitavanje već zauzetih termina da ih klijent vidi (opcionalno)
    df_termini = ucitaj_termine()
    
    # Forma za unos
    with st.form("rezervacija_forma", clear_on_submit=True):
        ime = st.text_input("Vaše Ime i Prezime:")
        kontakt = st.text_input("Vaš Instagram username ili broj mobitela:")
        
        # Biranje datuma (samo od danas pa nadalje)
        datum = st.date_input("Odaberite datum:", min_value=datetime.today().date())
        
        # Popis ponuđenih vremena (prilagodi po želji)
        vremena = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
        
        # Filtriranje već zauzetih vremena za taj dan
        zauzeta_vremena = df_termini[df_termini["Datum"] == str(datum)]["Vrijeme"].values
        slobodna_vremena = [v for v in vremena if v not in zauzeta_vremena]
        
        if slobodna_vremena:
            vrijeme = st.selectbox("Odaberite vrijeme:", slobodna_vremena)
            poslano = st.form_submit_button("Rezerviraj")
        else:
            st.warning("Nažalost, svi termini za ovaj dan su zauzeti. Odaberite drugi datum.")
            poslano = False
            
        if poslano:
            if ime and kontakt:
                spremi_termin(ime, kontakt, datum, vrijeme)
                st.success(f"Uspješno poslano! Rezervirali ste {datum} u {vrijeme}. Javit ću vam se uskoro!")
            else:
                st.error("Molimo ispunite sva polja.")

# --- 2. ADMIN PANEL (ZA TEBE) ---
elif stranica == "Admin Panel (Za tebe)":
    st.title("📥 Pristigli Termini")
    st.write("Ovdje vidiš tko se upisao i njihove kontakt podatke.")
    
    df_termini = ucitaj_termine()
    
    if df_termini.empty:
        st.info("Još nema zakazanih termina.")
    else:
        # Prikaz tablice s terminima
        st.dataframe(df_termini, use_container_width=True)
        
        # Gumb za brisanje/resetiranje baze ako želiš očistiti listu
        if st.button("Očisti sve termine"):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
                st.rerun()