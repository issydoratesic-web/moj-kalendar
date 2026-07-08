]
}
data = {"embeds": [embed]}
    try: requests.post(webhook_url, json=data)
    except: pass
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
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena"])

def ucitaj_ocjene():
    if os.path.exists("ocjene.csv"):
        return pd.read_csv("ocjene.csv")
    return pd.DataFrame(columns=["Ime", "Usluga", "Ocjena", "Komentar"])

def spremi_ocjenu(ime, usluga, ocjena, komentar):
    df_ocjene = pd.DataFrame([{"Ime": ime, "Usluga": usluga, "Ocjena": ocjena, "Komentar": komentar}])
    df_ocjene.to_csv("ocjene.csv", mode='a', header=not os.path.exists("ocjene.csv"), index=False)
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
        if st.button("Odjava"): st.session_state.admin_auth = False; st.rerun()
        tab1, tab2 = st.tabs(["📅 Termini", "⭐ Ocjene"])
        with tab1:
            df = ucitaj_termine()
            for idx, row in df.iterrows():
                with st.expander(f"{row['Ime']} - {row['Datum']} ({row['Vrijeme']})"):
                    st.write(f"Usluga: {row['Usluga']}")
                    if st.button(f"OBRIŠI {idx}", key=f"del_{idx}"):
                        df.drop(idx).to_csv("termini.csv", index=False); st.rerun()
        with tab2: st.dataframe(ucitaj_ocjene())
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
st.title("Adora Beauty Concept")
ime = st.text_input("Ime:")
kontakt = st.text_input("Kontakt:")
usluge_lista = ["Šminkanje", "Brow lift", "Punđa", "Oblikovanje obrva"]
odabrane = st.multiselect("Usluge:", usluge_lista)

dan, mjesec, godina = st.columns(3)
d = dan.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
m = mjesec.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
g = godina.selectbox("Godina:", ["2026", "2027"])
datum_str = f"{d}/{m}/{g}"

# LOGIKA ZAUZEĆA
trajanje = max(1, len(odabrane))
df_t = ucitaj_termine()
dostupni = []
for h in range(8, 21):
    moguce = True
    for i in range(trajanje):
        if (h+i) >= 20 or f"{h+i:02d}:00" in df_t[df_t['Datum'] == datum_str]['Vrijeme'].values:
            moguce = False
    if moguce: dostupni.append(f"{h:02d}:00")

termin = st.selectbox("Termin:", dostupni if dostupni else ["Nema slobodnih"])

if st.button("POTVRDI"):
    if termin != "Nema slobodnih" and ime:
        df = ucitaj_termine()
        for i in range(trajanje):
            v = f"{int(termin[:2]) + i:02d}:00"
            df = pd.concat([df, pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum_str, "Vrijeme": v, "Usluga": ", ".join(odabrane)}])], ignore_index=True)
        df.to_csv("termini.csv", index=False)
        st.success("Rezervirano!"); time.sleep(1); st.rerun()
st.title("Rezervacije termina u Adora Beauty Concept-u")
st.markdown("""<div class='custom-box'><strong>Napomena:</strong><br>• Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. Termini otkazani unutar 24h ili nedolazak bez obavijesti naplaćuju se u iznosu 100% cijene usluge.<br>• Prilikom zakazivanja termina za <strong>šminkanje</strong> potrebno je uplatiti akontaciju (50% cijene) na IBAN: HR03 2402 0061 1406 1395 3.</div>""", unsafe_allow_html=True)

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Broj mobitela ili instagram korisničko ime:")

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
    st.write("Navedite broj osoba (za pakete nije potrebno):")
    for usluga in odabrane_usluge:
        cijena_po_osobi = int(usluga.split(" - ")[-1].replace("€", ""))
        
        # Broj osoba samo ako NIJE Little Luxe
        if "Little Luxe" not in usluga:
            broj = st.number_input(f"Broj osoba za: {usluga}", min_value=1, value=1, key=f"num_{usluga}")
            broj_osoba[usluga] = broj
            ukupna_cijena += cijena_po_osobi * broj
        else:
            broj_osoba[usluga] = 1 # Fiksno 1 za pakete
            ukupna_cijena += cijena_po_osobi
            
    st.markdown(f"### 💰 Ukupno za platiti: {ukupna_cijena}€")

st.subheader("Dodatna pitanja")
novi_klijent = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None)
napomena = st.text_area("Napomena (alergije, osjetljiva koža):")

lam_da_ne, alergije = "N/A", "N/A"
if any("Brow lift" in u for u in odabrane_usluge):
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
        if ime and prezime and kontakt and novi_klijent and odabrane_usluge:
            # Formatiranje prikaza ovisno o tome je li paket ili ne
            lista_detalja = []
            for u in odabrane_usluge:
                if "Little Luxe" in u:
                    lista_detalja.append(u)
                else:
                    lista_detalja.append(f"{u} ({broj_osoba[u]} osoba)")
            
            detalji_usluga = ", ".join(lista_detalja)
            
            df = ucitaj_termine()
            novi = pd.DataFrame([{
                "Ime": f"{ime} {prezime}", 
                "Kontakt": kontakt, 
                "Datum": f"{dan}/{mjesec}/{godina}", 
                "Vrijeme": "08:00", 
                "Usluga": f"{detalji_usluga} (Ukupno: {ukupna_cijena}€)", 
                "Novi_klijent": novi_klijent, 
                "Napomena": napomena, 
                "Laminacija_DA_NE": lam_da_ne, 
                "Alergije": alergije
            }])
            pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
            
            posalji_na_discord("🔔 Nova rezervacija!", f"{ime} {prezime}", f"{detalji_usluga} | Cijena: {ukupna_cijena}€", kontakt, f"Novi: {novi_klijent}, Napomena: {napomena}")
            
            placeholder = st.empty()
            placeholder.success("Hvala na rezervaciji! Termin je zaprimljen. Potvrdu termina primit ćete u najkraćem roku putem Instagrama ili WhatsAppa.")
            time.sleep(5)
            placeholder.empty()
            st.rerun()
        else: st.error("Molimo ispunite obavezna polja.")
    else: st.warning("Molimo vas da potvrdite da ste pročitali pravila.")

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
                    st.success("Vaš termin je uspješno otkazan!"); st.rerun()
                
                if st.button("Izmjeni datum", key=f"edit_btn_{idx}"):
                    st.session_state[f"edit_mode_{idx}"] = True
                
                if st.session_state.get(f"edit_mode_{idx}", False):
                    n_dan = st.selectbox("Novi dan:", [f"{i:02d}" for i in range(1, 32)], key=f"d_{idx}")
                    n_mjesec = st.selectbox("Novi mjesec:", [f"{i:02d}" for i in range(1, 13)], key=f"m_{idx}")
                    n_godina = st.selectbox("Nova godina:", [str(i) for i in range(2026, 2031)], key=f"g_{idx}")
                    
                    if st.button("Spremi novi datum", key=f"save_{idx}"):
                        df_final = ucitaj_termine()
                        df_final.at[idx, 'Datum'] = f"{n_dan}/{n_mjesec}/{n_godina}"
                        df_final.to_csv("termini.csv", index=False)
                        st.success("Datum uspješno izmijenjen!")
                        st.session_state[f"edit_mode_{idx}"] = False
                        st.rerun()
    else: st.warning("Nije pronađen termin.")
