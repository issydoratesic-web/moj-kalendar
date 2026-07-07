import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests

def posalji_discord_obavijest(ime, kontakt, datum, vrijeme):
    try:
        DISCORD_WEBHOOK = st.secrets["DISCORD_WEBHOOK"]
    except Exception as e:
        st.error("Nedostaje DISCORD_WEBHOOK u Streamlit Secrets!")
        return

    # Elegantno formatirana Discord kartica (Embed)
    data = {
        "content": "🔔 **Stigla je nova rezervacija termina!**",
        "embeds": [{
            "title": f"👤 Klijent: {ime}",
            "color": 15418782, # Elegantna rozna/crvena boja za tvoj salon
            "fields": [
                {"name": "📱 Kontakt (Instagram/Mobitel)", "value": kontakt, "inline": False},
                {"name": "📅 Datum", "value": str(datum), "inline": True},
                {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True}
            ],
            "footer": {"text": "Adora Beauty Concept - Sustav obavijesti"}
        }]
    }
    
    try:
        requests.post(DISCORD_WEBHOOK, json=data)
    except Exception as e:
        st.error(f"Greska kod slanja na Discord: {e}")

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
    st.write("Odaberite datum i vrijeme koji vam odgovaraju, a ja cu vam se javiti za potvrdu.")
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
            st.warning("Svi termini za ovaj dan su zauzeti. Odaberite drugi datum.")
            poslano = False
            
        if poslano:
            if ime and kontakt:
                spremi_termin(ime, kontakt, datum, vrijeme)
                posalji_discord_obavijest(ime, kontakt, datum, vrijeme)
                st.success(f"Uspjesno poslano! Rezervirali ste {datum} u {vrijeme}. Javit cu vam se uskoro!")
            else:
                st.error("Molimo ispunite sva polja.")

elif stranica == "Admin Panel":
    st.title("📥 Pristigli Termini")
    df_termini = ucitaj_termine()
    if not df_termini.empty:
        st.dataframe(df_termini, use_container_width=True)