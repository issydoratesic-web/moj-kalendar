]
}
data = {"embeds": [embed]}
    requests.post(webhook_url, json=data)
    try: requests.post(webhook_url, json=data)
    except: pass

# --- FUNKCIJE ---
def ucitaj_termine():
@@ -35,147 +36,62 @@ def ucitaj_ocjene():

def spremi_ocjenu(ime, usluga, ocjena, komentar):
df_ocjene = pd.DataFrame([{"Ime": ime, "Usluga": usluga, "Ocjena": ocjena, "Komentar": komentar}])
    if os.path.exists("ocjene.csv"):
        df_ocjene.to_csv("ocjene.csv", mode='a', header=False, index=False)
    else:
        df_ocjene.to_csv("ocjene.csv", index=False)
    df_ocjene.to_csv("ocjene.csv", mode='a', header=not os.path.exists("ocjene.csv"), index=False)

# --- CSS STILOVI ---
st.markdown("""
    <style>
    .custom-box { background-color: #fff0f5; padding: 15px; border-radius: 10px; border-left: 5px solid #d63384; color: #4a4a4a; }
    </style>
    """, unsafe_allow_html=True)
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
        
        if st.button("Odjava"): st.session_state.admin_auth = False; st.rerun()
tab1, tab2 = st.tabs(["📅 Termini", "⭐ Ocjene"])
        
with tab1:
            st.subheader("Upravljanje terminima")
df = ucitaj_termine()
for idx, row in df.iterrows():
with st.expander(f"{row['Ime']} - {row['Datum']} ({row['Vrijeme']})"):
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
                    st.write(f"Usluga: {row['Usluga']}"); st.write(f"Kontakt: {row['Kontakt']}")
                    if st.button(f"OBRIŠI {idx}", key=f"del_{idx}"):
                        df.drop(idx).to_csv("termini.csv", index=False); st.rerun()
            if st.download_button("Preuzmi CSV", df.to_csv(index=False), "termini.csv"): st.success("OK")
        with tab2: st.dataframe(ucitaj_ocjene())

# --- GLAVNI UI ---
st.title("Rezervacije termina u Adora Beauty Concept-u")
st.markdown("""<div class='custom-box'><strong>Napomena:</strong><br>• Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. Termini otkazani unutar 24h ili nedolazak bez obavijesti naplaćuju se u iznosu 100% cijene usluge.<br>• Prilikom zakazivanja termina za <strong>šminkanje</strong> potrebno je uplatiti akontaciju (50% cijene) na IBAN: HR03 2402 0061 1406 1395 3.</div>""", unsafe_allow_html=True)
st.markdown("""<div class='custom-box'><strong>Napomena:</strong> Otkazivanje min 24h ranije. Akontacija 50% za šminkanje (IBAN: HR03 2402 0061 1406 1395 3).</div>""", unsafe_allow_html=True)

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Broj mobitela ili instagram korisničko ime:")
kontakt = st.text_input("Broj mobitela ili Instagram:")

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
usluge_lista = ["Šminkanje - 40€", "Terensko šminkanje - 50€", "Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€", "Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€", "Kratka kosa - Ravnanje - 10€", "Kratka kosa - Uvijanje - 20€", "Kratka kosa - Hollywood valovi - 25€", "Kratka kosa - Elegantni repovi - 15€", "Punđa - 15€", "Duga kosa - Ravnanje - 20€", "Duga kosa - Uvijanje - 30€", "Duga kosa - Hollywood valovi - 35€", "Duga kosa - Elegantni repovi - 25€", "Little Luxe Spa - Mini - 50€", "Little Luxe Spa - Classic - 70€", "Little Luxe Spa - VIP - 100€"]
odabrane_usluge = st.multiselect("Odaberite usluge:", usluge_lista)

broj_osoba = {}
ukupna_cijena = 0
for u in odabrane_usluge:
    cijena = int(u.split(" - ")[-1].replace("€", ""))
    br = st.number_input(f"Broj osoba za: {u}", min_value=1, value=1, key=f"n_{u}") if "Little Luxe" not in u else 1
    broj_osoba[u] = br
    ukupna_cijena += cijena * br

