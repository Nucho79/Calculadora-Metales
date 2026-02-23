import streamlit as st
import requests
from bs4 import BeautifulSoup

# Configuración de página
st.set_page_config(page_title="Calculadora Oro y Plata", page_icon="💰")

# --- ESTILO CSS PARA MÁXIMA VISIBILIDAD ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp { background-color: #f8f9fa; }
    
    /* Tarjetas de precios (Metrics) con alto contraste */
    [data-testid="stMetricValue"] {
        color: #1a1a1a !important;
        font-size: 28px !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricLabel"] {
        color: #444444 !important;
        font-size: 16px !important;
    }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 2px solid #f1c40f;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=600)
def obtener_precios_reales():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        url = "https://www.inversoro.es/precio-del-oro/precio-del-oro-hoy/"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        precios = soup.find_all("span", class_="price-value")
        
        # Extracción de valores
        oro = float(precios[0].text.replace('.', '').replace(',', '.').replace('€', '').strip())
        plata = float(precios[1].text.replace('.', '').replace(',', '.').replace('€', '').strip())
        return oro, plata, True
    except:
        return 2415.50, 29.10, False

oro_hoy, plata_hoy, es_real = obtener_precios_reales()

# --- INTERFAZ ---
st.title("💰 Calculadora de Metales")

if not es_real:
    st.warning("⚠️ Usando precios de referencia (Mercado cerrado o error de conexión).")
else:
    st.caption("✅ Cotización en tiempo real desde Inversoro.es")

# Mostrar precios con el nuevo estilo visual
col_a, col_b = st.columns(2)
col_a.metric("🥇 ORO (€/oz)", f"{oro_hoy:,.2f} €")
col_b.metric("🥈 PLATA (€/oz)", f"{plata_hoy:,.2f} €")

st.divider()

# Sección de Entradas
st.subheader("Simulador de Valor")
c1, c2 = st.columns([2,1])

with c1:
    metal = st.radio("Selecciona Metal", ["Oro", "Plata"], horizontal=True)
    peso = st.number_input("Cantidad a calcular", min_value=0.0, step=0.1, format="%.2f")

with c2:
    unidad = st.selectbox("Unidad", ["Gramos (g)", "Onzas (oz)", "Kilos (kg)"])
    pureza_def = 750 if metal == "Oro" else 999
    pureza = st.number_input("Milésimas", value=pureza_def, min_value=1, max_value=999)

# Lógica de cálculo
factor = {"Gramos (g)": 0.03215, "Onzas (oz)": 1.0, "Kilos (kg)": 32.15}
precio_m = oro_hoy if metal == "Oro" else plata_hoy
total = (peso * factor[unidad]) * (pureza / 1000) * precio_m

# RESULTADO FINAL (Caja Dorada Legible)
st.markdown(f"""
    <div style="background: #f1c40f; padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #b8860b;">
        <h3 style="color: #000; margin:0; font-size: 16px;">VALOR ESTIMADO TOTAL</h3>
        <h1 style="color: #000; font-size: 40px; margin:5px 0;">{total:,.2f} €</h1>
        <p style="color: #000; font-weight: bold; margin:0;">({peso} {unidad} de {metal} - {pureza}/1000)</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
if st.button("🔄 Actualizar Precios"):
    st.cache_data.clear()
    st.rerun()
