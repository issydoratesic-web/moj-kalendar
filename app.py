import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time as time_module

st.set_page_config(page_title="Adora Beauty Concept", page_icon="✂️", layout="centered")

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        # Učitavamo bez 'Kod' stupca ako ga više ne koristimo
        df = pd.read_csv("termini.csv", dtype=str)
        return df
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga"])

def spremi_termin(ime_puno, kontakt, dat_str, vrijeme, usluga):
    df = ucitaj_termine()
    novi = pd.DataFrame([{"Ime": ime_puno, "Kontakt": kontakt, "Datum": dat_str, "Vrijeme": vrijeme, "Usluga": usluga}])
    df = pd.concat([df, novi], ignore_index=True)
    df.to_csv("termini.csv", index=False)

def obrisi_termin_admin(index):
    df = ucitaj_termine()
    df = df.drop(index)
    df.to_csv("termini.csv", index=False)

# --- UI ---
st.title("✨ Adora Beauty Concept")

st.info("""
⚠️ **Napomena:** - Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. 
Termini otkazani unutar 24h ili nedolazak bez obavijesti naplaćuju se u iznosu 100% cijene usluge.

• Prilikom zakazivanja termina za **šminkanje** potrebno je uplatiti akontaciju u iznosu od 50% cijene usluge na IBAN: HR03 2402 0061 1406 1395 3
""")

usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Masaža i piling - 35€"],
    "Frizure": ["Kratka kosa - 20€", "Duga kosa - 30€", "Punđa - 15€"],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

# --- UNOS KORISNIKA ---
col_i, col_p = st.columns(2)
with col_i: ime = st.text_input("Ime:")
with col_p: prezime = st.text_input("Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")

kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None)

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        st.write("---")
        st.subheader("Odaberite datum:")
        col1, col2, col3 = st.columns(3)
        with col1: dan = st.selectbox("Dan:", [str(i).zfill(2) for i in range(1, 32)])
        with col2: mjesec = st.selectbox("Mjesec:", [str(i).zfill(2) for i in range(1, 13)])
        aktualna = datetime.now().year
        with col3: godina = st.selectbox("Godina:", [str(g) for g in range(aktualna, 2036)])
        
        dat_str = f"{dan}/{mjesec}/{godina}"
        
        df_svi = ucitaj_termine()
        zauzeti = df_svi[df_svi['Datum'] == dat_str]['Vrijeme'].tolist()
        slobodni = [f"{h:02d}:00" for h in range(8, 21) if f"{h:02d}:00" not in zauzeti]
        vrijeme = st.selectbox("Vrijeme:", slobodni)

        if st.button("POTVRDI REZERVACIJU"):
            if not ime.strip() or not prezime.strip() or not kontakt.strip():
                st.error("❌ Molimo vas da upišete Ime, Prezime i Kontakt!")
            else:
                ime_puno = f"{ime.strip()} {prezime.strip()}"
                spremi_termin(ime_puno, kontakt, dat_str, vrijeme, usluga)
                st.success("✅ Rezervacija uspješno zabilježena!")
                time_module.sleep(2)
                st.rerun()

# --- ADMIN PANEL ---
with st.sidebar:
    st.header("🔐 Admin Panel")
    lozinka = st.text_input("Lozinka:", type="password")
    
    if lozinka == st.secrets.get("ADMIN_PASSWORD"):
        st.subheader("Upravljanje terminima")
        df = ucitaj_termine()
        if not df.empty:
            for idx, row in df.iterrows():
                st.write(f"**{row['Ime']}** | {row['Datum']} | {row['Vrijeme']}")
                if st.button(f"❌ Obriši termin", key=f"del_{idx}"):
                    obrisi_termin_admin(idx)
                    st.rerun()
        else:
            st.write("Nema aktivnih termina.")
    elif lozinka != "":
        st.error("Pogrešna lozinka!")