if odabrane_usluge:
    st.write("Navedite broj osoba (za pakete nije potrebno):")
    for usluga in odabrane_usluge:
        cijena_po_osobi = int(usluga.split(" - ")[-1].replace("€", ""))
        if "Little Luxe" not in usluga:
            broj = st.number_input(f"Broj osoba za: {usluga}", min_value=1, value=1, key=f"num_{usluga}")
            broj_osoba[usluga] = broj
            ukupna_cijena += cijena_po_osobi * broj
        else:
            broj_osoba[usluga] = 1
            ukupna_cijena += cijena_po_osobi
    st.markdown(f"### 💰 Ukupno za platiti: {ukupna_cijena}€")

st.subheader("Datum i vrijeme")
st.write(f"### 💰 Ukupno: {ukupna_cijena}€")
c1, c2, c3 = st.columns(3)
dan = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
mjesec = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
godina = c3.selectbox("Godina:", [str(i) for i in range(2026, 2031)])

datum_odabir = f"{dan}/{mjesec}/{godina}"
df_svi = ucitaj_termine()
zauzeti = df_svi[df_svi['Datum'] == datum_odabir]['Vrijeme'].tolist()

sva_vremena = [f"{h:02d}:00" for h in range(8, 21)]
slobodna_vremena = [v for v in sva_vremena if v not in zauzeti]
odabrano_vrijeme = st.selectbox("Odaberite slobodan termin:", slobodna_vremena if slobodna_vremena else ["Nema slobodnih termina"])

st.subheader("Dodatna pitanja")
novi_klijent = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None)
napomena = st.text_area("Napomena (alergije, osjetljiva koža):")

lam_da_ne, alergije = "N/A", "N/A"
if any("Brow lift" in u for u in odabrane_usluge):
    st.markdown("### ⚠️ Za laminaciju obrva i trepavica")
    lam_da_ne = st.radio("Jeste li u posljednjih 6 tjedana radili laminaciju?", ["Da", "Ne"], index=None)
    alergije = st.text_input("Imate li poznate alergije?")

potvrda = st.checkbox("Potvrđujem da sam pročitao/la pravila otkazivanja i uvjete akontacije.")

if st.button("POTVRDI REZERVACIJU"):
    if potvrda and odabrano_vrijeme != "Nema slobodnih termina":
        if ime and prezime and kontakt and novi_klijent and odabrane_usluge:
            lista_detalja = [u if "Little Luxe" in u else f"{u} ({broj_osoba[u]} osoba)" for u in odabrane_usluge]
            detalji_usluga = ", ".join(lista_detalja)
            
            df = ucitaj_termine()
            novi = pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": datum_odabir, "Vrijeme": odabrano_vrijeme, "Usluga": f"{detalji_usluga} (Ukupno: {ukupna_cijena}€)", "Novi_klijent": novi_klijent, "Napomena": napomena, "Laminacija_DA_NE": lam_da_ne, "Alergije": alergije}])
            pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
            
            posalji_na_discord("🔔 Nova rezervacija!", f"{ime} {prezime}", f"{detalji_usluga} | Cijena: {ukupna_cijena}€", kontakt, f"Vrijeme: {odabrano_vrijeme}, Novi: {novi_klijent}, Napomena: {napomena}")
            
            st.success("Hvala na rezervaciji! Termin je zaprimljen.")
            time.sleep(2); st.rerun()
        else: st.error("Molimo ispunite obavezna polja.")
    else: st.warning("Molimo vas da potvrdite pravila i odaberete slobodan termin.")

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
                st.divider()
                st.write("### ⭐ Ocijenite nas:")
                ocjena = st.slider("Ocjena:", 1, 5, 5, key=f"rate_{idx}")
                komentar = st.text_area("Vaš komentar (opcionalno):", key=f"comm_{idx}")
                if st.button("Pošalji ocjenu", key=f"send_rate_{idx}"):
                    spremi_ocjenu(row['Ime'], row['Usluga'], ocjena, komentar)
                    st.success("Hvala na ocjeni!")
    else: st.warning("Nije pronađen termin.")
dan, mjesec, godina = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)]), c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)]), c3.selectbox("Godina:", ["2026", "2027", "2028"])
datum_str = f"{dan}/{mjesec}/{godina}"

# LOGIKA ZAUZEĆA
trajanje = max(1, sum(broj_osoba.values()))
df_termini = ucitaj_termine()
dostupni_sati = []
for h in range(8, 21):
    moguce = True
    for i in range(tra
