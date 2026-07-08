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

# NAPOMENA
st.info("⚠️ **Napomena:** Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. Prilikom zakazivanja termina za **šminkanje** potrebno je uplatiti akontaciju (50%) na IBAN: HR03 2402 0061 1406 1395 3.")

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

# ADMIN PANEL (Samo za tebe)
with st.sidebar:
    st.header("🔐 Admin")
    if st.text_input("Lozinka:", type="password") == st.secrets.get("ADMIN_PASSWORD"):
        st.write("Svi termini u bazi:")
        df = ucitaj_termine()
        st.dataframe(df)
        
        # Mogućnost brisanja iz Admina ostaje
        if not df.empty:
            odabrani = st.selectbox("Odaberi termin za brisanje:", df.index)
            if st.button("OBRIŠI ODABRANI"):
                df = df.drop(odabrani)
                df.to_csv("termini.csv", index=False)
                st.success("Termin obrisan!")
                st.rerun()
