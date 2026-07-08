import streamlit as st
import pandas as pd
import sqlite3
import re
import requests
from datetime import datetime, date, time, timedelta
from io import BytesIO

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

DB = "adora.db"

# --- USLUGE: naziv -> (cijena €, trajanje min, po_osobi) ---
USLUGE = {
    "Šminkanje": (40, 60, True),
    "Terensko šminkanje": (50, 75, True),
    "Oblikovanje obrva pincetom": (8, 20, True),
    "Oblikovanje i bojanje obrva": (15, 30, True),
    "Brow lift": (30, 60, True),
    "Brow lift i bojanje": (35, 75, True),
    "Enzimski piling": (25, 45, True),
    "Blagi mehanički piling": (20, 40, True),
    "Parenje toplim ručnikom i masaža uz piling": (35, 60, True),
    "Kratka kosa - Ravnanje": (10, 30, True),
    "Kratka kosa - Uvijanje": (20, 45, True),
    "Kratka kosa - Hollywood valovi": (25, 60, True),
    "Kratka kosa - Elegantni repovi": (15, 30, True),
    "Punđa": (15, 30, True),
    "Duga kosa - Ravnanje": (20, 45, True),
    "Duga kosa - Uvijanje": (30, 60, True),
    "Duga kosa - Hollywood valovi": (35, 75, True),
    "Duga kosa - Elegantni repovi": (25, 45, True),
    "Little Luxe Spa - Mini": (50, 60, False),
    "Little Luxe Spa - Classic": (70, 90, False),
    "Little Luxe Spa - VIP": (100, 120, False),
}

RADNO_OD = 8       # 08:00
RADNO_DO = 20      # zadnji start 20:00
SLOT_MIN = 15      # raster
NERADNI_DANI = {6} # 6 = nedjelja (0 = ponedjeljak)

