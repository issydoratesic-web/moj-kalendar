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

# --- CSS STILOVI ---
st.markdown("""
    <style>
    .custom-box { background-color: #fff0f5; padding: 15px; border-radius: 10px; border-left: 5px solid #d63384; color: #4a4a4a; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena", "Laminacija_DA_NE", "Alergije"])

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
            with st.expander(f"{row['Ime']} - {row['Datum']}"):
                st.write(f"Usluga: {row['Usluga']}")
                st.write(f"Kontakt: {row['Kontakt']}")
                if st.button(f"OBRIŠI TERMIN {idx}", key=f"del_{idx}"):
                    posalji_na_discord("❌ Termin otkazan", row['Ime'], row['Usluga'], row['Kontakt'], "Termin je uklonjen iz sustava.")
                    df.drop(idx).to_csv("termini.csv", index=False)
                    st.success("Obrisano!"); st.rerun()
        if st.download_button("Preuzmi CSV", df.to_csv(index=False), "termini.csv"): st.success("Pokrenuto!")

# --- GLAVNI UI ---
st.title("✨ Adora Beauty Concept")
st.markdown("""<div class='custom-box'><strong>Napomena:</strong><br>• Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. Termini otkazani unutar 24h ili nedolazak bez obavijesti naplaćuju se u iznosu 100% cijene usluge.<br>• Prilikom zakazivanja termina za <strong>šminkanje</strong> potrebno je uplatiti akontaciju (50% cijene) na IBAN: HR03 2402 0061 1406 1395 3.</div>""", unsafe_allow_html=True)

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Broj mobitela ili instagram korisničko ime:")

kat = st.selectbox("Odaberite kategoriju:", ["Šminkanje", "Oblikovanje i korekcija obrva", "Tretmani lica", "Frizure", "Little Luxe Spa"], index=None)

usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
    "Frizure": [
        "Kratka kosa - Ravnanje - 10€", "Kratka kosa - Uvijanje - 20€", "Kratka kosa - Hollywood valovi - 25€", "Kratka kosa - Elegantni repovi - 15€", "Punđa - 15€",
        "Duga kosa - Ravnanje - 20€", "Duga kosa - Uvijanje - 30€", "Duga kosa - Hollywood valovi - 35€", "Duga kosa - Elegantni repovi - 25€"
    ],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        st.subheader("Dodatna pitanja")
        novi_klijent = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None)
        napomena = st.text_area("Napomena (alergije, osjetljiva koža):")
        
        lam_da_ne, alergije = "N/A", "N/A"
        if "Brow lift" in usluga:
            st.markdown("### ⚠️ Za laminaciju obrva i trepavica")
            lam_da_ne = st.radio("Jeste li u posljednjih 6 tjedana radili laminaciju?", ["Da", "Ne"], index=None)
            alergije = st.text_input("Imate li poznate alergije?")

        c1, c2, c3 = st.columns(3)
        dan = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
        mjesec = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
        godina = c3.selectbox("Godina:", [str(i) for i in range(2026, 2031)])
        
        potvrda = st.checkbox("Potvrđujem da sam pročitao/la pravila otkazivanja i uvjete akontacije.")
        
        if st.button("POTVRDI REZERVACIJU"):
            if potvrda:
                if ime and prezime and kontakt and novi_klijent:
                    df = ucitaj_termine()
                    novi = pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": f"{dan}/{mjesec}/{godina}", "Vrijeme": "08:00", "Usluga": usluga, "Novi_klijent": novi_klijent, "Napomena": napomena, "Laminacija_DA_NE": lam_da_ne, "Alergije": alergije}])
                    pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
                    
                    posalji_na_discord("🔔 Nova rezervacija!", f"{ime} {prezime}", usluga, kontakt, f"Novi: {novi_klijent}, Napomena: {napomena}, Lam: {lam_da_ne}, Aler: {alergije}")
                    
                    placeholder = st.empty()
                    placeholder.success("Hvala na rezervaciji! Termin je zaprimljen. Potvrdu termina primit ćete u najkraćem roku putem Instagrama ili WhatsAppa.")
                    time.sleep(10)
                    placeholder.empty()
                    st.rerun()
                else: st.error("Molimo ispunite obavezna polja.")
            else:
                st.warning("Molimo vas da potvrdite da ste pročitali pravila otkazivanja kako biste mogli nastaviti.")

st.markdown("---")
st.subheader("👤 Upravljanje mojim terminom")
ime_otkaz = st.text_input("Upišite ime za pronalazak termina:")

if ime_otkaz:
    df = ucitaj_termine()
    df['Ime_clean'] = df['Ime'].astype(str).str.lower().str.strip()
    trazeno_ime = ime_otkaz.lower().strip()
    moji = df[df['Ime_clean'] == trazeno_ime]
    
    if not moji.empty:
        for idx, row in moji.iterrows():
            with st.expander(f"Termin: {row['Usluga']} ({row['Datum']})"):
                if st.button(f"Otkazi ovaj termin", key=f"del_user_{idx}"):
                    df_final = ucitaj_termine()
                    df_final.drop(idx).to_csv("termini.csv", index=False)
                    st.success("Vaš termin je uspješno otkazan!")
                    time.sleep(2)
                    st.rerun()
                
                if st.button("Izmjeni datum/vrijeme", key=f"edit_{idx}"):
                    st.session_state[f"edit_mode_{idx}"] = True
                
                if st.session_state.get(f"edit_mode_{idx}", False):
                    n_dan = st.selectbox("Novi dan:", [f"{i:02d}" for i in range(1, 32)], key=f"d_{idx}")
                    n_mjesec = st.selectbox("Novi mjesec:", [f"{i:02d}" for i in range(1, 13)], key=f"m_{idx}")
                    n_godina = st.selectbox("Nova godina:", [str(i) for i in range(2026, 2031)], key=f"g_{idx}")
                    
                    if st.button("Spremi novi termin", key=f"save_{idx}"):
                        df_final = ucitaj_termine()
                        df_final.at[idx, 'Datum'] = f"{n_dan}/{n_mjesec}/{n_godina}"
                        df_final.to_csv("termini.csv", index=False)
                        st.success("Termin uspješno izmijenjen!")
                        st.session_state[f"edit_mode_{idx}"] = False
                        time.sleep(2)
                        st.rerun()
    else: 
        st.warning(f"Nije pronađen termin pod imenom: {ime_otkaz}.")
