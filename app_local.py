import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="Control Financiero", layout="wide")

PASSWORD = "1234"

PRESUPUESTOS = {
    "Alimentación": 7900,
    "Servicios": 1550,
    "Vivienda": 1400,
    "Transporte": 750,
    "Ahorro": 1500,
    "Salud": 800,
    "Educación": 600,
    "Entretenimiento": 500
}

SUBCATEGORIAS = {
    "Alimentación": ["Despensa", "Comida fuera", "Antojos", "Bebidas", "Café"],
    "Servicios": ["Luz", "Agua", "Gas", "Internet", "Teléfono"],
    "Vivienda": ["Renta", "Mantenimiento", "Artículos hogar", "Limpiadores"],
    "Transporte": ["Gasolina", "Mantenimiento auto", "Pasajes", "Estacionamiento"],
    "Ahorro": ["Ahorro mensual", "Fondo emergencia", "Inversiones"],
    "Salud": ["Farmacia", "Consultas", "Medicamentos", "Seguro"],
    "Educación": ["Colegiaturas", "Libros", "Material", "Cursos"],
    "Entretenimiento": ["Cine", "Restaurantes", "Hobbies", "Suscripciones"]
}

ARCHIVO = "gastos.csv"

def cargar_gastos():
    if os.path.exists(ARCHIVO):
        df = pd.read_csv(ARCHIVO)
        df["fecha"] = pd.to_datetime(df["fecha"])
        return df
    return pd.DataFrame(columns=["fecha", "rubro", "subcategoria", "monto"])

def guardar_gasto(fecha, rubro, subcategoria, monto):
    df = cargar_gastos()
    nueva_fila = pd.DataFrame([[fecha, rubro, subcategoria, monto]], 
                               columns=["fecha", "rubro", "subcategoria", "monto"])
    df = pd.concat([df, nueva_fila], ignore_index=True)
    df.to_csv(ARCHIVO, index=False)

def eliminar_ultimo():
    df = cargar_gastos()
    if not df.empty:
        df = df.iloc[:-1]
        df.to_csv(ARCHIVO, index=False)

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

df = cargar_gastos()
total_presupuesto = sum(PRESUPUESTOS.values())

st.title("💰 Control Financiero PRO")

if not df.empty:
    total = df["monto"].sum()
    restante = total_presupuesto - total
    col1, col2 = st.columns(2)
    col1.metric("💸 Gastado", f"${total:,.0f}")
    col2.metric("💰 Presupuesto restante", f"${restante:,.0f}")

st.divider()

tab1, tab2, tab3 = st.tabs(["📝 Registrar", "📊 Análisis", "📋 Historial"])

with tab1:
    st.subheader("➕ Nuevo gasto")
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
        rubro = st.selectbox("Categoría", list(PRESUPUESTOS.keys()))
        subcategoria = st.selectbox("Subcategoría", SUBCATEGORIAS[rubro])
    with col2:
        monto = st.number_input("Monto ($)", step=10.0, min_value=0.0, format="%.2f")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Guardar", type="primary", use_container_width=True):
            if monto > 0:
                guardar_gasto(fecha.strftime("%Y-%m-%d"), rubro, subcategoria, monto)
                st.success(f"✅ Guardado: {rubro} → {subcategoria} | ${monto:,.2f}")
                st.rerun()
            else:
                st.warning("Ingresa un monto válido")
    with col2:
        if st.button("🗑️ Eliminar último", use_container_width=True):
            eliminar_ultimo()
            st.warning("Último gasto eliminado")
            st.rerun()

with tab2:
    if not df.empty:
        resumen = df.groupby("rubro")["monto"].sum().reset_index()
        fig = px.pie(resumen, names="rubro", values="monto", title="Distribución de gastos")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📊 Estado por categoría")
        for _, row in resumen.iterrows():
            presupuesto = PRESUPUESTOS[row["rubro"]]
            porcentaje = (row["monto"] / presupuesto * 100)
            if porcentaje > 100:
                st.error(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${presupuesto:,.0f} ({porcentaje:.0f}%) 🔴")
            elif porcentaje > 80:
                st.warning(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${presupuesto:,.0f} ({porcentaje:.0f}%) 🟡")
            else:
                st.success(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${presupuesto:,.0f} ({porcentaje:.0f}%) 🟢")
    else:
        st.info("No hay gastos registrados aún")

with tab3:
    if not df.empty:
        st.dataframe(df.sort_values("fecha", ascending=False), use_container_width=True)
        if st.button("📁 Descargar respaldo (CSV)"):
            csv = df.to_csv(index=False)
            st.download_button("✅ Descargar", csv, f"gastos_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    else:
        st.info("No hay gastos registrados")

st.divider()
st.caption("💰 Datos guardados localmente | 8 categorías | Subcategorías ampliadas")
