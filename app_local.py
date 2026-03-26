import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="Control Financiero PRO", layout="wide")

PASSWORD = "1234"

# Presupuestos por defecto
PRESUPUESTOS_POR_DEFECTO = {
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
PRESUP_ARCHIVO = "presupuestos.csv"

def cargar_presupuestos():
    if os.path.exists(PRESUP_ARCHIVO):
        df = pd.read_csv(PRESUP_ARCHIVO)
        return dict(zip(df["rubro"], df["monto"]))
    return PRESUPUESTOS_POR_DEFECTO.copy()

def guardar_presupuestos(presupuestos):
    df = pd.DataFrame(list(presupuestos.items()), columns=["rubro", "monto"])
    df.to_csv(PRESUP_ARCHIVO, index=False)

def cargar_gastos():
    if os.path.exists(ARCHIVO):
        df = pd.read_csv(ARCHIVO)
        df["fecha"] = pd.to_datetime(df["fecha"])
        return df
    return pd.DataFrame(columns=["id", "fecha", "rubro", "subcategoria", "monto"])

def guardar_gasto(fecha, rubro, subcategoria, monto):
    df = cargar_gastos()
    nuevo_id = df["id"].max() + 1 if not df.empty else 1
    nueva_fila = pd.DataFrame([[nuevo_id, fecha, rubro, subcategoria, monto]], 
                               columns=["id", "fecha", "rubro", "subcategoria", "monto"])
    df = pd.concat([df, nueva_fila], ignore_index=True)
    df.to_csv(ARCHIVO, index=False)

def eliminar_gasto(id_gasto):
    df = cargar_gastos()
    df = df[df["id"] != id_gasto]
    df.to_csv(ARCHIVO, index=False)

def actualizar_gasto(id_gasto, nueva_fecha, nuevo_rubro, nueva_subcategoria, nuevo_monto):
    df = cargar_gastos()
    df.loc[df["id"] == id_gasto, ["fecha", "rubro", "subcategoria", "monto"]] = [nueva_fecha, nuevo_rubro, nueva_subcategoria, nuevo_monto]
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

# Cargar datos
df = cargar_gastos()
presupuestos = cargar_presupuestos()
total_presupuesto = sum(presupuestos.values())

st.title("💰 Control Financiero PRO")

if not df.empty:
    total = df["monto"].sum()
    restante = total_presupuesto - total
    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Gastado", f"${total:,.0f}")
    col2.metric("💰 Presupuesto restante", f"${restante:,.0f}")
    porcentaje = (total / total_presupuesto * 100) if total_presupuesto > 0 else 0
    col3.metric("📊 Uso total", f"{porcentaje:.0f}%")

st.divider()

# TABS
tab1, tab2, tab3, tab4 = st.tabs(["📝 Registrar", "✏️ Editar presupuestos", "📊 Análisis", "📋 Historial"])

with tab1:
    st.subheader("➕ Nuevo gasto")
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
        rubro = st.selectbox("Categoría", list(presupuestos.keys()))
        subcategoria = st.selectbox("Subcategoría", SUBCATEGORIAS[rubro])
    with col2:
        monto = st.number_input("Monto ($)", step=10.0, min_value=0.0, format="%.2f")
    
    if st.button("💾 Guardar", type="primary", use_container_width=True):
        if monto > 0:
            guardar_gasto(fecha.strftime("%Y-%m-%d"), rubro, subcategoria, monto)
            st.success(f"✅ Guardado: {rubro} → {subcategoria} | ${monto:,.2f}")
            st.rerun()
        else:
            st.warning("Ingresa un monto válido")

with tab2:
    st.subheader("✏️ Editar presupuestos mensuales")
    st.caption("Modifica los valores según tus necesidades")
    
    nuevos_presupuestos = {}
    cols = st.columns(3)
    for i, (rubro, monto_actual) in enumerate(presupuestos.items()):
        with cols[i % 3]:
            nuevo = st.number_input(f"💰 {rubro}", value=float(monto_actual), step=100.0, key=f"pres_{rubro}", format="%.0f")
            nuevos_presupuestos[rubro] = nuevo
    
    if st.button("💾 Guardar presupuestos", use_container_width=True, type="primary"):
        guardar_presupuestos(nuevos_presupuestos)
        st.success("✅ Presupuestos actualizados")
        st.rerun()

with tab3:
    if not df.empty:
        resumen = df.groupby("rubro")["monto"].sum().reset_index()
        fig = px.pie(resumen, names="rubro", values="monto", title="Distribución de gastos")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📊 Estado por categoría")
        for _, row in resumen.iterrows():
            presupuesto = presupuestos[row["rubro"]]
            porcentaje = (row["monto"] / presupuesto * 100) if presupuesto > 0 else 0
            if porcentaje > 100:
                st.error(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${presupuesto:,.0f} ({porcentaje:.0f}%) 🔴 EXCEDIDO")
            elif porcentaje > 80:
                st.warning(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${presupuesto:,.0f} ({porcentaje:.0f}%) 🟡 CUIDADO")
            else:
                st.success(f"**{row['rubro']}**: ${row['monto']:,.0f} / ${presupuesto:,.0f} ({porcentaje:.0f}%) 🟢 OK")
        
        # Evolución diaria
        st.subheader("📈 Evolución diaria")
        gastos_por_dia = df.groupby(df["fecha"])["monto"].sum().reset_index()
        fig_line = px.line(gastos_por_dia, x="fecha", y="monto", title="Gastos por día")
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No hay gastos registrados aún")

with tab4:
    if not df.empty:
        st.subheader("📋 Historial de movimientos")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Desde", df["fecha"].min())
        with col2:
            fecha_fin = st.date_input("Hasta", df["fecha"].max())
        
        df_filtrado = df[(df["fecha"] >= pd.to_datetime(fecha_inicio)) & (df["fecha"] <= pd.to_datetime(fecha_fin))]
        
        # Mostrar tabla con botones de acción
        for idx, row in df_filtrado.sort_values("fecha", ascending=False).iterrows():
            with st.expander(f"📅 {row['fecha'].strftime('%d/%m/%Y')} - {row['rubro']} - ${row['monto']:,.0f}"):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Editar", key=f"edit_{row['id']}"):
                        st.session_state["editando"] = row["id"]
                with col2:
                    if st.button(f"🗑️ Eliminar", key=f"delete_{row['id']}"):
                        eliminar_gasto(row["id"])
                        st.success(f"✅ Gasto eliminado")
                        st.rerun()
                
                if st.session_state.get("editando") == row["id"]:
                    st.subheader("Editar gasto")
                    nueva_fecha = st.date_input("Nueva fecha", row["fecha"], key=f"fecha_{row['id']}")
                    nuevo_rubro = st.selectbox("Nueva categoría", list(presupuestos.keys()), 
                                               index=list(presupuestos.keys()).index(row["rubro"]), key=f"rubro_{row['id']}")
                    nueva_subcategoria = st.selectbox("Nueva subcategoría", SUBCATEGORIAS[nuevo_rubro], 
                                                      key=f"sub_{row['id']}")
                    nuevo_monto = st.number_input("Nuevo monto", value=float(row["monto"]), step=10.0, key=f"monto_{row['id']}")
                    
                    if st.button(f"💾 Guardar cambios", key=f"save_{row['id']}"):
                        actualizar_gasto(row["id"], nueva_fecha.strftime("%Y-%m-%d"), nuevo_rubro, nueva_subcategoria, nuevo_monto)
                        st.success("✅ Gasto actualizado")
                        st.session_state["editando"] = None
                        st.rerun()
        
        # Botón de respaldo
        if st.button("📁 Descargar respaldo completo (CSV)", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button(
                label="✅ Haz clic para descargar",
                data=csv,
                file_name=f"gastos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No hay gastos registrados aún")

st.divider()
st.caption("💰 Control Financiero PRO | 8 categorías | Subcategorías | Presupuestos editables | Editar/Eliminar gastos")
