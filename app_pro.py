import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
import base64
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Control Financiero PRO", layout="wide", page_icon="💰", initial_sidebar_state="expanded")

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================
PASSWORD = "1234"

# Categorías y subcategorías por defecto
CATEGORIAS_POR_DEFECTO = {
    "Alimentación": {
        "presupuesto": 7900,
        "subcategorias": ["Despensa", "Comida fuera", "Antojos", "Bebidas", "Café", "Panadería", "Carnes", "Verduras", "Fruta", "Botanas"]
    },
    "Servicios": {
        "presupuesto": 1550,
        "subcategorias": ["Luz", "Agua", "Gas", "Internet", "Teléfono", "Netflix", "Spotify", "Prime Video", "Mantenimiento", "Basura"]
    },
    "Vivienda": {
        "presupuesto": 1400,
        "subcategorias": ["Renta", "Hipoteca", "Mantenimiento", "Artículos hogar", "Limpiadores", "Muebles", "Electrodomésticos", "Decoración", "Jardinería", "Herramientas"]
    },
    "Transporte": {
        "presupuesto": 750,
        "subcategorias": ["Gasolina", "Mantenimiento auto", "Pasajes", "Estacionamiento", "Taxi", "Uber", "Didi", "Renta de auto", "Lavado auto", "Tenencia"]
    },
    "Ahorro": {
        "presupuesto": 1500,
        "subcategorias": ["Ahorro mensual", "Fondo emergencia", "Inversiones", "Meta viajes", "Meta retiro", "Educación hijos", "Navidad", "Casa propia"]
    },
    "Salud": {
        "presupuesto": 800,
        "subcategorias": ["Farmacia", "Consultas", "Dentista", "Terapias", "Medicamentos", "Seguro médico", "Gimnasio", "Nutrición", "Estudios", "Urgencias"]
    },
    "Educación": {
        "presupuesto": 600,
        "subcategorias": ["Colegiaturas", "Libros", "Material escolar", "Cursos", "Talleres", "Idiomas", "Computadora", "Software", "Uniformes", "Transporte escolar"]
    },
    "Entretenimiento": {
        "presupuesto": 500,
        "subcategorias": ["Cine", "Conciertos", "Restaurantes", "Bares", "Hobbies", "Deportes", "Videojuegos", "Suscripciones", "Viajes", "Parques"]
    },
    "Ropa": {
        "presupuesto": 600,
        "subcategorias": ["Ropa casual", "Ropa formal", "Calzado", "Accesorios", "Ropa deportiva", "Ropa niños", "Lavandería", "Sastrería"]
    },
    "Mascotas": {
        "presupuesto": 400,
        "subcategorias": ["Alimento", "Veterinaria", "Medicinas", "Accesorios", "Peluquería", "Paseos", "Guardería"]
    },
    "Regalos": {
        "presupuesto": 500,
        "subcategorias": ["Cumpleaños", "Navidad", "Aniversarios", "Bodas", "Bautizos", "Graduaciones", "Detalles"]
    },
    "Impuestos": {
        "presupuesto": 300,
        "subcategorias": ["ISR", "IVA", "Predial", "Agua", "Tenencia", "Multas"]
    }
}

# Archivos de datos
ARCHIVO_GASTOS = "gastos.csv"
ARCHIVO_CATEGORIAS = "categorias.json"
ARCHIVO_METAS = "metas.json"
ARCHIVO_RECORDATORIOS = "recordatorios.json"

# ============================================
# FUNCIONES DE CARGA Y GUARDADO
# ============================================
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
                if "recibo" not in df.columns:
                    df["recibo"] = ""
                if "descripcion" not in df.columns:
                    df["descripcion"] = ""
                if "id" not in df.columns:
                    df["id"] = range(1, len(df) + 1)
            return df
        except:
            return pd.DataFrame(columns=["id", "fecha", "rubro", "subcategoria", "monto", "descripcion", "recibo"])
    return pd.DataFrame(columns=["id", "fecha", "rubro", "subcategoria", "monto", "descripcion", "recibo"])

