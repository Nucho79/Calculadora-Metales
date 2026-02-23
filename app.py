import streamlit as st
import requests

# Configuración profesional de la página
st.set_page_config(page_title="Cotizador Pro - Metales", page_icon="⚖️", layout="wide")

# --- ESTILO VISUAL PERSONALIZADO ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    div.stButton > button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        font-weight: bold; 
        border: 1px solid #d1d5db;
    }
    /* Botones de Plata: Color plateado/gris */
    .stButton > button:focus { background-color: #d1d5db !important; }
    
    /* Tarjetas de precios superiores */
    .price-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 5px solid #d4af37;
    }
    </style>
    """, unsafe_allow_html=True)

# --- OBTENCIÓN DE PRECIOS (Nueva Fuente: API Global) ---
@st.cache_data(ttl=60)
def obtener_cotizacion_real():
    try:
        # Usamos una pasarela que conecta con mercados en tiempo real
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        data = requests.get(url).json()
        eur_usd = data['rates']['EUR']
        
        # Cotizaciones base del mercado internacional (Spot)
        # Estas APIs responden 24/7 con el último precio de mercado
        gold_usd = requests.get("https://api.gold-api.com/price/XAU").json()['price']
        silver_usd = requests.get("https://api.gold-api.com/price/XAG").json()['price']
        
        return gold_usd * eur_usd, silver_usd * eur_usd, "✅ MERCADO EN VIVO"
    except:
        # Precios de seguridad si falla la conexión
        return 2432.10, 29.55, "⚠️ PRECIO DE CIERRE"

oro_eur, plata_eur, estado = obtener_cotizacion_real()

# --- ENCABEZADO ---
st.title("⚖️ Calculadora Técnica de Metales")
st.write(f"Sincronización: **{estado}**")

col_oro, col_plata = st.columns(2)
with col_oro:
    st.markdown(f"<div class='price-card'><h3>ORO (oz)</h3><h1 style='color:#b8860b;'>{oro_eur:,.2f} €</h1></div>", unsafe_allow_html=True)
with col_plata:
    st.markdown(f"<div class='price-card' style='border-top-color:#9ca3af;'><h3>PLATA (oz)</h3><h1 style='color:#4b5563;'>{plata_eur:,.2f} €</h1></div>", unsafe_allow_html=True)

st.divider()

# --- SELECCIÓN DE METAL ---
metal = st.radio("Seleccione metal para calcular:", ["Oro", "Plata"], horizontal=True)

# Lógica de estados para botones
if 'pureza' not in st.session_state:
    st.session_state.pureza = 0.750

# --- BOTONES DE PUREZA ---
if metal == "Plata":
    st.subheader("Grados de Plata (Ley)")
    leyes = [0.100, 0.200, 0.300, 0.400, 0.500, 0.600, 0.640, 0.700, 0.720, 0.800, 0.900, 0.925, 0.999]
    cols = st.columns(7)
    cols2 = st.columns(6)
    for i, ley in enumerate(leyes):
        t = cols[i] if i < 7 else cols2[i-7]
        if t.button(f"{ley:.3f}"):
            st.session_state.pureza = ley

else: # ORO
    st.subheader("Grados de Oro (Kilates)")
    kts = {"8K": 0.333, "10K": 0.417, "12K": 0.500, "14K": 0.585, "18K": 0.750, "21.6K": 0.900, "22K": 0.916, "24K": 0.999}
    cols = st.columns(len(kts))
    for i, (k, v) in enumerate(kts.items()):
        if cols
