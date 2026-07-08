import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- FUNKCIJA ZA DISCORD ---
def posalji_na_discord(naslov, ime, usluga, kontakt, detalji):
    webhook_url = "https://discord.com/api/webhooks/1524442178896658673/2hu1ajtJxHlG-uOs8o5ticqUcaQtctnT5meKpTbr3bk1DvUnndBBTLBu1S1hBgL7sApo"
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
    try: requests.post(webhook_url, json=data, timeout=5)
    except: pass

def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena", "Laminacija", "Alergije"])

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
                if st.button(f"OBRIŠI TERMIN {idx}", key=f"del_admin_{idx}"):
                    df.drop(idx).to_csv("termini.csv", index=False); st.rerun()

# --- GLAVNI UI ---
st.title("Rezervacije termina u Adora Beauty Concept-u")
st.markdown("""<div class='custom-box'><strong>Napomena:</strong><br>• Otkazivanje termina potrebno je najaviti najmanje 24h prije termina.<br>• Prilikom zakazivanja termina za <strong>šminkanje</strong> potrebno je uplatiti akontaciju (50% cijene) na IBAN: HR03 2402 0061 1406 1395 3.</div>""", unsafe_allow_html=True)

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Broj mobitela ili instagram korisničko ime:")

usluge_lista = ["Šminkanje - 40€", "Terensko šminkanje - 50€", "Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€", "Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€", "Kratka kosa - Ravnanje - 10€", "Kratka kosa - Uvijanje - 20€", "Kratka kosa - Hollywood valovi - 25€", "Kratka kosa - Elegantni repovi - 15€", "Punđa - 15€", "Duga kosa - Ravnanje - 20€", "Duga kosa - Uvijanje - 30€", "Duga kosa - Hollywood valovi - 35€", "Duga kosa - Elegantni repovi - 25€", "Little Luxe Spa - Mini - 50€", "Little Luxe Spa - Classic - 70€", "Little Luxe Spa - VIP - 100€"]
odabrane_usluge = st.multiselect("Odaberite jednu ili više usluga:", usluge_lista)

ukupna_cijena = 0
for usluga in odabrane_usluge:
    try:
        cijena_po_osobi = int(usluga.split(" - ")[-1].replace("€", ""))
        ukupna_cijena += cijena_po_osobi
    except: continue
st.markdown(f"### 💰 Ukupno za platiti: {ukupna_cijena}€")

# --- PITANJA ---
lam_da_ne, alergije = "N/A", "N/A"
if any("Brow lift" in u or "laminacija" in u.lower() for u in odabrane_usluge):
    st.markdown("### ⚠️ Dodatna pitanja")
    lam_da_ne = st.radio("Jeste li u posljednjih 6 tjedana radili laminaciju ili lifting trepavica?", ["Da", "Ne"], index=None, key="lam_q")
    alergije = st.text_input("Imate li poznate alergije na kozmetičke proizvode?", key="alg_q")

novi_klijent = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None, key="novi_q")
napomena = st.text_area("Napomena (osjetljiva koža i sl.):", key="nap_q")

c1, c2, c3 = st.columns(3)
dan = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
mjesec = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
godina = c3.selectbox("Godina:", ["2026", "2027", "2028"])
vrijeme = st.selectbox("Vrijeme:", [f"{h:02d}:00" for h in range(8, 21)])

potvrda = st.checkbox("Potvrđujem da sam pročitao/la pravila.")

if st.button("POTVRDI REZERVACIJU"):
    if potvrda and ime and prezime and kontakt:
        df = ucitaj_termine()
        novi = pd.DataFrame([{
            "Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": f"{dan}/{mjesec}/{godina}", 
            "Vrijeme": vrijeme, "Usluga": ", ".join(odabrane_usluge), "Novi_klijent": novi_klijent, 
            "Napomena": napomena, "Laminacija": lam_da_ne, "Alergije": alergije
        }])
        pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
        posalji_na_discord("🔔 Nova rezervacija!", f"{ime} {prezime}", ", ".join(odabrane_usluge), kontakt, f"Datum: {dan}/{mjesec}/{godina}")
        st.success("Hvala na rezervaciji! Termin je zaprimljen. Potvrdu termina primit ćete u najkraćem roku putem Instagrama ili WhatsAppa.")
        time.sleep(5); st.rerun()
    else:
        st.warning("Molimo ispunite sva obavezna polja i prihvatite pravila.")

# --- UPRAVLJANJE MOJIM TERMINOM I OCJENJIVANJE ---
st.markdown("---")
st.subheader("👤 Upravljanje mojim terminom i ocjenjivanje")
ime_otkaz = st.text_input("Upišite ime za pronalazak:")
if ime_otkaz:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.contains(ime_otkaz, case=False, na=False)]
    for idx, row in moji.iterrows():
        with st.expander(f"Termin: {row['Usluga']} ({row['Datum']} u {row['Vrijeme']})"):
            if st.button(f"Otkazi ovaj termin", key=f"del_user_{idx}"):
                posalji_na_discord("❌ Otkazan termin!", row['Ime'], row['Usluga'], row['Kontakt'], f"Datum: {row['Datum']} u {row['Vrijeme']}")
                df.drop(idx).to_csv("termini.csv", index=False); st.rerun()
            
            # Postavke za editiranje
            n_dan = st.selectbox("Novi dan", [f"{i:02d}" for i in range(1, 32)], key=f"d{idx}")
            n_vr = st.selectbox("Novo vrijeme", [f"{h:02d}:00" for h in range(8, 21)], key=f"v{idx}")
            if st.button("Spremi izmjene", key=f"save{idx}"):
                df.at[idx, 'Datum'] = f"{n_dan}/{mjesec}/{godina}"
                df.at[idx, 'Vrijeme'] = n_vr
                df.to_csv("termini.csv", index=False); st.rerun()
            
            ocjena = st.slider("Ocjena:", 1, 5, 5, key=f"rate{idx}")
            komentar = st.text_input("Komentar:", key=f"comm{idx}")
            if st.button("Pošalji ocjenu", key=f"send{idx}"):
                spremi_ocjenu(row['Ime'], row['Usluga'], ocjena, komentar)
                st.success("Hvala na Vašoj ocjeni i komentaru!")
                time.sleep(1); st.rerun()

# --- RECENZIJE KLIJENATA ---
st.markdown("---")
st.subheader("🌟 Recenzije naših klijenata")
df_ocjene = ucitaj_ocjene()
if not df_ocjene.empty:
    for _, row in df_ocjene.iterrows():
        st.markdown(f"""<div class='review-box'><strong>{row['Ime']}</strong> - ⭐ {row['Ocjena']}/5<br><em>Usluga: {row['Usluga']}</em><br>{row['Komentar']}</div>""", unsafe_allow_html=True)
else:
    st.info("Još nema javnih recenzija.")
