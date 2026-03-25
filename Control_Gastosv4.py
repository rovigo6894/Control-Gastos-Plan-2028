import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Control Financiero V8 PRO", layout="centered")

# =============================
# CONFIG
# =============================
PRESUPUESTO_TOTAL = 13100
PRESUPUESTO = {
    "Alimentación": 7900,
    "Servicios": 1550,
    "Vivienda": 1400,
    "Transporte": 750,
    "Ahorro": 1500
}

PASSWORD = "1234"

# =============================
# LOGIN
# =============================
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

# =============================
# GOOGLE SHEETS
# =============================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)

client = gspread.authorize(credentials)
sheet = client.open("Control_Gastos").sheet1

# =============================
# CARGAR DATOS
# =============================

def cargar():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def guardar(fila):
    sheet.append_row(fila)

# =============================
# DATA
# =============================
df = cargar()

st.title("💰 Control Financiero V8 PRO")
st.caption("Sistema móvil con nube + inteligencia financiera")

# =============================
# KPIs (MÓVIL)
# =============================
if not df.empty:
    total = df["monto"].sum()
    dias = datetime.now().day
    proyeccion = (total / dias) * 30
    restante = PRESUPUESTO_TOTAL - total

    st.metric("💸 Gastado", f"${total:,.0f}")
    st.metric("📈 Proyección", f"${proyeccion:,.0f}")
    st.metric("💰 Disponible", f"${restante:,.0f}")

st.divider()

# =============================
# INPUT MÓVIL
# =============================
st.subheader("➕ Registrar gasto")

fecha = st.date_input("Fecha", datetime.now())
rubro = st.selectbox("Categoría", list(PRESUPUESTO.keys()))
monto = st.number_input("Monto", step=10.0)

if st.button("Guardar"):
    if monto > 0:
        guardar([
            fecha.strftime("%Y-%m-%d"),
            rubro,
            monto
        ])
        st.success("Guardado en la nube")
        st.rerun()

st.divider()

# =============================
# ANALISIS
# =============================
if not df.empty:
    resumen = df.groupby("rubro")["monto"].sum().reset_index()
    resumen["presupuesto"] = resumen["rubro"].map(PRESUPUESTO)
    resumen["uso %"] = (resumen["monto"] / resumen["presupuesto"] * 100)

    st.subheader("🧠 Diagnóstico")

    top = resumen.sort_values(by="uso %", ascending=False).iloc[0]

    if top["uso %"] > 100:
        st.error(f"Exceso en {top['rubro']}")
    elif top["uso %"] > 80:
        st.warning(f"Cuidado con {top['rubro']}")
    else:
        st.success("Buen control")

    # GRÁFICA SIMPLE MÓVIL
    fig = px.pie(resumen, names="rubro", values="monto")
    st.plotly_chart(fig, use_container_width=True)

    # HISTORIAL SIMPLE
    st.subheader("📋 Movimientos")
    st.dataframe(df.sort_values(by="fecha", ascending=False), use_container_width=True)

st.divider()
st.caption("V8 PRO: Sistema en la nube + optimizado para celular")
