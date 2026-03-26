import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import json
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Control Financiero PRO", layout="wide", page_icon="💰", initial_sidebar_state="expanded")

# ============================================
# CONFIGURACIÓN
# ============================================
PASSWORD = "1234"

CATEGORIAS_POR_DEFECTO = {
    "Alimentación": {"presupuesto": 7900, "subcategorias": ["Despensa", "Comida fuera", "Antojos", "Bebidas", "Café"]},
    "Servicios": {"presupuesto": 1550, "subcategorias": ["Luz", "Agua", "Gas", "Internet", "Teléfono"]},
    "Vivienda": {"presupuesto": 1400, "subcategorias": ["Renta", "Mantenimiento", "Artículos hogar", "Limpiadores"]},
    "Transporte": {"presupuesto": 750, "subcategorias": ["Gasolina", "Mantenimiento auto", "Pasajes", "Estacionamiento"]},
    "Ahorro": {"presupuesto": 1500, "subcategorias": ["Ahorro mensual", "Fondo emergencia", "Inversiones"]},
    "Salud": {"presupuesto": 800, "subcategorias": ["Farmacia", "Consultas", "Medicamentos", "Seguro"]},
    "Educación": {"presupuesto": 600, "subcategorias": ["Colegiaturas", "Libros", "Material", "Cursos"]},
    "Entretenimiento": {"presupuesto": 500, "subcategorias": ["Cine", "Restaurantes", "Hobbies", "Suscripciones"]}
}

ARCHIVO_GASTOS = "gastos.csv"
ARCHIVO_CATEGORIAS = "categorias.json"

