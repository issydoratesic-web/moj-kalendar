import streamlit as st
import pandas as pd
import os
import time
import requests
from streamlit_star_rating import st_star_rating

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- FUNKCIJE ---
def posalji_na_discord(naslov, ime, usluga, kontakt, detalji):
    webhook_url = "https://discord.com/api/webhooks/1524364417167261887/vacZD177MFgx-JaegBXKT2hM9ZtsDNj_D1eZoNACpjL9NB225Ewk5_zlxpLshBdPSzS4"
    embed = {"title": naslov, "color": 16753920, "fields": [{"name": "👤 Klijent", "value": ime, "inline": False}, {"name": "✂️ Usluga", "value": usluga, "inline": False}, {"name": "📱 Kontakt", "value": kontakt, "inline": False}, {"name": "📝 Detalji", "value": detalji, "inline": False}]}
    requests.post(webhook_url, json={"embeds": [embed]})

def ucitaj_termine():
    if os.path.exists("termini.csv"): return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena", "Laminacija_DA_NE", "Alergije"])

def ucitaj_ocjene():
    if os.path.exists("ocjene.csv"): return pd.read_csv("ocjene.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Usluga", "Ocjena", "Komentar"])

def spremi_ocjenu(ime, usluga, ocjena, komentar):
    df_ocjene = pd.DataFrame([{"Ime": ime, "Usluga": usluga, "Ocjena": ocjena, "Komentar": komentar}])
    if os.path.exists("ocjene.csv"): df_ocjene.to_csv("ocjene.csv", mode='a', header=False, index=False)
    else: df_ocjene.to_csv("ocjene.csv", index=False)

# --- ADMIN PANEL ---
with st.sidebar:
    st.header("🔐 Admin Panel")
    if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False
    
    if not st.session_state.admin_auth:
        pwd = st.text_input("Lozinka:", type="password")
        if st.button("Prijava"):
            if pwd == "171102": st.session_state.admin_auth = True; st.rerun()
    else:
        if st.button("Odjava"): st.session_state.admin_auth = False; st.rerun()
        
        tab1, tab2 = st.tabs(["📅 Termini", "⭐ Recenzije"])
        
        with tab1:
            df = ucitaj_termine()
            for idx, row in df.iterrows():
                with st.expander(f"{row['Ime']} | {row['Datum']}"):
                    st.write(f"**Usluga:** {row['Usluga']}")
                    if st.button(f"Obriši termin", key=f"del_{idx}"):
                        df.drop(idx).to_csv("termini.csv", index=False); st.rerun()
            if st.download_button("Preuzmi termine (CSV)", df.to_csv(index=False), "termini.csv"): st.success("Pokrenuto!")
            
        with tab2:
            df_ocj = ucitaj_ocjene()
            for idx, row in df_ocj.iterrows():
                st.write(f"**{row['Ime']}** ({row['Ocjena']}⭐): {row['Komentar']}")
                st.divider()

# --- GLAVNI UI ---
st.title("Rezervacije termina")
# ... (ostatak koda za UI ostaje isti kao i prije) ...

col_i, col_p = st.columns(2)
ime, prezime = col_i.text_input("Ime:"), col_p.text_input("Prezime:")
kontakt = st.text_input("Broj mobitela ili Instagram:")
usluge_lista = ["Šminkanje - 40€", "Little Luxe Spa - VIP - 100€"] # I ostale usluge
odabrane_usluge = st.multiselect("Odaberite usluge:", usluge_lista)

broj_osoba, ukupna_cijena = {}, 0
if odabrane_usluge:
    for usluga in odabrane_usluge:
        cijena = int(usluga.split(" - ")[-1].replace("€", ""))
        if "Little Luxe" not in usluga:
            broj = st.number_input(f"Broj osoba: {usluga}", min_value=1, value=1, key=f"num_{usluga}")
            broj_osoba[usluga] = broj; ukupna_cijena += cijena * broj
        else: broj_osoba[usluga] = 1; ukupna_cijena += cijena
    st.markdown(f"### 💰 Ukupno: {ukupna_cijena}€")

# Dodatna pitanja i gumbi (ostaje identično)
if st.button("POTVRDI REZERVACIJU"):
    # (Logika za spremanje termina ostaje nepromijenjena)
    st.success("Hvala na rezervaciji!")

st.markdown("---")
st.subheader("👤 Upravljanje mojim terminom")
ime_otkaz = st.text_input("Upišite ime za pronalazak termina:")
if ime_otkaz:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.contains(ime_otkaz, case=False, na=False)]
    if not moji.empty:
        for idx, row in moji.iterrows():
            with st.expander(f"Termin: {row['Usluga']}"):
                if st.button("Otkaži", key=f"del_user_{idx}"): df.drop(idx).to_csv("termini.csv", index=False); st.rerun()
                st.write("---")
                ocjena = st_star_rating("Ocijenite nas", 5, 5, key=f"rate_{idx}")
                komentar = st.text_area("Komentar:", key=f"comm_{idx}")
                if st.button("Pošalji ocjenu", key=f"send_{idx}"): spremi_ocjenu(row['Ime'], row['Usluga'], ocjena, komentar); st.success("Hvala!")
