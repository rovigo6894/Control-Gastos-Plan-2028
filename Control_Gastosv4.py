# ============================================
# CATEGORÍAS - VERSIÓN DE EMERGENCIA
# ============================================
for categoria, datos in PRESUPUESTOS.items():
    st.subheader(f"📌 {categoria}")
    
    for sub, presupuesto in datos['subcategorias'].items():
        gastado = sum(g['monto'] for g in gastos_del_mes() 
                     if g['categoria'] == categoria and g['subcategoria'] == sub)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{sub}**")
            if presupuesto['descripcion']:
                st.caption(presupuesto['descripcion'])
        with col2:
            st.write(f"${gastado:,.2f} de ${presupuesto['monto']:,.2f}")
        
        # Barra de progreso nativa de Streamlit
        porcentaje = min(gastado / presupuesto['monto'], 1.0) if presupuesto['monto'] > 0 else 0
        st.progress(porcentaje)
        st.divider()
