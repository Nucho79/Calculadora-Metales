import streamlit as st
import requests
from bs4 import BeautifulSoup

# Configuración de la página
st.set_page_config(page_title="Calculadora Metales Preciosos", page_icon="💰", layout="centered")

# --- FUNCIÓN DE SCRAPING ---
@st.cache_data(ttl=3600)
def obtener_precios():
    """
    Intenta obtener precios en vivo desde Inversoro.es.
    Devuelve (oro, plata, es_real)
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        url = "https://www.inversoro.es/"
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        oro_tag = soup.find("span", id="hp-gold-price")
        plata_tag = soup.find("span", id="hp-silver-price")

        if not oro_tag or not plata_tag:
            raise ValueError("No se encontraron los elementos de precio.")

        oro_text = oro_tag.text.strip()
        plata_text = plata_tag.text.strip()

        # Convertimos formato europeo (2.150,50 €) a float (2150.50)
        oro = float(oro_text.replace('.', '').replace(',', '.').replace('€', '').strip())
        plata = float(plata_text.replace('.', '').replace(',', '.').replace('€', '').strip())
        
        return oro, plata, True 
    except Exception:
        return 2350.00, 28.50, False

oro_hoy, plata_hoy, precios_reales = obtener_precios()

# --- INTERFAZ ---
st.title("💰 Calculadora de Metales Preciosos")

if precios_reales:
    st.caption("✅ Precios actualizados en tiempo real desde Inversoro.es")
else:
    st.warning("⚠️ Usando precios de referencia. Pulsa 'Actualizar' para reintentar.")

# Mostrar precios actuales
col_a, col_b = st.columns(2)
col_a.metric("🥇 Oro (€/oz)", f"{oro_hoy:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
col_b.metric("🥈 Plata (€/oz)", f"{plata_hoy:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

st.divider()

st.subheader("Simulador de Valor")
col1, col2 = st.columns([2, 1])

with col1:
    peso = st.number_input("Peso del metal", min_value=0.0, value=0.0, step=0.1, format="%.3f")
    metal = st.radio("Selecciona Metal", ["Oro", "Plata"], horizontal=True, key="metal_selector")

with col2:
    unidad = st.selectbox("Unidad", ["g", "oz", "kg"])
    # Reset de pureza basado en el metal
    pureza_defecto = 750 if st.session_state.metal_selector == "Oro" else 999
    pureza = st.number_input(
        "Pureza (milésimas)", 
        value=pureza_defecto, 
        step=1, 
        min_value=1, 
        max_value=999, 
        key=f"pureza_{st.session_state.metal_selector}"
    )

# --- LÓGICA DE CÁLCULO ---
def calcular_total(p, u, m, pur):
    conv = {"oz": 1.0, "g": 0.0321507, "kg": 32.1507}
    precio_actual = oro_hoy if m == "Oro" else plata_hoy
    onzas_reales = (p * conv[u]) * (pur / 1000)
    return onzas_reales * precio_actual

total = calcular_total(peso, unidad, metal, pureza)

def formato_europeo(valor: float) -> str:
    entero, decimal = f"{valor:.2f}".split('.')
    entero_formateado = f"{int(entero):,}".replace(',', '.')
    return f"{entero_formateado},{decimal}"

# --- RESULTADO FINAL ---
if peso <= 0:
    st.info("ℹ️ Introduce un peso para calcular el valor estimado.")
else:
    st.markdown(f"""
    <div style="background-color:#2ecc71; padding:20px; border-radius:15px; text-align:center; margin-top:20px;">
        <h2 style="color:white; margin:0; font-family:sans-serif; font-size:18px;">VALOR TOTAL ESTIMADO</h2>
        <h1 style="color:white; margin:0; font-family:sans-serif; font-size:42px;">{formato_europeo(total)} €</h1>
        <p style="color:rgba(255,255,255,0.85); margin:8px 0 0 0; font-size:13px;">
            {peso} {unidad} de {metal} · Pureza {pureza}/1000
        </p>
    </div>
    """, unsafe_allow_html=True)

st.write("") 
if st.button("🔄 Actualizar precios ahora"):
    st.cache_data.clear()
    st.rerun()