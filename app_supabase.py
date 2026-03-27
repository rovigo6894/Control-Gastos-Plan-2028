import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import json
from supabase import create_client, Client

st.set_page_config(page_title="Control Financiero PRO", layout="wide", page_icon="💰")

# ============================================
# CONFIGURACIÓN
# ============================================
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("""
    ❌ Error de configuración
    
    Agrega en Render (Environment):
    - SUPABASE_URL = https://ccudouinpjizoriqyvsj.supabase.co
    - SUPABASE_KEY = (tu anon key)
    """)
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

PASSWORD = "1234"

# ============================================
# FUNCIONES
# ============================================
def cargar_categorias():
    try:
        response = supabase.table("categorias").select("*").execute()
        categorias = {}
        for cat in response.data:
            nombre = cat["nombre"]
            presupuesto = cat["presupuesto"]
            subcategorias = cat["subcategorias"]
            # Si es string, convertirlo a lista
            if isinstance(subcategorias, str):
                try:
                    subcategorias = json.loads(subcategorias)
                except:
                    subcategorias = ["General"]
            categorias[nombre] = {
                "presupuesto": presupuesto,
                "subcategorias": subcategorias
            }
        return categorias
    except Exception as e:
        st.error(f"Error al cargar categorías: {e}")
        return {}

def cargar_gastos():
    try:
        response = supabase.table("gastos").select("*").order("fecha", desc=True).execute()
        df = pd.DataFrame(response.data)
        if not df.empty:
            df["fecha"] = pd.to_datetime(df["fecha"])
        return df
    except Exception as e:
        st.error(f"Error al cargar gastos: {e}")
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
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

def eliminar_gasto(id_gasto):
    try:
        supabase.table("gastos").delete().eq("id", id_gasto).execute()
        return True
    except Exception as e:
        st.error(f"Error al eliminar: {e}")
        return False

# ============================================
# LOGIN
# ============================================
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
            st.error("Contraseña incorrecta")
    st.stop()

# Cargar datos
categorias = cargar_categorias()
df = cargar_gastos()
total_presupuesto = sum(c["presupuesto"] for c in categorias.values())

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.title("💰 Control PRO")
    
    pagina = st.radio("📌 Navegación", ["📊 Dashboard", "📝 Registrar", "📋 Historial"])
    st.session_state.pagina = pagina
    
    st.divider()
    
    if not df.empty:
        hoy = datetime.now()
        df_mes = df[(df["fecha"].dt.year == hoy.year) & (df["fecha"].dt.month == hoy.month)]
        gasto_mes = df_mes["monto"].sum()
        st.metric("📅 Gasto del mes", f"${gasto_mes:,.0f}")
        if total_presupuesto > 0:
            st.progress(min(gasto_mes / total_presupuesto, 1.0))

# ============================================
# DASHBOARD
# ============================================
if st.session_state.pagina == "📊 Dashboard":
    st.title("📊 Dashboard Financiero")
    
    if not df.empty and categorias:
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
            if not evolucion.empty:
                fig = px.line(evolucion, x="mes", y="monto", markers=True)
                st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🚨 Alertas")
        alertas = False
        for _, row in resumen.iterrows():
            presupuesto = categorias.get(row["rubro"], {}).get("presupuesto", 0)
            if presupuesto > 0:
                pct = (row["monto"] / presupuesto * 100)
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

# ============================================
# REGISTRAR
# ============================================
elif st.session_state.pagina == "📝 Registrar":
    st.title("📝 Registrar gasto")
    
    if not categorias:
        st.error("❌ No hay categorías. Verifica la conexión con Supabase.")
        st.stop()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
        rubro = st.selectbox("Categoría", list(categorias.keys()))
        subcategorias = categorias[rubro]["subcategorias"]
        subcategoria = st.selectbox("Subcategoría", subcategorias)
        
    with col2:
        monto = st.number_input("Monto ($)", step=10.0, min_value=0.0, format="%.2f")
        descripcion = st.text_area("Descripción", placeholder="Ej: Supermercado", height=100)
    
    if st.button("💾 Guardar", type="primary", use_container_width=True):
        if monto > 0:
            if guardar_gasto(fecha.strftime("%Y-%m-%d"), rubro, subcategoria, monto, descripcion):
                st.success(f"✅ Guardado: {rubro} → {subcategoria} | ${monto:,.2f}")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Error al guardar")
        else:
            st.warning("Ingresa un monto válido")

# ============================================
# HISTORIAL
# ============================================
elif st.session_state.pagina == "📋 Historial":
    st.title("📋 Historial")
    
    if not df.empty:
        for _, row in df.sort_values("fecha", ascending=False).iterrows():
            with st.expander(f"📅 {row['fecha'].strftime('%d/%m/%Y')} - {row['rubro']} - ${row['monto']:,.0f}"):
                st.write(f"**Subcategoría:** {row['subcategoria']}")
                st.write(f"**Descripción:** {row['descripcion']}")
                if st.button(f"🗑️ Eliminar", key=f"del_{row['id']}"):
                    if eliminar_gasto(row["id"]):
                        st.success("✅ Eliminado")
                        st.rerun()
        
        if st.button("📁 Exportar CSV"):
            csv = df.to_csv(index=False)
            st.download_button("Descargar", csv, "gastos.csv", "text/csv")
    else:
        st.info("No hay gastos")

st.caption("💰 Control Financiero PRO | Datos en Supabase")
