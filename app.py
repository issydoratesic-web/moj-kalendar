import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", page_icon="✨", layout="centered")

# --- KONFIGURACIJA USLUGA ---
usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
    "Frizure": ["Kratka kosa - Ravnanje - 10€", "Kratka kosa - Uvijanje - 20€", "Kratka kosa - Hollywood valovi - 25€", "Kratka kosa - Elegantni repovi - 15€", "Duga kosa - Ravnanje - 20€", "Duga kosa - Uvijanje - 30€", "Duga kosa - Hollywood valovi - 35€", "Duga kosa - Elegantni repovi - 25€", "Punđa - 15€"],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

# --- FUNKCIJE ---
def posalji_na_discord(naslov, ime, usluga, kontakt, datum, vrijeme, extra=""):
    webhook_url = st.secrets.get("DISCORD_WEBHOOK")
    if not webhook_url: return
    embed = {"title": f"🔔 {naslov}", "color": 3066993, "fields": [
        {"name": "👤 Klijent", "value": ime, "inline": False},
        {"name": "✂️ Usluga", "value": usluga, "inline": False},
        {"name": "📱 Kontakt", "value": kontakt, "inline": False},
        {"name": "📅 Datum", "value": datum, "inline": True},
        {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True},
        {"name": "📝 Detalji", "value": extra, "inline": False}
    ]}
    try: requests.post(webhook_url, json={"embeds": [embed]})
    except: pass

def ucitaj_termine():
    kolone = ["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena", "Laminacija_DA_NE", "Alergije"]
    if os.path.exists("termini.csv"):
        try: return pd.read_csv("termini.csv", dtype=str)
        except: return pd.DataFrame(columns=kolone)
    return pd.DataFrame(columns=kolone)

def spremi_termin(ime, kontakt, datum, vrijeme, usluga, novi, napomena, lam, aler):
    df = ucitaj_termine()
    novi_df = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum, "Vrijeme": vrijeme, "Usluga": usluga, "Novi_klijent": novi, "Napomena": napomena, "Laminacija_DA_NE": lam, "Alergije": aler}])
    pd.concat([df, novi_df], ignore_index=True).to_csv("termini.csv", index=False)
    posalji_na_discord("Nova rezervacija!", ime, usluga, kontakt, datum, vrijeme, f"Novi: {novi}, Lam: {lam}, Aler: {aler}")

# --- BOČNA TRAKA (ADMIN) ---
with st.sidebar:
    st.header("🔐 Admin Panel")
    password = st.text_input("Lozinka:", type="password")
    if password == "Admin123":
        st.subheader("Pregled svih termina")
        df_admin = ucitaj_termine()
        st.dataframe(df_admin)
        if st.download_button("Preuzmi CSV", df_admin.to_csv(index=False), "termini.csv"):
            st.success("Preuzeto!")
    elif password:
        st.error("Pogrešna lozinka!")

# --- UI ---
st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>✨ Adora Beauty Concept</h1>", unsafe_allow_html=True)

st.info("""
**Napomena:** Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. Termini otkazani unutar 24h ili nedolazak bez obavijesti naplaćuju se u iznosu 100% cijene usluge.
""")

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")
kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None)

usluga = None 
if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        st.subheader("Dodatna pitanja")
        novi_klijent = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None)
        napomena = st.text_area("Napomena (stil, inspiracija...):")
        
        lam_da_ne, alergije = "N/A", "N/A"
        if "Brow lift" in usluga:
            st.markdown("---")
            st.markdown("### ⚠️ Za laminaciju obrva i trepavica")
            lam_da_ne = st.radio("Jeste li u posljednjih 6 tjedana radili laminaciju ili lifting trepavica?", ["Da", "Ne"], index=None)
            alergije = st.text_input("Imate li poznate alergije na kozmetičke proizvode?")

        c1, c2, c3 = st.columns(3)
        dan = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
        mjesec = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
        godina = c3.selectbox("Godina:", ["2026", "2027"])
        dat_str = f"{dan}/{mjesec}/{godina}"
        vrijeme = st.selectbox("Vrijeme:", [f"{h:02d}:00" for h in range(8, 21)])

        if st.button("POTVRDI REZERVACIJU"):
            if ime and prezime and kontakt and novi_klijent:
                spremi_termin(f"{ime} {prezime}", kontakt, dat_str, vrijeme, usluga, novi_klijent, napomena, lam_da_ne, alergije)
                st.success("Rezervacija potvrđena!"); time.sleep(1); st.rerun()
            else: st.error("Molimo ispunite obavezna polja (ime, prezime, kontakt, novi klijent).")

st.markdown("---")
st.subheader("👤 Otkazivanje termina")
ime_otkaz = st.text_input("Upišite puno ime i prezime za otkazivanje:")
if ime_otkaz:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.lower() == ime_otkaz.strip().lower()]
    if not moji.empty:
        for idx, row in moji.iterrows():
            if st.button(f"Otkazi: {row['Usluga']} ({row['Datum']} u {row['Vrijeme']})", key=idx):
                posalji_na_discord("Termin otkazan!", row['Ime'], row['Usluga'], row['Kontakt'], row['Datum'], row['Vrijeme'])
                df.drop(idx).to_csv("termini.csv", index=False)
                st.success("Termin je uspješno otkazan."); time.sleep(1); st.rerun()
    else: st.warning("Nije pronađen termin za to ime.")
