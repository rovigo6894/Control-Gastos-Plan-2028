import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# ============================================
# CONFIGURACIÓN
# ============================================
st.set_page_config(page_title="💰 Control de Gastos", layout="centered")

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
# DATOS
# ============================================
PRESUPUESTOS = {
    'Alimentación': {
        'total': 7900,
        'subs': ['Desayuno', 'Comida', 'Cena']
    },
    'Servicios': {
        'total': 1550,
        'subs': ['Internet', 'Luz', 'Agua']
    },
    'Vivienda': {
        'total': 2150,
        'subs': ['Mantenimiento', 'Transporte']
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

# ============================================
# TÍTULO
# ============================================
st.title("💰 CONTROL DE GASTOS")
st.caption("Ing. Roberto Villarreal")

# ============================================
# MÉTRICAS
# ============================================
total_gastado = sum(g['monto'] for g in st.session_state.gastos) if st.session_state.gastos else 0
restante = PRESUPUESTO_TOTAL - total_gastado
porcentaje = (total_gastado / PRESUPUESTO_TOTAL) * 100

col1, col2, col3 = st.columns(3)
col1.metric("PRESUPUESTO", f"${PRESUPUESTO_TOTAL:,.0f}")
col2.metric("GASTADO", f"${total_gastado:,.0f}", f"{porcentaje:.1f}%")
col3.metric("RESTANTE", f"${restante:,.0f}")

# ============================================
# BARRA DE PROGRESO
# ============================================
st.progress(min(porcentaje/100, 1.0), text=f"Progreso: {porcentaje:.1f}%")

# ============================================
# FORMULARIO - TODO DENTRO DEL MISMO FORM
# ============================================
st.subheader("➕ AGREGAR / CORREGIR GASTO")

with st.form("formulario_gastos"):
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
        categoria = st.selectbox("Categoría", list(PRESUPUESTOS.keys()))
    
    with col2:
        monto = st.number_input("Monto $", value=100, step=10)
        descripcion = st.text_input("Descripción")
    
    # SUBCATEGORÍA - DENTRO DEL FORM, DESPUÉS DE CATEGORÍA
    subcategorias = PRESUPUESTOS[categoria]['subs']
    subcategoria = st.selectbox("Subcategoría", subcategorias)
    
    # Mostrar límite (opcional)
    st.caption(f"Límite de {subcategoria}: ${PRESUPUESTOS[categoria]['total']/len(subcategorias):,.0f}")
    
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
            st.success("✅ Guardado")
            st.rerun()

# ============================================
# MOSTRAR GASTOS
# ============================================
if st.session_state.gastos:
    st.subheader("📋 ÚLTIMOS GASTOS")
    df = pd.DataFrame(st.session_state.gastos[-10:][::-1])
    st.dataframe(df, use_container_width=True)

# ============================================
# REINICIAR
# ============================================
if st.button("🗑️ REINICIAR", use_container_width=True):
    st.session_state.gastos = []
    guardar_gastos([])
    st.rerun()
