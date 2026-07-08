import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena"])

# --- ADMIN PANEL ---
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
                st.write(f"Vrijeme: {row['Vrijeme']}")
                st.write(f"Usluga: {row['Usluga']}")
                if st.button(f"OBRIŠI {idx}", key=f"del_{idx}"):
                    df.drop(idx).to_csv("termini.csv", index=False); st.rerun()
        if st.download_button("Preuzmi CSV", df.to_csv(index=False), "termini.csv"): st.success("OK")

# --- GLAVNI UI ---
st.title("Adora Beauty Concept")
ime = st.text_input("Ime:")
kontakt = st.text_input("Kontakt:")
# ... (ostatak forme) ...

# --- POPRAVLJENO PRETRAŽIVANJE (Ovo je ključni dio) ---
st.markdown("---")
st.subheader("👤 Upravljanje mojim terminom")
ime_otkaz = st.text_input("Upišite ime za pronalazak termina:")

if ime_otkaz:
    df = ucitaj_termine()
    # OČIŠĆENA LOGIKA: pretvaramo sve u mala slova i brišemo razmake da bi pretraga radila
    trazeno = ime_otkaz.strip().lower()
    df['Ime_clean'] = df['Ime'].astype(str).str.strip().str.lower()
    
    moji = df[df['Ime_clean'].str.contains(trazeno, na=False)]
    
    if not moji.empty:
        for idx, row in moji.iterrows():
            with st.expander(f"Termin: {row['Ime']} ({row['Datum']} u {row['Vrijeme']})"):
                st.write(f"Usluga: {row['Usluga']}")
                if st.button(f"Otkazi ovaj termin", key=f"del_user_{idx}"):
                    # Brišemo iz originalnog df-a
                    cijeli_df = ucitaj_termine()
                    cijeli_df.drop(idx).to_csv("termini.csv", index=False)
                    st.success("Otkazano!"); st.rerun()
    else:
        st.warning("Nije pronađen termin. Provjerite upisano ime.")