def guardar_gastos(df):
    if not df.empty:
        df_guardar = df.copy()
        df_guardar["fecha"] = df_guardar["fecha"].dt.strftime("%Y-%m-%d")
        df_guardar.to_csv(ARCHIVO_GASTOS, index=False)
    else:
        if os.path.exists(ARCHIVO_GASTOS):
            os.remove(ARCHIVO_GASTOS)

def cargar_metas():
    if os.path.exists(ARCHIVO_METAS):
        try:
            with open(ARCHIVO_METAS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_metas(metas):
    with open(ARCHIVO_METAS, 'w', encoding='utf-8') as f:
        json.dump(metas, f, ensure_ascii=False, indent=2)

def cargar_recordatorios():
    if os.path.exists(ARCHIVO_RECORDATORIOS):
        try:
            with open(ARCHIVO_RECORDATORIOS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_recordatorios(recordatorios):
    with open(ARCHIVO_RECORDATORIOS, 'w', encoding='utf-8') as f:
        json.dump(recordatorios, f, ensure_ascii=False, indent=2)

def obtener_nuevo_id(df):
    if df.empty:
        return 1
    return df["id"].max() + 1

# ============================================
# FUNCIONES DE ANÁLISIS
# ============================================
def calcular_tendencias(df, meses=3):
    if df.empty or len(df) < 10:
        return None
    df_mes = df.copy()
    df_mes["mes"] = df_mes["fecha"].dt.to_period("M")
    gastos_mensuales = df_mes.groupby("mes")["monto"].sum().reset_index()
    if len(gastos_mensuales) >= 2:
        ultimos = gastos_mensuales.tail(meses)
        if len(ultimos) >= 2 and ultimos["monto"].iloc[-2] > 0:
            tendencia = (ultimos["monto"].iloc[-1] - ultimos["monto"].iloc[-2]) / ultimos["monto"].iloc[-2] * 100
            return tendencia
    return None

def predecir_gasto_mensual(df):
    if df.empty or len(df) < 5:
        return None
    df_dias = df.groupby(df["fecha"].dt.day)["monto"].sum().reset_index()
    if len(df_dias) > 0:
        promedio_diario = df_dias["monto"].mean()
        dias_restantes = 30 - datetime.now().day
        return promedio_diario * dias_restantes
    return None

def comparar_meses(df):
    if df.empty:
        return None
    df["mes"] = df["fecha"].dt.to_period("M")
    actual = datetime.now().strftime("%Y-%m")
    anterior = (datetime.now() - timedelta(days=30)).strftime("%Y-%m")
    
    gasto_actual = df[df["mes"].astype(str) == actual]["monto"].sum()
    gasto_anterior = df[df["mes"].astype(str) == anterior]["monto"].sum()
    
    if gasto_anterior > 0:
        variacion = ((gasto_actual - gasto_anterior) / gasto_anterior) * 100
    else:
        variacion = 0
    
    return {
        "actual": gasto_actual,
        "anterior": gasto_anterior,
        "variacion": variacion
    }

def exportar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export = df.copy()
        df_export["fecha"] = df_export["fecha"].dt.strftime("%d/%m/%Y")
        df_export.to_excel(writer, sheet_name='Gastos', index=False)
        if not df_export.empty:
            resumen = df_export.groupby("rubro")["monto"].sum().reset_index()
            resumen.to_excel(writer, sheet_name='Resumen', index=False)
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
    st.markdown("""
        <style>
            .stApp { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
        </style>
    """, unsafe_allow_html=True)
    st.title("💰 Control Financiero PRO")
    st.markdown("### Sistema inteligente de gestión financiera")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Entrar", use_container_width=True):
        if pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta")
    st.stop()

# Cargar datos
categorias = cargar_categorias()
df = cargar_gastos()
metas = cargar_metas()
recordatorios = cargar_recordatorios()

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
        "🎯 Metas", 
        "⏰ Recordatorios",
        "📈 Análisis",
        "📋 Historial"
    ])
    st.session_state.pagina = pagina.split(" ")[1] if len(pagina.split(" ")) > 1 else pagina
    
    st.divider()
    
    if not df.empty:
        gasto_mes = df[df["fecha"].dt.month == datetime.now().month]["monto"].sum()
        st.metric("📅 Gasto del mes", f"${gasto_mes:,.0f}")
        st.metric("🎯 Presupuesto total", f"${total_presupuesto:,.0f}")
        porcentaje = (gasto_mes / total_presupuesto * 100) if total_presupuesto > 0 else 0
        st.progress(min(porcentaje / 100, 1.0))
        st.caption(f"{porcentaje:.0f}% usado")

