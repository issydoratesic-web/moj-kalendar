import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests

# --- FUNKCIJE ---
def posalji_discord_obavijest(ime, kontakt, datum, vrijeme, usluga):
    try:
        DISCORD_WEBHOOK = st.secrets["DISCORD_WEBHOOK"]
        data = {
            "content": "🔔 **Nova rezervacija!**",
            "embeds": [{
                "title": f"👤 Klijent: {ime}",
                "color": 15418782,
                "fields": [
                    {"name": "✂️ Usluga", "value": usluga, "inline": False},
                    {"name": "📱 Kontakt", "value": kontakt, "inline": False},
                    {"name": "📅 Datum", "value": datum, "inline": True},
                    {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True}
                ]
            }]
        }
        requests.post(DISCORD_WEBHOOK, json=data)
    except: pass

DB_FILE = "termini.csv"
def ucitaj_termine():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Status"])

def spremi_termin(ime, kontakt, datum, vrijeme, usluga):
    df = ucitaj_termine()
    # Datum spremamo kao string u formatu DD/MM/YYYY
    novi_termin = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum, "Vrijeme": vrijeme, "Usluga": usluga, "Status": "Na cekanju"}])
    df = pd.concat([df, novi_termin], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- APP ---
st.set_page_config(page_title="Adora Rezervacije", layout="centered")
stranica = st.sidebar.radio("Navigacija", ["Rezerviraj Termin", "Admin Panel"])

usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
    "Frizure": ["Kratka kosa", "Duga kosa", "Punđa - 15€"],
    "Ostale usluge": ["Relax zona - 25€"],
    "Little Luxe Spa tretman": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

frizure_po_duzini = {
    "Kratka kosa": ["Ravnanje kose - 10€", "Uvijanje kose - 20€", "Hollywood valovi - 25€", "Elegantni repovi - 15€"],
    "Duga kosa": ["Ravnanje kose - 20€", "Uvijanje kose - 30€", "Hollywood valovi - 35€", "Elegantni repovi - 25€"]
}

if stranica == "Rezerviraj Termin":
    st.title("📅 Adora Beauty Concept")
    ime = st.text_input("Ime i Prezime:")
    kontakt = st.text_input("Kontakt (Instagram/Broj):")
    
    kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None, placeholder="Odaberite kategoriju...")
    
    puna_usluga = None
    if kat:
        if kat == "Frizure":
            odabir = st.selectbox("Odaberite dužinu ili frizuru:", list(usluge_mapa["Frizure"]), index=None, placeholder="Odaberite...")
            if odabir:
                if odabir in frizure_po_duzini:
                    usluga = st.selectbox("Odaberite uslugu:", frizure_po_duzini[odabir], index=None, placeholder="Odaberite uslugu...")
                    if usluga: puna_usluga = f"{kat} -> {odabir} -> {usluga}"
                else: puna_usluga = f"{kat} -> {odabir}"
        else:
            usluga = st.selectbox("Odaberite uslugu:", usluge_mapa[kat], index=None, placeholder="Odaberite uslugu...")
            if usluga: puna_usluga = f"{kat} -> {usluga}"
    
    if puna_usluga:
        d_input = st.date_input("Datum:", min_value=datetime.today(), format="DD/MM/YYYY")
        datum_str = d_input.strftime("%d/%m/%Y") # Konverzija u string
        
        df_termini = ucitaj_termine()
        zauzeti = df_termini[df_termini['Datum'] == datum_str]['Vrijeme'].tolist()
        
        sva_vremena = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
        dostupna = [v for v in sva_vremena if v not in zauzeti]
        
        if dostupna:
            vrijeme = st.selectbox("Vrijeme:", dostupna)
            if st.button("Rezerviraj"):
                if ime and kontakt:
                    spremi_termin(ime, kontakt, datum_str, vrijeme, puna_usluga)
                    posalji_discord_obavijest(ime, kontakt, datum_str, vrijeme, puna_usluga)
                    st.success("Termin uspješno rezerviran!")
                    st.rerun()
                else: st.error("Ispunite ime i kontakt.")
        else: st.warning("Nema slobodnih termina za ovaj datum.")

elif stranica == "Admin Panel":
    st.title("🔐 Admin Pristup")
    lozinka = st.text_input("Lozinka:", type="password")
    if lozinka == st.secrets.get("ADMIN_PASSWORD"):
        st.title("📥 Pristigli Termini")
        df = ucitaj_termine()
        st.dataframe(df, use_container_width=True)
        if st.button("⚠️ Obriši sve"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()
    elif lozinka: st.error("Pogrešna lozinka!")