def cargar_categorias():
    if os.path.exists(ARCHIVO_CATEGORIAS):
        try:
            with open(ARCHIVO_CATEGORIAS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return CATEGORIAS_POR_DEFECTO.copy()
    return CATEGORIAS_POR_DEFECTO.copy()

def guardar_categorias(categorias):
    with open(ARCHIVO_CATEGORIAS, 'w', encoding='utf-8') as f:
        json.dump(categorias, f, ensure_ascii=False, indent=2)

def cargar_gastos():
    if os.path.exists(ARCHIVO_GASTOS):
        try:
            df = pd.read_csv(ARCHIVO_GASTOS)
            if not df.empty:
                df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce')
                df = df.dropna(subset=["fecha"])
                if "id" not in df.columns:
                    df["id"] = range(1, len(df) + 1)
            return df
        except:
            return pd.DataFrame(columns=["id", "fecha", "rubro", "subcategoria", "monto", "descripcion"])
    return pd.DataFrame(columns=["id", "fecha", "rubro", "subcategoria", "monto", "descripcion"])

def guardar_gastos(df):
    if not df.empty:
        df_guardar = df.copy()
        df_guardar["fecha"] = df_guardar["fecha"].dt.strftime("%Y-%m-%d")
        df_guardar.to_csv(ARCHIVO_GASTOS, index=False)
    else:
        if os.path.exists(ARCHIVO_GASTOS):
            os.remove(ARCHIVO_GASTOS)

def obtener_nuevo_id(df):
    if df.empty:
        return 1
    return df["id"].max() + 1

def exportar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export = df.copy()
        df_export["fecha"] = df_export["fecha"].dt.strftime("%d/%m/%Y")
        df_export.to_excel(writer, sheet_name='Gastos', index=False)
    return output.getvalue()

# ============================================
# LOGIN
# ============================================
if "auth" not in st.session_state:
    st.session_state.auth = False
if "modo_oscuro" not in st.session_state:
    st.session_state.modo_oscuro = False
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

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.title("💰 Control PRO")
    
    modo = st.toggle("🌙 Modo oscuro", value=st.session_state.modo_oscuro)
    if modo != st.session_state.modo_oscuro:
        st.session_state.modo_oscuro = modo
        st.rerun()
    
    st.divider()
    
    pagina = st.radio("📌 Navegación", [
        "📊 Dashboard", 
        "📝 Registrar", 
        "✏️ Configuración", 
        "📈 Análisis",
        "📋 Historial"
    ])
    st.session_state.pagina = pagina.split(" ")[1] if len(pagina.split(" ")) > 1 else pagina
    
    st.divider()
    
    if not df.empty:
        try:
            hoy = datetime.now()
            df_filtrado = df[df["fecha"].dt.year == hoy.year]
            df_filtrado = df_filtrado[df_filtrado["fecha"].dt.month == hoy.month]
            gasto_mes = df_filtrado["monto"].sum()
            st.metric("📅 Gasto del mes", f"${gasto_mes:,.0f}")
            porcentaje = (gasto_mes / total_presupuesto * 100) if total_presupuesto > 0 else 0
            st.progress(min(porcentaje / 100, 1.0))
            st.caption(f"{porcentaje:.0f}% usado")
        except:
            pass

# ============================================
# ESTILOS MODO OSCURO
# ============================================
if st.session_state.modo_oscuro:
    st.markdown("""
        <style>
            .stApp { background-color: #0e1117; color: #ffffff; }
        </style>
    """, unsafe_allow_html=True)

# ============================================
# DASHBOARD
# ============================================
if st.session_state.pagina == "Dashboard":
    st.title("📊 Dashboard Financiero")
    
    if not df.empty:
        try:
            hoy = datetime.now()
            df_mes = df[(df["fecha"].dt.year == hoy.year) & (df["fecha"].dt.month == hoy.month)]
            df_dia = df[df["fecha"].dt.date == hoy.date()]
            
            gasto_mes = df_mes["monto"].sum()
            gasto_dia = df_dia["monto"].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💸 Gasto del mes", f"${gasto_mes:,.0f}")
            with col2:
                st.metric("📅 Gasto hoy", f"${gasto_dia:,.0f}")
            with col3:
                restante = total_presupuesto - gasto_mes
                st.metric("💰 Presupuesto restante", f"${restante:,.0f}")
            
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
                fig = px.line(evolucion, x="mes", y="monto", markers=True)
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("🚨 Alertas")
            alertas = False
            for _, row in resumen.iterrows():
                presupuesto = categorias.get(row["rubro"], {}).get("presupuesto", 0)
                if presupuesto > 0:
                    porcentaje = (row["monto"] / presupuesto * 100)
                    if porcentaje > 100:
                        st.error(f"⚠️ EXCESO en {row['rubro']}: ${row['monto']:,.0f} / ${presupuesto:,.0f} ({porcentaje:.0f}%)")
                        alertas = True
                    elif porcentaje > 80:
                        st.warning(f"📌 ALERTA en {row['rubro']}: ${row['monto']:,.0f} / ${presupuesto:,.0f} ({porcentaje:.0f}%)")
                        alertas = True
            if not alertas:
                st.success("✅ Todo en orden")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("📝 No hay gastos registrados")

# ============================================
# REGISTRAR GASTO
# ============================================
elif st.session_state.pagina == "Registrar":
    st.title("📝 Registrar nuevo gasto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("📅 Fecha", datetime.now())
        rubro = st.selectbox("📂 Categoría", list(categorias.keys()))
        subcategorias = categorias[rubro]["subcategorias"]
        subcategoria = st.selectbox("🏷️ Subcategoría", subcategorias)
        
    with col2:
        monto = st.number_input("💰 Monto ($)", step=10.0, min_value=0.0, format="%.2f")
        descripcion = st.text_area("📝 Descripción", placeholder="Ej: Compras del supermercado", height=68)
    
    if st.button("💾 Guardar gasto", type="primary", use_container_width=True):
        if monto > 0:
            df = cargar_gastos()
            nuevo_id = obtener_nuevo_id(df)
            
            nueva_fila = pd.DataFrame([{
                "id": nuevo_id,
                "fecha": fecha.strftime("%Y-%m-%d"),
                "rubro": rubro,
                "subcategoria": subcategoria,
                "monto": monto,
                "descripcion": descripcion
            }])
            df = pd.concat([df, nueva_fila], ignore_index=True)
            guardar_gastos(df)
            st.success(f"✅ Guardado: {rubro} → {subcategoria} | ${monto:,.2f}")
            st.balloons()
            st.rerun()
        else:
            st.warning("⚠️ Ingresa un monto válido")

# ============================================
# CONFIGURACIÓN
# ============================================
elif st.session_state.pagina == "Configuración":
    st.title("✏️ Configuración")
    
    tab1, tab2, tab3 = st.tabs(["📂 Presupuestos", "🏷️ Subcategorías", "➕ Gestionar categorías"])
    
    with tab1:
        st.subheader("Editar presupuestos mensuales")
        nuevas_categorias = {}
        cols = st.columns(3)
        for i, (rubro, datos) in enumerate(categorias.items()):
            with cols[i % 3]:
                nuevo = st.number_input(f"💰 {rubro}", value=float(datos["presupuesto"]), step=100.0, key=f"cat_{rubro}", format="%.0f")
                nuevas_categorias[rubro] = {"presupuesto": nuevo, "subcategorias": datos["subcategorias"]}
        
        if st.button("💾 Guardar presupuestos", type="primary", use_container_width=True):
            guardar_categorias(nuevas_categorias)
            st.success("✅ Presupuestos actualizados")
            st.rerun()
    
    with tab2:
        st.subheader("Agregar/Editar subcategorías")
        rubro_editar = st.selectbox("Selecciona categoría", list(categorias.keys()))
        
        subcategorias_actuales = categorias[rubro_editar]["subcategorias"]
        st.write("**Subcategorías actuales:**")
        for sc in subcategorias_actuales:
            st.write(f"- {sc}")
        
        nueva_sub = st.text_input("Agregar nueva subcategoría")
        if st.button("➕ Agregar", use_container_width=True):
            if nueva_sub and nueva_sub not in subcategorias_actuales:
                categorias[rubro_editar]["subcategorias"].append(nueva_sub)
                guardar_categorias(categorias)
                st.success(f"✅ Subcategoría '{nueva_sub}' agregada")
                st.rerun()
        
        eliminar_sub = st.selectbox("Eliminar subcategoría", ["---"] + subcategorias_actuales)
        if st.button("🗑️ Eliminar", use_container_width=True):
            if eliminar_sub != "---":
                categorias[rubro_editar]["subcategorias"].remove(eliminar_sub)
                guardar_categorias(categorias)
                st.success(f"✅ Subcategoría '{eliminar_sub}' eliminada")
                st.rerun()
    
    with tab3:
        st.subheader("➕ Agregar nueva categoría")
        col1, col2 = st.columns(2)
        with col1:
            nueva_categoria = st.text_input("Nombre de la nueva categoría")
        with col2:
            presupuesto_categoria = st.number_input("Presupuesto mensual", step=100.0, min_value=0.0, format="%.0f")
        
        st.write("**Subcategorías iniciales (una por línea):**")
        subcategorias_iniciales = st.text_area("Ejemplo:\nCompra\nMantenimiento\nServicio", height=100)
        
        if st.button("➕ Crear categoría", type="primary", use_container_width=True):
            if nueva_categoria and nueva_categoria not in categorias:
                subs = [s.strip() for s in subcategorias_iniciales.split("\n") if s.strip()]
                if not subs:
                    subs = ["General"]
                categorias[nueva_categoria] = {
                    "presupuesto": presupuesto_categoria,
                    "subcategorias": subs
                }
                guardar_categorias(categorias)
                st.success(f"✅ Categoría '{nueva_categoria}' creada con {len(subs)} subcategorías")
                st.rerun()
            elif nueva_categoria in categorias:
                st.error("❌ Esta categoría ya existe")
        
        st.divider()
        st.subheader("🗑️ Eliminar categoría")
        categorias_lista = list(categorias.keys())
        categoria_eliminar = st.selectbox("Selecciona categoría a eliminar", categorias_lista)
        
        tiene_gastos = not df.empty and categoria_eliminar in df["rubro"].values
        if tiene_gastos:
            st.warning(f"⚠️ La categoría '{categoria_eliminar}' tiene gastos registrados")
        
        if st.button("🗑️ Eliminar categoría", use_container_width=True):
            if categoria_eliminar:
                if tiene_gastos:
                    df_temp = cargar_gastos()
                    df_temp = df_temp[df_temp["rubro"] != categoria_eliminar]
                    guardar_gastos(df_temp)
                del categorias[categoria_eliminar]
                guardar_categorias(categorias)
                st.success(f"✅ Categoría '{categoria_eliminar}' eliminada")
                st.rerun()

# ============================================
# ANÁLISIS
# ============================================
elif st.session_state.pagina == "Análisis":
    st.title("📈 Análisis avanzado")
    
    if not df.empty:
        try:
            col1, col2 = st.columns(2)
            with col1:
                fecha_inicio = st.date_input("Desde", df["fecha"].min())
            with col2:
                fecha_fin = st.date_input("Hasta", df["fecha"].max())
            
            df_filtrado = df[(df["fecha"] >= pd.to_datetime(fecha_inicio)) & (df["fecha"] <= pd.to_datetime(fecha_fin))]
            
            if not df_filtrado.empty:
                st.subheader("🏆 Top categorías")
                top_cat = df_filtrado.groupby("rubro")["monto"].sum().sort_values(ascending=False).head(5)
                fig = px.bar(top_cat, x=top_cat.values, y=top_cat.index, orientation='h')
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("📊 Evolución")
                df_filtrado["mes"] = df_filtrado["fecha"].dt.to_period("M").astype(str)
                evolucion = df_filtrado.groupby("mes")["monto"].sum().reset_index()
                fig = px.area(evolucion, x="mes", y="monto")
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("📅 Gastos por día")
                df_filtrado["dia"] = df_filtrado["fecha"].dt.day_name()
                gastos_dia = df_filtrado.groupby("dia")["monto"].sum().reset_index()
                orden = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                gastos_dia["dia"] = pd.Categorical(gastos_dia["dia"], categories=orden, ordered=True)
                gastos_dia = gastos_dia.sort_values("dia")
                fig = px.bar(gastos_dia, x="dia", y="monto")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("No hay datos suficientes")

# ============================================
# HISTORIAL
# ============================================
elif st.session_state.pagina == "Historial":
    st.title("📋 Historial completo")
    
    if not df.empty:
        try:
            col1, col2, col3 = st.columns(3)
            with col1:
                fecha_inicio = st.date_input("Desde", df["fecha"].min())
            with col2:
                fecha_fin = st.date_input("Hasta", df["fecha"].max())
            with col3:
                rubro_filtro = st.selectbox("Categoría", ["Todas"] + list(categorias.keys()))
            
            df_filtrado = df[(df["fecha"] >= pd.to_datetime(fecha_inicio)) & (df["fecha"] <= pd.to_datetime(fecha_fin))]
            if rubro_filtro != "Todas":
                df_filtrado = df_filtrado[df_filtrado["rubro"] == rubro_filtro]
            
            for idx, row in df_filtrado.sort_values("fecha", ascending=False).iterrows():
                with st.expander(f"📅 {row['fecha'].strftime('%d/%m/%Y')} - {row['rubro']} - {row['subcategoria']} - ${row['monto']:,.0f}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✏️ Editar", key=f"edit_{row['id']}"):
                            st.session_state["editando"] = row["id"]
                    with col2:
                        if st.button(f"🗑️ Eliminar", key=f"delete_{row['id']}"):
                            df_temp = cargar_gastos()
                            df_temp = df_temp[df_temp["id"] != row["id"]]
                            guardar_gastos(df_temp)
                            st.success("✅ Gasto eliminado")
                            st.rerun()
                    
                    if st.session_state.get("editando") == row["id"]:
                        st.subheader("Editar gasto")
                        nueva_fecha = st.date_input("Fecha", row["fecha"], key=f"fecha_{row['id']}")
                        nuevo_rubro = st.selectbox("Categoría", list(categorias.keys()), 
                                                   index=list(categorias.keys()).index(row["rubro"]), key=f"rubro_{row['id']}")
                        nueva_subcategoria = st.selectbox("Subcategoría", categorias[nuevo_rubro]["subcategorias"], 
                                                          key=f"sub_{row['id']}")
                        nuevo_monto = st.number_input("Monto", value=float(row["monto"]), step=10.0, key=f"monto_{row['id']}")
                        
                        if st.button(f"💾 Guardar cambios", key=f"save_{row['id']}"):
                            df_temp = cargar_gastos()
                            df_temp.loc[df_temp["id"] == row["id"], ["fecha", "rubro", "subcategoria", "monto"]] = [
                                nueva_fecha.strftime("%Y-%m-%d"), nuevo_rubro, nueva_subcategoria, nuevo_monto
                            ]
                            guardar_gastos(df_temp)
                            st.success("✅ Gasto actualizado")
                            st.session_state["editando"] = None
                            st.rerun()
            
            st.divider()
            if st.button("📁 Exportar a Excel", use_container_width=True):
                excel_data = exportar_excel(df)
                st.download_button(
                    label="✅ Descargar",
                    data=excel_data,
                    file_name=f"gastos_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("No hay gastos registrados")

st.divider()
st.caption("💰 Control Financiero PRO | Categorías editables | Subcategorías | Exportación Excel")
