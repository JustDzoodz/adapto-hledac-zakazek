import streamlit as st
import requests
from google import genai
import datetime

# 1. Nastavení vzhledu stránky
st.set_page_config(page_title="Monitorovací systém ADAPTO.space", page_icon="💼", layout="wide")

st.title("💼 Monitorovací systém zakázek pro ADAPTO.space")
st.caption("Webová aplikace s integrovaným AI pro screening vybraných portálů a příležitostí.")

# --- DATABÁZE PROVĚŘENÝCH A FUNKČNÍCH PORTÁLŮ NA CLOUDU ---
PORTALY = {
    "🍃 Životní prostředí, Lesy a Vodní hospodářství": {
        "Ministerstvo pro místní rozvoj (SPÚČR)": "https://zakazky.spucr.cz/contract_index.html",
        "KRNAP (Gemin)": "https://www.gemin.cz/profil/sprava-krkonosskeho-narodniho-parku-vrchlabi",
        "Národní park Podyjí (Web)": "https://www.nppodyji.cz/verejne-zakazky",
        "Lesy ČR (Eveza)": "https://eveza.cz/profil-zadavatele/lesy-ceske-republiky-sp/17",
        "eAgri - Ministerstvo zemědělství (E-ZAK)": "https://zakazky.eagri.cz/contract_index.html"
    },
    "🏛️ Kraje a regionální nákupy": {
        "Středočeský kraj (E-ZAK)": "https://zakazky.kr-stredocesky.cz/profile_display_2.html",
        "Centrální nákup Plzeňského kraje (E-ZAK)": "https://ezak.cnpk.cz/profile_display_140.html",
        "Pardubický kraj (E-ZAK)": "https://zakazky.pardubickraj.cz/profile_display_2.html",
        "Kraj Vysočina (E-ZAK)": "https://ezak.kr-vysocina.cz/profile_display_111.html",
        "Kraj bez korupce (E-ZAK)": "https://zakazky.krajbezkorupce.cz/profile_display_2.html"
    },
    "🏙️ Města, obce a regiony": {
        "Statutární město Brno (E-ZAK)": "https://ezak.brno.cz/",
        "Město Jihlava (E-ZAK)": "https://zakazky.jihlava.cz/profile_display_2.html",
        "Město Havlíčkův Brod (E-ZAK)": "https://zakazky.muhb.cz/profile_display_2.html",
        "Město Kolín (E-ZAK)": "https://zakazky.mukolin.cz/",
        "Město Mladá Boleslav (Vhodné uveřejnění)": "https://www.vhodne-uverejneni.cz/profil/statutarni-mesto-mlada-boleslav",
        "Město Třebíč (E-ZAK)": "https://zakazky.trebic.cz/profile_display_2.html",
        "Město Třeboň (E-ZAK)": "https://zakazky.mesto-trebon.cz/profile_display_2.html",
        "Město Žďár nad Sázavou (E-ZAK)": "https://zakazky.zdarns.cz/profile_display_2.html",
        "DSO Stražiště (E-ZAK)": "https://ezak.straziste.cz/profile_display_2.html",
        "Vhodné uveřejnění - Profil 00267759": "https://www.vhodne-uverejneni.cz/profil/00267759",
        "E-zakázky - Profil 73671d4c": "https://www.e-zakazky.cz/Profil-Zadavatele/73671d4c-f892-430d-8118-f1964c96a819",
        "E-zakázky - Služby 980f29ec": "https://sluzby.e-zakazky.cz/profil-zadavatele/980f29ec-5398-44b7-bbb5-f2d6a600699c",
        "Proebiz - Profil 00293881": "https://profily.proebiz.com/profile/00293881"
    }
}

def přepnout_celou_skupinu(kat_name):
    hlavni_stav = st.session_state[f"master_{kat_name}"]
    for jmeno in PORTALY[kat_name].keys():
        st.session_state[f"cb_{kat_name}_{jmeno}"] = hlavni_stav

st.markdown("##") 

# 2. Ovládací panel parametrů
with st.container(border=True):
    st.subheader("🎛️ Parametry vyhledávání")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        vychozi_slova = (
            "tůň, tůně, mokřad, mokřady, rybník, obnova rybníka, odbahnění rybníka, "
            "vodní tok, koryto, revitalizace toku, nádrž, retenční nádrž, VN, MVN, poldr, "
            "projektová dokumentace, studie proveditelnosti, návrh, realizace, revitalizace, "
            "obnova, protipovodňová opatření, zadržení vody, protierozní opatření, krajinné úpravy, "
            "meliorace, úprava meliorací, sucho, adaptace na sucho, eroze, protierozní, "
            "retenční, retenční nádrž, tok, ř. km"
        )
        klicova_slova = st.text_input("Sledovaná klíčová slova (oddělujte čárkou):", value=vychozi_slova)
        
    with col2:
        dny_zprah = st.number_input("Stáří zakázek (maximálně dní):", min_value=1, max_value=60, value=7)

