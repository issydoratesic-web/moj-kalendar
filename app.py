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
        naslov = "🔔 Nova rezervacija!" if tip == "rezervacija" else "❌ Otkazan termin!"
        data = {"content": naslov,
                "embeds": [{"title": f"👤 {ime}", "color": color, "fields": [
                    {"name": "✂️ Usluga", "value": usluga, "inline": False},
                    {"name": "📱 Kontakt", "value": kontakt, "inline": False},
                    {"name": "📅 Datum", "value": datum, "inline": True},
                    {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True},
                    {"name": "🔑 Kod", "value": kod, "inline": True}]}]}
        requests.post(DISCORD_WEBHOOK, json=data)
    except: pass

def ucitaj_termine():
    # Učitavamo kao tekst (dtype=str) kako se datumi ne bi formatirali naopako
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Kod"])

def spremi_termin(ime, kontakt, datum_obj, vrijeme, usluga, kod):
    df = ucitaj_termine()
    # Strogo formatiranje u DD/MM/YYYY
    datum_str = datum_obj.strftime('%d/%m/%Y')
    novi_termin = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum_str, "Vrijeme": vrijeme, "Usluga": usluga, "Kod": kod}])
    df = pd.concat([df, novi_termin], ignore_index=True)
    df.to_csv("termini.csv", index=False)

def obrisi_tocan_termin(ime, datum, vrijeme):
    df = ucitaj_termine()
    # Brišemo redak gdje se sve podudara
    novi_df = df[~((df['Ime'].str.lower() == ime.strip().lower()) & (df['Datum'] == datum) & (df['Vrijeme'] == vrijeme))]
    novi_df.to_csv("termini.csv", index=False)

# --- UI ---
st.title("✨ Adora Beauty Concept")

st.info("""
⚠️ **Napomena:** - Otkazivanje termina potrebno je najaviti najmanje 24h prije termina.
- Prilikom zakazivanja termina za **šminkanje** potrebno je uplatiti akontaciju (50%) na IBAN: HR03 2402 0061 1406 1395 3.
""")

usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Masaža i piling - 35€"],
    "Frizure": ["Kratka kosa", "Duga kosa", "Punđa - 15€"],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

# --- NOVA REZERVACIJA ---
st.subheader("Nova rezervacija")
ime = st.text_input("Ime i Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")
kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None)

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        col1, col2 = st.columns(2)
        with col1: 
            datum = st.date_input("Datum:", min_value=datetime.today())
            st.caption(f"Datum koji se sprema: {datum.strftime('%d.%m.%Y.')}")
        with col2:
            df_svi = ucitaj_termine()
            dat_str = datum.strftime("%d/%m/%Y")
            termini_dan = df_svi[df_svi['Datum'] == dat_str]
            zauzeti = termini_dan['Vrijeme'].tolist()
            slobodni = [f"{h:02d}:00" for h in range(8, 21) if f"{h:02d}:00" not in zauzeti]
            odabrano_vrijeme = st.selectbox("Vrijeme:", slobodni) if slobodni else st.error("Nema slobodnih termina.")

        if 'odabrano_vrijeme' in locals() and odabrano_vrijeme and st.button("POTVRDI REZERVACIJU"):
            if not ime or " " not in ime.strip():
                st.warning("Unesite puno ime i prezime.")
            else:
                kod = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                spremi_termin(ime.strip(), kontakt, datum, odabrano_vrijeme, usluga, kod)
                posalji_discord_obavijest(ime.strip(), kontakt, dat_str, odabrano_vrijeme, usluga, kod)
                st.success("Vaš termin je uspješno rezerviran!")
                time_module.sleep(3)
                st.rerun()

# --- PROVJERA I OTKAZIVANJE ---
st.markdown("---")
st.subheader("🔎 Provjera i otkazivanje")
ime_otkaz = st.text_input("Ime i Prezime za otkazivanje:")
if ime_otkaz:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.lower() == ime_otkaz.strip().lower()]
    for idx, row in moji.iterrows():
        st.write(f"Termin: {row['Usluga']} | {row['Datum']} u {row['Vrijeme']}")
        if st.button(f"❌ Otkazi {row['Vrijeme']}", key=f"btn_{idx}"):
            obrisi_tocan_termin(row['Ime'], row['Datum'], row['Vrijeme'])
            st.rerun()

# --- ADMIN PANEL ---
with st.sidebar:
    st.header("🔐 Admin")
    if st.text_input("Lozinka:", type="password") == st.secrets.get("ADMIN_PASSWORD"):
        df_a = ucitaj_termine()
        st.dataframe(df_a)
        if not df_a.empty:
            opcije = df_a.apply(lambda x: f"{x['Ime']} ({x['Datum']} - {x['Vrijeme']})", axis=1).tolist()
            odabrani = st.selectbox("Brisanje:", opcije)
            if st.button("OBRIŠI ODABRANI"):
                dio = odabrani.split(" (")
                datum_vr = dio[1].replace(")", "").split(" - ")
                obrisi_tocan_termin(dio[0], datum_vr[0], datum_vr[1])
                st.rerun()