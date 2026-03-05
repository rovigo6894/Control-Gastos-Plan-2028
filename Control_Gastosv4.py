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

# Forzar recarga de CSS (NUEVO)
st.markdown("""
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
""", unsafe_allow_html=True)

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
# CSS MEJORADO (MÁS ROBUSTO)
# ============================================
st.markdown("""
<style>
    /* Reset completo */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Fondo blanco forzado */
    .stApp, .main, .block-container {
        background: white !important;
        max-width: 1200px !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Header */
    .header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
        background: white;
        padding: 1rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
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
        box-shadow: 0 4px 6px -2px #cbd5e1;
    }
    
    .title h1 {
        color: #0f172a;
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
    }
    
    .title p {
        color: #475569;
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* Selector de mes */
    .month-selector {
        background: #f8fafc;
        border-radius: 2rem;
        padding: 0.8rem 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
        border: 1px solid #e2e8f0;
    }
    
    .month-selector span {
        font-weight: 600;
        color: #1e293b;
        font-size: 1.3rem;
    }
    
    /* Filas de resumen */
    .resumen-fila {
        background: #f8fafc;
        border-radius: 1rem;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #e2e8f0;
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
    
    /* Barra de progreso */
    .progress-container {
        background: #f8fafc;
        border-radius: 1rem;
        padding: 1.2rem 1.8rem;
        margin-bottom: 2rem;
        border: 1px solid #e2e8f0;
    }
    
    .progress-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.8rem;
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
        border-radius: 20px;
        transition: width 0.3s;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Botones */
    .stButton > button {
        background: #2563eb !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 1.5rem !important;
        border-radius: 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        background: #1d4ed8 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -2px #94a3b8 !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: #ef4444 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #dc2626 !important;
    }
    
    /* Inputs */
    .stSelectbox > div > div,
    .stDateInput > div > div,
    .stNumberInput > div > div,
    .stTextInput > div > div {
        border-radius: 0.8rem !important;
        border: 1px solid #e2e8f0 !important;
        background: #f8fafc !important;
    }
    
    /* Dividers */
    hr {
        margin: 1rem 0 !important;
        border-color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

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
color_barra = '#dc2626' if porcentaje > 100 else '#f59e0b' if porcentaje > 80 else '#2563eb'
st.markdown(f"""
<div class="progress-container">
    <div class="progress-header">
        <span>{porcentaje:.1f}% del presupuesto</span>
        <span>${PRESUPUESTOS['Alimentación']['diario']:.2f}/día</span>
    </div>
    <div class="progress-bar">
        <div class="progress-fill" style="background-color: {color_barra}; width: {min(porcentaje, 100)}%;"></div>
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
            
            # Barra de progreso individual
            progreso = min(gastado / presupuesto['monto'], 1.0) if presupuesto['monto'] > 0 else 0
            color = '#dc2626' if (gastado / presupuesto['monto']) > 1.0 else '#f59e0b' if (gastado / presupuesto['monto']) > 0.8 else '#10b981'
            st.markdown(f"""
            <div style="height:8px; background:#e2e8f0; border-radius:10px; margin:10px 0; width:100%;">
                <div style="height:8px; background:{color}; border-radius:10px; width:{progreso*100}%;"></div>
            </div>
            """, unsafe_allow_html=True)
            st.divider()

# ============================================
# FORMULARIO
# ============================================
st.markdown("### ➕ Agregar / Corregir gasto")

col1, col2 = st.columns(2)
with col1:
    fecha = st.date_input("Fecha", datetime.now())
    categoria_sel = st.selectbox("Categoría", list(PRESUPUESTOS.keys()))
    
with col2:
    subcategorias = list(PRESUPUESTOS[categoria_sel]['subcategorias'].keys())
    subcategoria_sel = st.selectbox("Subcategoría", subcategorias)
    monto = st.number_input("Monto $", value=100, step=1)

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
            st.rerun()
        else:
            st.error("Completa todos los campos")

with col_b2:
    if st.button("🔄 Reiniciar mes", use_container_width=True, type="secondary"):
        st.session_state.gastos = [g for g in st.session_state.gastos 
                                   if not (g['fecha'].year == st.session_state.current_month.year 
                                          and g['fecha'].month == st.session_state.current_month.month)]
        guardar_gastos(st.session_state.gastos)
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
            st.write(f"**{format_money(row['monto'])}**")

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    <p>📧 contacto@optipension73.com · 📱 871 579 1810</p>
    <p>© 2026 · OptiPensión 73</p>
</div>
""", unsafe_allow_html=True)
