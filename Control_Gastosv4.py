import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================
st.set_page_config(
    page_title="💰 Control de Gastos PRO",
    page_icon="💰",
    layout="centered"
)

# Ocultar menús
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ============================================
# CSS PROFESIONAL
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-title {
        text-align: center;
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .sub-title {
        text-align: center;
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #333;
        margin: 0.5rem 0;
    }
    
    .metric-delta {
        font-size: 0.9rem;
        color: #10b981;
    }
    
    .metric-delta.negative {
        color: #ef4444;
    }
    
    .progress-container {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 2rem 0;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
    }
    
    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        color: #666;
    }
    
    .progress-bar {
        height: 20px;
        background: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
        transition: width 0.3s;
    }
    
    .form-container {
        background: white;
        border-radius: 1rem;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
    }
    
    .form-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        color: #333;
    }
    
    .expenses-table {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 2rem 0;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
    }
    
    .footer {
        text-align: center;
        color: rgba(255,255,255,0.7);
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.2);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: opacity 0.2s !important;
    }
    
    .stButton > button:hover {
        opacity: 0.9;
    }
    
    .stTextInput > div > div {
        border-radius: 0.5rem !important;
    }
    
    .stNumberInput > div > div {
        border-radius: 0.5rem !important;
    }
    
    .stDateInput > div > div {
        border-radius: 0.5rem !important;
    }
    
    .stSelectbox > div > div {
        border-radius: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATOS
# ============================================
PRESUPUESTO_TOTAL = 13100
ARCHIVO_DATOS = "gastos.json"

def cargar_gastos():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, 'r') as f:
            return json.load(f)
    return []

def guardar_gastos(gastos):
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(gastos, f, indent=2)

# ============================================
# INICIALIZAR
# ============================================
if 'gastos' not in st.session_state:
    st.session_state.gastos = cargar_gastos()

# ============================================
# TÍTULO
# ============================================
st.markdown('<div class="main-title">💰 CONTROL DE GASTOS PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Ing. Roberto Villarreal · Plan Maestro 2026</div>', unsafe_allow_html=True)

# ============================================
# MÉTRICAS
# ============================================
gastos_mes = [g for g in st.session_state.gastos]
total_gastado = sum(g['monto'] for g in gastos_mes) if gastos_mes else 0
restante = PRESUPUESTO_TOTAL - total_gastado
porcentaje = (total_gastado / PRESUPUESTO_TOTAL) * 100

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💰 PRESUPUESTO</div>
        <div class="metric-value">${PRESUPUESTO_TOTAL:,.0f}</div>
        <div class="metric-delta">Mensual</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💸 GASTADO</div>
        <div class="metric-value">${total_gastado:,.0f}</div>
        <div class="metric-delta">{porcentaje:.1f}% del total</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    clase_delta = "metric-delta negative" if restante < 0 else "metric-delta"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">⚖️ RESTANTE</div>
        <div class="metric-value">${restante:,.0f}</div>
        <div class="{clase_delta}">Disponible</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# BARRA DE PROGRESO
# ============================================
st.markdown(f"""
<div class="progress-container">
    <div class="progress-label">
        <span>Progreso mensual</span>
        <span>{porcentaje:.1f}%</span>
    </div>
    <div class="progress-bar">
        <div class="progress-fill" style="width: {min(porcentaje, 100)}%;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# FORMULARIO
# ============================================
st.markdown('<div class="form-container">', unsafe_allow_html=True)
st.markdown('<div class="form-title">➕ AGREGAR GASTO</div>', unsafe_allow_html=True)

with st.form("nuevo_gasto"):
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
        categoria = st.selectbox("Categoría", ["Alimentación", "Servicios", "Vivienda", "Transporte", "Entretenimiento", "Salud", "Otros"])
    
    with col2:
        monto = st.number_input("Monto ($)", min_value=1, value=100, step=10)
        descripcion = st.text_input("Descripción", placeholder="Ej: Supermercado, Luz, Renta...")
    
    if st.form_submit_button("💾 GUARDAR GASTO", use_container_width=True):
        st.session_state.gastos.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'categoria': categoria,
            'descripcion': descripcion,
            'monto': monto
        })
        guardar_gastos(st.session_state.gastos)
        st.success("✅ Gasto guardado correctamente")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# GRÁFICA (si hay datos)
# ============================================
if st.session_state.gastos:
    df = pd.DataFrame(st.session_state.gastos)
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Gráfica de categorías
    st.markdown('<div class="expenses-table">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">📊 GASTOS POR CATEGORÍA</div>', unsafe_allow_html=True)
    
    cat_sum = df.groupby('categoria')['monto'].sum().reset_index()
    fig = px.pie(cat_sum, values='monto', names='categoria', 
                 color_discrete_sequence=px.colors.sequential.Blues_r)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Inter",
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabla de últimos gastos
    st.markdown('<div class="expenses-table">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">📋 ÚLTIMOS GASTOS</div>', unsafe_allow_html=True)
    
    df_show = df.sort_values('fecha', ascending=False).head(10)
    df_show['fecha'] = df_show['fecha'].dt.strftime('%d/%m/%Y')
    df_show['monto'] = df_show['monto'].apply(lambda x: f"${x:,.2f}")
    
    st.dataframe(df_show[['fecha', 'categoria', 'descripcion', 'monto']], 
                 use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# BOTONES DE ACCIÓN
# ============================================
col1, col2, col3 = st.columns(3)
with col2:
    if st.button("🗑️ REINICIAR DATOS"):
        st.session_state.gastos = []
        guardar_gastos([])
        st.rerun()

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    <p>📧 contacto@optipension73.com · 📱 871 579 1810</p>
    <p>⚡ Versión PRO · Datos guardados localmente</p>
    <p>© 2026 · OptiPensión 73</p>
</div>
""", unsafe_allow_html=True)
