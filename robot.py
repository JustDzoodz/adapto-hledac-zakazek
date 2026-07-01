import streamlit as st
import requests
from google import genai
import datetime

# 1. Nastavení vzhledu stránky
st.set_page_config(page_title="Monitorovací systém ADAPTO.space", page_icon="💼", layout="wide")

st.title("💼 Monitorovací systém zakázek pro ADAPTO.space")
st.caption("Webová aplikace s integrovaným AI pro screening vybraných portálů a příležitostí.")

# --- DATABÁZE VŠECH 41 PORTÁLŮ PODLE KATEGORIÍ ---
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
        "Pardubický kraj (E-ZAK)": "https://zakazky.pardubickraj.cz/profile_display_2.html",
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
        "Město Treboň (E-ZAK)": "https://zakazky.mesto-trebon.cz/profile_display_2.html",
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
        "Vhodné uveřejnění - Profil 0
