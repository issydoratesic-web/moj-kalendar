
def posalji_discord_obavijest(ime, kontakt, datum, vrijeme):
try:
        # Kod sada koristi novi Webhook koji si poslao
DISCORD_WEBHOOK = st.secrets["DISCORD_WEBHOOK"]
except Exception as e:
st.error("Nedostaje DISCORD_WEBHOOK u Streamlit Secrets!")
return

    # Elegantno formatirana Discord kartica (Embed)
data = {
"content": "🔔 **Stigla je nova rezervacija termina!**",
"embeds": [{
"title": f"👤 Klijent: {ime}",
            "color": 15418782, # Elegantna rozna/crvena boja za tvoj salon
            "color": 15418782, 
"fields": [
{"name": "📱 Kontakt (Instagram/Mobitel)", "value": kontakt, "inline": False},
{"name": "📅 Datum", "value": str(datum), "inline": True},
@@ -29,7 +29,7 @@ def posalji_discord_obavijest(ime, kontakt, datum, vrijeme):
try:
requests.post(DISCORD_WEBHOOK, json=data)
except Exception as e:
        st.error(f"Greska kod slanja na Discord: {e}")
        st.error(f"Greška kod slanja na Discord: {e}")

# --- BAZA PODATAKA ---
DB_FILE = "termini.csv"
@@ -51,14 +51,15 @@ def spremi_termin(ime, kontakt, datum, vrijeme):

if stranica == "Rezerviraj Termin":
st.title("📅 Rezervirajte svoj termin")
    st.write("Odaberite datum i vrijeme koji vam odgovaraju, a ja cu vam se javiti za potvrdu.")
    st.write("Odaberite datum i vrijeme koji vam odgovaraju.")
df_termini = ucitaj_termine()

with st.form("rezervacija_forma", clear_on_submit=True):
ime = st.text_input("Vase Ime i Prezime:")
kontakt = st.text_input("Vas Instagram username ili broj mobitela:")
datum = st.date_input("Odaberite datum:", min_value=datetime.today().date())

        # Ovdje je tvoj novi raspored do 20:00
vremena = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
zauzeta_vremena = df_termini[df_termini["Datum"] == str(datum)]["Vrijeme"].values
slobodna_vremena = [v for v in vremena if v not in zauzeta_vremena]
@@ -67,19 +68,19 @@ def spremi_termin(ime, kontakt, datum, vrijeme):
vrijeme = st.selectbox("Odaberite vrijeme:", slobodna_vremena)
poslano = st.form_submit_button("Rezerviraj")
else:
            st.warning("Svi termini za ovaj dan su zauzeti. Odaberite drugi datum.")
            st.warning("Svi termini za ovaj dan su zauzeti.")
poslano = False

if poslano:
if ime and kontakt:
spremi_termin(ime, kontakt, datum, vrijeme)
posalji_discord_obavijest(ime, kontakt, datum, vrijeme)
                st.success(f"Uspjesno poslano! Rezervirali ste {datum} u {vrijeme}. Javit cu vam se uskoro!")
                st.success(f"Uspjesno poslano! Rezervirali ste {datum} u {vrijeme}.")
else:
st.error("Molimo ispunite sva polja.")

elif stranica == "Admin Panel":
st.title("📥 Pristigli Termini")
df_termini = ucitaj_termine()
if not df_termini.empty:
        st.dataframe(df_termini, use_container_width=True)
        st.dataframe(df_termini, use_container_width=True)
