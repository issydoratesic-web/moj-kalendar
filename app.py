import streamlit as st
import pandas as pd
import os
import time

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

usluge_mapa = {
    "Šminkanje": {"Šminkanje": "40€", "Terensko šminkanje": "50€"},
    "Obrve": {"Oblikovanje pincetom": "8€", "Oblikovanje i bojanje": "15€", "Brow lift": "30€"},
    "Tretmani lica": {"Enzimski piling": "25€", "Masaža i piling": "35€"},
    "Frizure": {"Kratka kosa": "10€", "Duga kosa": "15€", "Punđa": "15€"},
    "Little Luxe Spa": {"Mini": "50€", "Classic": "70€", "VIP": "100€"}
}

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        df = pd.read_csv("termini.csv")
        # AKO STUPCI NEDOSTAJU, APLIKACIJA ĆE IH DODATI UMJESTO DA PADNE
        ocekivani = ["Ime_Prezime", "Kontakt", "Datum", "Usluga", "Cijena"]
        for col in ocekivani:
            if col not in df.columns:
                df[col] = "Nepoznato"
        return df
    return pd.DataFrame(columns=["Ime_Prezime", "Kontakt", "Datum", "Usluga", "Cijena"])

def spremi_termin(ime_prezime, kontakt, datum, usluga, cijena):
    df = ucitaj_termine()
    novi = pd.DataFrame([{"Ime_Prezime": ime_prezime.strip(), "Kontakt": kontakt, "Datum": datum, "Usluga": usluga, "Cijena": cijena}])
    df = pd.concat([df, novi], ignore_index=True)
    df.to_csv("termini.csv", index=False)

# --- UI ---
st.title("✨ Adora Beauty Concept")
st.info("⚠️ Napomena: Otkazivanje min. 24h prije. Akontacija 50% za šminkanje.")

st.subheader("Nova rezervacija")
ime_input = st.text_input("Unesite PUNO IME I PREZIME:")
kontakt = st.text_input("Kontakt (IG/Br):")
kat = st.selectbox("Kategorija:", list(usluge_mapa.keys()))
usluga = st.selectbox("Usluga:", list(usluge_mapa[kat].keys()))
cijena = usluge_mapa[kat][usluga]
st.write(f"Cijena: **{cijena}**")
datum = st.date_input("Odaberite datum:")

if st.button("POTVRDI REZERVACIJU"):
    if ime_input:
        spremi_termin(ime_input, kontakt, str(datum), usluga, cijena)
        st.success("VAŠ TERMIN JE USPJEŠNO REZERVIRAN!")
        time.sleep(1)
        st.rerun()

# ADMIN PANEL
with st.sidebar:
    st.header("🔐 Admin")
    if st.text_input("Lozinka:", type="password") == st.secrets.get("ADMIN_PASSWORD"):
        st.write("### Upravljanje terminima")
        df = ucitaj_termine()
        
        # PROVJERA JE LI BAZA PRAZNA ILI NEISPRAVNA
        if not df.empty and 'Ime_Prezime' in df.columns:
            opcije = df.apply(lambda x: f"{x['Ime_Prezime']} | {x['Datum']} | {x['Usluga']} ({x['Cijena']})", axis=1).tolist()
            odabrani = st.selectbox("Odaberi termin za brisanje:", opcije)
            
            if st.button("OBRIŠI ODABRANI"):
                idx = opcije.index(odabrani)
                df = df.drop(df.index[idx])
                df.to_csv("termini.csv", index=False)
                st.success("Termin obrisan!")
                st.rerun()
            st.dataframe(df)
        else:
            st.write("Nema rezervacija ili je baza prazna.")
