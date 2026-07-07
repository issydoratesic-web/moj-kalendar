import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import time as time_module

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Adora Beauty Concept", page_icon="✂️", layout="centered")

# --- FUNKCIJE ---
def posalji_discord_obavijest(ime, kontakt, datum, vrijeme, usluga, tip="rezervacija"):
    try:
        DISCORD_WEBHOOK = st.secrets["DISCORD_WEBHOOK"]
        color = 3066993 if tip == "rezervacija" else 15158332
        data = {"content": "🔔 Nova rezervacija!" if tip == "rezervacija" else "❌ Otkazan termin!",
                "embeds": [{"title": f"👤 {ime}", "color": color, "fields": [
                    {"name": "✂️ Usluga", "value": usluga, "inline": False},
                    {"name": "📱 Kontakt", "value": kontakt, "inline": False},
                    {"name": "📅 Datum", "value": datum, "inline": True},
                    {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True}]}]}
        requests.post(DISCORD_WEBHOOK, json=data)
    except: pass

def ucitaj_termine():
    if os.path.exists("termini.csv"): return pd.read_csv("termini.csv")
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga"])

def spremi_termin(ime, kontakt, datum, vrijeme, usluga):
    df = ucitaj_termine()
    novi_termin = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum, "Vrijeme": vrijeme, "Usluga": usluga}])
    df = pd.concat([df, novi_termin], ignore_index=True)
    df.to_csv("termini.csv", index=False)

def obrisi_termin(ime_klijenta):
    df = ucitaj_termine()
    termin = df[df['Ime'] == ime_klijenta]
    
    if not termin.empty:
        podaci = termin.iloc[0].to_dict()
        novi_df = df[df['Ime'] != ime_klijenta]
        novi_df.to_csv("termini.csv", index=False)
        return podaci
    return None

# --- DIALOG ZA OTKAZIVANJE ---
@st.dialog("❌ Otkazivanje termina")
def prozor_otkazivanje():
    st.write("Unesite ime i prezime kako bismo pronašli vaš termin.")
    ime_klijenta = st.text_input("Ime i prezime:")
    
    if st.button("Pronađi moj termin"):
        df = ucitaj_termine()
        termini = df[df['Ime'] == ime_klijenta]
        if not termini.empty:
            st.write("Pronađeni termin:", termini)
            st.session_state.klijent_za_brisanje = ime_klijenta
        else:
            st.error("Nema pronađenih termina.")
    
    if "klijent_za_brisanje" in st.session_state:
        if st.button("POTVRDI OTKAZIVANJE"):
            obrisani_termin = obrisi_termin(st.session_state.klijent_za_brisanje)
            
            if obrisani_termin:
                st.success("Termin je uspješno otkazan!")
                posalji_discord_obavijest(
                    obrisani_termin['Ime'], 
                    obrisani_termin['Kontakt'], 
                    obrisani_termin['Datum'], 
                    obrisani_termin['Vrijeme'], 
                    obrisani_termin['Usluga'], 
                    tip="otkazivanje"
                )
                del st.session_state.klijent_za_brisanje
                time_module.sleep(1)
                st.rerun()
    
    if st.button("Zatvori"):
        if "klijent_za_brisanje" in st.session_state: del st.session_state.klijent_za_brisanje
        st.rerun()

# --- UI ---
st.title("✨ Adora Beauty Concept")

st.info("""⚠️ **Napomena:**
- Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. Termini otkazani unutar 24h ili nedolazak bez obavijesti naplaćuju se u iznosu 100% cijene usluge.
- Prilikom zakazivanja termina za **šminkanje** potrebno je uplatiti akontaciju u iznosu od 50% cijene usluge na IBAN: HR03 2402 0061 1406 1395 3.""")

if st.button("❌ Želim otkazati termin"):
    prozor_otkazivanje()

st.markdown("---")
st.subheader("Nova rezervacija")

usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
    "Frizure": ["Kratka kosa", "Duga kosa", "Punđa - 15€"],
    "Ostale usluge": ["Relax zona - 25€"],
    "Little Luxe Spa tretman": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

ime = st.text_input("Ime i Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")
kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None)

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        col1, col2 = st.columns(2)
        with col1: datum = st.date_input("Datum:", min_value=datetime.today())
        with col2: 
            # Filtriranje zauzetih termina
            df_svi = ucitaj_termine()
            termini_na_taj_datum = df_svi[df_svi['Datum'] == datum.strftime("%d/%m/%Y")]
            zauzeti_sati = termini_na_taj_datum['Vrijeme'].tolist()
            
            svi_sati = [f"{h:02d}:00" for h in range(8, 21)]
            slobodni_sati = [sat for sat in svi_sati if sat not in zauzeti_sati]
            
            if slobodni_sati:
                odabrano_vrijeme = st.selectbox("Odaberite slobodno vrijeme:", slobodni_sati)
            else:
                st.error("Nažalost, za ovaj datum nema više slobodnih termina.")
                odabrano_vrijeme = None
        
        if odabrano_vrijeme and st.button("POTVRDI REZERVACIJU"):
            if not ime or not kontakt:
                st.warning("Molimo unesite ime i kontakt.")
            else:
                spremi_termin(ime, kontakt, datum.strftime("%d/%m/%Y"), odabrano_vrijeme, usluga)
                posalji_discord_obavijest(ime, kontakt, datum.strftime("%d/%m/%Y"), odabrano_vrijeme, usluga)
                st.success("✅ Termin uspješno rezerviran!")
                time_module.sleep(2)
                st.rerun()

# --- TAJNI ADMIN PANEL (SAMO TI GA VIDIŠ) ---
# Provjera ima li u URL-u "?p=admin"
if st.query_params.get("p") == "admin":
    st.markdown("---")
    st.subheader("🔐 Admin Login")
    lozinka = st.text_input("Lozinka:", type="password")
    if lozinka == st.secrets.get("ADMIN_PASSWORD"):
        st.subheader("📊 Popis svih termina")
        st.dataframe(ucitaj_termine())
        if st.button("Zatvori Admin panel"): 
            st.query_params.clear() # Čisti URL i skriva panel
            st.rerun()
    elif lozinka:
        st.error("Pogrešna lozinka!")