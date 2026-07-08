import streamlit as st
import pandas as pd
import os
import time
import requests

# --- RESETIRANJE OCJENA (Ovo ce obrisati stare recenzije) ---
if os.path.exists("ocjene.csv"):
    os.remove("ocjene.csv")

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

def ucitaj_ocjene():
    if os.path.exists("ocjene.csv"):
        return pd.read_csv("ocjene.csv")
    return pd.DataFrame()

# --- CSS ---
st.markdown("""<style>.custom-box { background-color: #fff0f5; padding: 15px; border-radius: 10px; border-left: 5px solid #d63384; color: #4a4a4a; } .review-box { background-color: #fff0f5; padding: 15px; border-radius: 10px; border-left: 5px solid #d63384; margin-bottom: 15px; color: #4a4a4a; }</style>""", unsafe_allow_html=True)

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
st.markdown("""<div class='custom-box'><strong>Napomena:</strong><br>• Otkazivanje termina potrebno je najaviti najmanje 24h prije termina.</div>""", unsafe_allow_html=True)

# --- FORMA ---
ime = st.text_input("Ime:")
prezime = st.text_input("Prezime:")
kontakt = st.text_input("Broj mobitela:")
usluge_lista = ["Šminkanje - 40€", "Brow lift - 30€"]
odabrane_usluge = st.multiselect("Odaberite usluge:", usluge_lista)
if st.button("POTVRDI REZERVACIJU"):
    df = ucitaj_termine()
    novi = pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": "01/01/2026", "Vrijeme": "08:00", "Usluga": ", ".join(odabrane_usluge)}])
    pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
    st.success("Vaš termin je zaprimljen!")

# --- UPRAVLJANJE MOJIM TERMINOM ---
st.markdown("---")
st.subheader("👤 Upravljanje mojim terminom i ocjenjivanje")
ime_pretraga = st.text_input("Upišite ime za pronalazak termina:")
if ime_pretraga:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.contains(ime_pretraga, case=False, na=False)]
    for idx, row in moji.iterrows():
        with st.expander(f"Termin: {row['Usluga']} ({row['Datum']} {row['Vrijeme']})"):
            if st.button(f"OTKAŽI {idx}", key=f"otk_{idx}"):
                df.drop(idx).to_csv("termini.csv", index=False); st.rerun()
            ocjena = st.slider("Ocjena:", 1, 5, 5, key=f"s{idx}")
            komentar = st.text_input("Komentar:", key=f"c{idx}")
            if st.button("Pošalji ocjenu", key=f"send{idx}"):
                spremi_ocjenu(row['Ime'], row['Usluga'], ocjena, komentar)
                st.rerun()

# --- RECENZIJE ---
st.markdown("---")
st.subheader("🌟 Recenzije naših klijenata")
df_oc = ucitaj_ocjene()
for _, r in df_oc.iterrows():
    st.markdown(f"<div class='review-box'><strong>{r['Ime']}</strong>: {r['Ocjena']}/5<br>{r['Komentar']}</div>", unsafe_allow_html=True)
