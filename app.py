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
kontakt = st.text_input("Broj mobitela ili Instagram:")

usluge_lista = ["Šminkanje - 40€", "Terensko šminkanje - 50€", "Brow lift - 30€", "Brow lift i bojanje - 35€", "Duga kosa - Elegantni repovi - 25€", "Kratka kosa - Hollywood valovi - 25€"]
odabrane_usluge = st.multiselect("Odaberite usluge:", usluge_lista)

ukupna_cijena = 0
for usluga in odabrane_usluge:
    cijena = int(usluga.split(" - ")[-1].replace("€", ""))
    ukupna_cijena += cijena
st.markdown(f"### 💰 Ukupno: {ukupna_cijena}€")

novi_klijent = st.radio("Novi klijent?", ["Da", "Ne"], index=None)
napomena = st.text_area("Napomena:")

c1, c2, c3 = st.columns(3)
dan = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
mjesec = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
godina = c3.selectbox("Godina:", ["2026", "2027"])
vrijeme = st.selectbox("Vrijeme:", [f"{h:02d}:00" for h in range(8, 21)])

potvrda = st.checkbox("Potvrđujem pravila.")

if st.button("POTVRDI REZERVACIJU"):
    if potvrda and ime and prezime:
        df = ucitaj_termine()
        novi = pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": f"{dan}/{mjesec}/{godina}", "Vrijeme": vrijeme, "Usluga": ", ".join(odabrane_usluge), "Novi_klijent": novi_klijent, "Napomena": napomena}])
        pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
        st.success("Rezervacija zaprimljena!")
        time.sleep(2); st.rerun()

# --- UPRAVLJANJE TERMINOM ---
st.markdown("---")
st.subheader("👤 Upravljanje mojim terminom")
trazi = st.text_input("Upišite ime za pronalazak termina:")

if trazi:
    df = ucitaj_termine()
    # Pretraživanje po dijelu imena, neovisno o velikim/malim slovima
    moji = df[df['Ime'].str.contains(trazi, case=False, na=False)]
    
    if not moji.empty:
        for idx, row in moji.iterrows():
            with st.expander(f"Termin: {row['Ime']} - {row['Datum']} u {row['Vrijeme']}"):
                if st.button("Otkazi ovaj termin", key=f"del_user_{idx}"):
                    df.drop(idx).to_csv("termini.csv", index=False)
                    st.success("Termin otkazan!"); st.rerun()
                
                # Izmjena
                n_dan = st.selectbox("Novi dan", [f"{i:02d}" for i in range(1, 32)], key=f"d_{idx}")
                n_vr = st.selectbox("Novo vrijeme", [f"{h:02d}:00" for h in range(8, 21)], key=f"v_{idx}")
                if st.button("Spremi izmjene", key=f"save_{idx}"):
                    df.at[idx, 'Datum'] = f"{n_dan}/{mjesec}/2026"
                    df.at[idx, 'Vrijeme'] = n_vr
                    df.to_csv("termini.csv", index=False)
                    st.success("Ažurirano!"); st.rerun()
    else:
        st.warning("Nije pronađen termin pod tim imenom.")
