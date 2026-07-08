import streamlit as st
import pandas as pd
import os
import time

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv")
    return pd.DataFrame(columns=["Ime_Prezime", "Kontakt", "Datum", "Usluga"])

def spremi_termin(ime_prezime, kontakt, datum, usluga):
    df = ucitaj_termine()
    novi = pd.DataFrame([{"Ime_Prezime": ime_prezime.strip(), "Kontakt": kontakt, "Datum": datum, "Usluga": usluga}])
    df = pd.concat([df, novi], ignore_index=True)
    df.to_csv("termini.csv", index=False)

# --- UI ---
st.title("✨ Adora Beauty Concept")

# REZERVACIJA
st.subheader("Nova rezervacija")
ime_input = st.text_input("Unesite PUNO IME I PREZIME:")
kontakt = st.text_input("Kontakt (IG/Br):")
datum = st.date_input("Odaberite datum:")

if st.button("POTVRDI REZERVACIJU"):
    if ime_input:
        spremi_termin(ime_input, kontakt, str(datum), "Usluga")
        st.success("VAŠ TERMIN JE USPJEŠNO REZERVIRAN!")
        time.sleep(1)
        st.rerun()
    else:
        st.warning("Molimo unesite ime i prezime.")

# OTKAZIVANJE
st.markdown("---")
st.subheader("🔎 Otkazivanje rezervacije")
otkaz_input = st.text_input("Upisite puno ime i prezime za otkazivanje:")

if otkaz_input:
    df = ucitaj_termine()
    # Pretraživanje po točnom unosu (bez obzira na velika/mala slova)
    rezultati = df[df['Ime_Prezime'].str.lower() == otkaz_input.strip().lower()]
    
    if not rezultati.empty:
        for idx, row in rezultati.iterrows():
            st.write(f"Pronađeno: {row['Ime_Prezime']} | {row['Datum']}")
            if st.button(f"❌ Otkazi ovaj termin", key=idx):
                df = df.drop(idx)
                df.to_csv("termini.csv", index=False)
                st.success("Termin otkazan!")
                st.rerun()
    else:
        st.warning("Nije pronađen termin za to ime. Provjerite jeste li upisali isto kao pri rezervaciji.")

# ADMIN PANEL
with st.sidebar:
    st.header("🔐 Admin")
    if st.text_input("Lozinka:", type="password") == st.secrets.get("ADMIN_PASSWORD"):
        df = ucitaj_termine()
        st.write("Svi termini u bazi:")
        st.dataframe(df) # OVDJE ĆEŠ VIDJETI ŠTO JE TOČNO U BAZI
