import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from supabase import create_client, Client

st.set_page_config(page_title="Control Financiero PRO", layout="wide", page_icon="💰")

# Configuración Supabase
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY", ""))

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Configuración de Supabase no encontrada")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

PASSWORD = "1234"

def cargar_categorias():
    try:
        response = supabase.table("categorias").select("*").execute()
        return {cat["nombre"]: {"presupuesto": cat["presupuesto"], "subcategorias": cat["subcategorias"]} for cat in response.data}
    except:
        return {}

def cargar_gastos():
    try:
        response = supabase.table("gastos").select("*").order("fecha", desc=True).execute()
        df = pd.DataFrame(response.data)
        if not df.empty:
            df["fecha"] = pd.to_datetime(df["fecha"])
        return df
    except:
        return pd.DataFrame()

def guardar_gasto(fecha, rubro, subcategoria, monto, descripcion):
    try:
        supabase.table("gastos").insert({
            "fecha": fecha,
            "rubro": rubro,
            "subcategoria": subcategoria,
            "monto": monto,
            "descripcion": descripcion
        }).execute()
        return True
    except:
        return False

def eliminar_gasto(id_gasto):
    try:
        supabase.table("gastos").delete().eq("id", id_gasto).execute()
        return True
    except:
        return False

def actualizar_gasto(id_gasto, fecha, rubro, subcategoria, monto, descripcion):
    try:
        supabase.table("gastos").update({
            "fecha": fecha,
            "rubro": rubro,
            "subcategoria": subcategoria,
            "monto": monto,
            "descripcion": descripcion
        }).eq("id", id_gasto).execute()
        return True
    except:
        return False

# Login
if "auth" not in st.session_state:
    st.session_state.auth = False
if "pagina" not in st.session_state:
    st.session_state.pagina = "dashboard"

if not st.session_state.auth:
    st.title("💰 Control Financiero PRO")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta")
    st.stop()

# Cargar datos
categorias = cargar_categorias()
df = cargar_gastos()
total_presupuesto = sum(c["presupuesto"] for c in categorias.values())

# Sidebar
with st.sidebar:
    st.title("💰 Control PRO")
    pagina = st.radio("📌 Navegación", ["Dashboard", "Registrar", "Historial"])
    st.session_state.pagina = pagina
    
    if not df.empty:
        hoy = datetime.now()
        df_mes = df[(df["fecha"].dt.year == hoy.year) & (df["fecha"].dt.month == hoy.month)]
        gasto_mes = df_mes["monto"].sum()
        st.metric("📅 Gasto del mes", f"${gasto_mes:,.0f}")
        porcentaje = (gasto_mes / total_presupuesto * 100) if total_presupuesto > 0 else 0
        st.progress(min(porcentaje / 100, 1.0))

# Dashboard
if st.session_state.pagina == "Dashboard":
    st.title("📊 Dashboard Financiero")
    
    if not df.empty:
        hoy = datetime.now()
        df_mes = df[(df["fecha"].dt.year == hoy.year) & (df["fecha"].dt.month == hoy.month)]
        gasto_mes = df_mes["monto"].sum()
        restante = total_presupuesto - gasto_mes
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💸 Gasto del mes", f"${gasto_mes:,.0f}")
        col2.metric("💰 Restante", f"${restante:,.0f}")
        col3.metric("🎯 Presupuesto", f"${total_presupuesto:,.0f}")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🥧 Distribución")
            resumen = df_mes.groupby("rubro")["monto"].sum().reset_index()
            if not resumen.empty:
                fig = px.pie(resumen, names="rubro", values="monto", hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Evolución")
            df["mes"] = df["fecha"].dt.to_period("M").astype(str)
            evolucion = df.groupby("mes")["monto"].sum().reset_index()
            fig = px.line(evolucion, x="mes", y="monto", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🚨 Alertas")
        alertas = False
        for _, row in resumen.iterrows():
            presupuesto = categorias.get(row["rubro"], {}).get("presupuesto", 0)
            if presupuesto > 0:
                pct = row["monto"] / presupuesto * 100
                if pct > 100:
                    st.error(f"⚠️ EXCESO en {row['rubro']}: {pct:.0f}%")
                    alertas = True
                elif pct > 80:
                    st.warning(f"📌 ALERTA en {row['rubro']}: {pct:.0f}%")
                    alertas = True
        if not alertas:
            st.success("✅ Todo en orden")
    else:
        st.info("📝 No hay gastos registrados")

# Registrar
elif st.session_state.pagina == "Registrar":
    st.title("📝 Registrar gasto")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
        rubro = st.selectbox("Categoría", list(categorias.keys()))
        subcategorias = categorias[rubro]["subcategorias"]
        subcategoria = st.selectbox("Subcategoría", subcategorias)
    with col2:
        monto = st.number_input("Monto ($)", step=10.0, min_value=0.0)
        descripcion = st.text_area("Descripción")
    
    if st.button("💾 Guardar", type="primary"):
        if monto > 0:
            if guardar_gasto(fecha.strftime("%Y-%m-%d"), rubro, subcategoria, monto, descripcion):
                st.success("✅ Guardado")
                st.rerun()
            else:
                st.error("❌ Error")

# Historial
elif st.session_state.pagina == "Historial":
    st.title("📋 Historial")
    
    if not df.empty:
        for idx, row in df.sort_values("fecha", ascending=False).iterrows():
            with st.expander(f"📅 {row['fecha'].strftime('%d/%m/%Y')} - {row['rubro']} - ${row['monto']:,.0f}"):
                st.write(f"**Subcategoría:** {row['subcategoria']}")
                st.write(f"**Descripción:** {row['descripcion']}")
                if st.button(f"🗑️ Eliminar", key=f"del_{row['id']}"):
                    if eliminar_gasto(row["id"]):
                        st.success("✅ Eliminado")
                        st.rerun()
        
        if st.button("📁 Descargar CSV"):
            csv = df.to_csv(index=False)
            st.download_button("✅ Descargar", csv, "gastos.csv", "text/csv")
    else:
        st.info("No hay gastos")

st.caption("💰 Control Financiero PRO | Datos en Supabase")
