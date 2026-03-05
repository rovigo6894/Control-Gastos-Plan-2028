import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# ============================================
# CONFIGURACIÓN
# ============================================
st.set_page_config(page_title="💰 Control de Gastos", page_icon="💰", layout="centered")

st.title("💰 CONTROL DE GASTOS")
st.caption("Ing. Roberto Villarreal")

# ============================================
# DATOS
# ============================================
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

if 'gastos' not in st.session_state:
    st.session_state.gastos = cargar_gastos()

# ============================================
# MÉTRICAS
# ============================================
total = sum(g['monto'] for g in st.session_state.gastos) if st.session_state.gastos else 0
restante = PRESUPUESTO_TOTAL - total
porcentaje = (total / PRESUPUESTO_TOTAL) * 100

col1, col2, col3 = st.columns(3)
col1.metric("PRESUPUESTO", f"${PRESUPUESTO_TOTAL:,.0f}")
col2.metric("GASTADO", f"${total:,.0f}", f"{porcentaje:.1f}%")
col3.metric("RESTANTE", f"${restante:,.0f}")

st.progress(min(porcentaje/100, 1.0))

# ============================================
# FORMULARIO - VERSIÓN ULTRA SIMPLE
# ============================================
st.subheader("➕ AGREGAR GASTO")

with st.form("form"):
    fecha = st.date_input("Fecha", datetime.now())
    categoria = st.selectbox("Categoría", ["Alimentación", "Servicios", "Vivienda"])
    
    # SUBCATEGORÍAS - EXPLÍCITAS Y CLARAS
    if categoria == "Alimentación":
        subcategoria = st.selectbox("Subcategoría", ["Desayuno", "Comida", "Cena"])
    elif categoria == "Servicios":
        subcategoria = st.selectbox("Subcategoría", ["Internet", "Luz", "Agua"])
    else:
        subcategoria = st.selectbox("Subcategoría", ["Mantenimiento", "Transporte"])
    
    monto = st.number_input("Monto $", value=100, step=10)
    descripcion = st.text_input("Descripción")
    
    if st.form_submit_button("💾 GUARDAR"):
        st.session_state.gastos.append({
            'fecha': str(fecha),
            'categoria': categoria,
            'subcategoria': subcategoria,
            'descripcion': descripcion,
            'monto': monto
        })
        guardar_gastos(st.session_state.gastos)
        st.rerun()

# ============================================
# MOSTRAR GASTOS
# ============================================
if st.session_state.gastos:
    st.subheader("📋 GASTOS")
    df = pd.DataFrame(st.session_state.gastos[-10:][::-1])
    st.dataframe(df, use_container_width=True)

# ============================================
# REINICIAR
# ============================================
if st.button("🗑️ REINICIAR"):
    st.session_state.gastos = []
    guardar_gastos([])
    st.rerun()
