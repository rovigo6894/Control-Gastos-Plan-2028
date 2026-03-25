import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="Control Gastos PRO", layout="wide")

st.title("💰 CONTROL DE GASTOS PRO")
st.markdown("Sistema avanzado de control financiero personal")
st.divider()

PRESUPUESTO = {
    "Alimentación - Casa": 2250,
    "Alimentación - Salidas": 4450,
    "Cena ligera": 1200,
    "Internet": 600,
    "Luz": 450,
    "Agua": 200,
    "Celular": 200,
    "Gas": 100,
    "Mantenimiento": 1400,
    "Transporte": 750,
    "Ahorro": 1500
}

ARCHIVO = "gastos_pro.csv"

# =============================
# FUNCIONES
# =============================

def cargar():
    if os.path.exists(ARCHIVO):
        df = pd.read_csv(ARCHIVO)
        df["fecha"] = pd.to_datetime(df["fecha"])
        return df
    return pd.DataFrame(columns=["fecha", "rubro", "monto", "tipo"])


def guardar(df):
    df.to_csv(ARCHIVO, index=False)


# =============================
# INICIO
# =============================

df = cargar()

# =============================
# REGISTRO
# =============================

st.subheader("📥 Registrar movimiento")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    fecha = st.date_input("Fecha", datetime.now())

with col2:
    rubro = st.selectbox("Rubro", list(PRESUPUESTO.keys()))

with col3:
    tipo = st.selectbox("Tipo", ["Gasto", "Corrección"])

with col4:
    monto = st.number_input("Monto", step=10.0)

with col5:
    st.write("")
    st.write("")
    if st.button("Agregar"):
        if tipo == "Gasto" and monto < 0:
            st.warning("Un gasto no puede ser negativo")
        elif monto != 0:
            nuevo = pd.DataFrame([{
                "fecha": fecha,
                "rubro": rubro,
                "monto": monto,
                "tipo": tipo
            }])
            df = pd.concat([df, nuevo], ignore_index=True)
            guardar(df)
            st.success("Guardado")
            st.rerun()

st.divider()

# =============================
# FILTROS
# =============================

st.subheader("🔍 Filtros")

colf1, colf2 = st.columns(2)

with colf1:
    inicio = st.date_input("Desde", datetime.now().replace(day=1))

with colf2:
    fin = st.date_input("Hasta", datetime.now())

if not df.empty:
    df_filtrado = df[(df["fecha"] >= pd.to_datetime(inicio)) & (df["fecha"] <= pd.to_datetime(fin))]
else:
    df_filtrado = df

# =============================
# TABLA
# =============================

if not df_filtrado.empty:
    df_filtrado = df_filtrado.sort_values(by="fecha", ascending=False)
    st.dataframe(df_filtrado, use_container_width=True)

# =============================
# ANALISIS
# =============================

st.subheader("📊 Análisis")

if not df_filtrado.empty:
    resumen = df_filtrado.groupby("rubro")["monto"].sum().reset_index()
    resumen["presupuesto"] = resumen["rubro"].map(PRESUPUESTO)
    resumen["disponible"] = resumen["presupuesto"] - resumen["monto"]

    total = df_filtrado["monto"].sum()
    dias = datetime.now().day
    proyeccion = (total / dias) * 30

    colm1, colm2 = st.columns(2)

    with colm1:
        st.metric("Total gastado", f"${total:,.2f}")

    with colm2:
        st.metric("Proyección mensual", f"${proyeccion:,.2f}")

    # GRAFICAS
    fig1 = px.pie(resumen, names="rubro", values="monto", title="Distribución")
    st.plotly_chart(fig1, use_container_width=True)

    gastos_dia = df_filtrado.groupby("fecha")["monto"].sum().reset_index()
    fig2 = px.line(gastos_dia, x="fecha", y="monto", title="Tendencia diaria")
    st.plotly_chart(fig2, use_container_width=True)

    # ALERTAS
    for _, row in resumen.iterrows():
        if row["disponible"] < 0:
            st.error(f"Exceso en {row['rubro']}")

# =============================
# BOTONES
# =============================

st.divider()

colb1, colb2 = st.columns(2)

with colb1:
    if st.button("Reiniciar datos"):
        df = pd.DataFrame(columns=df.columns)
        guardar(df)
        st.rerun()

with colb2:
    if st.button("Exportar Excel"):
        df.to_excel("gastos_pro.xlsx", index=False)
        st.success("Exportado")

st.divider()

st.markdown("""
### 🎯 Mentalidad PRO
- Control diario
- Decisiones conscientes
- Visión a largo plazo
""")
