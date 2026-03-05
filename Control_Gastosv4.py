import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os

# ============================================
# CONFIGURACIÓN
# ============================================
st.set_page_config(page_title="💰 Control de Gastos PRO", page_icon="💰", layout="centered")

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
# CSS ELEGANTE
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
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
    
    .progress-container {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 2rem 0;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
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
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
    }
    
    .chart-container {
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
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATOS DE PRESUPUESTOS (CORREGIDOS)
# ============================================
PRESUPUESTOS = {
    'Alimentación': {
        'total': 7900,
        'subcategorias': {
            'Desayuno': {'monto': 75, 'descripcion': 'Huevos con manteca, queso, aguacate'},
            'Comida': {'monto': 148.33, 'descripcion': 'Comida fuerte. Rib Eye'},
            'Cena': {'monto': 40, 'descripcion': 'Ligero: aceitunas, frutos secos'}
        }
    },
    'Servicios': {
        'total': 1550,
        'subcategorias': {
            'Internet': {'monto': 600, 'descripcion': 'Plan mensual'},
            'Luz': {'monto': 450, 'descripcion': 'CFE'},
            'Agua': {'monto': 200, 'descripcion': 'IPAM aplicado'}
        }
    },
    'Vivienda': {
        'total': 2150,
        'subcategorias': {
            'Mantenimiento': {'monto': 1400, 'descripcion': 'Casa al cien'},
            'Transporte': {'monto': 750, 'descripcion': 'Gasolina, Uber'}
        }
    }
}

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
total_gastado = sum(g['monto'] for g in st.session_state.gastos) if st.session_state.gastos else 0
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
        <div class="metric-delta">{porcentaje:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">⚖️ RESTANTE</div>
        <div class="metric-value">${restante:,.0f}</div>
        <div class="metric-delta">{'🔴 Negativo' if restante < 0 else '✅ Disponible'}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# BARRA DE PROGRESO
# ============================================
st.markdown(f"""
<div class="progress-container">
    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span>📊 Progreso mensual</span>
        <span>{porcentaje:.1f}%</span>
    </div>
    <div style="height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden;">
        <div style="height: 100%; width: {min(porcentaje, 100)}%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 10px;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# FORMULARIO CORREGIDO
# ============================================
st.markdown('<div class="form-container">', unsafe_allow_html=True)
st.markdown('<div class="form-title">➕ AGREGAR / CORREGIR GASTO</div>', unsafe_allow_html=True)

with st.form("form_gastos"):
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("📅 Fecha", datetime.now())
        categoria = st.selectbox("📁 Categoría", list(PRESUPUESTOS.keys()))
    
    with col2:
        monto = st.number_input("💰 Monto $", value=100, step=10)
        descripcion = st.text_input("📝 Descripción")
    
    # SUBCATEGORÍA - AHORA SÍ depende de la categoría seleccionada
    subcategorias = list(PRESUPUESTOS[categoria]['subcategorias'].keys())
    subcategoria = st.selectbox("📂 Subcategoría", subcategorias)
    
    # Mostrar información de la subcategoría
    info_sub = PRESUPUESTOS[categoria]['subcategorias'][subcategoria]
    st.info(f"ℹ️ {info_sub['descripcion']} - Límite: ${info_sub['monto']:,.2f}")
    
    if st.form_submit_button("💾 GUARDAR GASTO", use_container_width=True):
        if fecha and categoria and subcategoria and monto != 0:
            st.session_state.gastos.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'categoria': categoria,
                'subcategoria': subcategoria,
                'descripcion': descripcion,
                'monto': monto
            })
            guardar_gastos(st.session_state.gastos)
            st.success("✅ Gasto guardado correctamente")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# GRÁFICAS
# ============================================
if st.session_state.gastos:
    df = pd.DataFrame(st.session_state.gastos)
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">📊 DISTRIBUCIÓN DE GASTOS</div>', unsafe_allow_html=True)
    
    cat_sum = df.groupby('categoria')['monto'].sum().reset_index()
    fig = px.pie(cat_sum, values='monto', names='categoria')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# LISTA DE GASTOS
# ============================================
if st.session_state.gastos:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">📋 ÚLTIMOS GASTOS</div>', unsafe_allow_html=True)
    
    df_show = pd.DataFrame(st.session_state.gastos[-10:][::-1])
    st.dataframe(df_show, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# BOTÓN REINICIAR
# ============================================
col1, col2, col3 = st.columns(3)
with col2:
    if st.button("🗑️ REINICIAR DATOS", use_container_width=True):
        st.session_state.gastos = []
        guardar_gastos([])
        st.rerun()

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    <p>📧 contacto@optipension73.com · 📱 871 579 1810</p>
    <p>⚡ Versión PRO · Subcategorías dinámicas</p>
    <p>© 2026 · OptiPensión 73</p>
</div>
""", unsafe_allow_html=True)
