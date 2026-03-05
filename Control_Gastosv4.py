import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================
st.set_page_config(
    page_title="💰 Control de Gastos · OptiPensión 73",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Ocultar menús de Streamlit
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ============================================
# DATOS DE PRESUPUESTOS (PRIMERO, ANTES DE USARLOS)
# ============================================
PRESUPUESTOS = {
    'Alimentación': {
        'total': 7900,
        'diario': 263.33,
        'subcategorias': {
            'Desayuno': {'monto': 75, 'descripcion': 'Huevos con manteca, queso, aguacate o jamón serrano'},
            'Comida': {'monto': 148.33, 'descripcion': 'Comida fuerte. Rib Eye, carnita asada'},
            'Cena': {'monto': 40, 'descripcion': 'Ligero: aceitunas, plátano, frutos secos, quesadillas'}
        }
    },
    'Servicios': {
        'total': 1550,
        'subcategorias': {
            'Internet': {'monto': 600, 'descripcion': ''},
            'Luz': {'monto': 450, 'descripcion': ''},
            'Agua': {'monto': 200, 'descripcion': 'Beneficio IPAM aplicado'},
            'Celular': {'monto': 200, 'descripcion': ''},
            'Gas': {'monto': 100, 'descripcion': ''}
        }
    },
    'Vivienda': {
        'total': 2150,
        'subcategorias': {
            'Mantenimiento': {'monto': 1400, 'descripcion': 'Para que la casa siempre esté al cien'},
            'Transporte': {'monto': 750, 'descripcion': ''}
        }
    }
}

PRESUPUESTO_TOTAL = 13100
ARCHIVO_DATOS = "gastos.json"

# ============================================
# FUNCIONES DE PERSISTENCIA
# ============================================
def cargar_gastos():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for gasto in data:
                    gasto['fecha'] = datetime.fromisoformat(gasto['fecha'])
                return data
        except:
            return []
    return []

def guardar_gastos(gastos):
    data = []
    for gasto in gastos:
        g = gasto.copy()
        g['fecha'] = g['fecha'].isoformat()
        data.append(g)
    
    with open(ARCHIVO_DATOS, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ============================================
# INICIALIZAR SESSION STATE
# ============================================
if 'gastos' not in st.session_state:
    st.session_state.gastos = cargar_gastos()
    
if 'current_month' not in st.session_state:
    st.session_state.current_month = datetime(2026, 3, 1)

# ============================================
# FUNCIONES DE AYUDA
# ============================================
def format_money(num):
    return f"${num:,.2f}"

def get_month_name(date):
    meses = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 
             'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
    return meses[date.month - 1]

def gastos_del_mes():
    return [g for g in st.session_state.gastos 
            if g['fecha'].year == st.session_state.current_month.year 
            and g['fecha'].month == st.session_state.current_month.month]

def calcular_totales():
    gastos = gastos_del_mes()
    total = sum(g['monto'] for g in gastos)
    restante = PRESUPUESTO_TOTAL - total
    porcentaje = (total / PRESUPUESTO_TOTAL) * 100 if PRESUPUESTO_TOTAL > 0 else 0
    return total, restante, porcentaje

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1rem;
    }
    
    .header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .logo {
        background: #0f3b4f;
        color: white;
        width: 60px;
        height: 60px;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: 0 10px 18px -8px #0b2a3a;
    }
    
    .title h1 {
        color: #103c51;
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
    }
    
    .title p {
        color: #3c647a;
        font-size: 0.9rem;
        margin: 0;
    }
    
    .month-selector {
        background: white;
        border-radius: 3rem;
        padding: 0.8rem 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px -6px #94a3b8;
    }
    
    .month-selector span {
        font-weight: 600;
        color: #1e293b;
        font-size: 1.3rem;
    }
    
    .resumen-fila {
        background: white;
        border-radius: 1.5rem;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 16px -10px #94a3b8;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #f1f5f9;
    }
    
    .resumen-label {
        color: #475569;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .resumen-number {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
    }
    
    .resumen-number.warning {
        color: #dc2626;
    }
    
    .progress-container {
        background: white;
        border-radius: 1.5rem;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 16px -10px #94a3b8;
        border: 1px solid #f1f5f9;
    }
    
    .progress-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        color: #475569;
        font-weight: 500;
    }
    
    .progress-bar {
        background: #e2e8f0;
        height: 12px;
        border-radius: 20px;
        width: 100%;
    }
    
    .progress-fill {
        height: 12px;
        background: #2563eb;
        border-radius: 20px;
        width: 0%;
        transition: width 0.3s;
    }
    
    .progress-fill.warning { background: #f59e0b; }
    .progress-fill.danger { background: #dc2626; }
    
    .categoria {
        background: white;
        border-radius: 1.5rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 16px -10px #94a3b8;
        border: 1px solid #f1f5f9;
    }
    
    .categoria-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .categoria-nombre {
        font-size: 1.2rem;
        font-weight: 600;
        color: #0f172a;
    }
    
    .categoria-total {
        font-weight: 600;
        color: #2563eb;
    }
    
    .subcategoria {
        padding: 1rem 0;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .subcategoria:last-child {
        border-bottom: none;
    }
    
    .subcategoria-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .subcategoria-nombre {
        font-weight: 600;
        color: #1e293b;
    }
    
    .subcategoria-detalle {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 0.5rem;
        font-style: italic;
    }
    
    .subcategoria-montos {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem 0;
    }
    
    .subcategoria-gastado {
        font-size: 1.3rem;
        font-weight: 700;
        color: #0f172a;
    }
    
    .subcategoria-presupuesto {
        color: #64748b;
        font-size: 0.95rem;
    }
    
    .mini-progress {
        height: 8px;
        background: #e2e8f0;
        border-radius: 10px;
        width: 100%;
        margin: 0.5rem 0;
    }
    
    .mini-fill {
        height: 8px;
        border-radius: 10px;
        width: 0%;
        transition: width 0.3s;
    }
    
    .fill-green { background: #10b981; }
    .fill-yellow { background: #f59e0b; }
    .fill-red { background: #ef4444; }
    
    .status-badge {
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-good { background: #d1fae5; color: #047857; }
    .status-warning { background: #fed7aa; color: #b45309; }
    .status-danger { background: #fee2e2; color: #b91c1c; }
    
    .form-card {
        background: white;
        border-radius: 1.5rem;
        padding: 1.5rem;
        margin: 2rem 0;
        box-shadow: 0 8px 16px -10px #94a3b8;
        border: 1px solid #f1f5f9;
    }
    
    .form-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        color: #0f172a;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e2e8f0;
    }
    
    .stButton > button {
        background: #2563eb !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 12px -6px #1e40af !important;
    }
    
    .stButton > button:hover {
        background: #1d4ed8 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px -6px #1e3a8a !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: #ef4444 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #dc2626 !important;
    }
    
    .stSelectbox > div > div {
        border-radius: 1rem !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .stDateInput > div > div {
        border-radius: 1rem !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .stNumberInput > div > div {
        border-radius: 1rem !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .stTextInput > div > div {
        border-radius: 1rem !important;
        border: 1px solid #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# INTERFAZ PRINCIPAL
# ============================================

# Header
st.markdown("""
<div class="header">
    <div class="logo">💰</div>
    <div class="title">
        <h1>Control de Gastos</h1>
        <p>Ing. Roberto Villarreal · Plan Maestro 2026</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Selector de mes
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if st.button("←", key="prev_month"):
        if st.session_state.current_month.month == 1:
            st.session_state.current_month = st.session_state.current_month.replace(
                month=12, year=st.session_state.current_month.year - 1
            )
        else:
            st.session_state.current_month = st.session_state.current_month.replace(
                month=st.session_state.current_month.month - 1
            )
        st.rerun()
        
with col2:
    st.markdown(f"""
    <div class="month-selector">
        <span>{get_month_name(st.session_state.current_month)} {st.session_state.current_month.year}</span>
    </div>
    """, unsafe_allow_html=True)
    
with col3:
    if st.button("→", key="next_month"):
        if st.session_state.current_month.month == 12:
            st.session_state.current_month = st.session_state.current_month.replace(
                month=1, year=st.session_state.current_month.year + 1
            )
        else:
            st.session_state.current_month = st.session_state.current_month.replace(
                month=st.session_state.current_month.month + 1
            )
        st.rerun()

# Calcular totales
total_gastado, restante, porcentaje = calcular_totales()

# Filas de resumen
st.markdown(f"""
<div class="resumen-fila">
    <span class="resumen-label">PRESUPUESTO</span>
    <span class="resumen-number">{format_money(PRESUPUESTO_TOTAL)}</span>
</div>
<div class="resumen-fila">
    <span class="resumen-label">GASTADO</span>
    <span class="resumen-number">{format_money(total_gastado)}</span>
</div>
<div class="resumen-fila">
    <span class="resumen-label">RESTANTE</span>
    <span class="resumen-number {'warning' if restante < 0 else ''}">{format_money(restante)}</span>
</div>
""", unsafe_allow_html=True)

# Barra de progreso
fill_class = ''
if porcentaje > 100:
    fill_class = 'danger'
elif porcentaje > 80:
    fill_class = 'warning'

st.markdown(f"""
<div class="progress-container">
    <div class="progress-header">
        <span>{porcentaje:.1f}% del presupuesto</span>
        <span>${PRESUPUESTOS['Alimentación']['diario']:.2f}/día</span>
    </div>
    <div class="progress-bar">
        <div class="progress-fill {fill_class}" style="width:{min(porcentaje, 100)}%"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# CATEGORÍAS (VERSIÓN SIMPLE QUE SÍ FUNCIONA)
# ============================================
for categoria, datos in PRESUPUESTOS.items():
    with st.expander(f"**{categoria}**", expanded=True):
        for sub, presupuesto in datos['subcategorias'].items():
            gastado = sum(g['monto'] for g in gastos_del_mes() 
                         if g['categoria'] == categoria and g['subcategoria'] == sub)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{sub}**")
                if presupuesto['descripcion']:
                    st.caption(presupuesto['descripcion'])
            with col2:
                st.markdown(f"**${gastado:,.2f}**")
                st.markdown(f"de ${presupuesto['monto']:,.2f}")
            
            # Barra de progreso nativa de Streamlit
            progreso = min(gastado / presupuesto['monto'], 1.0) if presupuesto['monto'] > 0 else 0
            st.progress(progreso)
            st.divider()

# ============================================
# FORMULARIO PARA AGREGAR GASTOS
# ============================================
st.markdown("### ➕ Agregar / Corregir gasto")

col1, col2 = st.columns(2)
with col1:
    fecha = st.date_input("Fecha", datetime.now())
    categoria_sel = st.selectbox("Categoría", list(PRESUPUESTOS.keys()))
    
with col2:
    subcategorias = list(PRESUPUESTOS[categoria_sel]['subcategorias'].keys())
    subcategoria_sel = st.selectbox("Subcategoría", subcategorias)
    monto = st.number_input("Monto $ (positivo o negativo)", value=100, step=1)

descripcion = st.text_input("Descripción")

col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    if st.button("💾 Guardar", use_container_width=True):
        if fecha and categoria_sel and subcategoria_sel and descripcion and monto != 0:
            nuevo_gasto = {
                'fecha': datetime.combine(fecha, datetime.min.time()),
                'categoria': categoria_sel,
                'subcategoria': subcategoria_sel,
                'descripcion': descripcion,
                'monto': monto
            }
            st.session_state.gastos.append(nuevo_gasto)
            guardar_gastos(st.session_state.gastos)
            st.success("✅ Gasto guardado")
            st.rerun()
        else:
            st.error("❌ Completa todos los campos")

with col_b2:
    if st.button("🔄 Reiniciar mes", use_container_width=True, type="secondary"):
        st.session_state.gastos = [g for g in st.session_state.gastos 
                                   if not (g['fecha'].year == st.session_state.current_month.year 
                                          and g['fecha'].month == st.session_state.current_month.month)]
        guardar_gastos(st.session_state.gastos)
        st.success("✅ Mes reiniciado")
        st.rerun()

# ============================================
# ÚLTIMOS GASTOS
# ============================================
gastos_mes = gastos_del_mes()
if gastos_mes:
    st.markdown("### 📋 Últimos gastos")
    df = pd.DataFrame(gastos_mes)
    df = df.sort_values('fecha', ascending=False).head(10)
    for _, row in df.iterrows():
        cols = st.columns([2, 2, 2, 4, 2])
        with cols[0]:
            st.write(row['fecha'].strftime('%d/%m'))
        with cols[1]:
            st.write(row['categoria'])
        with cols[2]:
            st.write(row['subcategoria'])
        with cols[3]:
            st.write(row['descripcion'][:20])
        with cols[4]:
            st.write(f"**${row['monto']:,.2f}**")

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    <p>📧 contacto@optipension73.com · 📱 871 579 1810</p>
    <p>✅ Datos guardados permanentemente · Cada mes independiente</p>
    <p>© 2026 · OptiPensión 73</p>
</div>
""", unsafe_allow_html=True)
