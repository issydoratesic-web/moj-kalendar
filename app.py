import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests

def posalji_email_obavijest(ime, kontakt, datum, vrijeme):
    # Sustav sigurno povlači tvoj Hotmail iz postavki
    try:
        HOTMAIL_USER = st.secrets["HOTMAIL_USER"]
    except Exception as e:
        st.error("Nedostaje HOTMAIL_USER u Streamlit Secrets!")
        return

    naslov = f"Nova rezervacija: {ime}"
    tijelo_maila = (
        f"Imate novu rezervaciju!\n\n"
        f"Ime i prezime: {ime}\n"
        f"Instagram / Kontakt: {kontakt}\n"
        f"Datum: {datum}\n"
        f"Vrijeme: {vrijeme}"
    )
    
    # Šaljemo izravno preko besplatnog FormSubmit servisa bez lozinki
    try:
        response = requests.post(f"https://formsubmit.co/ajax/{HOTMAIL_USER}", data={
            "_subject": naslov,
            "Detalji": tijelo_maila
        })
        if response.status_code != 200:
            st.error("Servis za slanje trenutno nije dostupan.")
    except Exception as e:
        st.error(f"Greška kod slanja: {e}")

# --- BAZA PODATAKA ---
DB_FILE = "termini.csv"

def ucitaj_termine():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Status"])

def spremi_termin(ime, kontakt, datum, vrijeme):
    df = ucitaj_termine()
    novi_termin = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": str(datum), "Vrijeme": vrijeme, "Status": "Na cekanju"}])
    df = pd.concat([df, novi_termin], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- GLAVNI PROGRAM ---
st.set_page_config(page_title="Rezervacija Termina", layout="centered")
stranica = st.sidebar.radio("Navigacija", ["Rezerviraj Termin", "Admin Panel"])

if stranica == "Rezerviraj Termin":
    st.title("📅 Rezervirajte svoj termin")
    df_termini = ucitaj_termine()
    
    with st.form("rezervacija_forma", clear_on_submit=True):
        ime = st.text_input("Vase Ime i Prezime:")
        kontakt = st.text_input("Vas Instagram username ili broj mobitela:")
        datum = st.date_input("Odaberite datum:", min_value=datetime.today().date())
        
        vremena = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
        zauzeta_vremena = df_termini[df_termini["Datum"] == str(datum)]["Vrijeme"].values
        slobodna_vremena = [v for v in vremena if v not in zauzeta_vremena]
        
        if slobodna_vremena:
            vrijeme = st.selectbox("Odaberite vrijeme:", slobodna_vremena)
            poslano = st.form_submit_button("Rezerviraj")
        else:
            st.warning("Svi termini za ovaj dan su zauzeti.")
            poslano = False
            
        if poslano:
            if ime and kontakt:
                spremi_termin(ime, kontakt, datum, vrijeme)
                posalji_email_obavijest(ime, kontakt, datum, vrijeme)
                st.success(f"Uspjesno poslano! Rezervirali ste {datum} u {vrijeme}.")
            else:
                st.error("Molimo ispunite sva polja.")

elif stranica == "Admin Panel":
    st.title("📥 Pristigli Termini")
    df_termini = ucitaj_termine()
    if not df_termini.empty:
        st.dataframe(df_termini, use_container_width=True)