# ============================================
# ESTILOS
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
        gasto_mes = df[df["fecha"].dt.month == datetime.now().month]["monto"].sum()
        gasto_dia = df[df["fecha"].dt.date == datetime.now().date()]["monto"].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💸 Gasto del mes", f"${gasto_mes:,.0f}")
        with col2:
            st.metric("📅 Gasto hoy", f"${gasto_dia:,.0f}")
        with col3:
            tendencia = calcular_tendencias(df)
            if tendencia is not None:
                st.metric("📈 Tendencia", f"{tendencia:.1f}%")
            else:
                st.metric("📈 Tendencia", "N/D")
        with col4:
            prediccion = predecir_gasto_mensual(df)
            if prediccion is not None:
                st.metric("🔮 Predicción", f"${prediccion:,.0f}")
        
        comparacion = comparar_meses(df)
        if comparacion:
            st.subheader("📊 Comparativa mes vs mes")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Mes actual", f"${comparacion['actual']:,.0f}")
            with col2:
                st.metric("Mes anterior", f"${comparacion['anterior']:,.0f}", delta=f"{comparacion['variacion']:.1f}%")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🥧 Distribución")
            resumen = df[df["fecha"].dt.month == datetime.now().month].groupby("rubro")["monto"].sum().reset_index()
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
        resumen_cat = df[df["fecha"].dt.month == datetime.now().month].groupby("rubro")["monto"].sum().reset_index()
        alertas = False
        for _, row in resumen_cat.iterrows():
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
                "descripcion": descripcion,
                "recibo": ""
            }])
            df = pd.concat([df, nueva_fila], ignore_index=True)
            guardar_gastos(df)
            st.success(f"✅ Guardado: {rubro} → {subcategoria} | ${monto:,.2f}")
            st.balloons()
            st.rerun()
        else:
            st.warning("⚠️ Ingresa un monto válido")

# ============================================
# CONFIGURACIÓN (CON CREAR/ELIMINAR CATEGORÍAS)
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
        
        # Subcategorías iniciales para la nueva categoría
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
            else:
                st.warning("⚠️ Ingresa un nombre para la categoría")
        
        st.divider()
        st.subheader("🗑️ Eliminar categoría")
        categorias_lista = list(categorias.keys())
        categoria_eliminar = st.selectbox("Selecciona categoría a eliminar", categorias_lista)
        
        # Verificar si tiene gastos asociados
        tiene_gastos = not df.empty and categoria_eliminar in df["rubro"].values
        if tiene_gastos:
            st.warning(f"⚠️ La categoría '{categoria_eliminar}' tiene gastos registrados. Si la eliminas, esos gastos se perderán.")
        
        if st.button("🗑️ Eliminar categoría", use_container_width=True):
            if categoria_eliminar:
                if tiene_gastos:
                    # Eliminar también los gastos asociados
                    df = cargar_gastos()
                    df = df[df["rubro"] != categoria_eliminar]
                    guardar_gastos(df)
                del categorias[categoria_eliminar]
                guardar_categorias(categorias)
                st.success(f"✅ Categoría '{categoria_eliminar}' eliminada")
                st.rerun()

