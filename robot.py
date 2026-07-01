import streamlit as st
import requests
from google import genai
import datetime

# 1. Nastavení vzhledu stránky
st.set_page_config(page_title="Monitorovací systém ADAPTO.space", page_icon="💼", layout="wide")

st.title("💼 Monitorovací systém zakázek pro ADAPTO.space")
st.caption("Automatizovaná aplikace pro screening firemních příležitostí. Integrace AI do vnitřních procesů.")

# --- DATABÁZE VŠECH 41 DODANÝCH PORTÁLŮ PODLE KATEGORIÍ ---
PORTALY = {
    "🍃 Životní prostředí, Lesy a Národní parky": {
        "AOPK ČR (NEN)": "https://nen.nipez.cz/profily-zadavatelu-platne/p:pzp:query=agentura/detail-profilu/AOPK/zahajene-zakazky",
        "Národní park Šumava (NEN)": "https://nen.nipez.cz/profily-zadavatelu-platne/detail-profilu/NPSUMAVA/zahajene-zakazky",
        "KRNAP (NEN)": "https://nen.nipez.cz/profily-zadavatelu-platne/detail-profilu/krnap/zahajene-zakazky",
        "KRNAP (Gemin)": "https://www.gemin.cz/profil/sprava-krkonosskeho-narodniho-parku-vrchlabi",
        "Národní park Podyjí (Web)": "https://www.nppodyji.cz/verejne-zakazky",
        "Národní park Podyjí (NEN)": "https://nen.nipez.cz/profily-zadavatelu-platne/detail-profilu/SpravaNPPodyji/zahajene-zakazky",
        "NP České Švýcarsko (NEN)": "https://nen.nipez.cz/profily-zadavatelu-platne/p:pzp:query=%C4%8Desk%C3%A9%20%C5%A1v%C3%BDcarsko/detail-profilu/ceskesvycarsko/zahajene-zakazky",
        "Lesy ČR (Eveza)": "https://eveza.cz/profil-zadavatele/lesy-ceske-republiky-sp/17",
        "eAgri - Ministerstvo zemědělství (E-ZAK)": "https://zakazky.eagri.cz/contract_index.html",
        "Ministerstvo životního prostředí (NEN)": "https://nen.nipez.cz/profily-zadavatelu-platne/detail-profilu/MZP/zahajene-zakazky"
    },
    "🏛️ Kraje a regionální nákupy": {
        "Středočeský kraj (NEN)": "https://nen.nipez.cz/profily-zadavatelu-platne/detail-profilu/stredoceskykraj/zahajene-zakazky",
        "Středočeský kraj (E-ZAK)": "https://zakazky.kr-stredocesky.cz/profile_display_2.html",
        "Centrální nákup Plzeňského kraje (E-ZAK)": "https://ezak.cnpk.cz/profile_display_140.html",
        "Pardubický kraj (E-ZAK)": "https://zakazky.pardubickykraj.cz/profile_display_2.html",
        "Kraj Vysočina (E-ZAK)": "https://ezak.kr-vysocina.cz/profile_display_111.html",
        "Kraj Vysočina (NEN)": "https://nen.nipez.cz/profily-zadavatelu-platne/detail-profilu/krajvysocina/zahajene-zakazky",
        "Kraj bez korupce (E-ZAK)": "https://zakazky.krajbezkorupce.cz/profile_display_2.html"
    },
    "🏙️ Města a obce": {
        "Statutární město Brno (E-ZAK)": "https://ezak.brno.cz/",
        "Město Jihlava (E-ZAK)": "https://zakazky.jihlava.cz/profile_display_2.html",
        "Město Havlíčkův Brod (E-ZAK)": "https://zakazky.muhb.cz/profile_display_2.html",
        "Město Klatovy (NEN)": "https://nen.nipez.cz/profily-zadavatelu-platne/detail-profilu/mestoKlatovy/zahajene-zakazky",
        "Město Kolín (E-ZAK)": "https://zakazky.mukolin.cz/",
        "Město Mladá Boleslav (Vhodné uveřejnění)": "https://www.vhodne-uverejneni.cz/profil/statutarni-mesto-mlada-boleslav",
        "Městský úřad Příbram (NEN)": "https://nen.nipez.cz/profily-zadavatelu-platne/detail-profilu/MeUPB/zahajene-zakazky",
        "Město Třebíč (E-ZAK)": "https://zakazky.trebic.cz/profile_display_2.html",
        "Město Třeboň (E-ZAK)": "https://zakazky.mesto-trebon.cz/profile_display_2.html",
        "Město Telč (NEN)": "https://nen.nipez.cz/profily-zadavatelu-platne/detail-profilu/mestotelc/zahajene-zakazky",
        "Město Žďár nad Sázavou (E-ZAK)": "https://zakazky.zdarns.cz/profile_display_2.html",
        "DSO Stražiště (E-ZAK)": "https://ezak.straziste.cz/profile_display_2.html"
    },
    "🎯 Specifické profily zadavatelů (Tenderarena a další)": {
        "Tenderarena - Profil Z0001501": "https://tenderarena.cz/dodavatel/seznam-profilu-zadavatelu/detail/Z0001501",
        "Tenderarena - Profil Z0001977": "https://tenderarena.cz/dodavatel/seznam-profilu-zadavatelu/detail/Z0001977",
        "Tenderarena - Profil Z0002739": "https://tenderarena.cz/dodavatel/seznam-profilu-zadavatelu/detail/Z0002739",
        "Tenderarena - Profil Z0001380": "https://tenderarena.cz/dodavatel/seznam-profilu-zadavatelu/detail/Z0001380",
        "Tenderarena - Profil Z0001901": "https://tenderarena.cz/dodavatel/seznam-profilu-zadavatelu/detail/Z0001901",
        "Tenderarena - Profil Z0002380": "https://tenderarena.cz/dodavatel/seznam-profilu-zadavatelu/detail/Z0002380",
        "NEN - Ministerstvo obrany VIII": "https://nen.nipez.cz/profily-zadavatelu-platne/detail-profilu/MOVIII/zahajene-zakazky",
        "NEN - Profil 00246875": "https://nen.nipez.cz/profily-zadavatelu-platne/detail-profilu/00246875/zahajene-zakazky",
        "Vhodné uveřejnění - Profil 00267759": "https://www.vhodne-uverejneni.cz/profil/00267759",
        "E-zakázky - Profil 73671d4c": "https://www.e-zakazky.cz/Profil-Zadavatele/73671d4c-f892-430d-8118-f1964c96a819",
        "E-zakázky - Služby 980f29ec": "https://sluzby.e-zakazky.cz/profil-zadavatele/980f29ec-5398-44b7-bbb5-f2d6a600699c",
        "Proebiz - Profil 00293881": "https://profily.proebiz.com/profile/00293881"
    }
}

