import streamlit as st
import requests
from google import genai
import datetime

# 1. Moderní nastavení vzhledu stránky
st.set_page_config(page_title="Zakázkový Dashboard AI", page_icon="💼", layout="wide")

# Vlastní CSS pro modernější vzezření (stíny, zaoblené rohy, hezčí písmo)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 3em;
    }
    </style>
""", unsafe_allow_html=True)

# Hlavička aplikace
st.title("💼 Inteligentní monitorovací systém zakázek")
st.caption("AI vyhledávač napojený na Gemini 3.5 Flash • Automatický screening firemních příležitostí")

# --- NASTAVENÍ WEBOVÝCH STRÁNEK ---
# Sem budeme přidávat další weby. Formát je: "Název": "Odkaz"
WEBOVE_PORTALY = {
    "Ministerstvo pro místní rozvoj (SPÚČR)": "https://zakazky.spucr.cz/contract_index.html",
    "Ukázkový druhý web (Doplníme)": "https://zakazky.spucr.cz/contract_index.html" # Dočasně stejný pro test
}

# 2. Ovládací panel (Karty s nastavením)
st.subheader("🎛️ Parametry vyhledávání")

col1, col2 = st.columns([2, 1])

with col1:
    # Tady jsou tvá nová výchozí klíčová slova (změň podle potřeby)
    klicova_slova = st.text_input(
        "Sledovaná klíčová slova (oddělujte čárkou):", 
        value="projektová činnost, inženýrské sítě, realizace staveb, geodetické práce"
    )

with col2:
    dny_zprah = st.number_input(
        "Stáří zakázek (maximálně dní):", 
        min_value=1, max_value=60, value=7
    )

# Automatické načtení skrytého API klíče
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("🔑 V nastavení Streamlit Cloud chybí GEMINI_API_KEY!")
    st.stop()

# 3. Spuštění analýzy
if st.button("🚀 SPUSTIT KOMPLETNÍ SCREENING", type="primary"):
    
    st.markdown("---")
    st.subheader("📊 Stav zpracování a výsledky")
    
    # Vytvoříme záložky pro jednotlivé weby pro moderní vzhled
    tabs = st.tabs(list(WEBOVE_PORTALY.keys()))
    
    # Projedeme všechny weby jeden po druhém
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
                
                # Inicializace a dotaz na Gemini
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
                
                # Zobrazení výsledků v moderním boxu
                if "Nebyly nalezeny žádné" in res.text:
                    st.info(res.text)
                else:
                    st.success(f"🎉 Na portálu {nazev_webu} nalezeny shody!")
                    st.markdown(res.text)
                    
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Nepodařilo se zpracovat tento web: {e}")
