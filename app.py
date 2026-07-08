import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- FUNKCIJA ZA DISCORD ---
def posalji_na_discord(naslov, ime, usluga, kontakt, detalji):
    webhook_url = "https://discord.com/api/webhooks/1524364417167261887/vacZD177MFgx-JaegBXKT2hM9ZtsDNj_D1eZoNACpjL9NB225Ewk5_zlxpLshBdPSzS4"
    embed = {
        "title": naslov,
        "color": 16753920,
        "fields": [
            {"name": "👤 Klijent", "value": ime, "inline": False},
            {"name": "✂️ Usluga", "value": usluga, "inline": False},
            {"name": "📱 Kontakt", "value": kontakt, "inline": False},
            {"name": "📝 Detalji", "value": detalji, "inline": False}
        ]
    }
    data = {"embeds": [embed]}
    requests.post(webhook_url, json=data)

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena", "Laminacija_DA_NE", "Alergije"])

def spremi_ocjenu(ime, usluga, ocjena, komentar):
    df_ocjene = pd.DataFrame([{"Ime": ime, "Usluga": usluga, "Ocjena": ocjena, "Komentar": komentar}])
    if os.path.exists("ocjene.csv"):
        df_ocjene.to_csv("ocjene.csv", mode='a', header=False, index=False)
    else:
        df_ocjene.to_csv("ocjene.csv", index=False)

# --- CSS ---
st.markdown("""<style>.custom-box { background-color: #fff0f5; padding: 15px; border-radius: 10px; border-left: 5px solid #d63384; color: #4a4a4a; }</style>""", unsafe_allow_html=True)

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
        if st.button("Odjava", key="logout_btn"): st.session_state.admin_auth = False; st.rerun()
        st.subheader("Upravljanje terminima")
        df = ucitaj_termine()
        for idx, row in df.iterrows():
            with st.expander(f"{row['Ime']} - {row['Datum']} ({row['Vrijeme']})"):
                st.write(f"Usluga: {row['Usluga']}")
                if st.button(f"OBRIŠI TERMIN {idx}", key=f"del_{idx}"):
                    df.drop(idx).to_csv("termini.csv", index=False); st.rerun()

# --- GLAVNI UI ---
st.title("Rezervacije termina u Adora Beauty Concept-u")
st.markdown("""<div class='custom-box'><strong>Napomena:</strong><br>• Otkazivanje termina min 24h prije.<br>• Akontacija 50% za šminkanje (IBAN: HR03 2402 0061 1406 1395 3).</div>""", unsafe_allow_html=True)

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Broj mobitela ili instagram korisničko ime:")

usluge_lista = ["Šminkanje - 40€", "Terensko šminkanje - 50€", "Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€", "Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€", "Kratka kosa - Ravnanje - 10€", "Kratka kosa - Uvijanje - 20€", "Kratka kosa - Hollywood valovi - 25€", "Kratka kosa - Elegantni repovi - 15€", "Punđa - 15€", "Duga kosa - Ravnanje - 20€", "Duga kosa - Uvijanje - 30€", "Duga kosa - Hollywood valovi - 35€", "Duga kosa - Elegantni repovi - 25€", "Little Luxe Spa - Mini - 50€", "Little Luxe Spa - Classic - 70€", "Little Luxe Spa - VIP - 100€"]
odabrane_usluge = st.multiselect("Odaberite usluge:", usluge_lista)

broj_osoba = {}
ukupna_cijena = 0
for usluga in odabrane_usluge:
    cijena_po_osobi = int(usluga.split(" - ")[-1].replace("€", ""))
    broj = st.number_input(f"Broj osoba za: {usluga}", min_value=1, value=1) if "Little Luxe" not in usluga else 1
    broj_osoba[usluga] = broj
    ukupna_cijena += cijena_po_osobi * broj
st.markdown(f"### 💰 Ukupno: {ukupna_cijena}€")

# Dodano vrijeme 08:00-20:00
c1, c2, c3 = st.columns(3)
dan = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
mjesec = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
godina = c3.selectbox("Godina:", [str(i) for i in range(2026, 2031)])
vrijeme_odabir = st.selectbox("Vrijeme:", [f"{h:02d}:00" for h in range(8, 21)])

novi_klijent = st.radio("Novi klijent?", ["Da", "Ne"], index=None)
napomena = st.text_area("Napomena:")
potvrda = st.checkbox("Potvrđujem pravila.")

if st.button("POTVRDI REZERVACIJU"):
    if potvrda and ime:
        df = ucitaj_termine()
        novi = pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": f"{dan}/{mjesec}/{godina}", "Vrijeme": vrijeme_odabir, "Usluga": ", ".join(odabrane_usluge), "Novi_klijent": novi_klijent, "Napomena": napomena}])
        pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
        st.success("Rezervacija zaprimljena!"); st.rerun()

# --- UPRAVLJANJE I OCJENE ---
st.markdown("---")
st.subheader("👤 Upravljanje mojim terminom i ocjenjivanje")
ime_otkaz = st.text_input("Upišite ime za pronalazak:")
if ime_otkaz:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.contains(ime_otkaz, case=False, na=False)]
    for idx, row in moji.iterrows():
        with st.expander(f"Termin: {row['Usluga']} ({row['Datum']} u {row['Vrijeme']})"):
            # Izmjena termina
            n_dan, n_mjesec, n_vr = st.selectbox("Dan", [f"{i:02d}" for i in range(1, 32)], key=f"d{idx}"), st.selectbox("Mjesec", [f"{i:02d}" for i in range(1, 13)], key=f"m{idx}"), st.selectbox("Vrijeme", [f"{h:02d}:00" for h in range(8, 21)], key=f"v{idx}")
            if st.button("Spremi izmjene", key=f"save{idx}"):
                df.at[idx, 'Datum'] = f"{n_dan}/{n_mjesec}/{godina}"; df.at[idx, 'Vrijeme'] = n_vr; df.to_csv("termini.csv", index=False); st.success("Izmijenjeno!"); st.rerun()
            # Ocjene
            ocjena = st.slider("Ocjena:", 1, 5, 5, key=f"rate{idx}")
            if st.button("Pošalji ocjenu", key=f"send{idx}"):
                spremi_ocjenu(row['Ime'], row['Usluga'], ocjena, "Komentar")
                st.success("Hvala!")
