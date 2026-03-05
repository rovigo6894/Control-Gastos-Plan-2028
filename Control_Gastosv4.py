import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import hashlib
from io import BytesIO

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================
st.set_page_config(
    page_title="💰 Control de Gastos · Personal PRO",
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
ARCHIVO_DATOS = "gastos_completo.json"

# ============================================
# FUNCIONES DE PERSISTENCIA MEJORADAS
# ============================================
def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convertir fechas
                for gasto in data['gastos']:
                    gasto['fecha'] = datetime.fromisoformat(gasto['fecha'])
                return data
        except:
            return {'gastos': [], 'presupuestos': PRESUPUESTOS, 'metas': []}
    return {'gastos': [], 'presupuestos': PRESUPUESTOS, 'metas': []}

def guardar_datos(data):
    # Convertir fechas a string
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
    restante = PRESUPUESTO_TOTAL - total
    porcentaje = (total / PRESUPUESTO_TOTAL) * 100 if PRESUPUESTO_TOTAL > 0 else 0
    return total, restante, porcentaje

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
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff, #e2e8f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    
    .metric-value.warning {
        background: linear-gradient(135deg, #ef4444, #f87171);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
    
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(148,163,184,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# INTERFAZ PRINCIPAL
# ============================================

# Título
st.markdown("""
<div class="title-container">
    <div class="main-title">Control de Gastos PRO</div>
    <div class="sub-title">Ing. Roberto Villarreal · Plan Maestro 2026</div>
</div>
""", unsafe_allow_html=True)

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
    total_gastado, restante, porcentaje = calcular_totales(gastos_mes)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">💰 PRESUPUESTO</div>
            <div class="metric-value">{format_money(PRESUPUESTO_TOTAL)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">💸 GASTADO</div>
            <div class="metric-value">{format_money(total_gastado)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">⚖️ RESTANTE</div>
            <div class="metric-value {'warning' if restante < 0 else ''}">{format_money(restante)}</div>
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
                            color_discrete_sequence=px.colors.sequential.Blues_r)
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin gastos este mes")
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
                            markers=True, line_shape='spline')
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin datos diarios")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Barra de progreso
    st.markdown(f"""
    <div class="chart-container">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span>Progreso mensual: {porcentaje:.1f}%</span>
            <span>{format_money(total_gastado)} de {format_money(PRESUPUESTO_TOTAL)}</span>
        </div>
        <div style="height: 20px; background: rgba(226,232,240,0.2); border-radius: 10px; overflow: hidden;">
            <div style="height: 20px; width: {min(porcentaje, 100)}%; 
                      background: linear-gradient(90deg, {'#ef4444' if porcentaje>100 else '#f59e0b' if porcentaje>80 else '#10b981'}, 
                      {'#f87171' if porcentaje>100 else '#fbbf24' if porcentaje>80 else '#34d399'}); 
                      border-radius: 10px; transition: width 0.5s;">
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# PESTAÑA 2: GASTOS (con subcategorías)
# ============================================
with tab2:
    st.subheader("📋 Registro de Gastos")
    
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
    
    # Vista por categorías
    st.subheader("📊 Detalle por Categoría")
    
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
                
                progreso = min(gastado / presupuesto['monto'], 1.0) if presupuesto['monto'] > 0 else 0
                color = '#ef4444' if (gastado / presupuesto['monto']) > 1.0 else '#f59e0b' if (gastado / presupuesto['monto']) > 0.8 else '#10b981'
                
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
# PESTAÑA 3: ANÁLISIS AVANZADO
# ============================================
with tab3:
    st.subheader("📈 Análisis Avanzado")
    
    # Selector de rango
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha inicio", 
                                     datetime.now().replace(day=1, month=1))
    with col2:
        fecha_fin = st.date_input("Fecha fin", datetime.now())
    
    if fecha_inicio and fecha_fin:
        # Filtrar gastos por rango
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
            st.info("No hay gastos en el período seleccionado")

# ============================================
# PESTAÑA 4: METAS DE AHORRO
# ============================================
with tab4:
    st.subheader("🎯 Metas de Ahorro")
    
    # Formulario para nueva meta
    with st.expander("➕ NUEVA META"):
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
                
                st.session_state.datos['metas'].append({
                    'nombre': nombre_meta,
                    'monto_objetivo': monto_meta,
                    'fecha_limite': fecha_meta.isoformat(),
                    'progreso': 0
                })
                guardar_datos(st.session_state.datos)
                st.success("Meta creada")
                st.rerun()
    
    # Mostrar metas
    if 'metas' in st.session_state.datos and st.session_state.datos['metas']:
        for meta in st.session_state.datos['metas']:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{meta['nombre']}**")
                    st.caption(f"Límite: {meta['fecha_limite']}")
                with col2:
                    st.markdown(f"**${meta['monto_objetivo']:,.0f}**")
                with col3:
                    if st.button("🗑️", key=f"del_{meta['nombre']}"):
                        st.session_state.datos['metas'].remove(meta)
                        guardar_datos(st.session_state.datos)
                        st.rerun()
                
                # Barra de progreso simulada
                st.progress(0.3)
                st.divider()
    else:
        st.info("No hay metas de ahorro configuradas")

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

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    <p>📧 contacto@optipension73.com · 📱 871 579 1810</p>
    <p>⚡ Versión Personal PRO · Todas las funciones · Datos locales</p>
    <p>© 2026 · OptiPensión 73</p>
</div>
""", unsafe_allow_html=True)
