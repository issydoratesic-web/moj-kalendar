import streamlit as st
import pandas as pd
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_USER = "adorabeatyconcept.official0@gmail.com"
GMAIL_PASSWORD = "tiox yxkg rbfl bnic"

def posalji_email_obavijest(ime, kontakt, datum, vrijeme):
    naslov = f"⚠️ Nova rezervacija: {ime}"
    tijelo_maila = f"""Pozdrav,
    
Imate novu rezervaciju termina preko web aplikacije!
    
Detalji:
-------------------------------------------
👤 Ime i prezime: {ime}
📱 Instagram / Kontakt: {kontakt}
📅 Datum: {datum}
⏰ Vrijeme: {vrijeme}
-------------------------------------------
    
Ugodan rad želi vam vaš sustav!"""
    
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = GMAIL_USER
    msg['Subject'] = naslov
    msg.attach(MIMEText(tijelo_maila, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(GMAIL_USER, GMAIL_USER, text)
        server.quit()
    except Exception as e:
        pass

DB_FILE = "termini.csv"

def ucitaj_termine():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Status"])

def spremi_termin(ime, kontakt, datum, vrijeme):
    df = ucitaj_termine()
    novi_termin = pd.DataFrame([{
        "Ime": ime, 
        "Kontakt": kontakt, 
        "Datum": str(datum), 
        "Vrijeme": vrijeme, 
        "Status": "Na čekanju"
    }])
    df = pd.concat([df, novi_termin], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

st.set_page_config(page_title="Rezervacija Termina", layout="centered")

stranica = st.sidebar.radio("Navigacija", ["Rezerviraj Termin", "Admin Panel (Za tebe)"])

if stranica == "Rezerviraj Termin":
    st.title("📅 Rezervirajte svoj termin")
    st.write("Odaberite datum i vrijeme koji vam odgovaraju, a ja ću vam se javiti za potvrdu.")
    
    df_termini = ucitaj_termine()
    
    with st.form("rezervacija_forma", clear_on_submit=True):
        ime = st.text_input("Vaše Ime i Prezime:")
        kontakt = st.text_input("Vaš Instagram username ili broj mobitela:")
        datum = st.date_input("Odaberite datum:", min_value=datetime.today().date())
        
        vremena = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
        zauzeta_vremena = df_termini[df_termini["Datum"] == str(datum)]["Vrijeme"].values
        slobodna_vremena = [v for v in vremena if v not in zauzeta_vremena]
        
        if slobodna_vremena:
            vrijeme = st.selectbox("Odaberite vrijeme:", slobodna_vremena)
            poslano = st.form_submit_button("Rezerviraj")
        else:
            st.warning("Nažalost, svi termini za ovaj dan su zauzeti. Odaberite drugi datum.")
            poslano = False
            
        if poslano:
            if ime and kontakt:
                spremi_termin(ime, kontakt, datum, vrijeme)
                posalji_email_obavijest(ime, kontakt, datum, vrijeme)
                st.success(f"Uspješno poslano! Rezervirali ste {datum} u {vrijeme}. Javit ću vam se uskoro!")
            else:
                st.error("Molimo ispunite sva polja.")

elif stranica == "Admin Panel (Za tebe)":
    st.title("📥 Pristigli Termini")
    df_termini = ucitaj_termine()
    if df_termini.empty:
        st.info("Još nema zakazanih termina.")
    else:
        st.dataframe(df_termini, use_container_width=True)
        if st.button("Očisti sve termine"):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
                st.rerun()