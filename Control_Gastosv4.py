import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================
st.set_page_config(
    page_title="💰 Control de Gastos PRO · OptiPensión 73",
    page_icon="💰",
    layout="wide",
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
# DATOS DE PRESUPUESTOS CON INPC 2026
# ============================================
INPC_2026 = 1.042  # 4.2% de inflación estimada

PRESUPUESTOS = {
    'Alimentación': {
        'total': 7900,
        'total_2026': round(7900 * INPC_2026, 2),
        'subcategorias': {
            'Desayuno': {'monto': 75, 'monto_2026': round(75 * INPC_2026, 2), 
                        'descripcion': 'Huevos con manteca, queso, aguacate o jamón serrano'},
            'Comida': {'monto': 148.33, 'monto_2026': round(148.33 * INPC_2026, 2),
                      'descripcion': 'Comida fuerte. Rib Eye, carnita asada'},
            'Cena': {'monto': 40, 'monto_2026': round(40 * INPC_2026, 2),
                    'descripcion': 'Ligero: aceitunas, plátano, frutos secos, quesadillas'}
        }
    },
    'Servicios': {
        'total': 1550,
        'total_2026': round(1550 * INPC_2026, 2),
        'subcategorias': {
            'Internet': {'monto': 600, 'monto_2026': round(600 * INPC_2026, 2), 'descripcion': ''},
            'Luz': {'monto': 450, 'monto_2026': round(450 * INPC_2026, 2), 'descripcion': ''},
            'Agua': {'monto': 200, 'monto_2026': round(200 * INPC_2026, 2), 
                    'descripcion': 'Beneficio IPAM aplicado'},
            'Celular': {'monto': 200, 'monto_2026': round(200 * INPC_2026, 2), 'descripcion': ''},
            'Gas': {'monto': 100, 'monto_2026': round(100 * INPC_2026, 2), 'descripcion': ''}
        }
    },
    'Vivienda': {
        'total': 2150,
        'total_2026': round(2150 * INPC_2026, 2),
        'subcategorias': {
            'Mantenimiento': {'monto': 1400, 'monto_2026': round(1400 * INPC_2026, 2),
                             'descripcion': 'Para que la casa siempre esté al cien'},
            'Transporte': {'monto': 750, 'monto_2026': round(750 * INPC_2026, 2), 'descripcion': ''}
        }
    }
}

PRESUPUESTO_TOTAL = 13100
PRESUPUESTO_TOTAL_2026 = round(13100 * INPC_2026, 2)
ARCHIVO_DATOS = "gastos_completo.json"

# ============================================
# FUNCIONES DE PERSISTENCIA
# ============================================
def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for gasto in data['gastos']:
                    gasto['fecha'] = datetime.fromisoformat(gasto['fecha'])
                return data
        except:
            return {'gastos': [], 'presupuestos': PRESUPUESTOS, 'metas': []}
    return {'gastos': [], 'presupuestos': PRESUPUESTOS, 'metas': []}

def guardar_datos(data):
    datos_guardar = {
        'gastos': [],
        'presupuestos': data['presupuestos'],
        'metas': data.get('metas', [])
    }
    
    for gasto in data['gastos']:
        g = gasto.copy()
        g['fecha'] = g['fecha'].isoformat()
        datos_guardar['gastos'].append(g)
    
    with open(ARCHIVO_DATOS, 'w', encoding='utf-8') as f:
        json.dump(datos_guardar, f, indent=2, ensure_ascii=False)

# ============================================
# INICIALIZAR SESSION STATE
# ============================================
if 'datos' not in st.session_state:
    st.session_state.datos = cargar_datos()
    
if 'current_month' not in st.session_state:
    st.session_state.current_month = datetime.now().replace(day=1)
    
if 'mostrar_2026' not in st.session_state:
    st.session_state.mostrar_2026 = False

# ============================================
# FUNCIONES DE AYUDA
# ============================================
def format_money(num):
    return f"${num:,.2f}"

def get_month_name(date):
    meses = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 
             'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
    return meses[date.month - 1]

def gastos_del_mes(fecha=None):
    if fecha is None:
        fecha = st.session_state.current_month
    return [g for g in st.session_state.datos['gastos'] 
            if g['fecha'].year == fecha.year 
            and g['fecha'].month == fecha.month]

def calcular_totales(gastos_mes=None):
    if gastos_mes is None:
        gastos_mes = gastos_del_mes()
    total = sum(g['monto'] for g in gastos_mes)
    presupuesto_actual = PRESUPUESTO_TOTAL_2026 if st.session_state.mostrar_2026 else PRESUPUESTO_TOTAL
    restante = presupuesto_actual - total
    porcentaje = (total / presupuesto_actual) * 100 if presupuesto_actual > 0 else 0
    return total, restante, porcentaje, presupuesto_actual

# ============================================
# CSS CON TEXTO GRANDE
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(145deg, #0b1c26 0%, #1a2f3a 50%, #0f2a35 100%);
    }
    
    /* TÍTULOS GRANDES */
    .main-title {
        font-size: 4rem !important;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #e0f2fe 50%, #bae6fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-title {
        font-size: 1.5rem !important;
        color: #94a3b8;
        text-align: center;
    }
    
    /* TARJETAS DE MÉTRICAS - MÁS GRANDES */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-radius: 2rem;
        padding: 2rem;
        box-shadow: 0 20px 35px -15px #000000;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 30px 45px -15px #000000;
    }
    
    .metric-title {
        color: #94a3b8;
        font-size: 1.2rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 3rem !important;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff, #e2e8f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        margin: 0.5rem 0;
    }
    
    .metric-value.warning {
        background: linear-gradient(135deg, #ef4444, #f87171);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-sub {
        font-size: 1rem !important;
        color: #64748b;
        margin-top: 0.5rem;
    }
    
    .metric-sub strong {
        color: #f59e0b;
        font-size: 1.2rem;
    }
    
    /* EXPLICACIONES GRANDES */
    .explanation-box {
        background: rgba(0,0,0,0.3);
        border-radius: 1.5rem;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-left: 6px solid #f59e0b;
        font-size: 1.1rem !important;
        color: #cbd5e1;
        line-height: 1.6;
    }
    
    .explanation-box strong {
        color: #f59e0b;
        font-size: 1.2rem;
    }
    
    .explanation-box ul {
        margin-top: 0.5rem;
        padding-left: 1.5rem;
    }
    
    .explanation-box li {
        margin: 0.5rem 0;
    }
    
    /* BOTONES GRANDES */
    .stButton > button {
        font-size: 1.2rem !important;
        padding: 1rem 2rem !important;
        border-radius: 3rem !important;
    }
    
    /* SELECTORES DE MES */
    .month-selector {
        font-size: 2rem !important;
        font-weight: 600;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* CHECKBOX GRANDE */
    .stCheckbox > div > label {
        font-size: 1.2rem !important;
        color: white !important;
    }
    
    /* GRÁFICAS */
    .chart-title {
        font-size: 1.5rem !important;
        color: white;
        margin-bottom: 1rem;
    }
    
    .chart-container {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-radius: 2rem;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* TABLAS */
    .dataframe {
        font-size: 1rem !important;
    }
    
    /* FOOTER */
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 1rem !important;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(148,163,184,0.2);
    }
    
    .footer p {
        margin: 0.5rem 0;
    }
    
    /* EXPANDER */
    .streamlit-expanderHeader {
        font-size: 1.2rem !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# TÍTULO GRANDE
# ============================================
st.markdown('<div class="main-title">💰 CONTROL DE GASTOS PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Ing. Roberto Villarreal · Plan Maestro 2026</div>', unsafe_allow_html=True)

# ============================================
# EXPLICACIÓN INPC GRANDE
# ============================================
with st.expander("📈 ¿QUÉ ES EL INPC Y POR QUÉ ES IMPORTANTE?", expanded=True):
    st.markdown("""
    <div class="explanation-box">
        <strong>📊 INPC (Índice Nacional de Precios al Consumidor)</strong><br><br>
        El INPC mide la <strong>inflación</strong>, es decir, cómo aumenta el costo de vida con el tiempo.
        Para mantener tu poder adquisitivo, tu presupuesto debe aumentar cada año.<br><br>
        
        <strong>⚡ EN ESTA APP:</strong>
        <ul>
            <li>✅ Puedes activar/desactivar el INPC 2026 (4.2%) con el checkbox</li>
            <li>✅ Al activarlo, <strong>TODOS los presupuestos se ajustan automáticamente</strong></li>
            <li>✅ Así sabes cuánto deberías gastar HOY para mantener tu estilo de vida en 2026</li>
        </ul>
        
        <div style="background: rgba(245,158,11,0.2); padding:1rem; border-radius:1rem; margin-top:1rem;">
            <strong>💡 EJEMPLO:</strong> Si hoy gastas $13,100, en 2026 necesitarás <strong>$13,650</strong> 
            para comprar lo mismo (con 4.2% de inflación).
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# CONTROL INPC GRANDE
# ============================================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.session_state.mostrar_2026 = st.checkbox("✅ APLICAR INPC 2026 (4.2%)", value=False)

# ============================================
# PESTAÑAS
# ============================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 DASHBOARD", 
    "💰 GASTOS", 
    "📈 ANÁLISIS", 
    "🎯 METAS", 
    "⚙️ CONFIGURACIÓN"
])

# ============================================
# PESTAÑA 1: DASHBOARD
# ============================================
with tab1:
    # Selector de mes GRANDE
    col1, col2, col3, col4 = st.columns([1, 2, 1, 2])
    with col2:
        if st.button("← MES ANTERIOR", use_container_width=True):
            st.session_state.current_month = st.session_state.current_month.replace(
                month=st.session_state.current_month.month - 1 if st.session_state.current_month.month > 1 else 12,
                year=st.session_state.current_month.year - 1 if st.session_state.current_month.month == 1 else st.session_state.current_month.year
            )
            st.rerun()
    
    with col3:
        st.markdown(f"<div class='month-selector'>{get_month_name(st.session_state.current_month)} {st.session_state.current_month.year}</div>", unsafe_allow_html=True)
    
    with col4:
        if st.button("MES SIGUIENTE →", use_container_width=True):
            st.session_state.current_month = st.session_state.current_month.replace(
                month=st.session_state.current_month.month + 1 if st.session_state.current_month.month < 12 else 1,
                year=st.session_state.current_month.year + 1 if st.session_state.current_month.month == 12 else st.session_state.current_month.year
            )
            st.rerun()
    
    # Métricas principales GRANDES
    gastos_mes = gastos_del_mes()
    total_gastado, restante, porcentaje, presupuesto_actual = calcular_totales(gastos_mes)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">
                💰 PRESUPUESTO
                <span style="background:#f59e0b; padding:0.3rem 1rem; border-radius:2rem; font-size:0.9rem;">{'2026' if st.session_state.mostrar_2026 else '2025'}</span>
            </div>
            <div class="metric-value">{format_money(presupuesto_actual)}</div>
            <div class="metric-sub">Base: {format_money(PRESUPUESTO_TOTAL)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">💸 GASTADO</div>
            <div class="metric-value">{format_money(total_gastado)}</div>
            <div class="metric-sub"><strong>{porcentaje:.1f}%</strong> del presupuesto</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">⚖️ RESTANTE</div>
            <div class="metric-value {'warning' if restante < 0 else ''}">{format_money(restante)}</div>
            <div class="metric-sub">Disponible hasta fin de mes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        dias_restantes = (datetime(st.session_state.current_month.year, 
                                  st.session_state.current_month.month + 1, 1) - 
                         datetime.now()).days if st.session_state.current_month.month < 12 else 31
        presupuesto_diario = restante / dias_restantes if dias_restantes > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📅 DÍAS REST.</div>
            <div class="metric-value">{dias_restantes}</div>
            <div class="metric-sub"><strong>{format_money(presupuesto_diario)}</strong> por día</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Explicación GRANDE
    with st.expander("📊 ¿QUÉ SIGNIFICAN ESTAS CIFRAS?", expanded=True):
        st.markdown("""
        <div class="explanation-box">
            <strong>📈 INTERPRETACIÓN DE MÉTRICAS:</strong><br><br>
            
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
                <div>
                    <strong style="color:#f59e0b;">💰 PRESUPUESTO:</strong>
                    <p>Monto total disponible para el mes (ajustado por INPC si está activado).</p>
                    
                    <strong style="color:#f59e0b;">💸 GASTADO:</strong>
                    <p>Suma de todos los gastos registrados en el mes.</p>
                </div>
                <div>
                    <strong style="color:#f59e0b;">⚖️ RESTANTE:</strong>
                    <p>Diferencia entre presupuesto y gastado (rojo si es negativo).</p>
                    
                    <strong style="color:#f59e0b;">📅 DÍAS REST.:</strong>
                    <p>Días que faltan para terminar el mes y presupuesto diario recomendado.</p>
                </div>
            </div>
            
            <div style="background:rgba(59,130,246,0.2); padding:1rem; border-radius:1rem; margin-top:1rem;">
                <strong>🎯 OBJETIVO:</strong> Mantener el gasto diario por debajo del presupuesto diario
                para terminar el mes en positivo.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficas GRANDES
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("<div class='chart-title'>📊 GASTOS POR CATEGORÍA</div>", unsafe_allow_html=True)
            
            if gastos_mes:
                df_cat = pd.DataFrame(gastos_mes)
                cat_sum = df_cat.groupby('categoria')['monto'].sum().reset_index()
                fig = px.pie(cat_sum, values='monto', names='categoria', 
                            title="Distribución de gastos por categoría",
                            color_discrete_sequence=px.colors.sequential.Blues_r)
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8',
                    font_size=14,
                    title_font_size=18
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📭 Sin gastos este mes - Agrega gastos en la pestaña GASTOS")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("<div class='chart-title'>📈 EVOLUCIÓN DIARIA</div>", unsafe_allow_html=True)
            
            if gastos_mes:
                df_daily = pd.DataFrame(gastos_mes)
                df_daily['dia'] = df_daily['fecha'].dt.day
                daily_sum = df_daily.groupby('dia')['monto'].sum().reset_index()
                fig = px.line(daily_sum, x='dia', y='monto', 
                            title="Gastos acumulados por día",
                            markers=True, line_shape='spline')
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8',
                    font_size=14,
                    title_font_size=18
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📭 Sin datos diarios - Registra tus primeros gastos")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Barra de progreso GRANDE
    st.markdown(f"""
    <div class="chart-container">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <span style="font-size:1.5rem; font-weight:600;">📊 PROGRESO MENSUAL</span>
            <span style="font-size:1.5rem; font-weight:600; color:#f59e0b;">{porcentaje:.1f}%</span>
        </div>
        <div style="height: 30px; background: rgba(226,232,240,0.2); border-radius: 15px; overflow: hidden;">
            <div style="height: 30px; width: {min(porcentaje, 100)}%; 
                      background: linear-gradient(90deg, {'#ef4444' if porcentaje>100 else '#f59e0b' if porcentaje>80 else '#10b981'}, 
                      {'#f87171' if porcentaje>100 else '#fbbf24' if porcentaje>80 else '#34d399'}); 
                      border-radius: 15px; transition: width 0.5s;">
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 1rem; font-size:1.2rem;">
            <span>💰 Gastado: {format_money(total_gastado)}</span>
            <span>⚡ Restante: {format_money(presupuesto_actual - total_gastado)}</span>
            <span>📅 {dias_restantes} días</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# PESTAÑA 2: GASTOS (simplificada)
# ============================================
with tab2:
    st.markdown("<div class='chart-title'>📋 REGISTRO DE GASTOS</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="explanation-box">
        <strong>➕ AGREGAR GASTOS:</strong> Selecciona categoría, subcategoría, monto y descripción.
        Los montos se comparan automáticamente con el presupuesto ajustado por INPC.
    </div>
    """, unsafe_allow_html=True)
    
    # Formulario
    with st.form("form_gastos"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            fecha = st.date_input("📅 Fecha", datetime.now())
        with col2:
            categoria = st.selectbox("📁 Categoría", list(PRESUPUESTOS.keys()))
        with col3:
            subcategorias = list(PRESUPUESTOS[categoria]['subcategorias'].keys())
            subcategoria = st.selectbox("📂 Subcategoría", subcategorias)
        with col4:
            monto = st.number_input("💰 Monto $", value=0, step=10)
        
        descripcion = st.text_input("📝 Descripción")
        
        if st.form_submit_button("💾 GUARDAR GASTO", use_container_width=True):
            if fecha and categoria and subcategoria and descripcion and monto != 0:
                nuevo_gasto = {
                    'fecha': datetime.combine(fecha, datetime.min.time()),
                    'categoria': categoria,
                    'subcategoria': subcategoria,
                    'descripcion': descripcion,
                    'monto': monto
                }
                st.session_state.datos['gastos'].append(nuevo_gasto)
                guardar_datos(st.session_state.datos)
                st.success("✅ Gasto guardado")
                st.rerun()

# ============================================
# FOOTER GRANDE
# ============================================
st.markdown("""
<div class="footer">
    <p>📧 contacto@optipension73.com · 📱 871 579 1810</p>
    <p>⚡ Versión Personal PRO · Con INPC 2026 · Datos locales</p>
    <p>© 2026 · OptiPensión 73 · Optimización Integral</p>
</div>
""", unsafe_allow_html=True)