# ============================================
# METAS
# ============================================
elif st.session_state.pagina == "Metas":
    st.title("🎯 Metas de ahorro")
    
    if metas:
        st.subheader("📊 Progreso de metas")
        for i, meta in enumerate(metas):
            gastado = df[df["subcategoria"] == meta["nombre"]]["monto"].sum() if not df.empty else 0
            progreso = min(gastado / meta["monto"], 1.0) if meta["monto"] > 0 else 0
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{meta['nombre']}**: ${gastado:,.0f} / ${meta['monto']:,.0f}")
                st.progress(progreso)
            with col2:
                if st.button(f"🗑️ Eliminar", key=f"del_{i}"):
                    metas.pop(i)
                    guardar_metas(metas)
                    st.rerun()
    
    st.subheader("➕ Nueva meta")
    col1, col2 = st.columns(2)
    with col1:
        nombre_meta = st.text_input("Nombre de la meta")
    with col2:
        monto_meta = st.number_input("Monto objetivo ($)", step=1000.0, min_value=0.0)
    
    if st.button("🎯 Crear meta", use_container_width=True):
        if nombre_meta and monto_meta > 0:
            metas.append({"nombre": nombre_meta, "monto": monto_meta})
            guardar_metas(metas)
            st.success(f"✅ Meta '{nombre_meta}' creada")
            st.rerun()

# ============================================
# RECORDATORIOS
# ============================================
elif st.session_state.pagina == "Recordatorios":
    st.title("⏰ Recordatorios de pagos")
    
    if recordatorios:
        st.subheader("📋 Recordatorios activos")
        for i, rec in enumerate(recordatorios):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.write(f"**{rec['nombre']}**")
            with col2:
                st.write(f"💰 ${rec['monto']:,.0f}")
            with col3:
                st.write(f"📅 {rec['fecha']}")
            with col4:
                if st.button(f"🗑️", key=f"rec_{i}"):
                    recordatorios.pop(i)
                    guardar_recordatorios(recordatorios)
                    st.rerun()
    
    st.subheader("➕ Nuevo recordatorio")
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre_rec = st.text_input("Concepto")
    with col2:
        monto_rec = st.number_input("Monto", step=100.0, min_value=0.0)
    with col3:
        fecha_rec = st.date_input("Fecha de pago")
    
    if st.button("⏰ Crear recordatorio", use_container_width=True):
        if nombre_rec and monto_rec > 0:
            recordatorios.append({
                "nombre": nombre_rec,
                "monto": monto_rec,
                "fecha": fecha_rec.strftime("%Y-%m-%d")
            })
            guardar_recordatorios(recordatorios)
            st.success(f"✅ Recordatorio '{nombre_rec}' creado")
            st.rerun()
    
    st.subheader("📅 Próximos pagos")
    hoy = datetime.now().date()
    proximos = [r for r in recordatorios if datetime.strptime(r["fecha"], "%Y-%m-%d").date() >= hoy]
    if proximos:
        for r in proximos:
            fecha_pago = datetime.strptime(r["fecha"], "%Y-%m-%d").date()
            dias = (fecha_pago - hoy).days
            st.warning(f"📌 {r['nombre']}: ${r['monto']:,.0f} - Vence en {dias} días")
    else:
        st.info("No hay pagos próximos")

# ============================================
# ANÁLISIS
# ============================================
elif st.session_state.pagina == "Análisis":
    st.title("📈 Análisis avanzado")
    
    if not df.empty:
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
    else:
        st.info("No hay datos suficientes")

# ============================================
# HISTORIAL
# ============================================
elif st.session_state.pagina == "Historial":
    st.title("📋 Historial completo")
    
    if not df.empty:
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
                        df = cargar_gastos()
                        df = df[df["id"] != row["id"]]
                        guardar_gastos(df)
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
                        df = cargar_gastos()
                        df.loc[df["id"] == row["id"], ["fecha", "rubro", "subcategoria", "monto"]] = [
                            nueva_fecha.strftime("%Y-%m-%d"), nuevo_rubro, nueva_subcategoria, nuevo_monto
                        ]
                        guardar_gastos(df)
                        st.success("✅ Gasto actualizado")
                        st.session_state["editando"] = None
                        st.rerun()
        
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📁 Exportar a Excel", use_container_width=True):
                excel_data = exportar_excel(df)
                st.download_button(
                    label="✅ Descargar",
                    data=excel_data,
                    file_name=f"gastos_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        with col2:
            if st.button("📄 Exportar a CSV", use_container_width=True):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="✅ Descargar",
                    data=csv,
                    file_name=f"gastos_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    else:
        st.info("No hay gastos registrados")

st.divider()
st.caption("💰 Control Financiero PRO | 12+ categorías | Crear/eliminar categorías | Metas | Recordatorios")