st.markdown("##") 

# 2. Ovládací panel parametrů
with st.container(border=True):
    st.subheader("🎛️ Parametry vyhledávání")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Vaše expertní ekologická klíčová slova natvrdo nastavená
        vychozi_slova = (
            "tůň, tůně, mokřad, mokřady, rybník, obnova rybníka, odbahnění rybníka, "
            "vodní tok, koryto, revitalizace toku, nádrž, retenční nádrž, VN, MVN, poldr, "
            "projektová dokumentace, studie proveditelnosti, návrh, realizace, revitalizace, "
            "obnova, protipovodňová opatření, zadržení vody, protierozní opatření, krajinné úpravy, "
            "meliorace, úprava meliorací, sucho, adaptace na sucho, eroze, protierozní, "
            "retenční, retenční nádrž, tok, ř. km"
        )
        
        klicova_slova = st.text_input(
            "Sledovaná klíčová slova (oddělujte čárkou):", 
            value=vychozi_slova
        )
        
    with col2:
        dny_zprah = st.number_input(
            "Stáří zakázek (maximálně dní):", 
            min_value=1, max_value=60, value=7
        )

# 3. Výběr portálů ke screeningu
st.subheader("🌐 Výběr cílových portálů ke kontrole")
st.caption("Rozbalte kategorii a vyberte buď celou skupinu, nebo jednotlivé weby.")

vybrane_portaly = {}

# Generování rozbalovacích skupin pro elegantní design
for kategorie, weby in PORTALY.items():
    with st.expander(kategorie, expanded=(kategorie.startswith("🍃"))):
        # Hromadný přepínač pro celou skupinu
        vybrat_vse = st.checkbox(f"Vybrat celou skupinu: {kategorie}", value=False, key=f"all_{kategorie}")
        
        # Rozdělení webů do dvou sloupců uvnitř expanderu, ať to vypadá moderně
        sub_col1, sub_col2 = st.columns(2)
        items = list(weby.items())
        half = (len(items) + 1) // 2
        
        with sub_col1:
            for jmeno, url in items[:half]:
                if st.checkbox(jmeno, value=vybrat_vse, key=url):
                    vybrane_portaly[jmeno] = url
        with sub_col2:
            for jmeno, url in items[half:]:
                if st.checkbox(jmeno, value=vybrat_vse, key=url):
                    vybrane_portaly[jmeno] = url

# Načtení skrytého klíče
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.warning("🔑 V nastavení Streamlit Cloud (Secrets) chybí GEMINI_API_KEY.")
    api_key = None

st.markdown("##")

# Informace o počtu vybraných webů a doporučení
pocet_vybranych = len(vybrane_portaly)
if pocet_vybranych > 0:
    st.info(f"🔢 Celkem vybráno k analýze: **{pocet_vybranych} webů**.")
    if pocet_vybranych > 15:
        st.warning("⚠️ Vybrali jste více než 15 webů naráz. Kvůli rychlostním limitům bezplatné verze Gemini doporučujeme weby kontrolovat raději po menších skupinách (např. do 12 webů na jedno kliknutí), aby nedošlo k odmítnutí ze strany serverů Google.")

# 4. Spuštění analýzy
if st.button("🚀 SPUSTIT KOMPLETNÍ SCREENING", type="primary", disabled=(pocet_vybranych == 0)):
    if not api_key:
        st.error("❌ Nelze spustit vyhledávání bez API klíče v Secrets.")
    else:
        st.markdown("---")
        st.subheader("📊 Výsledky monitoringu")
        
        # Vytvoření dynamických záložek podle toho, které weby uživatel reálně zaškrtnul
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
                    
                    # Hlavička, aby nás servery hned neodmítly jako roboty
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
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
                    4. **Klíčový přínos pro ADAPTO.space**: (stručné, odborné zdůvodnění, proč zakázka odpovídá našemu zaměření).
                    
                    Pokud nic neodpovídá nebo kód neobsahuje aktuální zakázky, napiš přesně text: 
                    "Nebyly nalezeny žádné nové zakázky odpovídající vašim kritériím."
                    
                    Zde jsou surová data z portálu:
                    {html_kod[:60000]}  # Ochrana před příliš obřími stránkami, které by přetížily paměť
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
                    st.error(f"❌ Tento portál se nepodařilo automaticky načíst (může vyžadovat přihlášení nebo pokročilé ověření): {e}")
