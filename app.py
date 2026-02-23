
import streamlit as st
import requests
import time

# Configuración de página
st.set_page_config(page_title="Calculadora Metales Pro", page_icon="⚖️", layout="wide")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    div.stButton > button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
    .metric-card { background: white; border: 2px solid #d4af37; padding: 15px; border-radius: 10px; text-align: center; }
    /* Botón de actualización destacado */
    .update-btn button { background-color: #ff4b4b !important; color: white !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE OBTENCIÓN DE PRECIOS (NUEVA FUENTE) ---
def obtener_precios_frescos():
    try:
        # Usamos un parámetro de tiempo para engañar al cache del navegador
        timestamp = int(time.time())
        # Fuente: API de tipos de cambio (incluye XAU y XAG en USD)
        url = f"https://open.er-api.com/v6/latest/USD?t={timestamp}"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data['result'] == 'success':
            eur_usd = data['rates']['EUR']
            # Los precios de metales en esta API vienen como (1 / precio_en_usd)
            # Oro (XAU) y Plata (XAG)
            oro_usd = 1 / data['rates']['XAU']
            plata_usd = 1 / data['rates']['XAG']
            
            return oro_usd * eur_usd, plata_usd * eur_usd, "✅ ACTUALIZADO (API GLOBAL)"
        else:
            return 2438.40, 29.75, "⚠️ MODO REFERENCIA"
    except:
        return 2438.40, 29.75, "⚠️ ERROR DE CONEXIÓN"

# Llamada inicial
oro_spot, plata_spot, estado = obtener_precios_frescos()

# --- INTERFAZ ---
st.title("⚖️ Cotizador Profesional de Metales")
st.write(f"Estado del mercado: **{estado}**")

# BOTÓN DE ACTUALIZACIÓN (Muy visible)
st.markdown('<div class="update-btn">', unsafe_allow_html=True)
if st.button("🔄 ACTUALIZAR PRECIOS EN VIVO"):
    st.cache_data.clear()
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"<div class='metric-card'><h3>ORO (oz)</h3><h1 style='color:#b8860b;'>{oro_spot:,.2f} €</h1></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card' style='border-color: #9ca3af;'><h3>PLATA (oz)</h3><h1 style='color:#4b5563;'>{plata_spot:,.2f} €</h1></div>", unsafe_allow_html=True)

st.divider()

# --- SELECCIÓN DE METAL Y BOTONES ---
metal = st.radio("Seleccione metal:", ["Oro", "Plata"], horizontal=True)

if 'p_val' not in st.session_state:
    st.session_state.p_val = 0.750

if metal == "Plata":
    st.write("### Graduaciones de Plata")
    op_p = [0.100, 0.200, 0.300, 0.400, 0.500, 0.600, 0.640, 0.700, 0.720, 0.800, 0.900, 0.925, 0.999]
    cols = st.columns(len(op_p))
    for i, v in enumerate(op_p):
        if cols[i].button(f"{v:.3f}"):
            st.session_state.p_val = v
else:
    st.write("### Graduaciones de Oro (Kilates)")
    op_o = {"8K": 0.333, "10K": 0.417, "12K": 0.500, "14K": 0.585, "18K": 0.750, "21.6K": 0.900, "22K": 0.916, "24K": 0.999}
    cols = st.columns(len(op_o))
    for i, (k, v) in enumerate(op_o.items()):
        if cols[i].button(k):
            st.session_state.p_val = v

# Widget Manual
pureza = st.number_input("Ajuste manual:", 0.0, 1.0, st.session_state.p_val, format="%.3f", step=0.001)

# INFO WIDGET
porc = pureza * 100
if metal == "Oro":
    kt = pureza * 24
    st.info(f"📍 **INFO:** {kt:.1f} Kilates | **Graduación:** {pureza:.3f} | **Porcentaje:** {porc:.1f}% de pureza")
else:
    st.info(f"📍 **INFO:** Plata Ley {pureza:.3f} | **Graduación:** {pureza:.3f} | **Porcentaje:** {porc:.1f}% de pureza")

# PESO Y CÁLCULO
col_w, col_u = st.columns(2)
with col_w:
    peso = st.number_input("Peso total:", min_value=0.0, value=10.0)
with col_u:
    unidad = st.selectbox("Unidad:", ["Gramos (g)", "Onzas (oz)", "Kilos (kg)"])

conv = {"Gramos (g)": 0.03215, "Onzas (oz)": 1.0, "Kilos (kg)": 32.15}
precio_m = oro_spot if metal == "Oro" else plata_spot
total_f = (peso * conv[unidad]) * pureza * precio_m

# RESULTADO
color_res = "#d4af37" if metal == "Oro" else "#ced4da"
st.markdown(f"""
    <div style="background-color: {color_res}; padding: 30px; border-radius: 15px; text-align: center; border: 2px solid #333;">
        <h2 style="color: black; margin: 0;">VALOR TOTAL ESTIMADO</h2>
        <h1 style="color: black; font-size: 55px; margin: 10px 0;">{total_f:,.2f} €</h1>
    </div>
    """, unsafe_allow_html=True)
