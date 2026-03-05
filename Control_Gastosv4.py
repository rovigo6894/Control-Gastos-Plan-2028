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
# DATOS DE PRESUPUESTOS
# ============================================
PRESUPUESTOS = {
    'Alimentación': {
        'total': 7900,
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
# FUNCIÓN PARA EXPORTAR A CSV
# ============================================
def exportar_a_csv():
    if st.session_state.gastos:
        df = pd.DataFrame(st.session_state.gastos)
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%Y-%m-%d')
        df = df.sort_values('fecha', ascending=False)
        return df.to_csv(index=False, encoding='utf-8-sig')
    return None

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
# CSS MEJORADO CON ANIMACIONES Y EFECTOS
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fondo con gradiente mejorado */
    .main {
        background: linear-gradient(145deg, #0b1c26 0%, #1a2f3a 50%, #0f2a35 100%);
        padding: 1rem;
        position: relative;
    }
    
    .main::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 200px;
        background: radial-gradient(circle at 50% 0%, rgba(37,99,235,0.15), transparent 70%);
        pointer-events: none;
    }
    
    /* Animaciones de entrada */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Header */
    .header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .logo {
        background: linear-gradient(135deg, #0f3b4f, #1a5f7a);
        color: white;
        width: 70px;
        height: 70px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.2rem;
        box-shadow: 0 15px 25px -10px #00000060;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(5px);
    }
    
    .title h1 {
        background: linear-gradient(135deg, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .title p {
        color: #94a3b8;
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* Selector de mes */
    .month-selector {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-radius: 3rem;
        padding: 0.8rem 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 10px 25px -10px #000000;
        animation: fadeInUp 0.5s ease-out 0.1s both;
    }
    
    .month-selector span {
        font-weight: 600;
        color: #1a4d6b;
        font-size: 1.3rem;
    }
    
    .month-selector button {
        background: linear-gradient(135deg, #e2e8f0, #cbd5e1);
        border: none;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        font-size: 1.3rem;
        cursor: pointer;
        color: #0f172a;
        font-weight: bold;
        transition: all 0.3s;
        box-shadow: 0 4px 10px -4px #00000040;
    }
    
    .month-selector button:hover {
        transform: scale(1.1);
        box-shadow: 0 8px 15px -6px #000000;
    }
    
    /* Tarjetas de resumen mejoradas */
    .resumen-fila {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-radius: 1.5rem;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1rem;
        box-shadow: 0 15px 30px -12px #000000;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .resumen-fila:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 25px 40px -15px #000000;
        border-color: rgba(37,99,235,0.3);
    }
    
    .resumen-fila::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: translateX(-100%);
        transition: transform 0.6s;
    }
    
    .resumen-fila:hover::after {
        transform: translateX(100%);
    }
    
    .resumen-label {
        color: #475569;
        font-size: 1.1rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .resumen-number {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0f172a, #1e293b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .resumen-number.warning {
        background: linear-gradient(135deg, #dc2626, #ef4444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Barra de progreso animada */
    .progress-container {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-radius: 1.5rem;
        padding: 1.2rem 1.8rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 15px 30px -12px #000000;
        animation: fadeInUp 0.5s ease-out 0.2s both;
    }
    
    .progress-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.8rem;
        color: #94a3b8;
        font-weight: 500;
    }
    
    .progress-bar {
        background: rgba(226,232,240,0.3);
        height: 14px;
        border-radius: 20px;
        width: 100%;
        overflow: hidden;
        position: relative;
    }
    
    .progress-fill {
        height: 14px;
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        border-radius: 20px;
        width: 0%;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .progress-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 2s infinite;
    }
    
    .progress-fill.warning {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
    }
    
    .progress-fill.danger {
        background: linear-gradient(90deg, #dc2626, #ef4444);
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Categorías mejoradas */
    .categoria {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-radius: 2rem;
        padding: 1.8rem;
        margin-bottom: 1.8rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 20px 35px -15px #000000;
        animation: fadeInUp 0.5s ease-out;
        transition: all 0.3s;
    }
    
    .categoria:nth-child(2) { animation-delay: 0.1s; }
    .categoria:nth-child(3) { animation-delay: 0.2s; }
    .categoria:nth-child(4) { animation-delay: 0.3s; }
    
    .categoria:hover {
        transform: translateY(-2px);
        box-shadow: 0 30px 45px -15px #000000;
        border-color: rgba(37,99,235,0.3);
    }
    
    .categoria-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid rgba(37,99,235,0.2);
    }
    
    .categoria-nombre {
        font-size: 1.3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e293b, #0f172a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .categoria-total {
        font-weight: 600;
        color: #2563eb;
        background: rgba(37,99,235,0.1);
        padding: 0.3rem 1rem;
        border-radius: 2rem;
        font-size: 1rem;
    }
    
    /* Subcategorías */
    .subcategoria {
        padding: 1rem 0;
        border-bottom: 1px solid rgba(203,213,225,0.2);
        transition: all 0.3s;
    }
    
    .subcategoria:last-child {
        border-bottom: none;
    }
    
    .subcategoria:hover {
        background: rgba(255,255,255,0.05);
        border-radius: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
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
        font-size: 1rem;
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
    
    /* Mini barras de progreso */
    .mini-progress {
        height: 8px;
        background: rgba(226,232,240,0.2);
        border-radius: 10px;
        width: 100%;
        margin: 0.8rem 0;
        overflow: hidden;
    }
    
    .mini-fill {
        height: 8px;
        border-radius: 10px;
        width: 0%;
        transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .mini-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 2s infinite;
    }
    
    .fill-green { 
        background: linear-gradient(90deg, #10b981, #34d399);
    }
    .fill-yellow { 
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
    }
    .fill-red { 
        background: linear-gradient(90deg, #ef4444, #f87171);
    }
    
    /* Badges de estado */
    .status-badge {
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        transition: all 0.3s;
        box-shadow: 0 2px 8px -4px #000000;
    }
    
    .status-good { 
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        color: #047857;
    }
    .status-warning { 
        background: linear-gradient(135deg, #fed7aa, #fcd34d);
        color: #b45309;
    }
    .status-danger { 
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        color: #b91c1c;
    }
    
    /* Formulario */
    .form-card {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-radius: 2rem;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 25px 40px -15px #000000;
        border: 1px solid rgba(255,255,255,0.1);
        animation: fadeInUp 0.5s ease-out 0.4s both;
    }
    
    .form-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        color: #0f172a;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    /* Botones mejorados */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 3rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.3s !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: 0 10px 20px -8px #1e3a8a !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 20px 30px -10px #1e3a8a !important;
    }
    
    .stButton > button::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::after {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        box-shadow: 0 10px 20px -8px #991b1b !important;
    }
    
    /* Inputs */
    .stSelectbox > div > div,
    .stDateInput > div > div,
    .stNumberInput > div > div,
    .stTextInput > div > div {
        border-radius: 1rem !important;
        border: 1px solid rgba(203,213,225,0.2) !important;
        background: rgba(255,255,255,0.9) !important;
        transition: all 0.3s !important;
    }
    
    .stSelectbox > div > div:hover,
    .stDateInput > div > div:hover,
    .stNumberInput > div > div:hover,
    .stTextInput > div > div:hover {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(148,163,184,0.2);
        animation: fadeInUp 0.5s ease-out 0.5s both;
    }
    
    /* Tooltips */
    [data-tooltip] {
        position: relative;
        cursor: help;
    }
    
    [data-tooltip]:hover::before {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        padding: 0.5rem 1rem;
        background: #1e293b;
        color: white;
        border-radius: 2rem;
        font-size: 0.8rem;
        white-space: nowrap;
        z-index: 1000;
        box-shadow: 0 10px 20px -5px black;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# INTERFAZ PRINCIPAL
# ============================================

# Header con iconos
st.markdown("""
<div class="header">
    <div class="logo">💰</div>
    <div class="title">
        <h1>Control de Gastos</h1>
        <p>Ing. Roberto Villarreal · Plan Maestro 2026</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Botón de exportar
col_exp1, col_exp2, col_exp3 = st.columns([1, 1, 1])
with col_exp2:
    csv_data = exportar_a_csv()
    if csv_data:
        st.download_button(
            label="📥 Exportar a CSV",
            data=csv_data,
            file_name=f"gastos_{datetime.now().strftime('%Y%m')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.button("📥 Exportar a CSV", disabled=True, use_container_width=True)

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

# Filas de resumen con iconos
st.markdown(f"""
<div class="resumen-fila">
    <span class="resumen-label">💰 PRESUPUESTO</span>
    <span class="resumen-number">{format_money(PRESUPUESTO_TOTAL)}</span>
</div>
<div class="resumen-fila">
    <span class="resumen-label">💸 GASTADO</span>
    <span class="resumen-number">{format_money(total_gastado)}</span>
</div>
<div class="resumen-fila">
    <span class="resumen-label">⚖️ RESTANTE</span>
    <span class="resumen-number {'warning' if restante < 0 else ''}">{format_money(restante)}</span>
</div>
""", unsafe_allow_html=True)

# Barra de progreso mejorada
fill_class = ''
if porcentaje > 100:
    fill_class = 'danger'
elif porcentaje > 80:
    fill_class = 'warning'

st.markdown(f"""
<div class="progress-container">
    <div class="progress-header">
        <span data-tooltip="Porcentaje del presupuesto mensual">{porcentaje:.1f}% del presupuesto</span>
        <span data-tooltip="Presupuesto total del mes">💰 {format_money(PRESUPUESTO_TOTAL)}</span>
    </div>
    <div class="progress-bar">
        <div class="progress-fill {fill_class}" style="width:{min(porcentaje, 100)}%"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# CATEGORÍAS
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
                st.markdown(f"**{format_money(gastado)}**")
                st.markdown(f"de {format_money(presupuesto['monto'])}")
            
            # Barra de progreso individual mejorada
            progreso = min(gastado / presupuesto['monto'], 1.0) if presupuesto['monto'] > 0 else 0
            fill_class = 'fill-red' if (gastado / presupuesto['monto']) > 1.0 else 'fill-yellow' if (gastado / presupuesto['monto']) > 0.8 else 'fill-green'
            st.markdown(f"""
            <div class="mini-progress">
                <div class="mini-fill {fill_class}" style="width:{progreso*100}%"></div>
            </div>
            """, unsafe_allow_html=True)
            st.divider()

# ============================================
# FORMULARIO PARA AGREGAR GASTOS
# ============================================
st.markdown("""
<div class="form-card">
    <div class="form-title">
        <span>➕ Agregar / Corregir gasto</span>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    fecha = st.date_input("📅 Fecha", datetime.now())
    categoria_sel = st.selectbox("📁 Categoría", list(PRESUPUESTOS.keys()), key="cat_select")
    
with col2:
    subcategorias = list(PRESUPUESTOS[categoria_sel]['subcategorias'].keys())
    subcategoria_sel = st.selectbox("📂 Subcategoría", subcategorias, key="sub_select")
    monto = st.number_input("💰 Monto $", value=100, step=1, key="monto_input", 
                           help="Usa números negativos para corregir errores")

descripcion = st.text_input("📝 Descripción", key="desc_input", 
                           placeholder="Ej: Supermercado, Uber, Luz...")

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
            st.success("✅ Gasto guardado correctamente")
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
            st.write(f"**{row['fecha'].strftime('%d/%m')}**")
        with cols[1]:
            st.write(row['categoria'])
        with cols[2]:
            st.write(row['subcategoria'])
        with cols[3]:
            st.write(row['descripcion'][:20] + ('...' if len(row['descripcion']) > 20 else ''))
        with cols[4]:
            st.write(f"**{format_money(row['monto'])}**")

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    <p>📧 contacto@optipension73.com · 📱 871 579 1810</p>
    <p>⚡ Datos guardados permanentemente · Cada mes independiente</p>
    <p>© 2026 · OptiPensión 73</p>
</div>
""", unsafe_allow_html=True)
