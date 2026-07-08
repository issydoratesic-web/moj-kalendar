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
    try: requests.post(webhook_url, json=data)
    except: pass

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena", "Laminacija_DA_NE", "Alergije"])

def ucitaj_ocjene():
    if os.path.exists("ocjene.csv"):
        return pd.read_csv("ocjene.csv")
    return pd.DataFrame(columns=["Ime", "Usluga", "Ocjena", "Komentar"])

def spremi_ocjenu(ime, usluga, ocjena, komentar):
    df_ocjene = pd.DataFrame([{"Ime": ime, "Usluga": usluga, "Ocjena": ocjena, "Komentar": komentar}])
    df_ocjene.to_csv("ocjene.csv", mode='a', header=not os.path.exists("ocjene.csv"), index=False)

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
        if st.button("Odjava"): st.session_state.admin_auth = False; st.rerun()
        tab1, tab2 = st.tabs(["📅 Termini", "⭐ Ocjene"])
        with tab1:
            df = ucitaj_termine()
            for idx, row in df.iterrows():
                with st.expander(f"{row['Ime']} - {row['Datum']} ({row['Vrijeme']})"):
                    st.write(f"Usluga: {row['Usluga']}"); st.write(f"Kontakt: {row['Kontakt']}")
                    if st.button(f"OBRIŠI {idx}", key=f"del_{idx}"):
                        df.drop(idx).to_csv("termini.csv", index=False); st.rerun()
            if st.download_button("Preuzmi CSV", df.to_csv(index=False), "termini.csv"): st.success("OK")
        with tab2: st.dataframe(ucitaj_ocjene())

# --- GLAVNI UI ---
st.title("Rezervacije termina u Adora Beauty Concept-u")
col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Broj mobitela ili Instagram:")

usluge_lista = ["Šminkanje - 40€", "Terensko šminkanje - 50€", "Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€", "Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€", "Kratka kosa - Ravnanje - 10€", "Kratka kosa - Uvijanje - 20€", "Kratka kosa - Hollywood valovi - 25€", "Kratka kosa - Elegantni repovi - 15€", "Punđa - 15€", "Duga kosa - Ravnanje - 20€", "Duga kosa - Uvijanje - 30€", "Duga kosa - Hollywood valovi - 35€", "Duga kosa - Elegantni repovi - 25€", "Little Luxe Spa - Mini - 50€", "Little Luxe Spa - Classic - 70€", "Little Luxe Spa - VIP - 100€"]
odabrane_usluge = st.multiselect("Odaberite usluge:", usluge_lista)

broj_osoba = {}
ukupna_cijena = 0
for u in odabrane_usluge:
    cijena = int(u.split(" - ")[-1].replace("€", ""))
    br = st.number_input(f"Broj osoba za: {u}", min_value=1, value=1, key=f"n_{u}") if "Little Luxe" not in u else 1
    broj_osoba[u] = br
    ukupna_cijena += cijena * br

st.write(f"### 💰 Ukupno: {ukupna_cijena}€")
c1, c2, c3 = st.columns(3)
dan, mjesec, godina = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)]), c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)]), c3.selectbox("Godina:", ["2026", "2027", "2028"])
datum_str = f"{dan}/{mjesec}/{godina}"

# LOGIKA ZAUZEĆA
trajanje = max(1, sum(broj_osoba.values()))
df_termini = ucitaj_termine()
dostupni_sati = []
for h in range(8, 21):
    moguce = True
    for i in range(trajanje):
        if (h + i) >= 20 or f"{h+i:02d}:00" in df_termini[df_termini['Datum'] == datum_str]['Vrijeme'].values:
            moguce = False
            break
    if moguce: dostupni_sati.append(f"{h:02d}:00")

odabrano_vrijeme = st.selectbox("Odaberite slobodan termin:", dostupni_sati if dostupni_sati else ["Nema slobodnih termina"])
novi_klijent = st.radio("Novi klijent?", ["Da", "Ne"], index=None)
napomena = st.text_area("Napomena:")

if st.button("POTVRDI REZERVACIJU"):
    if odabrano_vrijeme != "Nema slobodnih termina" and ime and kontakt:
        df = ucitaj_termine()
        for i in range(trajanje):
            vrijeme_i = f"{int(odabrano_vrijeme[:2]) + i:02d}:00"
            df = pd.concat([df, pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": datum_str, "Vrijeme": vrijeme_i, "Usluga": ", ".join(odabrane_usluge), "Novi_klijent": novi_klijent, "Napomena": napomena}])], ignore_index=True)
        df.to_csv("termini.csv", index=False)
        posalji_na_discord("🔔 Nova rezervacija", f"{ime} {prezime}", ", ".join(odabrane_usluge), kontakt, f"Datum: {datum_str} u {odabrano_vrijeme}")
        st.success("Rezervacija uspješna!"); time.sleep(2); st.rerun()
    else: st.error("Greška ili termin nedostupan.")
