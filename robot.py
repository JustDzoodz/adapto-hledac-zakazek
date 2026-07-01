import streamlit as st
import requests
from google import genai
import datetime

# 1. Moderní nastavení vzhledu stránky (Bez divokého CSS, které rozbíjí Dark Mode)
st.set_page_config(page_title="Zakázkový Dashboard AI", page_icon="💼", layout="wide")

# Hlavička aplikace
st.title("💼 Inteligentní monitorovací systém zakázek")
st.caption("AI vyhledávač napojený na Gemini • Automatický screening firemních příležitostí")

# --- NASTAVENÍ WEBOVÝCH STRÁNEK ---
WEBOVE_PORTALY = {
    "Ministerstvo pro místní rozvoj (SPÚČR)": "https://zakazky.spucr.cz/contract_index.html",
    "Ukázkový druhý web (Doplníme)": "https://zakazky.spucr.cz/contract_index.html"
}

st.markdown("##") # Drobná mezera

# 2. Ovládací panel zabalený do vestavěné moderní karty s okrajem
with st.container(border=True):
    st.subheader("🎛️ Parametry vyhledávání")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        klicova_slova = st.text_input(
            "Sledovaná klíčová slova (oddělujte čárkou):", 
            value="projektová činnost, inženýrské sítě, realizace staveb, geodetické práce"
        )
        
    with col2:
        dny_zprah = st.number_input(
            "Stáří zakázek (maximálně dní):", 
            min_value=1, max_value=60, value=7
        )

# Automatické načtení skrytého API klíče ze Secrets
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.warning("🔑 Upozornění: V nastavení Streamlit Cloud (Secrets) zatím chybí přesný název GEMINI_API_KEY. Pokud ho tam ještě nemáš vložený, vyhledávání nepojede.")
    api_key = None

st.markdown("##") # Mezera

# 3. Spuštění analýzy
if st.button("🚀 SPUSTIT KOMPLETNÍ SCREENING", type="primary"):
    if not api_key:
        st.error("❌ Nelze spustit vyhledávání. Nejprve prosím ulož svůj Gemini API klíč do nastavení Secrets na Streamlit Cloudu.")
    else:
        st.markdown("---")
        st.subheader("📊 Stav zpracování a výsledky")
        
        # Vytvoříme moderní záložky (Tabs) pro jednotlivé weby
        tabs = st.tabs(list(WEBOVE_PORTALY.keys()))
        
        for i, (nazev_webu, odkaz_webu) in enumerate(WEBOVE_PORTALY.items()):
            with tabs[i]:
                st.markdown(f"### 🌐 Analýza portálu: `{nazev_webu}`")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("⬇️ Stahuji data z webového serveru...")
                    progress_bar.progress(30)
                    
                    response = requests.get(odkaz_webu, timeout=30)
                    response.encoding = 'utf-8'
                    html_kod = response.text
                    
                    progress_bar.progress(60)
                    status_text.text("🧠 Posílám texty k AI analýze do Gemini...")
                    
                    client = genai.Client(api_key=api_key)
                    dnesni_datum = datetime.date.today().strftime("%d.%m.%Y")
                    
                    prompt = f"""
                    Jsi špičkový analytik veřejných zakázek. Tvým úkolem je projít HTML kód portálu: {nazev_webu}
                    Dnešní datum je: {dnesni_datum}.
                    
                    Kritéria vyhledávání:
                    - Hledáme pouze zakázky odpovídající těmto výrazům: {klicova_slova}
                    - Pouze NOVÉ zakázky (Datum zahájení max {dny_zprah} dní zpětně od {dnesni_datum}).
                    
                    Formát výstupu (Použij čistý a přehledný Markdown):
                    Pokud najdeš zakázky, vypiš je jako seznam. U každé uveď:
                    1. **Název zakázky** (Pokud je v HTML relativní odkaz jako 'contract_X.html', udělej z názvu klikatelný odkaz složením s hlavní doménou webu)
                    2. **Datum zahájení**
                    3. **Lhůta pro nabídky**
                    4. **Proč odpovídá**: (stručné zdůvodnění)
                    
                    Pokud nic neodpovídá, napiš přesně: "Nebyly nalezeny žádné nové zakázky odpovídající vašim kritériím."
                    
                    Zde je zdrojový kód:
                    {html_kod}
                    """
                    
                    res = client.models.generate_content(model='gemini-3.5-flash', contents=prompt)
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    
                    if "Nebyly nalezeny žádné" in res.text:
                        st.info(res.text)
                    else:
                        st.success(f"🎉 Na portálu {nazev_webu} nalezeny shody!")
                        st.markdown(res.text)
                        
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ Nepodařilo se zpracovat tento web: {e}")
