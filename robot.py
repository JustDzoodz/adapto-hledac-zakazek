import streamlit as st
import requests
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
        with st.spinner("Robot právě bleskově stahuje aktuální seznam zakázek ze serveru SPÚČR..."):
            try:
                st.text("🔗 Připojuji se na zakazky.spucr.cz...")
                
                # Stáhneme celou stránku jako text (mnohem rychlejší a stabilnější než prohlížeč)
                response = requests.get("https://zakazky.spucr.cz/contract_index.html", timeout=30)
                response.encoding = 'utf-8' # Ošetření správné české diakritiky
                html_kod = response.text
                
                st.success("✅ Data z webu úspěšně stažena! Nyní posílám data do Gemini k analýze...")
                
                # Inicializace Gemini
                client = genai.Client(api_key=api_key)
                dnesni_datum = datetime.date.today().strftime("%d.%m.%Y")
                
                # Instrukce pro Gemini - chceme navíc i klikatelné odkazy!
                prompt = f"""
                Jsi špičkový analytik veřejných zakázek. Tvým úkolem je projít kód stažený ze zakázkového portálu.
                Dnešní datum je: {dnesni_datum}.
                
                Zadání od uživatele:
                - Hledáme pouze zakázky, které odpovídají (i významově) těmto klíčovým slovům: {klicova_slova}
                - Zajímavé jsou pro nás pouze NOVÉ zakázky, které mají 'Datum zahájení' maximálně {dny_zprah} dní zpětně od dnešního data ({dnesni_datum}).
                
                Formát výstupu:
                Pokud najdeš odpovídající zakázky, vypiš je jako přehledný seznam. U každé uveď:
                1. **Název zakázky** (Vytvoř z názvu zakázky klikatelný odkaz! V HTML kódu vyhledej relativní odkaz k této zakázce, bývá ve tvaru 'contract_X.html'. Spoj ho se základní adresou, aby vznikl funkční odkaz ve tvaru: https://zakazky.spucr.cz/contract_X.html)
                2. **Datum zahájení**
                3. **Lhůta pro nabídky**
                4. **Stručný důvod**, proč zakázka odpovídá klíčovým slovům.
                
                Pokud žádná zakázka neodpovídá klíčovým slovům nebo jsou všechny příliš staré, napiš přesně text:
                "Nebyly nalezeny žádné nové zakázky odpovídající vašim kritériím."
                
                Zde je surový kód z webu:
                {html_kod}
                """
                
                with st.spinner("Gemini nyní čte texty a filtruje výsledky..."):
                    res = client.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=prompt
                    )
                
                st.markdown("## 📋 Výsledky vyhledávání")
                st.markdown(res.text)
                
            except Exception as e:
                st.error(f"Došlo k chybě při běhu robota: {e}")
