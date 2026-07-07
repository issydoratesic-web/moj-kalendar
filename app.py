import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import time as time_module
import random
import string

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Adora Beauty Concept", page_icon="✂️", layout="centered")

# --- FUNKCIJE ---
def posalji_discord_obavijest(ime, kontakt, datum, vrijeme, usluga, kod, tip="rezervacija"):
    try:
        DISCORD_WEBHOOK = st.secrets["DISCORD_WEBHOOK"]
        color = 3066993 if tip == "rezervacija" else 15158332
        data = {"content": "🔔 Nova rezervacija!" if tip == "rezervacija" else "❌ Otkazan termin!",
                "embeds": [{"title": f"👤 {ime}", "color": color, "fields": [
                    {"name": "✂️ Usluga", "value": usluga, "inline": False},
                    {"name": "📱 Kontakt", "value": kontakt, "inline": False},
                    {"name": "📅 Datum", "value": datum, "inline": True},
                    {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True},
                    {"name": "🔑 Kod", "value": kod, "inline": True}]}]}
        requests.post(DISCORD_WEBHOOK, json=data)
    except: pass

def ucitaj_termine():
    if os.path.exists("termini.csv"): return pd.read_csv("termini.csv")
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Kod"])

def spremi_termin(ime, kontakt, datum, vrijeme, usluga, kod):
    df = ucitaj_termine()
    novi_termin = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum, "Vrijeme": vrijeme, "Usluga": usluga, "Kod": kod}])
    df = pd.concat([df, novi_termin], ignore_index=True)
    df.to_csv("termini.csv", index=False)

def obrisi_termin_po_imenu(ime):
    df = ucitaj_termine()
    # Brisanje retka gdje ime odgovara (case insensitive)
    novi_df = df[df['Ime'].str.lower() != ime.strip().lower()]
    novi_df.to_csv("termini.csv", index=False)

# --- UI ---
st.title("✨ Adora Beauty Concept")

# --- NOVA REZERVACIJA ---
st.subheader("Nova rezervacija")
ime = st.text_input("Ime i Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")
# ... (ostatak koda za odabir usluge ostaje isti)

# LOGIKA REZERVACIJE SA PROVJEROM IMENA I PREZIMENA
if st.button("POTVRDI REZERVACIJU"):
    if not ime or " " not in ime.strip():
        st.warning("Molimo unesite PUNO ime i prezime (npr. Mario Marić).")
    elif not kontakt:
        st.warning("Molimo unesite kontakt.")
    else:
        # Nastavak spremanja...
        kod = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        spremi_termin(ime.strip(), kontakt, datum.strftime("%d/%m/%Y"), odabrano_vrijeme, usluga, kod)
        st.success("✅ Uspješno rezervirano!")
        st.rerun()

# --- PROVJERA I OTKAZIVANJE (BEZ KODA) ---
st.markdown("---")
st.subheader("🔎 Provjera i otkazivanje termina")
ime_otkazivanje = st.text_input("Unesite PUNO ime i prezime za otkazivanje:")

if ime_otkazivanje:
    df = ucitaj_termine()
    moj_termin = df[df['Ime'].str.lower() == ime_otkazivanje.strip().lower()]
    
    if not moj_termin.empty:
        st.info(f"Pronađen termin: {moj_termin.iloc[0]['Usluga']} na datum {moj_termin.iloc[0]['Datum']}")
        if st.button("❌ OTKAŽI TERMIN"):
            obrisi_termin_po_imenu(ime_otkazivanje)
            st.success("Termin je otkazan.")
            st.rerun()
    else:
        st.write("Nema termina za to puno ime i prezime.")

# --- ADMIN PANEL ---
with st.sidebar:
    st.header("🔐 Admin")
    lozinka = st.text_input("Lozinka:", type="password")
    if lozinka == st.secrets.get("ADMIN_PASSWORD"):
        df_admin = ucitaj_termine()
        st.dataframe(df_admin)
        
        st.subheader("Brisanje (Admin)")
        ime_za_brisanje = st.text_input("Upišite ime klijenta za brisanje:")
        if st.button("OBRIŠI KLIJENTA"):
            obrisi_termin_po_imenu(ime_za_brisanje)
            st.success("Obrisano!")
            st.rerun()