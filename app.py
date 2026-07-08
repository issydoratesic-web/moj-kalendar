import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena"])

def ucitaj_ocjene():
    if os.path.exists("ocjene.csv"):
        return pd.read_csv("ocjene.csv")
    return pd.DataFrame(columns=["Ime", "Usluga", "Ocjena", "Komentar"])

def spremi_ocjenu(ime, usluga, ocjena, komentar):
    df_ocjene = pd.DataFrame([{"Ime": ime, "Usluga": usluga, "Ocjena": ocjena, "Komentar": komentar}])
    df_ocjene.to_csv("ocjene.csv", mode='a', header=not os.path.exists("ocjene.csv"), index=False)

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
        
        tab1, tab2 = st.tabs(["📅 Termini", "⭐ Ocjene"])
        with tab1:
            st.subheader("Upravljanje terminima")
            df = ucitaj_termine()
            for idx, row in df.iterrows():
                # Ovdje je vraćeno VRIJEME u naziv expandera
                with st.expander(f"{row['Ime']} - {row['Datum']} u {row['Vrijeme']}"):
                    st.write(f"Usluga: {row['Usluga']}")
                    if st.button(f"OBRIŠI {idx}", key=f"del_{idx}"):
                        df.drop(idx).to_csv("termini.csv", index=False); st.rerun()
            if st.download_button("Preuzmi CSV", df.to_csv(index=False), "termini.csv"): st.success("OK")
        
        with tab2:
            st.subheader("Ocjene klijenata")
            st.dataframe(ucitaj_ocjene())

# --- GLAVNI UI ---
st.title("Adora Beauty Concept")
ime = st.text_input("Ime:")
kontakt = st.text_input("Kontakt:")
usluge_lista = ["Šminkanje", "Brow lift", "Punđa", "Oblikovanje obrva"]
odabrane = st.multiselect("Usluge:", usluge_lista)

c1, c2, c3 = st.columns(3)
d = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
m = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
g = c3.selectbox("Godina:", ["2026", "2027"])
datum_str = f"{d}/{m}/{g}"

# Logika zauzeća
trajanje = max(1, len(odabrane))
df_t = ucitaj_termine()
dostupni = []
for h in range(8, 21):
    moguce = True
    for i in range(trajanje):
        if (h+i) >= 20 or f"{h+i:02d}:00" in df_t[df_t['Datum'] == datum_str]['Vrijeme'].values:
            moguce = False
    if moguce: dostupni.append(f"{h:02d}:00")

termin = st.selectbox("Odaberite slobodan termin:", dostupni if dostupni else ["Nema slobodnih"])

if st.button("POTVRDI"):
    if termin != "Nema slobodnih" and ime:
        df = ucitaj_termine()
        for i in range(trajanje):
            v = f"{int(termin[:2]) + i:02d}:00"
            df = pd.concat([df, pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum_str, "Vrijeme": v, "Usluga": ", ".join(odabrane)}])], ignore_index=True)
        df.to_csv("termini.csv", index=False)
        st.success("Rezervirano!"); time.sleep(1); st.rerun()

# --- SUČELJE ZA OCJENE ---
st.markdown("---")
st.subheader("⭐ Ostavite ocjenu")
ocjena_ime = st.text_input("Vaše ime za ocjenu:")
ocjena_val = st.slider("Ocjena:", 1, 5, 5)
komentar = st.text_area("Komentar:")
if st.button("Pošalji ocjenu"):
    spremi_ocjenu(ocjena_ime, ", ".join(odabrane), ocjena_val, komentar)
    st.success("Hvala na ocjeni!")
