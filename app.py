import streamlit as st
import pandas as pd
import yfinance as yf # Asegúrate de que tu requirements.txt tenga yfinance

st.set_page_config(page_title="Calculadora Final", layout="wide")

# Estilos de botones
st.markdown("""<style> div.stButton > button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; } </style>""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def obtener_precios():
    try:
        # Tickers de Yahoo Finance para Oro y Plata en EUR
        oro = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
        plata = yf.Ticker("SI=F").history(period="1d")['Close'].iloc[-1]
        # Conversión simple de USD a EUR aproximada
        return oro * 0.92, plata * 0.92, "✅ Yahoo Finance"
    except:
        return 2440.0, 29.80, "⚠️ Offline"

oro_p, plata_p, fuente = obtener_precios()

st.title("⚖️ Calculadora de Metales")
st.write(f"Fuente: {fuente}")

if st.button("🔄 RECARGAR PÁGINA"):
    st.cache_data.clear()
    st.rerun()

c1, c2 = st.columns(2)
c1.metric("ORO (oz)", f"{oro_p:,.2f} €")
c2.metric("PLATA (oz)", f"{plata_p:,.2f} €")

metal = st.radio("Metal:", ["Oro", "Plata"], horizontal=True)

if 'pureza' not in st.session_state: st.session_state.pureza = 0.750

if metal == "Plata":
    op = [0.100, 0.200, 0.300, 0.400, 0.500, 0.600, 0.640, 0.700, 0.720, 0.800, 0.900, 0.925, 0.999]
    cols = st.columns(len(op))
    for i, v in enumerate(op):
        if cols[i].button(f"{v:.3f}"): st.session_state.pureza = v
else:
    op_o = {"8K": 0.333, "10K": 0.417, "12K": 0.500, "14K": 0.585, "18K": 0.750, "21.6K": 0.900, "22K": 0.916, "24K": 0.999}
    cols = st.columns(len(op_o))
    for i, (k, v) in enumerate(op_o.items()):
        if cols[i].button(k): st.session_state.pureza = v

val = st.number_input("Ajuste manual:", 0.0, 1.0, st.session_state.pureza, format="%.3f")

# Widget informativo que pediste
por = val * 100
if metal == "Oro":
    st.info(f"📍 {val*24:.1f} Kilates | {val:.3f} Graduación | {por:.1f}% Pureza")
else:
    st.info(f"📍 Plata Ley {val:.3f} | {val:.3f} Graduación | {por:.1f}% Pureza")

peso = st.number_input("Peso total:", value=10.0)
uni = st.selectbox("Unidad:", ["Gramos (g)", "Onzas (oz)", "Kilos (kg)"])
conv = {"Gramos (g)": 0.03215, "Onzas (oz)": 1.0, "Kilos (kg)": 32.15}
precio = oro_p if metal == "Oro" else plata_p
total = (peso * conv[uni]) * val * precio

st.success(f"### VALOR TOTAL: {total:,.2f} €")
