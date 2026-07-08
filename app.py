import streamlit as st
import pandas as pd
import os
import time

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# Definiramo usluge i cijene
usluge_mapa = {
    "Šminkanje": {"Šminkanje (40€)": "40€", "Terensko šminkanje (50€)": "50€"},
    "Obrve": {"Oblikovanje pincetom (8€)": "8€", "Oblikovanje i bojanje (15€)": "15€", "Brow lift (30€)": "30€"},
    "Tretmani lica": {"Enzimski piling (25€)": "25€", "Masaža i piling (35€)": "35€"},
    "Frizure": {"Kratka kosa (10€)": "10€", "Duga kosa (15€)": "15€", "Punđa (15€)": "15€"},
    "Little Luxe Spa": {"Mini (50€)": "50€", "Classic (70€)": "70€", "VIP (100€)": "100€"}
}

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        df = pd.read_csv("termini.csv")
        # Osiguravamo da postoje potrebni stupci
        for col in ["Ime_Prezime", "Kontakt", "Datum", "Usluga", "Cijena"]:
            if col not in df.columns: df[col] = ""
        return df
    return pd.DataFrame(columns=["Ime_Prezime", "Kontakt", "Datum", "Usluga", "Cijena"])

def spremi_termin(ime, kontakt, datum, usluga, cijena):
    df = ucitaj_termine()
    novi = pd.DataFrame([{"Ime_Prezime": ime.strip(), "Kontakt": kontakt, "Datum": datum, "Usluga": usluga, "Cijena": cijena}])
    df = pd.concat([df, novi], ignore_index=True)
    df.to_csv("termini.csv", index=False)

# --- UI ---
st.title("✨ Adora Beauty Concept")
st.info("⚠️ Napomena: Otkazivanje termina min. 24h prije. Akontacija 50% za šminkanje.")

st.subheader("Nova rezervacija")
ime = st.text_input("Unesite PUNO IME I PREZIME:")
kontakt = st.text_input("Kontakt (IG/Br):")

kat = st.selectbox("Kategorija:", list(usluge_mapa.keys()))
usluga_labela = st.selectbox("Usluga:", list(usluge_mapa[kat].keys()))
cijena = usluge_mapa[kat][usluga_labela]

datum = st.date_input("Odaberite datum:")

if st.button("POTVRDI REZERVACIJU"):
    if ime:
        spremi_termin(ime, kontakt, str(datum), usluga_labela, cijena)
        st.success("VAŠ TERMIN JE USPJEŠNO REZERVIRAN!")
        time.sleep(1)
        st.rerun()
    else:
        st.warning("Molimo unesite ime i prezime.")

# --- ADMIN PANEL ---
with st.sidebar:
    st.header("🔐 Admin")
    pw = st.text_input("Lozinka:", type="password")
    if pw == st.secrets.get("ADMIN_PASSWORD"):
        st.write("### Upravljanje terminima")
        df = ucitaj_termine()
        if not df.empty:
            opcije = df.apply(lambda x: f"{x['Ime_Prezime']} | {x['Datum']} | {x['Usluga']}", axis=1).tolist()
            odabrani = st.selectbox("Odaberi termin:", opcije)
            if st.button("OBRIŠI ODABRANI"):
                idx = opcije.index(odabrani)
                df = df.drop(df.index[idx])
                df.to_csv("termini.csv", index=False)
                st.rerun()
            st.dataframe(df)
        else:
            st.write("Nema rezervacija.")
