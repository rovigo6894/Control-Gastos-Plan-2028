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
# CSS MEJORADO
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
    
    .title-container {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
    }
    
    .main-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #e0f2fe 50%, #bae6fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    
    .sub-title {
        font-size: 1.1rem;
        color: #94a3b8;
    }
    
    .inpc-badge {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 0.2rem 1rem;
        border-radius: 2rem;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 0.5rem;
    }
    
    .metric-card {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-radius: 1.5rem;
        padding: 1.5rem;
        box-shadow: 0 15px 30px -12px #000000;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 25px 40px -15px #000000;
    }
    
    .metric-title {
        color: #94a3b8;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff, #e2e8f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        margin-top: 0.5rem;
    }
    
    .metric-value.warning {
        background: linear-gradient(135deg, #ef4444, #f87171);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 0.3rem;
    }
    
    .chart-container {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-radius: 2rem;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 20px 35px -15px #000000;
    }
    
    .explanation-box {
        background: rgba(0,0,0,0.2);
        border-radius: 1rem;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #f59e0b;
        font-size: 0.9rem;
        color: #cbd5e1;
    }
    
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(148,163,184,0.2);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
        border: none !important;
        border-radius: 2rem !important;
        font-weight: 600 !important;
    }
    
    .stCheckbox > div > div {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# TÍTULO CON INPC
# ============================================
st.markdown("""
<div class="title-container">
    <div class="main-title">
        Control de Gastos PRO
        <span class="inpc-badge">INPC 2026</span>
    </div>
    <div class="sub-title">Ing. Roberto Villarreal · Plan Maestro 2026</div>
</div>
""", unsafe_allow_html=True)

# ============================================
# EXPLICACIÓN INPC
# ============================================
with st.expander("📈 ¿Qué es el INPC y por qué es importante?", expanded=False):
    st.markdown("""
    <div class="explanation-box">
        <strong>📊 INPC (Índice Nacional de Precios al Consumidor)</strong><br><br>
        El INPC mide la inflación, es decir, cómo aumenta el costo de vida con el tiempo.
        Para mantener tu poder adquisitivo, tu presupuesto debe aumentar cada año.<br><br>
        <strong>⚡ En esta app:</strong>
        <ul>
            <li>Puedes activar/desactivar el INPC 2026 (4.2%) con el checkbox</li>
            <li>Al activarlo, todos los presupuestos se ajustan automáticamente</li>
            <li>Así sabes cuánto deberías gastar HOY para mantener tu estilo de vida en 2026</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# CONTROL INPC
# ============================================
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.session_state.mostrar_2026 = st.checkbox("📈 Aplicar INPC 2026 (4.2%)", value=False)

# ============================================
# PESTAÑAS PRINCIPALES
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
    # Selector de mes
    col1, col2, col3, col4 = st.columns([1, 2, 1, 2])
    with col2:
        if st.button("← MES ANTERIOR"):
            st.session_state.current_month = st.session_state.current_month.replace(
                month=st.session_state.current_month.month - 1 if st.session_state.current_month.month > 1 else 12,
                year=st.session_state.current_month.year - 1 if st.session_state.current_month.month == 1 else st.session_state.current_month.year
            )
            st.rerun()
    
    with col3:
        st.markdown(f"### {get_month_name(st.session_state.current_month)} {st.session_state.current_month.year}")
    
    with col4:
        if st.button("MES SIGUIENTE →"):
            st.session_state.current_month = st.session_state.current_month.replace(
                month=st.session_state.current_month.month + 1 if st.session_state.current_month.month < 12 else 1,
                year=st.session_state.current_month.year + 1 if st.session_state.current_month.month == 12 else st.session_state.current_month.year
            )
            st.rerun()
    
    # Métricas principales
    gastos_mes = gastos_del_mes()
    total_gastado, restante, porcentaje, presupuesto_actual = calcular_totales(gastos_mes)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">
                💰 PRESUPUESTO
                <span style="font-size:0.7rem;">{'2026' if st.session_state.mostrar_2026 else '2025'}</span>
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
            <div class="metric-sub">{porcentaje:.1f}% del presupuesto</div>
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
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📅 DÍAS REST.</div>
            <div class="metric-value">{dias_restantes}</div>
            <div class="metric-sub">Presupuesto diario: {format_money(restante/dias_restantes if dias_restantes>0 else 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Explicación de métricas
    with st.expander("📊 ¿Qué significan estas cifras?", expanded=False):
        st.markdown("""
        <div class="explanation-box">
            <strong>📈 Interpretación de métricas:</strong><br><br>
            <strong>💰 PRESUPUESTO:</strong> Monto total disponible para el mes (ajustado por INPC si está activado).<br>
            <strong>💸 GASTADO:</strong> Suma de todos los gastos registrados en el mes.<br>
            <strong>⚖️ RESTANTE:</strong> Diferencia entre presupuesto y gastado (rojo si es negativo).<br>
            <strong>📅 DÍAS REST:</strong> Días que faltan para terminar el mes y presupuesto diario recomendado.<br>
            <strong>📊 Gráficas:</strong> Distribución por categoría y evolución diaria de gastos.
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficas
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📊 Gastos por Categoría")
            
            if gastos_mes:
                df_cat = pd.DataFrame(gastos_mes)
                cat_sum = df_cat.groupby('categoria')['monto'].sum().reset_index()
                fig = px.pie(cat_sum, values='monto', names='categoria', 
                            title="Distribución de gastos por categoría",
                            color_discrete_sequence=px.colors.sequential.Blues_r)
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📭 Sin gastos este mes - Agrega gastos en la pestaña GASTOS")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📈 Evolución Diaria")
            
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
                    font_color='#94a3b8'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📭 Sin datos diarios - Registra tus primeros gastos")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Barra de progreso
    st.markdown(f"""
    <div class="chart-container">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span>📊 Progreso mensual: {porcentaje:.1f}%</span>
            <span>{format_money(total_gastado)} de {format_money(presupuesto_actual)}</span>
        </div>
        <div style="height: 20px; background: rgba(226,232,240,0.2); border-radius: 10px; overflow: hidden;">
            <div style="height: 20px; width: {min(porcentaje, 100)}%; 
                      background: linear-gradient(90deg, {'#ef4444' if porcentaje>100 else '#f59e0b' if porcentaje>80 else '#10b981'}, 
                      {'#f87171' if porcentaje>100 else '#fbbf24' if porcentaje>80 else '#34d399'}); 
                      border-radius: 10px; transition: width 0.5s;">
            </div>
        </div>
        <div style="margin-top: 0.5rem; font-size:0.8rem; color:#94a3b8;">
            {format_money(presupuesto_actual - total_gastado)} restantes para {dias_restantes} días
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# PESTAÑA 2: GASTOS (con INPC)
# ============================================
with tab2:
    st.subheader("📋 Registro de Gastos")
    
    # Explicación rápida
    st.markdown("""
    <div class="explanation-box">
        <strong>➕ Agrega tus gastos diarios aquí:</strong> Selecciona categoría, subcategoría, monto y descripción.
        Los montos se comparan automáticamente con el presupuesto ajustado por INPC.
    </div>
    """, unsafe_allow_html=True)
    
    # Formulario rápido
    with st.expander("➕ AGREGAR GASTO RÁPIDO", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fecha = st.date_input("Fecha", datetime.now())
        
        with col2:
            categoria = st.selectbox("Categoría", list(PRESUPUESTOS.keys()))
        
        with col3:
            subcategorias = list(PRESUPUESTOS[categoria]['subcategorias'].keys())
            subcategoria = st.selectbox("Subcategoría", subcategorias)
        
        with col4:
            monto = st.number_input("Monto $", value=0, step=10)
        
        descripcion = st.text_input("Descripción")
        
        if st.button("💾 GUARDAR GASTO", use_container_width=True):
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
    
    # Vista por categorías con INPC
    st.subheader("📊 Detalle por Categoría")
    
    for categoria, datos in PRESUPUESTOS.items():
        with st.expander(f"**{categoria}**", expanded=True):
            # Totales de categoría
            total_cat = sum(g['monto'] for g in gastos_del_mes() if g['categoria'] == categoria)
            presupuesto_cat = datos['total_2026'] if st.session_state.mostrar_2026 else datos['total']
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Total categoría:** {format_money(total_cat)}")
            with col2:
                st.markdown(f"**Presupuesto:** {format_money(presupuesto_cat)}")
            
            # Barra de progreso de categoría
            progreso_cat = min(total_cat / presupuesto_cat, 1.0) if presupuesto_cat > 0 else 0
            color_cat = '#ef4444' if total_cat > presupuesto_cat else '#f59e0b' if total_cat > presupuesto_cat * 0.8 else '#10b981'
            st.markdown(f"""
            <div style="height: 8px; background: rgba(226,232,240,0.2); border-radius: 10px; margin: 10px 0;">
                <div style="height: 8px; width: {progreso_cat*100}%; background: {color_cat}; border-radius: 10px;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Subcategorías
            for sub, presupuesto in datos['subcategorias'].items():
                gastado = sum(g['monto'] for g in gastos_del_mes() 
                            if g['categoria'] == categoria and g['subcategoria'] == sub)
                
                presupuesto_sub = presupuesto['monto_2026'] if st.session_state.mostrar_2026 else presupuesto['monto']
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{sub}**")
                    if presupuesto['descripcion']:
                        st.caption(presupuesto['descripcion'])
                with col2:
                    st.markdown(f"**{format_money(gastado)}**")
                    st.markdown(f"de {format_money(presupuesto_sub)}")
                
                progreso = min(gastado / presupuesto_sub, 1.0) if presupuesto_sub > 0 else 0
                color = '#ef4444' if gastado > presupuesto_sub else '#f59e0b' if gastado > presupuesto_sub * 0.8 else '#10b981'
                
                st.markdown(f"""
                <div style="height: 8px; background: rgba(226,232,240,0.2); border-radius: 10px; margin: 10px 0;">
                    <div style="height: 8px; width: {progreso*100}%; background: {color}; border-radius: 10px;"></div>
                </div>
                """, unsafe_allow_html=True)
                st.divider()
    
    # Últimos gastos
    if gastos_mes:
        st.subheader("📋 Últimos Gastos")
        df = pd.DataFrame(gastos_mes)
        df = df.sort_values('fecha', ascending=False).head(20)
        df['fecha'] = df['fecha'].dt.strftime('%d/%m/%Y')
        df['monto'] = df['monto'].apply(lambda x: format_money(x))
        st.dataframe(df[['fecha', 'categoria', 'subcategoria', 'descripcion', 'monto']], 
                    use_container_width=True, hide_index=True)

# ============================================
# PESTAÑA 3: ANÁLISIS (con INPC)
# ============================================
with tab3:
    st.subheader("📈 Análisis Avanzado")
    
    st.markdown("""
    <div class="explanation-box">
        <strong>📊 Análisis de tendencias:</strong> Selecciona un rango de fechas para ver cómo han evolucionado tus gastos.
        Las métricas se ajustan automáticamente al INPC si está activado.
    </div>
    """, unsafe_allow_html=True)
    
    # Selector de rango
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha inicio", 
                                     datetime.now().replace(day=1, month=1))
    with col2:
        fecha_fin = st.date_input("Fecha fin", datetime.now())
    
    if fecha_inicio and fecha_fin:
        gastos_rango = [g for g in st.session_state.datos['gastos'] 
                       if fecha_inicio <= g['fecha'].date() <= fecha_fin]
        
        if gastos_rango:
            df_rango = pd.DataFrame(gastos_rango)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gastos por mes
                df_rango['mes'] = df_rango['fecha'].dt.strftime('%Y-%m')
                mes_sum = df_rango.groupby('mes')['monto'].sum().reset_index()
                fig = px.bar(mes_sum, x='mes', y='monto', 
                            title="Gastos por Mes",
                            color_discrete_sequence=['#3b82f6'])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top 10 gastos
                top_gastos = df_rango.nlargest(10, 'monto')[['descripcion', 'monto', 'fecha']]
                fig = px.bar(top_gastos, x='monto', y='descripcion', 
                            orientation='h',
                            title="Top 10 Gastos",
                            color_discrete_sequence=['#ef4444'])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8',
                    yaxis={'categoryorder':'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Estadísticas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total período", format_money(df_rango['monto'].sum()))
            with col2:
                st.metric("Promedio mensual", format_money(df_rango['monto'].mean() * 30))
            with col3:
                st.metric("Gasto promedio", format_money(df_rango['monto'].mean()))
            with col4:
                st.metric("Número de gastos", len(df_rango))
        else:
            st.info("📭 No hay gastos en el período seleccionado")

# ============================================
# PESTAÑA 4: METAS DE AHORRO
# ============================================
with tab4:
    st.subheader("🎯 Metas de Ahorro")
    
    st.markdown("""
    <div class="explanation-box">
        <strong>🎯 Metas inteligentes:</strong> Define objetivos de ahorro y dales seguimiento.
        Las metas se ajustan automáticamente con INPC para mantener su valor real.
    </div>
    """, unsafe_allow_html=True)
    
    # Formulario para nueva meta
    with st.expander("➕ NUEVA META", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre_meta = st.text_input("Nombre de la meta")
            monto_meta = st.number_input("Monto objetivo $", min_value=0, step=1000)
        with col2:
            fecha_meta = st.date_input("Fecha límite", 
                                       datetime.now() + timedelta(days=365))
        
        if st.button("Crear Meta"):
            if nombre_meta and monto_meta > 0:
                if 'metas' not in st.session_state.datos:
                    st.session_state.datos['metas'] = []
                
                # Ajustar por INPC si está activado
                monto_final = monto_meta * INPC_2026 if st.session_state.mostrar_2026 else monto_meta
                
                st.session_state.datos['metas'].append({
                    'nombre': nombre_meta,
                    'monto_objetivo': monto_final,
                    'monto_original': monto_meta,
                    'fecha_limite': fecha_meta.isoformat(),
                    'progreso': 0,
                    'ahorrado': 0
                })
                guardar_datos(st.session_state.datos)
                st.success("Meta creada")
                st.rerun()
    
    # Mostrar metas
    if 'metas' in st.session_state.datos and st.session_state.datos['metas']:
        for i, meta in enumerate(st.session_state.datos['metas']):
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{meta['nombre']}**")
                    st.caption(f"Límite: {meta['fecha_limite']}")
                with col2:
                    st.markdown(f"**Objetivo:** ${meta['monto_objetivo']:,.0f}")
                with col3:
                    ahorrado = st.number_input(f"Ahorrado", min_value=0, value=meta.get('ahorrado', 0), step=100, key=f"ahorro_{i}")
                    meta['ahorrado'] = ahorrado
                with col4:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.datos['metas'].pop(i)
                        guardar_datos(st.session_state.datos)
                        st.rerun()
                
                progreso = min(ahorrado / meta['monto_objetivo'], 1.0) if meta['monto_objetivo'] > 0 else 0
                st.progress(progreso, text=f"Progreso: {progreso*100:.1f}%")
                st.divider()
        
        if st.button("💾 Guardar progreso", type="primary"):
            guardar_datos(st.session_state.datos)
            st.success("Progreso guardado")
    else:
        st.info("🎯 No hay metas de ahorro configuradas - Crea tu primera meta")

# ============================================
# PESTAÑA 5: CONFIGURACIÓN
# ============================================
with tab5:
    st.subheader("⚙️ Configuración")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Exportar Datos")
        if st.button("📥 Exportar TODO a CSV"):
            if st.session_state.datos['gastos']:
                df_all = pd.DataFrame(st.session_state.datos['gastos'])
                df_all['fecha'] = pd.to_datetime(df_all['fecha']).dt.strftime('%Y-%m-%d')
                csv = df_all.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"todos_gastos_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    with col2:
        st.markdown("### 🗑️ Mantenimiento")
        if st.button("⚠️ RESPALDAR DATOS", type="primary"):
            backup = st.session_state.datos.copy()
            backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w') as f:
                json.dump(backup, f, indent=2)
            st.success(f"Backup creado: {backup_file}")
        
        if st.button("🗑️ REINICIAR TODO", type="secondary"):
            if st.checkbox("Confirmar eliminación total"):
                st.session_state.datos = {'gastos': [], 'presupuestos': PRESUPUESTOS, 'metas': []}
                guardar_datos(st.session_state.datos)
                st.success("Datos reiniciados")
                st.rerun()
    
    st.markdown("### 📊 Estadísticas Globales")
    total_gastos = len(st.session_state.datos['gastos'])
    total_monto = sum(g['monto'] for g in st.session_state.datos['gastos'])
    primer_gasto = min([g['fecha'] for g in st.session_state.datos['gastos']]) if st.session_state.datos['gastos'] else None
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total gastos", total_gastos)
    with col2:
        st.metric("Monto total", format_money(total_monto))
    with col3:
        st.metric("Desde", primer_gasto.strftime('%d/%m/%Y') if primer_gasto else "N/A")
    
    st.markdown("### ⚡ Ajustes de INPC")
    st.info(f"📈 INPC 2026 actual: {INPC_2026*100-100:.1f}% - Puedes activarlo/desactivarlo en el dashboard")

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    <p>📧 contacto@optipension73.com · 📱 871 579 1810</p>
    <p>⚡ Versión Personal PRO · Con INPC 2026 · Datos locales</p>
    <p>© 2026 · OptiPensión 73 · Optimización Integral</p>
</div>
""", unsafe_allow_html=True)
