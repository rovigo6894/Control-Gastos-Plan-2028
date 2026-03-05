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
    
    .metric-card.exceeded {
        border: 2px solid #ef4444;
        position: relative;
    }
    
    .metric-card.exceeded::after {
        content: "⚠️ EXCEDIDO";
        position: absolute;
        top: -10px;
        right: 10px;
        background: #ef4444;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    .metric-card.warning {
        border: 2px solid #f59e0b;
        position: relative;
    }
    
    .metric-card.warning::after {
        content: "⚠️ ALERTA";
        position: absolute;
        top: -10px;
        right: 10px;
        background: #f59e0b;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.7rem;
        font-weight: 600;
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
    
    .progress-fill.exceeded {
        background: linear-gradient(90deg, #ef4444, #f87171);
    }
    
    .progress-fill.warning {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
    }
    
    /* ALERTAS CORREGIDAS */
    .alert-container {
        background: white;
        border-radius: 1rem;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
    }
    
    .alert-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .alert-danger {
        border-left: 4px solid #ef4444;
    }
    
    .alert-warning {
        border-left: 4px solid #f59e0b;
    }
    
    .alert-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem;
        margin: 0.3rem 0;
        background: #f8f9fa;
        border-radius: 0.5rem;
    }
    
    .alert-item.exceeded {
        background: #fee2e2;
    }
    
    .alert-item.warning {
        background: #fef3c7;
    }
    
    .alert-name {
        font-weight: 500;
    }
    
    .alert-amount {
        font-weight: 600;
    }
    
    .alert-amount.exceeded {
        color: #dc2626;
    }
    
    .alert-amount.warning {
        color: #d97706;
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
    
    .subcategoria-info {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.2rem;
        font-style: italic;
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
    }
    
    .stNumberInput > div > div {
        border-radius: 0.5rem !important;
    }
    
    .warning-text {
        color: #ef4444;
        font-size: 0.8rem;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATOS
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
# FUNCIÓN DE ALERTAS
# ============================================
def obtener_alertas():
    excedidos = []
    cerca_limite = []
    
    if not st.session_state.gastos:
        return excedidos, cerca_limite
    
    df = pd.DataFrame(st.session_state.gastos)
    
    for cat, datos in PRESUPUESTOS.items():
        # Por categoría
        gastos_cat = df[df['categoria'] == cat]['monto'].sum() if not df.empty else 0
        if gastos_cat > datos['total']:
            excedidos.append({
                'nombre': cat,
                'tipo': 'categoría',
                'gastado': gastos_cat,
                'limite': datos['total'],
                'exceso': gastos_cat - datos['total']
            })
        elif gastos_cat > datos['total'] * 0.8:
            cerca_limite.append({
                'nombre': cat,
                'tipo': 'categoría',
                'gastado': gastos_cat,
                'limite': datos['total'],
                'restante': datos['total'] - gastos_cat
            })
        
        # Por subcategoría
        for sub, sub_data in datos['subcategorias'].items():
            gastos_sub = df[(df['categoria'] == cat) & (df['subcategoria'] == sub)]['monto'].sum() if not df.empty else 0
            if gastos_sub > sub_data['monto']:
                excedidos.append({
                    'nombre': f"{cat} - {sub}",
                    'tipo': 'subcategoría',
                    'gastado': gastos_sub,
                    'limite': sub_data['monto'],
                    'exceso': gastos_sub - sub_data['monto']
                })
            elif gastos_sub > sub_data['monto'] * 0.8:
                cerca_limite.append({
                    'nombre': f"{cat} - {sub}",
                    'tipo': 'subcategoría',
                    'gastado': gastos_sub,
                    'limite': sub_data['monto'],
                    'restante': sub_data['monto'] - gastos_sub
                })
    
    return excedidos, cerca_limite

# ============================================
# TÍTULO
# ============================================
st.markdown('<div class="main-title">💰 CONTROL DE GASTOS PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Ing. Roberto Villarreal · Plan Maestro 2026</div>', unsafe_allow_html=True)

# ============================================
# MOSTRAR ALERTAS (CORREGIDO)
# ============================================
excedidos, cerca_limite = obtener_alertas()

if excedidos:
    st.markdown('<div class="alert-container alert-danger">', unsafe_allow_html=True)
    st.markdown('<div class="alert-title">⚠️ PRESUPUESTOS EXCEDIDOS</div>', unsafe_allow_html=True)
    
    for item in excedidos:
        st.markdown(f"""
        <div class="alert-item exceeded">
            <span class="alert-name">{item['nombre']}</span>
            <span class="alert-amount exceeded">+${item['exceso']:,.0f} (${item['gastado']:,.0f}/${item['limite']:,.0f})</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if cerca_limite:
    st.markdown('<div class="alert-container alert-warning">', unsafe_allow_html=True)
    st.markdown('<div class="alert-title">⚠️ CERCA DEL LÍMITE (80%)</div>', unsafe_allow_html=True)
    
    for item in cerca_limite:
        st.markdown(f"""
        <div class="alert-item warning">
            <span class="alert-name">{item['nombre']}</span>
            <span class="alert-amount warning">Te quedan ${item['restante']:,.0f} (${item['gastado']:,.0f}/{item['limite']:,.0f})</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MÉTRICAS
# ============================================
gastos_mes = [g for g in st.session_state.gastos]
total_gastado = sum(g['monto'] for g in gastos_mes) if gastos_mes else 0
restante = PRESUPUESTO_TOTAL - total_gastado
porcentaje = (total_gastado / PRESUPUESTO_TOTAL) * 100

col1, col2, col3 = st.columns(3)

# Clase para tarjeta de gastado
clase_gastado = ""
if total_gastado > PRESUPUESTO_TOTAL:
    clase_gastado = "exceeded"
elif total_gastado > PRESUPUESTO_TOTAL * 0.8:
    clase_gastado = "warning"

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
    <div class="metric-card {clase_gastado}">
        <div class="metric-label">💸 GASTADO</div>
        <div class="metric-value">${total_gastado:,.0f}</div>
        <div class="metric-delta {'negative' if porcentaje > 100 else ''}">{porcentaje:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">⚖️ RESTANTE</div>
        <div class="metric-value">${restante:,.0f}</div>
        <div class="metric-delta {'negative' if restante < 0 else ''}">Disponible</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# BARRA DE PROGRESO
# ============================================
clase_progress = ""
if porcentaje > 100:
    clase_progress = "exceeded"
elif porcentaje > 80:
    clase_progress = "warning"

st.markdown(f"""
<div class="progress-container">
    <div class="progress-label">
        <span>Progreso mensual</span>
        <span>{porcentaje:.1f}%</span>
    </div>
    <div class="progress-bar">
        <div class="progress-fill {clase_progress}" style="width: {min(porcentaje, 100)}%;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# FORMULARIO
# ============================================
st.markdown('<div class="form-container">', unsafe_allow_html=True)
st.markdown('<div class="form-title">➕ AGREGAR / CORREGIR GASTO</div>', unsafe_allow_html=True)

with st.form("nuevo_gasto"):
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("📅 Fecha", datetime.now())
        categoria = st.selectbox("📁 Categoría", list(PRESUPUESTOS.keys()))
        subcategorias = list(PRESUPUESTOS[categoria]['subcategorias'].keys())
        subcategoria = st.selectbox("📂 Subcategoría", subcategorias)
    
    with col2:
        monto = st.number_input("💰 Monto $ (negativo para corregir)", value=100, step=10)
        descripcion = st.text_input("📝 Descripción")
        if monto < 0:
            st.markdown('<div class="warning-text">⚠️ Corrección (restando)</div>', unsafe_allow_html=True)
    
    if st.form_submit_button("💾 GUARDAR", use_container_width=True):
        if fecha and categoria and subcategoria and monto != 0:
            st.session_state.gastos.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'categoria': categoria,
                'subcategoria': subcategoria,
                'descripcion': descripcion,
                'monto': monto
            })
            guardar_gastos(st.session_state.gastos)
            st.success("✅ Gasto guardado")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# RESUMEN
# ============================================
if st.session_state.gastos:
    df = pd.DataFrame(st.session_state.gastos)
    
    st.markdown('<div class="expenses-table">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">📊 RESUMEN</div>', unsafe_allow_html=True)
    
    for cat, datos in PRESUPUESTOS.items():
        gastos_cat = df[df['categoria'] == cat]['monto'].sum() if not df.empty else 0
        porcentaje_cat = (gastos_cat / datos['total']) * 100
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{cat}**")
            for sub in datos['subcategorias'].keys():
                gastos_sub = df[(df['categoria'] == cat) & (df['subcategoria'] == sub)]['monto'].sum() if not df.empty else 0
                if gastos_sub != 0:
                    limite_sub = datos['subcategorias'][sub]['monto']
                    emoji = "🔴" if gastos_sub > limite_sub else "🟡" if gastos_sub > limite_sub * 0.8 else "🟢"
                    st.markdown(f"&nbsp;&nbsp;{emoji} {sub}: ${gastos_sub:,.0f}/${limite_sub:,.0f}")
        
        with col2:
            st.markdown(f"**${gastos_cat:,.0f}**")
            st.markdown(f"*{porcentaje_cat:.1f}%*")
        
        st.divider()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    <p>📧 contacto@optipension73.com · 📱 871 579 1810</p>
    <p>⚡ Versión PRO · Alertas automáticas</p>
    <p>© 2026 · OptiPensión 73</p>
</div>
""", unsafe_allow_html=True)
