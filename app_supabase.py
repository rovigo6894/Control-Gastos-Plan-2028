import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from supabase import create_client, Client

st.set_page_config(page_title="Control Financiero PRO", layout="wide", page_icon="💰")

# ============================================
# LEER VARIABLES DESDE ARCHIVO .ENV
# ============================================
def cargar_env():
    """Lee las variables del archivo .env en /etc/secrets/"""
    env_path = "/etc/secrets/.env"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value

cargar_env()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("""
    ❌ **Error de configuración**
    
    No se encontraron las variables SUPABASE_URL y SUPABASE_KEY.
    
    **En Render, asegúrate de:**
    1. Ir a Environment → Secret Files
    2. Crear un archivo llamado `.env`
    3. Contenido:
       SUPABASE_URL=https://ccudouinpjizoriqyvsj.supabase.co
       SUPABASE_KEY=sb_publitasble_IdtoSzhv3L6TGoS_8-C9XA_ZFbMC__
    4. Guardar y hacer deploy
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
        if response.data:
            return {cat["nombre"]: {"presupuesto": cat["presupuesto"], "subcategorias": cat["subcategorias"]} for cat in response.data}
        return {}
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
    st.markdown("### Sistema de gestión financiera con Supabase")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Entrar", use_container_width=True):
        if pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta")
    st.stop()

# ============================================
# CARGAR DATOS
# ============================================
categorias = cargar_categorias()
df = cargar_gastos()
total_presupuesto = sum(c["presupuesto"] for c in categorias.values())

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.title("💰 Control PRO")
    
    pagina = st.radio("📌 Navegación", [
        "📊 Dashboard", 
        "📝 Registrar", 
        "📋 Historial"
    ])
    st.session_state.pagina = pagina
    
    st.divider()
    
    if not df.empty:
        hoy = datetime.now()
        df_mes = df[(df["fecha"].dt.year == hoy.year) & (df["fecha"].dt.month == hoy.month)]
        gasto_mes = df_mes["monto"].sum()
        st.metric("📅 Gasto del mes", f"${gasto_mes:,.0f}")
        
        if total_presupuesto > 0:
            porcentaje = (gasto_mes / total_presupuesto * 100)
            st.progress(min(porcentaje / 100, 1.0))
            st.caption(f"{porcentaje:.0f}% usado")

# ============================================
# DASHBOARD
# ============================================
if st.session_state.pagina == "📊 Dashboard":
    st.title("📊 Dashboard Financiero")
    
    if not df.empty:
        hoy = datetime.now()
        df_mes = df[(df["fecha"].dt.year == hoy.year) & (df["fecha"].dt.month == hoy.month)]
        gasto_mes = df_mes["monto"].sum()
        restante = total_presupuesto - gasto_mes if total_presupuesto > 0 else 0
        
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
            st.subheader("📈 Evolución mensual")
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
                    st.error(f"⚠️ EXCESO en {row['rubro']}: ${row['monto']:,.0f} / ${presupuesto:,.0f} ({pct:.0f}%)")
                    alertas = True
                elif pct > 80:
                    st.warning(f"📌 ALERTA en {row['rubro']}: ${row['monto']:,.0f} / ${presupuesto:,.0f} ({pct:.0f}%)")
                    alertas = True
        if not alertas:
            st.success("✅ Todo en orden")
    else:
        st.info("📝 No hay gastos registrados. Ve a la pestaña Registrar.")

# ============================================
# REGISTRAR GASTO
# ============================================
elif st.session_state.pagina == "📝 Registrar":
    st.title("📝 Registrar nuevo gasto")
    
    if not categorias:
        st.error("❌ No hay categorías disponibles. Verifica la conexión con Supabase.")
        st.stop()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("📅 Fecha", datetime.now())
        rubro = st.selectbox("📂 Categoría", list(categorias.keys()))
        subcategorias = categorias[rubro]["subcategorias"]
        subcategoria = st.selectbox("🏷️ Subcategoría", subcategorias)
        
    with col2:
        monto = st.number_input("💰 Monto ($)", step=10.0, min_value=0.0, format="%.2f")
        descripcion = st.text_area("📝 Descripción", placeholder="Ej: Compras del supermercado", height=100)
    
    if st.button("💾 Guardar gasto", type="primary", use_container_width=True):
        if monto > 0:
            if guardar_gasto(fecha.strftime("%Y-%m-%d"), rubro, subcategoria, monto, descripcion):
                st.success(f"✅ Guardado: {rubro} → {subcategoria} | ${monto:,.2f}")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Error al guardar en Supabase")
        else:
            st.warning("⚠️ Ingresa un monto válido")

# ============================================
# HISTORIAL
# ============================================
elif st.session_state.pagina == "📋 Historial":
    st.title("📋 Historial completo")
    
    if not df.empty:
        for idx, row in df.sort_values("fecha", ascending=False).iterrows():
            with st.expander(f"📅 {row['fecha'].strftime('%d/%m/%Y')} - {row['rubro']} - {row['subcategoria']} - ${row['monto']:,.0f}"):
                st.write(f"**Descripción:** {row['descripcion']}")
                if st.button(f"🗑️ Eliminar", key=f"del_{row['id']}"):
                    if eliminar_gasto(row["id"]):
                        st.success("✅ Gasto eliminado")
                        st.rerun()
        
        st.divider()
        if st.button("📁 Exportar a CSV", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button(
                label="✅ Descargar CSV",
                data=csv,
                file_name=f"gastos_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No hay gastos registrados")

st.divider()
st.caption("💰 Control Financiero PRO | Datos en Supabase | Nunca se pierden")
