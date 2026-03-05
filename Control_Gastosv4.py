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
# CSS ELEGANTE
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
        color: #ef4444;
    }
    
    .alert-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem;
        margin: 0.3rem 0;
        background: #f8f9fa;
        border-radius: 0.5rem;
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
</style>
""", unsafe_allow_html=True)

# ============================================
# DATOS DE PRESUPUESTOS
# ============================================
PRESUPUESTOS = {
    'Alimentación': {
        'total': 7900,
        'subcategorias': {
            'Desayuno': 75,
            'Comida': 148.33,
            'Cena': 40
        }
    },
    'Servicios': {
        'total': 1550,
        'subcategorias': {
            'Internet': 600,
            'Luz': 450,
            'Agua': 200
        }
    },
    'Vivienda': {
        'total': 2150,
        'subcategorias': {
            'Mantenimiento': 1400,
            'Transporte': 750
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
    
if 'categoria_actual' not in st.session_state:
    st.session_state.categoria_actual = list(PRESUPUESTOS.keys())[0]

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
    delta_class = "metric-delta negative" if porcentaje > 100 else "metric-delta"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💸 GASTADO</div>
        <div class="metric-value">${total_gastado:,.0f}</div>
        <div class="{delta_class}">{porcentaje:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    delta_class = "metric-delta negative" if restante < 0 else "metric-delta"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">⚖️ RESTANTE</div>
        <div class="metric-value">${restante:,.0f}</div>
        <div class="{delta_class}">Disponible</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# BARRA DE PROGRESO
# ============================================
st.markdown(f"""
<div class="progress-container">
    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span>Progreso mensual</span>
        <span>{porcentaje:.1f}%</span>
    </div>
    <div class="progress-bar">
        <div class="progress-fill" style="width: {min(porcentaje, 100)}%;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# FORMULARIO CON SUBCATEGORÍAS CORREGIDO
# ============================================
st.markdown('<div class="form-container">', unsafe_allow_html=True)
st.markdown('<div class="form-title">➕ AGREGAR / CORREGIR GASTO</div>', unsafe_allow_html=True)

with st.form("nuevo_gasto"):
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("📅 Fecha", datetime.now())
        # Categoría - al cambiar, se actualiza la sesión
        categoria = st.selectbox(
            "📁 Categoría",
            list(PRESUPUESTOS.keys())
        )
    
    with col2:
        monto = st.number_input("💰 Monto $", value=100, step=10)
        descripcion = st.text_input("📝 Descripción")
    
    # SUBCATEGORÍAS - Se actualizan BASADO EN LA CATEGORÍA SELECCIONADA
    subcategorias = list(PRESUPUESTOS[categoria]['subcategorias'].keys())
    subcategoria = st.selectbox("📂 Subcategoría", subcategorias)
    
    # Mostrar límite de la subcategoría
    limite_sub = PRESUPUESTOS[categoria]['subcategorias'][subcategoria]
    st.caption(f"Límite: ${limite_sub:,.2f}")
    
    if monto < 0:
        st.warning("⚠️ Número negativo - Esto RESTARÁ del presupuesto")
    
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
# ALERTAS
# ============================================
if st.session_state.gastos:
    df = pd.DataFrame(st.session_state.gastos)
    excedidos = []
    
    for cat, datos in PRESUPUESTOS.items():
        gastos_cat = df[df['categoria'] == cat]['monto'].sum() if not df.empty else 0
        if gastos_cat > datos['total']:
            excedidos.append(f"🔴 {cat}: +${gastos_cat - datos['total']:,.0f} (${gastos_cat:,.0f}/${datos['total']:,.0f})")
    
    if excedidos:
        st.markdown('<div class="alert-container">', unsafe_allow_html=True)
        st.markdown('<div class="alert-title">⚠️ ALERTAS</div>', unsafe_allow_html=True)
        for item in excedidos:
            st.markdown(f'<div class="alert-item">{item}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# GRÁFICAS
# ============================================
if st.session_state.gastos:
    df = pd.DataFrame(st.session_state.gastos)
    
    st.markdown('<div class="expenses-table">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">📊 DISTRIBUCIÓN</div>', unsafe_allow_html=True)
    
    cat_sum = df.groupby('categoria')['monto'].sum().reset_index()
    fig = px.pie(cat_sum, values='monto', names='categoria')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# DETALLE POR CATEGORÍA
# ============================================
if st.session_state.gastos:
    st.markdown('<div class="expenses-table">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">📋 DETALLE</div>', unsafe_allow_html=True)
    
    for cat, datos in PRESUPUESTOS.items():
        gastos_cat = df[df['categoria'] == cat]['monto'].sum() if not df.empty else 0
        
        with st.expander(f"{cat} - ${gastos_cat:,.0f} / ${datos['total']:,.0f}"):
            for sub, limite in datos['subcategorias'].items():
                gastos_sub = df[(df['categoria'] == cat) & (df['subcategoria'] == sub)]['monto'].sum() if not df.empty else 0
                progreso = min(gastos_sub / limite, 1.0)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{sub}**")
                with col2:
                    st.write(f"${gastos_sub:,.0f} / ${limite:,.0f}")
                
                # Barra de progreso
                st.progress(progreso)
                st.divider()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# ÚLTIMOS GASTOS
# ============================================
if st.session_state.gastos:
    st.markdown('<div class="expenses-table">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">📋 ÚLTIMOS</div>', unsafe_allow_html=True)
    
    df_show = pd.DataFrame(st.session_state.gastos[-10:][::-1])
    st.dataframe(df_show, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# BOTÓN REINICIAR
# ============================================
col1, col2, col3 = st.columns(3)
with col2:
    if st.button("🗑️ REINICIAR", use_container_width=True):
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
