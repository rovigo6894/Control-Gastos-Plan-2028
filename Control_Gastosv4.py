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
# CSS MEJORADO - TÍTULO CENTRADO Y CLARO
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(145deg, #0b1c26 0%, #1a2f3a 50%, #0f2a35 100%);
        padding: 1rem;
    }
    
    /* ===== TÍTULO CENTRADO, GRANDE Y CLARO ===== */
    .title-container {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .main-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #e0f2fe 50%, #bae6fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 10px rgba(255,255,255,0.2);
    }
    
    .sub-title {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    
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
    }
    
    .resumen-fila:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 25px 40px -15px #000000;
        border-color: rgba(37,99,235,0.3);
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
    }
    
    .progress-fill {
        height: 14px;
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        border-radius: 20px;
        width: 0%;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .progress-fill.warning {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
    }
    
    .progress-fill.danger {
        background: linear-gradient(90deg, #dc2626, #ef4444);
    }
    
    .categoria {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-radius: 2rem;
        padding: 1.8rem;
        margin-bottom: 1.8rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 20px 35px -15px #000000;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(148,163,184,0.2);
        animation: fadeInUp 0.5s ease-out 0.5s both;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 3rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.3s !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# INTERFAZ PRINCIPAL
# ============================================

# ===== TÍTULO CENTRADO, GRANDE Y CLARO =====
st.markdown("""
<div class="title-container">
    <div class="main-title">Control de Gastos</div>
    <div class="sub-title">Ing. Roberto Villarreal · Plan Maestro 2026</div>
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

# Filas de resumen
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
        <span>💰 {format_money(PRESUPUESTO_TOTAL)}</span>
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
# FORMULARIO PARA AGREGAR GASTOS
# ============================================
st.markdown("### ➕ Agregar / Corregir gasto")

col1, col2 = st.columns(2)
with col1:
    fecha = st.date_input("📅 Fecha", datetime.now())
    categoria_sel = st.selectbox("📁 Categoría", list(PRESUPUESTOS.keys()), key="cat_select")
    
with col2:
    subcategorias = list(PRESUPUESTOS[categoria_sel]['subcategorias'].keys())
    subcategoria_sel = st.selectbox("📂 Subcategoría", subcategorias, key="sub_select")
    monto = st.number_input("💰 Monto $", value=100, step=1, key="monto_input")

descripcion = st.text_input("📝 Descripción", key="desc_input")

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