# 3. Výběr portálů ke screeningu
st.subheader("🌐 Výběr cílových portálů ke kontrole")
st.caption("Rozbalte kategorii a vyberte buď celou skupinu, nebo jednotlivé weby.")

vybrane_portaly = {}

for kategorie, weby in PORTALY.items():
    with st.expander(kategorie, expanded=(kategorie.startswith("🍃"))):
        
        st.checkbox(
            f"Vybrat celou skupinu: {kategorie}", 
            value=False, 
            key=f"master_{kategorie}", 
            on_change=přepnout_celou_skupinu, 
            args=(kategorie,)
        )
        
        sub_col1, sub_col2 = st.columns(2)
        items = list(weby.items())
        half = (len(items) + 1) // 2
        
        with sub_col1:
            for jmeno, url in items[:half]:
                if st.checkbox(jmeno, key=f"cb_{kategorie}_{jmeno}"):
                    vybrane_portaly[jmeno] = url
        with sub_col2:
            for jmeno, url in items[half:]:
                if st.checkbox(jmeno, key=f"cb_{kategorie}_{jmeno}"):
                    vybrane_portaly[jmeno] = url

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.warning("🔑 V nastavení Streamlit Cloud (Secrets) chybí GEMINI_API_KEY.")
    api_key = None

st.markdown("##")

pocet_vybranych = len(vybrane_portaly)
if pocet_vybranych > 0:
    st.info(f"🔢 Celkem vybráno k analýze: **{pocet_vybranych} webů**.")

# 4. Spuštění analýzy
button_disabled = (pocet_vybranych == 0)
if st.button("🚀 SPUSTIT KOMPLETNÍ SCREENING", type="primary", disabled=button_disabled):
    if not api_key:
        st.error("❌ Nelze spustit vyhledávání bez API klíče v Secrets.")
    else:
        st.markdown("---")
        st.subheader("📊 Výsledky monitoringu")
        
        tabs = st.tabs(list(vybrane_portaly.keys()))
        
        for i, (nazev_webu, odkaz_webu) in enumerate(vybrane_portaly.items()):
            with tabs[i]:
                st.markdown(f"### 🌐 Průzkum: `{nazev_webu}`")
                st.caption(f"Cílová adresa: {odkaz_webu}")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("⬇️ Navazuji spojení a stahuji data ze serveru...")
                    progress_bar.progress(30)
                    
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "cs,cs-CZ;q=0.9,en;q=0.8",
                        "Connection": "keep-alive"
                    }
                    
                    response = requests.get(odkaz_webu, headers=headers, timeout=25)
                    response.encoding = 'utf-8'
                    html_kod = response.text
                    
                    progress_bar.progress(60)
                    status_text.text("🧠 Analytik Gemini prochází strukturu a vyhledává shody...")
                    
                    client = genai.Client(api_key=api_key)
                    dnesni_datum = datetime.date.today().strftime("%d.%m.%Y")
                    
                    prompt = f"""
                    Jsi špičkový analytik veřejných zakázek specializovaný na stavby v krajině, vodní hospodářství a ekologická opatření.
                    Tvým úkolem je projít zdrojový text/kód portálu zakázek: {nazev_webu}.
                    Odkaz na tento portál je: {odkaz_webu}
                    Dnešní datum je: {dnesni_datum}.
                    
                    Kritéria vyhledávání:
                    - Hledáme zakázky věnující se tématům: {klicova_slova} (hledej i významové shody související s hydrologií, revitalizací, protipovodňovou ochranou a krajinným inženýrstvím).
                    - Pouze nové zakázky (Zahájení max {dny_zprah} dní zpětně od dnešního data {dnesni_datum}).
                    
                    Formát výstupu (Čistý a přehledný Markdown):
                    Pokud najdeš odpovídající zakázky, vypiš je jako přehledný seznam. U každé uveď:
                    1. **Název zakázky** (Pokud je v kódu dohledatelný odkaz k zakázce, vytvoř z názvu klikatelný odkaz. Pokud ne, uveď název jako čistý text)
                    2. **Datum zahájení**
                    3. **Lhůta pro nabídky**
                    4. **Klíčový přínos pre ADAPTO.space**: (stručné, odborné zdůvodnění, proč zakázka odpovídá našemu zaměření).
                    
                    Pokud nic neodpovídá nebo kód neobsahuje aktuální zakázky, napiš přesně text: 
                    "Nebyly nalezeny žádné nové zakázky odpovídající vašim kritériím."
                    
                    Zde jsou surová data z portálu:
                    {html_kod[:60000]}
                    """
                    
                    res = client.models.generate_content(model='gemini-3.5-flash', contents=prompt)
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    
                    if "Nebyly nalezeny žádné" in res.text:
                        st.info(res.text)
                    else:
                        st.success(f"🎉 Na portálu {nazev_webu} byly identifikovány příležitosti!")
                        st.markdown(res.text)
                        
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ Tento portál se nepodařilo automaticky načíst: {e}")
