import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
# CSS PERSONALIZADO (LA BELLEZA DEL HTML)
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(145deg, #f0f5fa 0%, #e6ecf2 100%);
        padding: 1rem;
    }
    
    .card {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        border-radius: 2.5rem;
        padding: 2rem;
        box-shadow: 0 25px 45px -15px #1a3b4e;
        margin-bottom: 1.5rem;
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
        border: 1px solid #caddf0;
        box-shadow: 0 4px 12px -6px #809aaf;
    }
    
    .month-selector span {
        font-weight: 600;
        color: #1a4d6b;
        font-size: 1.3rem;
    }
    
    .resumen-fila {
        background: white;
        border-radius: 1.5rem;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 16px -10px #7f9bb3;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .resumen-label {
        color: #3c5a70;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .resumen-number {
        font-size: 2rem;
        font-weight: 700;
        color: #103c51;
    }
    
    .resumen-number.warning {
        color: #d32f2f;
    }
    
    .progress-container {
        background: white;
        border-radius: 1.5rem;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 16px -10px #7f9bb3;
    }
    
    .progress-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        color: #2f5777;
    }
    
    .progress-bar {
        background: #e4ecf3;
        height: 12px;
        border-radius: 20px;
        width: 100%;
    }
    
    .progress-fill {
        height: 12px;
        background: #146b9e;
        border-radius: 20px;
        width: 0%;
        transition: width 0.3s;
    }
    
    .progress-fill.warning { background: #f57c00; }
    .progress-fill.danger { background: #d32f2f; }
    
    .categoria {
        background: white;
        border-radius: 1.5rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 16px -10px #7f9bb3;
    }
    
    .categoria-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e4ecf3;
    }
    
    .categoria-nombre {
        font-size: 1.2rem;
        font-weight: 600;
        color: #103c51;
    }
    
    .categoria-total {
        font-weight: 600;
        color: #146b9e;
    }
    
    .subcategoria {
        padding: 1rem 0;
        border-bottom: 1px solid #e4ecf3;
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
        color: #1a4d6b;
    }
    
    .subcategoria-detalle {
        font-size: 0.8rem;
        color: #578197;
        margin-bottom: 0.5rem;
    }
    
    .subcategoria-montos {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.5rem 0;
    }
    
    .subcategoria-gastado {
        font-size: 1.3rem;
        font-weight: 700;
        color: #103c51;
    }
    
    .subcategoria-presupuesto {
        color: #578197;
    }
    
    .mini-progress {
        height: 8px;
        background: #e4ecf3;
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
    
    .fill-green { background: #2e7d32; }
    .fill-yellow { background: #f57c00; }
    .fill-red { background: #d32f2f; }
    
    .status-badge {
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-good { background: #e8f5e9; color: #2e7d32; }
    .status-warning { background: #fff3e0; color: #f57c00; }
    .status-danger { background: #ffebee; color: #d32f2f; }
    
    .form-card {
        background: white;
        border-radius: 1.5rem;
        padding: 1.5rem;
        margin: 2rem 0;
        box-shadow: 0 8px 16px -10px #7f9bb3;
    }
    
    .form-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        color: #103c51;
        font-weight: 600;
    }
    
    .footer {
        text-align: center;
        color: #456476;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid #c9deef;
    }
    
    .stButton > button {
        background: #146b9e !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: background 0.2s !important;
    }
    
    .stButton > button:hover {
        background: #0f5a85 !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: #d32f2f !important;
    }
    
    .stSelectbox > div > div {
        border-radius: 1rem !important;
        border: 1px solid #caddf0 !important;
    }
    
    .stDateInput > div > div {
        border-radius: 1rem !important;
        border: 1px solid #caddf0 !important;
    }
    
    .stNumberInput > div > div {
        border-radius: 1rem !important;
        border: 1px solid #caddf0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATOS DE PRESUPUESTOS
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
# FUNCIONES DE PERSISTENCIA (ARCHIVO JSON)
# ============================================
def cargar_gastos():
    """Carga los gastos desde el archivo JSON"""
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convertir fechas de string a datetime
                for gasto in data:
                    gasto['fecha'] = datetime.fromisoformat(gasto['fecha'])
                return data
        except:
            return []
    return []

def guardar_gastos(gastos):
    """Guarda los gastos en el archivo JSON"""
    # Convertir fechas a string para JSON
    data = []
    for gasto in gastos:
        g = gasto.copy()
        g['fecha'] = g['fecha'].isoformat()
        data.append(g)
    
    with open(ARCHIVO_DATOS, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ============================================
# INICIALIZAR SESSION STATE (con datos del archivo)
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
                month=12, 
                year=st.session_state.current_month.year - 1
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
                month=1, 
                year=st.session_state.current_month.year + 1
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
# CATEGORÍAS
# ============================================
for categoria, datos in PRESUPUESTOS.items():
    # Calcular gastos por subcategoría
    gastos_cat = {}
    for sub in datos['subcategorias']:
        gastos_cat[sub] = sum(g['monto'] for g in gastos_del_mes() 
                              if g['categoria'] == categoria and g['subcategoria'] == sub)
    
    with st.expander(f"**{categoria}**", expanded=True):
        for sub, presupuesto in datos['subcategorias'].items():
            gastado = gastos_cat.get(sub, 0)
            porcentaje_sub = (gastado / presupuesto['monto']) * 100 if presupuesto['monto'] > 0 else 0
            
            # Determinar clase de color
            fill_class = 'fill-green'
            status_class = 'status-good'
            status_text = 'Bien'
            
            if porcentaje_sub > 100:
                fill_class = 'fill-red'
                status_class = 'status-danger'
                status_text = '¡Excedido!'
            elif porcentaje_sub > 80:
                fill_class = 'fill-yellow'
                status_class = 'status-warning'
                status_text = 'Cuidado'
            
            st.markdown(f"""
            <div class="subcategoria">
                <div class="subcategoria-header">
                    <span class="subcategoria-nombre">{sub}</span>
                    <span class="status-badge {status_class}">{porcentaje_sub:.0f}%</span>
                </div>
                {f'<div class="subcategoria-detalle">{presupuesto["descripcion"]}</div>' if presupuesto['descripcion'] else ''}
                <div class="subcategoria-montos">
                    <span class="subcategoria-gastado">{format_money(gastado)}</span>
                    <span class="subcategoria-presupuesto">de {format_money(presupuesto['monto'])}</span>
                </div>
                <div class="mini-progress">
                    <div class="mini-fill {fill_class}" style="width:{min(porcentaje_sub, 100)}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ============================================
# FORMULARIO PARA AGREGAR GASTOS
# ============================================
st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<div class="form-title">➕ Agregar / Corregir gasto</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    fecha = st.date_input("Fecha", datetime.now())
    categoria_sel = st.selectbox("Categoría", list(PRESUPUESTOS.keys()), key="cat_select")
    
with col2:
    # Subcategorías según categoría
    subcategorias = list(PRESUPUESTOS[categoria_sel]['subcategorias'].keys())
    subcategoria_sel = st.selectbox("Subcategoría", subcategorias, key="sub_select")
    monto = st.number_input("Monto $ (positivo o negativo)", value=100, step=1, format="%d")

descripcion = st.text_input("Descripción")

# Botones en fila
col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
with col_b2:
    if st.button("💾 Guardar gasto", use_container_width=True):
        if fecha and categoria_sel and subcategoria_sel and descripcion and monto != 0:
            # Crear nuevo gasto
            nuevo_gasto = {
                'fecha': datetime.combine(fecha, datetime.min.time()),
                'categoria': categoria_sel,
                'subcategoria': subcategoria_sel,
                'descripcion': descripcion,
                'monto': monto
            }
            st.session_state.gastos.append(nuevo_gasto)
            # Guardar en archivo
            guardar_gastos(st.session_state.gastos)
            st.success("✅ Gasto guardado permanentemente")
            st.rerun()
        else:
            st.error("❌ Todos los campos son obligatorios")

# Botón para reiniciar mes
with col_b3:
    if st.button("🔄 Reiniciar mes", use_container_width=True, type="secondary"):
        # Eliminar solo gastos del mes actual
        st.session_state.gastos = [g for g in st.session_state.gastos 
                                   if not (g['fecha'].year == st.session_state.current_month.year 
                                          and g['fecha'].month == st.session_state.current_month.month)]
        guardar_gastos(st.session_state.gastos)
        st.success("✅ Mes reiniciado")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# TABLA DE ÚLTIMOS GASTOS
# ============================================
gastos_mes = gastos_del_mes()
if gastos_mes:
    st.markdown("### 📋 Últimos gastos")
    df = pd.DataFrame(gastos_mes)
    df = df.sort_values('fecha', ascending=False).head(10)
    df['fecha_str'] = df['fecha'].dt.strftime('%d/%m')
    df['monto_str'] = df['monto'].apply(lambda x: format_money(x))
    
    # Mostrar tabla elegante
    for _, row in df.iterrows():
        col_f, col_c, col_s, col_d, col_m = st.columns([1, 1.5, 1.5, 3, 1.5])
        with col_f:
            st.write(row['fecha_str'])
        with col_c:
            st.write(row['categoria'])
        with col_s:
            st.write(row['subcategoria'])
        with col_d:
            st.write(row['descripcion'][:20] + '...' if len(row['descripcion']) > 20 else row['descripcion'])
        with col_m:
            st.write(f"**{row['monto_str']}**")

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    <p>📧 contacto@optipension73.com · 📱 871 579 1810</p>
    <p style="margin-top: 0.5rem;">✅ Datos guardados permanentemente en archivo · Cada mes independiente</p>
    <p style="margin-top: 0.5rem;">© 2026 · OptiPensión 73 · Optimización Integral</p>
</div>
""", unsafe_allow_html=True)
