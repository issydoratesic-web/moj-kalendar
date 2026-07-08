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

def ucitaj_ocjene():
    if os.path.exists("ocjene.csv"):
        return pd.read_csv("ocjene.csv")
    return pd.DataFrame(columns=["Ime", "Usluga", "Ocjena", "Komentar"])

def spremi_ocjenu(ime, usluga, ocjena, komentar):
    df_ocjene = pd.DataFrame([{"Ime": ime, "Usluga": usluga, "Ocjena": ocjena, "Komentar": komentar}])
    if os.path.exists("ocjene.csv"):
        df_ocjene.to_csv("ocjene.csv", mode='a', header=False, index=False)
    else:
        df_ocjene.to_csv("ocjene.csv", index=False)

# --- CSS STILOVI ---
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
        
        tab1, tab2 = st.tabs(["📅 Termini", "⭐ Ocjene"])
        
        with tab1:
            st.subheader("Upravljanje terminima")
            df = ucitaj_termine()
            for idx, row in df.iterrows():
                with st.expander(f"{row['Datum']} u {row['Vrijeme']} - {row['Ime']}"):
                    st.write(f"Usluga: {row['Usluga']}")
                    st.write(f"Kontakt: {row['Kontakt']}")
                    if st.button(f"OBRIŠI TERMIN {idx}", key=f"del_{idx}"):
                        posalji_na_discord("❌ Termin otkazan", row['Ime'], row['Usluga'], row['Kontakt'], "Termin je uklonjen iz sustava.")
                        df.drop(idx).to_csv("termini.csv", index=False)
                        st.rerun()
            if st.download_button("Preuzmi CSV", df.to_csv(index=False), "termini.csv"): st.success("Pokrenuto!")
            
        with tab2:
            st.subheader("Ocjene klijenata")
            st.dataframe(ucitaj_ocjene())

# --- GLAVNI UI ---
st.title("Rezervacije termina u Adora Beauty Concept-u")
st.markdown("""<div class='custom-box'><strong>Napomena:</strong><br>• Otkazivanje termina potrebno je najaviti najmanje 24h prije termina.</div>""", unsafe_allow_html=True)

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Kontakt (mobitel/IG):")

usluge_lista = ["Šminkanje - 40€", "Brow lift - 30€", "Punđa - 15€", "Oblikovanje obrva - 8€"]
odabrane_usluge = st.multiselect("Odaberite jednu ili više usluga:", usluge_lista)

# --- ODABIR DATUMA I VREMENA ---
st.subheader("Datum i vrijeme")
c1, c2, c3 = st.columns(3)
dan = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
mjesec = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
godina = c3.selectbox("Godina:", ["2026", "2027"])

datum_odabir = f"{dan}/{mjesec}/{godina}"
df_svi = ucitaj_termine()
zauzeti = df_svi[df_svi['Datum'] == datum_odabir]['Vrijeme'].tolist()

sva_vremena = [f"{h:02d}:00" for h in range(8, 21)]
slobodna_vremena = [v for v in sva_vremena if v not in zauzeti]

odabrano_vrijeme = st.selectbox("Odaberite vrijeme:", slobodna_vremena if slobodna_vremena else ["Nema slobodnih termina"])

novi_klijent = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None)
napomena = st.text_area("Napomena:")

potvrda = st.checkbox("Potvrđujem pravila otkazivanja.")

if st.button("POTVRDI REZERVACIJU"):
    if potvrda and ime and prezime and odabrano_vrijeme != "Nema slobodnih termina":
        df = ucitaj_termine()
        novi = pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": datum_odabir, "Vrijeme": odabrano_vrijeme, "Usluga": ", ".join(odabrane_usluge), "Novi_klijent": novi_klijent, "Napomena": napomena, "Laminacija_DA_NE": "N/A", "Alergije": "N/A"}])
        pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
        posalji_na_discord("🔔 Nova rezervacija!", f"{ime} {prezime}", ", ".join(odabrane_usluge), kontakt, f"Datum: {datum_odabir} u {odabrano_vrijeme}")
        st.success("Termin uspješno rezerviran!"); time.sleep(2); st.rerun()
    else: st.error("Ispunite sva polja ili odaberite drugi termin.")

# --- UPRAVLJANJE MOJIM TERMINOM ---
st.markdown("---")
st.subheader("👤 Upravljanje mojim terminom i ocjenjivanje")
ime_otkaz = st.text_input("Upišite ime za pronalazak termina:")

if ime_otkaz:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.contains(ime_otkaz, case=False, na=False)]
    if not moji.empty:
        for idx, row in moji.iterrows():
            with st.expander(f"Termin: {row['Usluga']} ({row['Datum']} u {row['Vrijeme']})"):
                if st.button(f"Otkazi ovaj termin", key=f"del_user_{idx}"):
                    df.drop(idx).to_csv("termini.csv", index=False); st.rerun()
                st.write("---")
                ocjena = st.slider("Ocjena:", 1, 5, 5, key=f"rate_{idx}")
                komentar = st.text_area("Komentar:", key=f"comm_{idx}")
                if st.button("Pošalji ocjenu", key=f"send_rate_{idx}"):
                    spremi_ocjenu(row['Ime'], row['Usluga'], ocjena, komentar)
                    st.success("Hvala!")
