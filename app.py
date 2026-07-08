import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- CSS STILOVI ---
st.markdown("""
    <style>
    .elegant-title { font-family: 'Georgia', serif; text-align: center; color: #d63384; }
    .custom-box { background-color: #fff0f5; padding: 15px; border-radius: 10px; border-left: 5px solid #d63384; color: #4a4a4a; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCIJE ---
def ucitaj_termine():
    kolone = ["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena", "Laminacija_DA_NE", "Alergije"]
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=kolone)

# --- ADMIN PANEL (SIDEBAR) ---
with st.sidebar:
    st.header("🔐 Admin Panel")
    if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False
    
    if not st.session_state.admin_auth:
        pwd = st.text_input("Lozinka:", type="password")
        if st.button("Prijava"):
            if pwd == "171102": st.session_state.admin_auth = True; st.rerun()
            else: st.error("Pogrešna lozinka!")
    else:
        if st.button("Odjava"): st.session_state.admin_auth = False; st.rerun()
        st.subheader("Upravljanje terminima")
        df = ucitaj_termine()
        for idx, row in df.iterrows():
            with st.expander(f"{row['Ime']} - {row['Datum']}"):
                st.write(f"Usluga: {row['Usluga']}")
                if st.button(f"OBRIŠI TERMIN {idx}", key=f"del_{idx}"):
                    df.drop(idx).to_csv("termini.csv", index=False); st.rerun()

# --- GLAVNI UI ---
st.markdown("<h1 class='elegant-title'>✨ Adora Beauty Concept</h1>", unsafe_allow_html=True)

st.markdown("""
<div class='custom-box'>
    <strong>Napomena:</strong><br>
    • Otkazivanje termina potrebno je najaviti najmanje 24h prije termina.<br>
    • Prilikom zakazivanja termina za <strong>šminkanje</strong> potrebno je uplatiti akontaciju (50% cijene) na IBAN: HR03 2402 0061 1406 1395 3.
</div>
""", unsafe_allow_html=True)

# ... (Ovdje nastavljaš ostatak koda za formu za rezervaciju)
if kat:
    usluge_mapa = {
        "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
        "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
        "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
        "Frizure": ["Kratka kosa - Ravnanje - 10€", "Kratka kosa - Uvijanje - 20€", "Kratka kosa - Hollywood valovi - 25€", "Kratka kosa - Elegantni repovi - 15€", "Duga kosa - Ravnanje - 20€", "Duga kosa - Uvijanje - 30€", "Duga kosa - Hollywood valovi - 35€", "Duga kosa - Elegantni repovi - 25€", "Punđa - 15€"],
        "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
    }
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        st.subheader("Dodatna pitanja")
        novi_klijent = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None)
        napomena = st.text_area("Napomena:")
        
        lam, aler = "N/A", "N/A"
        if "Brow lift" in usluga:
            lam = st.radio("Laminacija u zadnjih 6 tjedana?", ["Da", "Ne"], index=None)
            aler = st.text_input("Alergije:")

        c1, c2, c3 = st.columns(3)
        dan = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
        mjesec = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
        godina = c3.selectbox("Godina:", ["2026", "2027"])
        vrijeme = st.selectbox("Vrijeme:", [f"{h:02d}:00" for h in range(8, 21)])

        if st.button("POTVRDI REZERVACIJU"):
            df = ucitaj_termine()
            novi = pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": f"{dan}/{mjesec}/{godina}", "Vrijeme": vrijeme, "Usluga": usluga, "Novi_klijent": novi_klijent, "Napomena": napomena, "Laminacija_DA_NE": lam, "Alergije": aler}])
            pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
            st.success("Rezervacija potvrđena!"); time.sleep(1); st.rerun()

st.markdown("---")
st.subheader("👤 Otkazivanje termina")
ime_otkaz = st.text_input("Upišite ime za otkazivanje:")
if ime_otkaz:
    df = ucitaj_termine()
    # Tražimo podudaranje (case insensitive)
    maska = df['Ime'].str.contains(ime_otkaz, case=False, na=False)
    moji = df[maska]
    if not moji.empty:
        for idx, row in moji.iterrows():
            if st.button(f"Otkazi: {row['Ime']} - {row['Usluga']}", key=f"c_{idx}"):
                df.drop(idx).to_csv("termini.csv", index=False); st.success("Termin obrisan!"); st.rerun()
    else: st.warning("Nije pronađen termin. Pazi na razmake u imenu!")
