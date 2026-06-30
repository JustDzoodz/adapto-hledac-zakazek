import streamlit as st
from playwright.sync_api import sync_playwright
from google import genai
import datetime

# 1. Nastavení vzhledu stránky
st.set_page_config(page_title="Hledač zakázek SPÚČR", page_icon="🔎", layout="wide")

st.title("🔎 Vyhledávač nových zakázek na SPÚČR")
st.write("Tento nástroj projde web zakazky.spucr.cz a pomocí AI vyfiltruje nejnovější výzvy podle vašich klíčových slov.")

# 2. Formulář pro uživatele (Kolegu)
col1, col2 = st.columns(2)

with col1:
    klicova_slova = st.text_input(
        "Zadejte klíčová slova (oddělená čárkou):", 
        value="pozemky, stavba, IT, monitoring, projektová činnost"
    )

with col2:
    dny_zprah = st.number_input("Kontrolovat zakázky maximálně kolik dní staré?", min_value=1, max_value=30, value=3)

api_key = st.text_input("Vložte váš Gemini API klíč:", type="password", value="")

# 3. Spuštění bota po kliknutí na tlačítko
if st.button("🚀 SPUSTIT KONTROLU WEBU", type="primary"):
    if not api_key:
        st.error("❌ Prosím, vložte váš Gemini API klíč, který jste si zkopíroval.")
    else:
        with st.spinner("Robot právě otevírá prohlížeč a stahuje aktuální seznam zakázek..."):
            try:
                text_z_webu = ""
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    
                    st.text("🔗 Připojuji se na zakazky.spucr.cz...")
                    page.goto("https://zakazky.spucr.cz/contract_index.html", timeout=60000)
                    page.wait_for_timeout(2000)
                    
                    text_z_webu = page.locator("body").inner_text()
                    browser.close()
                
                st.success("✅ Web úspěšně stažen! Nyní posílám data do Gemini k analýze...")
                
                client = genai.Client(api_key=api_key)
                dnesni_datum = datetime.date.today().strftime("%d.%m.%Y")
                
                prompt = f"""
                Jsi špičkový analytik veřejných zakázek. Tvým úkolem je projít text stažený z dotačního/zakázkového portálu.
                Dnešní datum je: {dnesni_datum}.
                
                Zadání od uživatele:
                - Hledáme pouze zakázky, které odpovídají (i významově) těmto klíčovým slovům: {klicova_slova}
                - Zajímavé jsou pro nás pouze NOVÉ zakázky, které mají 'Datum zahájení' maximálně {dny_zprah} dní zpětně od dnešního data ({dnesni_datum}).
                
                Formát výstupu:
                Pokud najdeš odpovídající zakázky, vypiš je jako přehledný seznam. U každé uveď:
                1. **Název zakázky**
                2. **Datum zahájení**
                3. **Lhůta pro nabídky**
                4. **Stručný důvod**, proč zakázka odpovídá klíčovým slovům.
                
                Pokud žádná zakázka neodpovídá klíčovým slovům nebo jsou všechny příliš staré, napiš přesně text:
                "Nebyly nalezeny žádné nové zakázky odpovídající vašim kritériím."
                
                Zde je surový text z webu:
                {text_z_webu}
                """
                
                with st.spinner("Gemini nyní čte texty a filtruje výsledky..."):
                    response = client.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=prompt
                    )
                
                st.markdown("## 📋 Výsledky vyhledávání")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Došlo k chybě při běhu robota: {e}")