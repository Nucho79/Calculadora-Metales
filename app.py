import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

# Configuración de página con estilo oscuro/oro
st.set_page_config(page_title="Calculadora Oro y Plata", page_icon="💰")

# --- ESTILO CSS PARA QUE NO SEA BÁSICA ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #f1c40f; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=600) # Se actualiza cada 10 minutos
def obtener_precios_reales():
    try:
        # User-Agent más real para evitar bloqueos
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # Usamos una URL directa de lingotes que suele ser más estable
        url = "https://www.inversoro.es/precio-del-oro/precio-del-oro-hoy/"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscamos los precios en las tablas principales
        precios = soup.find_all("span", class_="price-value")
        
        # Extracción agresiva de números
        oro = float(precios[0].text.replace('.', '').replace(',', '.').replace('€', '').strip())
        plata = float(precios[1].text.replace('.', '').replace(',', '.').replace('€', '').strip())
        return oro, plata, True
    except:
        # Si falla Inversoro, intentamos otra fuente o damos aviso claro
        return 2415.50, 29.10, False

oro_hoy, plata_hoy, es_real = obtener_precios_reales()

# --- INTERFAZ ---
st.title("🥇 Monitor de Metales Preciosos")

if not es_real:
    st.error("⚠️ Error de conexión con el mercado. Mostrando último cierre conocido.")
else:
    st.success("✅ Precios del mercado en vivo (EUR)")

# Tarjetas visuales
c1, c2 = st.columns(2)
c1.metric("ORO (oz)", f"{oro_hoy:,.2f} €")
c2.metric("PLATA (oz)", f"{plata_hoy:,.2f} €")

st.divider()

# Calculadora avanzada
with st.container():
    col_izq, col_der = st.columns([2,1])
    
    with col_izq:
        metal = st.selectbox("Metal a valorar", ["Oro", "Plata"])
        peso = st.number_input("Cantidad", min_value=0.0, step=0.1, format="%.2f")
    
    with col_der:
        unidad = st.selectbox("Unidad", ["Gramos (g)", "Onzas (oz)", "Kilos (kg)"])
        # Ajuste de pureza automático
        def_pureza = 750 if metal == "Oro" else 999
        pureza = st.number_input("Milésimas", value=def_pureza, min_value=1, max_value=999)

# Cálculo
factor = {"Gramos (g)": 0.03215, "Onzas (oz)": 1.0, "Kilos (kg)": 32.15}
precio = oro_hoy if metal == "Oro" else plata_hoy
total = (peso * factor[unidad]) * (pureza / 1000) * precio

# DISEÑO DEL RESULTADO (Caja Oro)
st.markdown(f"""
    <div style="background: linear-gradient(45deg, #f1c40f, #d4af37); padding: 30px; border-radius: 15px; text-align: center; border: 2px solid #ffffff;">
        <h3 style="color: #000; margin:0;">VALOR ESTIMADO</h3>
        <h1 style="color: #000; font-size: 50px; margin:0;">{total:,.2f} €</h1>
        <p style="color: #333;">Cotización actual: {precio:,.2f} €/oz</p>
    </div>
    """, unsafe_allow_html=True)

if st.button("🔄 Forzar Actualización de Precios"):
    st.cache_data.clear()
    st.rerun()
