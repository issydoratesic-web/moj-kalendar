import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- FUNKCIJA ZA DISCORD ---
def posalji_na_discord(ime, usluga, kontakt, datum, vrijeme):
    webhook_url = "https://discord.com/api/webhooks/1524364417167261887/vacZD177MFgx-JaegBXKT2hM9ZtsDNj_D1eZoNACpjL9NB225Ewk5_zlxpLshBdPSzS4"
    embed = {
        "title": "🔔 Nova rezervacija!",
        "color": 16753920,
        "fields": [
            {"name": "👤 Klijent", "value": ime, "inline": False},
            {"name": "📅 Termin", "value": f"{datum} u {vrijeme}", "inline": False},
            {"name": "✂️ Usluga", "value": usluga, "inline": False},
            {"name": "📱 Kontakt", "value": kontakt, "inline": False}
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
        if st.button("Odjava"): st.session_state.admin_auth = False; st.rerun()
        df = ucitaj_termine()
        st.subheader("Upravljanje terminima")
        if not df.empty:
            for idx, row in df.iterrows():
                with st.expander(f"{row['Ime']} - {row['Datum']} ({row['Vrijeme']})"):
                    st.write(f"Usluga: {row['Usluga']}")
                    if st.button(f"🗑️ OBRIŠI {idx}", key=f"del_{idx}"):
                        df.drop(idx).to_csv("termini.csv", index=False); st.rerun()
        if st.button("Preuzmi CSV"): st.download_button("📥 Preuzmi", df.to_csv(index=False), "termini.csv")

# --- GLAVNI UI ---
st.title("Rezervacije termina u Adora Beauty Concept-u")
st.markdown("""<div class='custom-box'><strong>Napomena:</strong><br>• Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. Termini otkazani unutar 24h ili nedolazak bez obavijesti naplaćuju se u iznosu 100% cijene usluge.<br>• Prilikom zakazivanja termina za <strong>šminkanje</strong> potrebno je uplatiti akontaciju (50% cijene) na IBAN: HR03 2402 0061 1406 1395 3.</div>""", unsafe_allow_html=True)

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Kontakt (mobitel/Instagram):")

usluge_lista = ["Šminkanje - 40€", "Terensko šminkanje - 50€", "Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"]
odabrane_usluge = st.multiselect("Odaberite usluge:", usluge_lista)

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
        zauzeti = df[(df['Datum'] == datum_str) & (df['Vrijeme'] == vrijeme)]
        
        if not zauzeti.empty:
            st.error("❌ Termin je već zauzet! Molimo odaberite drugo vrijeme.")
        else:
            usluga_str = ", ".join(odabrane_usluge)
            novi = pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": datum_str, "Vrijeme": vrijeme, "Usluga": usluga_str}])
            pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
            posalji_na_discord(f"{ime} {prezime}", usluga_str, kontakt, datum_str, vrijeme)
            st.success("Hvala na rezervaciji! Termin je zaprimljen. Potvrdu termina primit ćete u najkraćem roku putem Instagrama ili WhatsAppa."); time.sleep(2); st.rerun()
    else: st.error("Molimo ispunite sva polja.")

st.markdown("---")
st.subheader("👤 Upravljanje mojim terminom")
ime_otkaz = st.text_input("Upišite ime za pronalazak:")
if ime_otkaz:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.contains(ime_otkaz, case=False, na=False)]
    for idx, row in moji.iterrows():
        if st.button(f"Otkaži termin: {row['Datum']} u {row['Vrijeme']}", key=f"k_{idx}"):
            df.drop(idx).to_csv("termini.csv", index=False); st.success("Otkazano!"); st.rerun()
