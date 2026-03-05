import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
# DATOS DE PRESUPUESTOS
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
# INICIALIZAR SESSION STATE
# ============================================
if 'gastos' not in st.session_state:
    st.session_state.gastos = cargar_gastos()

# ============================================
# FUNCIONES DE AYUDA
# ============================================
def obtener_subcategorias(categoria):
    return list(PRESUPUESTOS[categoria]['subcategorias'].keys())

# ============================================
# TÍTULO
# ============================================
st.title("💰 CONTROL DE GASTOS PRO")
st.caption("Ing. Roberto Villarreal · Plan Maestro 2026")

# ============================================
# MÉTRICAS
# ============================================
gastos_mes = [g for g in st.session_state.gastos]
total_gastado = sum(g['monto'] for g in gastos_mes) if gastos_mes else 0
restante = PRESUPUESTO_TOTAL - total_gastado
porcentaje = (total_gastado / PRESUPUESTO_TOTAL) * 100

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 PRESUPUESTO", f"${PRESUPUESTO_TOTAL:,.0f}")
with col2:
    st.metric("💸 GASTADO", f"${total_gastado:,.0f}", f"{porcentaje:.1f}%")
with col3:
    delta_color = "inverse" if restante < 0 else "normal"
    st.metric("⚖️ RESTANTE", f"${restante:,.0f}", delta_color=delta_color)

# ============================================
# BARRA DE PROGRESO
# ============================================
st.progress(min(porcentaje/100, 1.0), text=f"Progreso: {porcentaje:.1f}%")

# ============================================
# FORMULARIO CON SUBCATEGORÍAS DINÁMICAS
# ============================================
st.subheader("➕ AGREGAR / CORREGIR GASTO")

with st.form("nuevo_gasto"):
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("📅 Fecha", datetime.now())
        categoria = st.selectbox(
            "📁 Categoría", 
            list(PRESUPUESTOS.keys()),
            key='categoria_form'
        )
    
    with col2:
        monto = st.number_input("💰 Monto $ (negativo para corregir)", value=100, step=10)
        descripcion = st.text_input("📝 Descripción")
    
    # SUBCATEGORÍAS DINÁMICAS - Se actualizan con cada cambio de categoría
    subcategorias = obtener_subcategorias(categoria)
    subcategoria = st.selectbox("📂 Subcategoría", subcategorias, key='subcategoria_form')
    
    # Mostrar descripción de la subcategoría seleccionada
    desc_sub = PRESUPUESTOS[categoria]['subcategorias'][subcategoria]['descripcion']
    if desc_sub:
        st.info(f"ℹ️ {desc_sub}")
    
    if monto < 0:
        st.warning("⚠️ Estás restando dinero (corrección)")
    
    if st.form_submit_button("💾 GUARDAR GASTO", use_container_width=True):
        if fecha and categoria and subcategoria and monto != 0:
            nuevo_gasto = {
                'fecha': fecha.strftime('%Y-%m-%d'),
                'categoria': categoria,
                'subcategoria': subcategoria,
                'descripcion': descripcion if descripcion else desc_sub,
                'monto': monto
            }
            st.session_state.gastos.append(nuevo_gasto)
            guardar_gastos(st.session_state.gastos)
            st.success("✅ Gasto guardado correctamente")
            st.rerun()

# ============================================
# ALERTAS
# ============================================
if st.session_state.gastos:
    df = pd.DataFrame(st.session_state.gastos)
    alertas = []
    
    for cat, datos in PRESUPUESTOS.items():
        gastos_cat = df[df['categoria'] == cat]['monto'].sum() if not df.empty else 0
        if gastos_cat > datos['total']:
            alertas.append(f"🔴 {cat}: +${gastos_cat - datos['total']:,.0f} (${gastos_cat:,.0f}/${datos['total']:,.0f})")
        elif gastos_cat > datos['total'] * 0.8:
            alertas.append(f"🟡 {cat}: Te quedan ${datos['total'] - gastos_cat:,.0f} (${gastos_cat:,.0f}/${datos['total']:,.0f})")
    
    if alertas:
        with st.expander("⚠️ ALERTAS DE PRESUPUESTO", expanded=True):
            for alerta in alertas:
                st.write(alerta)

# ============================================
# GRÁFICAS
# ============================================
if st.session_state.gastos:
    df = pd.DataFrame(st.session_state.gastos)
    
    tab1, tab2 = st.tabs(["📊 Por Categoría", "📈 Evolución"])
    
    with tab1:
        cat_sum = df.groupby('categoria')['monto'].sum().reset_index()
        fig = px.pie(cat_sum, values='monto', names='categoria')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        df['fecha'] = pd.to_datetime(df['fecha'])
        df_time = df.groupby('fecha')['monto'].sum().reset_index().sort_values('fecha')
        fig = px.line(df_time, x='fecha', y='monto', markers=True)
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# DETALLE POR CATEGORÍA
# ============================================
if st.session_state.gastos:
    st.subheader("📋 DETALLE POR CATEGORÍA")
    
    for cat, datos in PRESUPUESTOS.items():
        gastos_cat = df[df['categoria'] == cat]['monto'].sum() if not df.empty else 0
        
        with st.expander(f"{cat} - ${gastos_cat:,.0f} / ${datos['total']:,.0f}"):
            # Barra de progreso
            progreso_cat = min(gastos_cat / datos['total'], 1.0)
            st.progress(progreso_cat)
            
            # Subcategorías
            for sub, sub_data in datos['subcategorias'].items():
                gastos_sub = df[(df['categoria'] == cat) & (df['subcategoria'] == sub)]['monto'].sum() if not df.empty else 0
                progreso_sub = min(gastos_sub / sub_data['monto'], 1.0)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{sub}**")
                    if sub_data['descripcion']:
                        st.caption(sub_data['descripcion'])
                with col2:
                    st.write(f"${gastos_sub:,.0f} / ${sub_data['monto']:,.0f}")
                
                st.progress(progreso_sub)
                st.divider()

# ============================================
# ÚLTIMOS GASTOS
# ============================================
if st.session_state.gastos:
    st.subheader("📋 ÚLTIMOS 10 GASTOS")
    df_show = pd.DataFrame(st.session_state.gastos[-10:][::-1])
    df_show['fecha'] = pd.to_datetime(df_show['fecha']).dt.strftime('%d/%m/%Y')
    df_show['monto'] = df_show['monto'].apply(lambda x: f"${x:,.2f}")
    st.dataframe(df_show[['fecha', 'categoria', 'subcategoria', 'descripcion', 'monto']], 
                 use_container_width=True, hide_index=True)

# ============================================
# BOTÓN REINICIAR
# ============================================
col1, col2, col3 = st.columns(3)
with col2:
    if st.button("🗑️ REINICIAR DATOS", use_container_width=True):
        st.session_state.gastos = []
        guardar_gastos([])
        st.rerun()

# ============================================
# FOOTER
# ============================================
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📧 contacto@optipension73.com · 📱 871 579 1810</p>
    <p>⚡ Versión PRO · Subcategorías dinámicas · Alertas automáticas</p>
    <p>© 2026 · OptiPensión 73</p>
</div>
""", unsafe_allow_html=True)
