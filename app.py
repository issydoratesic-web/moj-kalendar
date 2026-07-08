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
    try:
        requests.post(webhook_url, json=data)
    except:
        pass

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

# --- CSS STILOVI ---
st.markdown("""
    <style>
    .custom-box { background-color: #fff0f5; padding: 15px; border-radius: 10px; border-left: 5px solid #d63384; color: #4a4a4a; }
    </style>
    """, unsafe_allow_html=True)

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
        
        tab1, tab2 = st.tabs(["📅 Termini", "⭐ Ocjene"])
        
        with tab1:
            st.subheader("Upravljanje terminima")
            df = ucitaj_termine()
            if not df.empty:
                for idx, row in df.iterrows():
                    with st.expander(f"{row['Ime']} - {row['Datum']} ({row['Vrijeme']})"):
                        st.write(f"**Usluga:** {row['Usluga']}")
                        st.write(f"**Kontakt:** {row['Kontakt']}")
                        st.write(f"**Napomena:** {row['Napomena']}")
                        if st.button(f"🗑️ OBRIŠI TERMIN {idx}", key=f"del_{idx}"):
                            posalji_na_discord("❌ Termin otkazan", row['Ime'], row['Usluga'], row['Kontakt'], "Termin je uklonjen.")
                            df.drop(idx).to_csv("termini.csv", index=False)
                            st.rerun()
                if st.download_button("📥 Preuzmi CSV termina", df.to_csv(index=False), "termini.csv"): st.success("Pokrenuto!")
            else: st.info("Nema termina.")

        with tab2:
            st.subheader("Pregled ocjena")
            if os.path.exists("ocjene.csv"):
                df_ocjene = pd.read_csv("ocjene.csv")
                for idx, row in df_ocjene.iterrows():
                    st.markdown(f"**{row['Ime']}** ({row['Ocjena']}⭐)")
                    st.caption(f"Usluga: {row['Usluga']}")
                    st.write(f"💬: *{row['Komentar']}*")
                    st.divider()
            else: st.info("Još nema ocjena.")

# --- GLAVNI UI ---
st.title("Rezervacije termina u Adora Beauty Concept-u")
st.markdown("""<div class='custom-box'><strong>Napomena:</strong><br>• Otkazivanje termina potrebno je najaviti najmanje 24h prije termina.<br>• Prilikom zakazivanja termina za <strong>šminkanje</strong> potrebno je uplatiti akontaciju (50% cijene).</div>""", unsafe_allow_html=True)

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Kontakt (mobitel/Instagram):")

usluge_lista = [
    "Šminkanje - 40€", "Terensko šminkanje - 50€",
    "Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€",
    "Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€",
    "Kratka kosa - Ravnanje - 10€", "Kratka kosa - Uvijanje - 20€", "Kratka kosa - Hollywood valovi - 25€", "Kratka kosa - Elegantni repovi - 15€", "Punđa - 15€",
    "Duga kosa - Ravnanje - 20€", "Duga kosa - Uvijanje - 30€", "Duga kosa - Hollywood valovi - 35€", "Duga kosa - Elegantni repovi - 25€",
    "Little Luxe Spa - Mini - 50€", "Little Luxe Spa - Classic - 70€", "Little Luxe Spa - VIP - 100€"
]

st.subheader("Odabir usluga")
odabrane_usluge = st.multiselect("Odaberite jednu ili više usluga:", usluge_lista)

broj_osoba = {}
ukupna_cijena = 0
if odabrane_usluge:
    for usluga in odabrane_usluge:
        cijena = int(usluga.split(" - ")[-1].replace("€", ""))
        broj = st.number_input(f"Broj osoba za: {usluga}", min_value=1, value=1, key=f"num_{usluga}")
        broj_osoba[usluga] = broj
        ukupna_cijena += cijena * broj
    st.markdown(f"### 💰 Ukupno za platiti: {ukupna_cijena}€")

c1, c2, c3, c4 = st.columns(4)
dan = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
mjesec = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
godina = c3.selectbox("Godina:", [str(i) for i in range(2026, 2031)])
vrijeme = c4.selectbox("Vrijeme:", [f"{i:02d}:00" for i in range(8, 21)])

potvrda = st.checkbox("Potvrđujem da sam pročitao/la pravila.")

if st.button("POTVRDI REZERVACIJU"):
    if potvrda and ime and prezime and kontakt and odabrane_usluge:
        datum_str = f"{dan}/{mjesec}/{godina}"
        df = ucitaj_termine()
        
        # PROVJERA JE LI TERMIN ZAUZET
        zauzeti = df[(df['Datum'] == datum_str) & (df['Vrijeme'] == vrijeme)]
        if not zauzeti.empty:
            st.error("❌ Žao nam je, ovaj termin je već zauzet. Molimo odaberite drugo vrijeme.")
        else:
            lista_detalja = [f"{u} ({broj_osoba[u]} os.)" for u in odabrane_usluge]
            novi = pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": datum_str, "Vrijeme": vrijeme, "Usluga": ", ".join(lista_detalja), "Napomena": "", "Laminacija_DA_NE": "", "Alergije": ""}])
            pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
            posalji_na_discord("🔔 Nova rezervacija!", f"{ime} {prezime}", str(ukupna_cijena), kontakt, datum_str)
            st.success("Hvala! Termin je uspješno rezerviran."); time.sleep(2); st.rerun()
    else: st.error("Molimo ispunite sve podatke.")