# --- SECRETS (postavi u .streamlit/secrets.toml) ---
def _secret(key, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return default

DISCORD_WEBHOOK = _secret("DISCORD_WEBHOOK", "")
ADMIN_PASSWORD = _secret("ADMIN_PASSWORD", "171102")  # fallback za lokalni test

# --- BAZA ---
def get_conn():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    with get_conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS termini(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ime TEXT, kontakt TEXT,
            datum TEXT, vrijeme TEXT, trajanje INTEGER,
            usluge TEXT, cijena INTEGER,
            novi_klijent TEXT, napomena TEXT,
            laminacija TEXT, alergije TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS ocjene(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            termin_id INTEGER, ime TEXT, usluga TEXT,
            ocjena INTEGER, komentar TEXT,
            odobreno INTEGER DEFAULT 0,
            created_at TEXT
        )""")
init_db()

# --- HELPERI ---
def posalji_discord(naslov, ime, usluga, kontakt, detalji, boja=16753920):
    if not DISCORD_WEBHOOK:
        return
    try:
        requests.post(DISCORD_WEBHOOK, json={"embeds":[{
            "title": naslov, "color": boja,
            "fields":[
                {"name":"👤 Klijent","value":ime or "-"},
                {"name":"✂️ Usluga","value":usluga or "-"},
                {"name":"📱 Kontakt","value":kontakt or "-"},
                {"name":"📝 Detalji","value":detalji or "-"},
            ]
        }]}, timeout=5)
    except Exception as e:
        st.warning(f"Discord obavijest nije poslana ({e}).")

def valid_kontakt(s):
    s = s.strip()
    if s.startswith("@") and len(s) > 1: return True
    return re.fullmatch(r"(\+?385|0)[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{3,4}", s) is not None

def preklapa(dat, start_hm, trajanje):
    start = datetime.combine(dat, datetime.strptime(start_hm, "%H:%M").time())
    end = start + timedelta(minutes=trajanje)
    with get_conn() as c:
        rows = c.execute("SELECT vrijeme, trajanje FROM termini WHERE datum=? AND status!='cancelled'",
                         (dat.isoformat(),)).fetchall()
    for v, t in rows:
        s2 = datetime.combine(dat, datetime.strptime(v, "%H:%M").time())
        e2 = s2 + timedelta(minutes=t or 30)
        if start < e2 and s2 < end:
            return True
    return False

def slobodni_slotovi(dat, trajanje):
    slots = []
    cur = datetime.combine(dat, time(RADNO_OD, 0))
    kraj = datetime.combine(dat, time(RADNO_DO, 0))
    while cur <= kraj:
        hm = cur.strftime("%H:%M")
        if not preklapa(dat, hm, trajanje):
            slots.append(hm)
        cur += timedelta(minutes=SLOT_MIN)
    return slots

# --- STIL ---
st.markdown("""<style>
.custom-box{background:#fff0f5;padding:15px;border-radius:10px;border-left:5px solid #d63384;color:#4a4a4a}
.review-box{background:#fff0f5;padding:15px;border-radius:10px;border-left:5px solid #d63384;margin-bottom:15px;color:#4a4a4a}
</style>""", unsafe_allow_html=True)

# --- ADMIN ---
with st.sidebar:
    st.header("🔐 Admin Panel")
    if "admin" not in st.session_state: st.session_state.admin = False
    if not st.session_state.admin:
        pwd = st.text_input("Lozinka:", type="password")
        if st.button("Prijava"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin = True; st.rerun()
            else: st.error("Pogrešna lozinka!")
    else:
        if st.button("Odjava"): st.session_state.admin = False; st.rerun()

        tab1, tab2, tab3, tab4 = st.tabs(["📅 Termini", "📊 Statistika", "⭐ Recenzije", "⬇️ Export"])

        with tab1:
            with get_conn() as c:
                df = pd.read_sql("SELECT * FROM termini ORDER BY datum, vrijeme", c)
            if df.empty:
                st.info("Nema termina.")
            else:
                for _, r in df.iterrows():
                    with st.expander(f"{r['datum']} {r['vrijeme']} — {r['ime']} ({r['status']})"):
                        st.write(f"**Usluge:** {r['usluge']}")
                        st.write(f"**Kontakt:** {r['kontakt']} | **Cijena:** {r['cijena']}€")
                        st.write(f"**Napomena:** {r['napomena'] or '-'}")
                        col1, col2, col3 = st.columns(3)
                        if r['status'] == 'pending' and col1.button("✅ Potvrdi", key=f"c{r['id']}"):
                            with get_conn() as c: c.execute("UPDATE termini SET status='confirmed' WHERE id=?", (r['id'],))
                            st.rerun()
                        if r['status'] != 'done' and col2.button("✔️ Obavljen", key=f"d{r['id']}"):
                            with get_conn() as c: c.execute("UPDATE termini SET status='done' WHERE id=?", (r['id'],))
                            st.rerun()
                        if col3.button("🗑️ Obriši", key=f"x{r['id']}"):
                            with get_conn() as c: c.execute("DELETE FROM termini WHERE id=?", (r['id'],))
                            st.rerun()

        with tab2:
            with get_conn() as c:
                df = pd.read_sql("SELECT * FROM termini", c)
            if df.empty: st.info("Nema podataka.")
            else:
                df['datum_dt'] = pd.to_datetime(df['datum'], errors='coerce')
                st.metric("Ukupno termina", len(df))
                st.metric("Prihod (obavljeni)", f"{df[df['status']=='done']['cijena'].sum()}€")
                st.metric("Novi klijenti", (df['novi_klijent']=='Da').sum())
                mj = df.groupby(df['datum_dt'].dt.to_period('M'))['cijena'].sum()
                if not mj.empty:
                    st.bar_chart(mj.rename(lambda p: str(p)))
                top = df['usluge'].str.split(', ').explode().value_counts().head(5)
                st.write("**Top 5 usluga:**"); st.dataframe(top)

        with tab3:
            with get_conn() as c:
                oc = pd.read_sql("SELECT * FROM ocjene ORDER BY created_at DESC", c)
            for _, r in oc.iterrows():
                with st.expander(f"{r['ime']} — {r['ocjena']}⭐ ({'✅' if r['odobreno'] else '⏳'})"):
                    st.write(r['komentar'])
                    col1, col2 = st.columns(2)
                    if not r['odobreno'] and col1.button("Odobri", key=f"oa{r['id']}"):
                        with get_conn() as c: c.execute("UPDATE ocjene SET odobreno=1 WHERE id=?", (r['id'],))
                        st.rerun()
                    if col2.button("Obriši", key=f"ox{r['id']}"):
                        with get_conn() as c: c.execute("DELETE FROM ocjene WHERE id=?", (r['id'],))
                        st.rerun()

        with tab4:
            with get_conn() as c:
                df = pd.read_sql("SELECT * FROM termini", c)
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as w:
                df.to_excel(w, index=False, sheet_name='Termini')
            st.download_button("⬇️ Preuzmi Excel", buf.getvalue(), "termini.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- GLAVNI UI ---
st.title("Rezervacije termina — Adora Beauty Concept")

# Prosjek ocjena
with get_conn() as c:
    prosjek = c.execute("SELECT AVG(ocjena), COUNT(*) FROM ocjene WHERE odobreno=1").fetchone()
if prosjek[1]:
    st.markdown(f"### ⭐ {prosjek[0]:.1f}/5 ({prosjek[1]} recenzija)")

st.markdown("""<div class='custom-box'><strong>Napomena:</strong><br>
• Otkazivanje najmanje 24h prije termina. Kasnija otkazivanja ili nedolazak = 100% cijene.<br>
• Za <strong>šminkanje</strong> potrebna akontacija (50%) na IBAN: HR03 2402 0061 1406 1395 3.</div>""",
unsafe_allow_html=True)

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Broj mobitela (+385...) ili @instagram:")

odabrane = st.multiselect("Odaberite jednu ili više usluga:",
    [f"{n} - {c}€" for n, (c, _, _) in USLUGE.items()])

broj_osoba = {}
ukupna_cijena = 0
ukupno_trajanje = 0
odabrani_kljucevi = []
for label in odabrane:
    naziv = label.rsplit(" - ", 1)[0]
    cijena, traj, po_osobi = USLUGE[naziv]
    broj = st.number_input(f"Broj osoba za: {naziv}", 1, 10, 1) if po_osobi else 1
    broj_osoba[naziv] = broj
    ukupna_cijena += cijena * broj
    ukupno_trajanje += traj * broj
    odabrani_kljucevi.append(naziv)

if odabrane:
    st.markdown(f"### 💰 Ukupno: {ukupna_cijena}€ · ⏱️ ~{ukupno_trajanje} min")

novi_klijent = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None)
napomena = st.text_area("Napomena:")
lam, alerg = "N/A", "N/A"
if any("Brow lift" in n for n in odabrani_kljucevi):
    st.markdown("### ⚠️ Laminacija")
    lam = st.radio("Laminacija u zadnjih 6 tjedana?", ["Da", "Ne"], index=None)
    alerg = st.text_input("Alergije?")

dat = st.date_input("Datum:", min_value=date.today(), max_value=date.today()+timedelta(days=365))
if dat.weekday() in NERADNI_DANI:
    st.error("Nedjeljom ne radimo. Odaberi drugi dan.")
    slobodni = []
elif ukupno_trajanje == 0:
    slobodni = []
else:
    slobodni = slobodni_slotovi(dat, ukupno_trajanje)

vrijeme = st.selectbox("Slobodno vrijeme:", slobodni) if slobodni else None
if odabrane and not slobodni and dat.weekday() not in NERADNI_DANI:
    st.warning("Nema slobodnih slotova za odabrane usluge tog dana.")

potvrda = st.checkbox("Prihvaćam pravila otkazivanja i akontacije.")

if st.button("POTVRDI REZERVACIJU", type="primary"):
    if not (ime and prezime): st.error("Unesite ime i prezime.")
    elif not valid_kontakt(kontakt): st.error("Neispravan mobitel ili @instagram.")
    elif not odabrane: st.error("Odaberite barem jednu uslugu.")
    elif not vrijeme: st.error("Odaberite vrijeme.")
    elif not potvrda: st.error("Morate prihvatiti pravila.")
    elif preklapa(dat, vrijeme, ukupno_trajanje):
        st.error("Slot je upravo zauzet, odaberite drugi.")
    else:
        puno_ime = f"{ime.strip()} {prezime.strip()}"
        with get_conn() as c:
            c.execute("""INSERT INTO termini(ime,kontakt,datum,vrijeme,trajanje,usluge,cijena,
                novi_klijent,napomena,laminacija,alergije,status,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (puno_ime, kontakt, dat.isoformat(), vrijeme, ukupno_trajanje,
                 ", ".join(odabrani_kljucevi), ukupna_cijena,
                 novi_klijent or "-", napomena, lam, alerg, "pending",
                 datetime.now().isoformat()))
        posalji_discord("🔔 Nova rezervacija", puno_ime, ", ".join(odabrani_kljucevi),
                        kontakt, f"{dat.isoformat()} u {vrijeme} · {ukupna_cijena}€")
        st.success("Rezervacija zaprimljena! Javit ćemo se za potvrdu.")
        st.balloons()

# --- MOJI TERMINI ---
st.markdown("---")
st.subheader("👤 Moji termini / ocjenjivanje")
trazi = st.text_input("Upišite ime za pronalazak:")
if trazi:
    with get_conn() as c:
        moji = pd.read_sql("SELECT * FROM termini WHERE lower(ime) LIKE ? ORDER BY datum DESC",
                           c, params=(f"%{trazi.lower()}%",))
    if moji.empty: st.info("Nema termina pod tim imenom.")
    for _, r in moji.iterrows():
        with st.expander(f"{r['datum']} u {r['vrijeme']} — {r['usluge']} ({r['status']})"):
            budući = r['datum'] >= date.today().isoformat()
            if budući and r['status'] != 'done':
                if st.button("❌ Otkaži", key=f"uc{r['id']}"):
                    with get_conn() as c: c.execute("UPDATE termini SET status='cancelled' WHERE id=?", (r['id'],))
                    posalji_discord("❌ Otkazan termin", r['ime'], r['usluge'], r['kontakt'],
                                    f"{r['datum']} u {r['vrijeme']}", boja=15158332)
                    st.rerun()
                n_dat = st.date_input("Novi datum", min_value=date.today(), key=f"nd{r['id']}")
                if n_dat.weekday() in NERADNI_DANI:
                    st.error("Nedjelja — odaberi drugi dan.")
                else:
                    slot = slobodni_slotovi(n_dat, r['trajanje'] or 30)
                    if slot:
                        n_vr = st.selectbox("Novo vrijeme", slot, key=f"nv{r['id']}")
                        if st.button("💾 Spremi izmjene", key=f"sv{r['id']}"):
                            with get_conn() as c:
                                c.execute("UPDATE termini SET datum=?, vrijeme=? WHERE id=?",
                                          (n_dat.isoformat(), n_vr, r['id']))
                            posalji_discord("✏️ Izmjena termina", r['ime'], r['usluge'], r['kontakt'],
                                            f"Novi: {n_dat.isoformat()} u {n_vr}", boja=3447003)
                            st.rerun()
            if r['status'] == 'done':
                with get_conn() as c:
                    ima = c.execute("SELECT 1 FROM ocjene WHERE termin_id=?", (r['id'],)).fetchone()
                if ima:
                    st.info("Već ste ocijenili ovaj termin.")
                else:
                    oc = st.slider("Ocjena", 1, 5, 5, key=f"oc{r['id']}")
                    km = st.text_input("Komentar", key=f"km{r['id']}")
                    if st.button("Pošalji ocjenu", key=f"so{r['id']}"):
                        with get_conn() as c:
                            c.execute("""INSERT INTO ocjene(termin_id,ime,usluga,ocjena,komentar,created_at)
                                VALUES(?,?,?,?,?,?)""",
                                (r['id'], r['ime'], r['usluge'], oc, km, datetime.now().isoformat()))
                        st.success("Hvala! Ocjena čeka odobrenje.")
            elif budući:
                st.caption("Ocjenjivanje moguće nakon što admin označi termin kao obavljen.")

# --- RECENZIJE ---
st.markdown("---")
st.subheader("🌟 Recenzije klijenata")
with get_conn() as c:
    oc = pd.read_sql("SELECT * FROM ocjene WHERE odobreno=1 ORDER BY created_at DESC LIMIT 20", c)
if oc.empty: st.info("Još nema recenzija.")
else:
    for _, r in oc.iterrows():
        st.markdown(f"""<div class='review-box'><strong>{r['ime']}</strong> — ⭐ {r['ocjena']}/5<br>
        <em>{r['usluga']}</em><br>{r['komentar'] or ''}</div>""", unsafe_allow_html=True)
