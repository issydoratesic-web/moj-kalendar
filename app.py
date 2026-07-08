import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- CSS STILOVI ---
st.markdown("""
    <style>
    .custom-box { background-color: #fff0f5; padding: 15px; border-radius: 10px; border-left: 5px solid #d63384; color: #4a4a4a; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena", "Laminacija_DA_NE", "Alergije"])

def spremi_termin(ime, kontakt, datum, vrijeme, usluga, novi_klijent, napomena, lam, al):
    df = ucitaj_termine()
    novi = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum, "Vrijeme": vrijeme, "Usluga": usluga, "Novi_klijent": novi_klijent, "Napomena": napomena, "Laminacija_DA_NE": lam, "Alergije": al}])
    pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)

# --- ADMIN PANEL ---
with st.sidebar:
    st.header("🔐 Admin Panel")
    if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False
    
    if not st.session_state.admin_auth:
        pwd = st.text_input("Lozinka:", type="password", key="pwd_input")
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
                st.write(f"Kontakt: {row['Kontakt']}")
                if st.button(f"OBRIŠI TERMIN {idx}", key=f"del_{idx}"):
                    df.drop(idx).to_csv("termini.csv", index=False)
                    st.success("Obrisano!")
                    st.rerun()
        if st.download_button("Preuzmi CSV", df.to_csv(index=False), "termini.csv"): st.success("Pokrenuto!")

# --- GLAVNI UI ---
st.title("✨ Adora Beauty Concept")
st.markdown("""<div class='custom-box'><strong>Napomena:</strong><br>• Otkazivanje termina potrebno je najaviti najmanje 24h prije termina.<br>• Prilikom zakazivanja termina za <strong>šminkanje</strong> potrebno je uplatiti akontaciju (50% cijene) na IBAN: HR03 2402 0061 1406 1395 3.</div>""", unsafe_allow_html=True)

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")

kat = st.selectbox("Odaberite kategoriju:", ["Šminkanje", "Oblikovanje i korekcija obrva", "Tretmani lica", "Frizure", "Little Luxe Spa"], index=None)

usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
    "Frizure": ["Kratka kosa - Ravnanje - 10€", "Duga kosa - Ravnanje - 20€"],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        st.subheader("Dodatna pitanja")
        novi_klijent = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None)
        napomena = st.text_area("Napomena:")
        
        lam_da_ne, alergije = "N/A", "N/A"
        if "Brow lift" in usluga:
            st.markdown("### ⚠️ Za laminaciju obrva i trepavica")
            lam_da_ne = st.radio("Jeste li u posljednjih 6 tjedana radili laminaciju?", ["Da", "Ne"], index=None)
            alergije = st.text_input("Imate li poznate alergije?")

        c1, c2, c3 = st.columns(3)
        dan = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
        mjesec = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
        godina = c3.selectbox("Godina:", ["2026", "2027"])
        
        if st.button("POTVRDI REZERVACIJU"):
            if ime and prezime and kontakt and novi_klijent:
                spremi_termin(f"{ime} {prezime}", kontakt, f"{dan}/{mjesec}/{godina}", "08:00", usluga, novi_klijent, napomena, lam_da_ne, alergije)
                placeholder = st.empty()
                placeholder.success("Hvala na rezervaciji! Termin je zaprimljen. Potvrdu termina primit ćete u najkraćem roku putem Instagrama ili WhatsAppa.")
                time.sleep(10)
                placeholder.empty()
                st.rerun()
            else: st.error("Molimo ispunite obavezna polja.")

st.markdown("---")
st.subheader("👤 Otkazivanje termina")
ime_otkaz = st.text_input("Upišite ime za otkazivanje:")
if ime_otkaz:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.lower() == ime_otkaz.strip().lower()]
    if not moji.empty:
        for idx, row in moji.iterrows():
            if st.button(f"Otkazi: {row['Usluga']} ({row['Datum']})", key=f"del_{idx}"):
                df.drop(idx).to_csv("termini.csv", index=False); st.success("Termin otkazan!"); st.rerun()
    else: st.warning("Nije pronađen termin.")
