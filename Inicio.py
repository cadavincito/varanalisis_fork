import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px
import numpy as np

# --------------------------------------------------
# Configuración de página
# --------------------------------------------------
st.set_page_config(
    page_title="Monitoreo de Nivel de Gas - EAFIT",
    page_icon="🧪",
    layout="wide"
)

# --------------------------------------------------
# Estilos personalizados
# --------------------------------------------------
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1150px;
    }

    /* Título principal */
    .title-container {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 24px;
        color: #f9fafb;
    }
    .title-container h1 {
        font-size: 1.9rem;
        margin-bottom: 0.2rem;
    }
    .title-container p {
        font-size: 0.95rem;
        opacity: 0.9;
        margin-bottom: 0;
    }

    /* Tarjetas de métricas */
    .metric-card {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 16px 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 10px 30px rgba(15,23,42,0.06);
    }
    .metric-label {
        font-size: 0.80rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #6b7280;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: 600;
        color: #0f172a;
    }
    .metric-footer {
        font-size: 0.78rem;
        color: #9ca3af;
        margin-top: 2px;
    }

    .section-title {
        font-weight: 600;
        font-size: 1.05rem;
        margin-top: 0.5rem;
        margin-bottom: 0.3rem;
    }
    .section-subtitle {
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HERO / Encabezado
# --------------------------------------------------
st.markdown("""
<div class="title-container">
    <h1>Monitoreo de Nivel de Gas – Universidad EAFIT</h1>
    <p>
        Visualización y análisis de los datos registrados por el sensor de nivel de gas.
        Carga el archivo CSV exportado desde Influx/Grafana para explorar su comportamiento en el tiempo.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Controles laterales
# --------------------------------------------------
with st.sidebar:
    st.header("📁 Entrada de datos")
    uploaded_file = st.file_uploader(
        "Selecciona el archivo CSV de nivel de gas",
        type=["csv"]
    )

    st.markdown("---")
    st.subheader("🎛️ Configuración de gráfico")
    chart_type = st.selectbox(
        "Tipo de visualización",
        ["Línea", "Área", "Dispersión"]
    )

    st.markdown("---")
    st.subheader("⚠️ Umbral de alerta")
    umbral_alerta = st.number_input(
        "Umbral (nivel de gas)",
        value=3000.0,
        step=100.0
    )

# --------------------------------------------------
# Contenido principal
# --------------------------------------------------
if uploaded_file is not None:
    try:
        df1 = pd.read_csv(uploaded_file)

        # Normalizar columnas: Time + nivel de gas
        # Renombrar columna de nivel de gas a un nombre estándar
        if "Time" in df1.columns:
            otras = [c for c in df1.columns if c != "Time"]
            if len(otras) > 0:
                df1 = df1.rename(columns={otras[0]: "nivel_gas"})
        else:
            df1 = df1.rename(columns={df1.columns[0]: "nivel_gas"})

        # Procesar columna de tiempo
        if "Time" in df1.columns:
            df1["Time"] = pd.to_datetime(df1["Time"])
            df1 = df1.set_index("Time")

        # Asegurar que los datos sean numéricos
        df1["nivel_gas"] = pd.to_numeric(df1["nivel_gas"], errors="coerce")
        df1 = df1.dropna(subset=["nivel_gas"])

        # --------------------------------------------------
        # Métricas principales
        # --------------------------------------------------
        serie = df1["nivel_gas"]
        valor_actual = float(serie.iloc[-1])
        valor_max = float(serie.max())
        valor_min = float(serie.min())
        valor_mean = float(serie.mean())
        valor_std = float(serie.std()) if len(serie) > 1 else 0.0

        # Estado relativo del nivel de gas
        if valor_actual > valor_mean + valor_std:
            estado = "Alto"
            color_estado = "🔴"
        elif valor_actual < valor_mean - valor_std:
            estado = "Bajo"
            color_estado = "🟡"
        else:
            estado = "Normal"
            color_estado = "🟢"

        # Duración del registro
        if len(df1.index) > 1:
            duracion = df1.index[-1] - df1.index[0]
            duracion_str = str(duracion).split(".")[0]
        else:
            duracion_str = "No disponible"

        col_a, col_b, col_c, col_d = st.columns(4)

        with col_a:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Nivel actual de gas</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{valor_actual:,.0f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-footer">{color_estado} Estado: {estado}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Máximo registrado</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{valor_max:,.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-footer">Pico más alto del período</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_c:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Promedio</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{valor_mean:,.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-footer">Nivel medio en el intervalo</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_d:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Duración del registro</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{duracion_str}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-footer">Desde la primera hasta la última muestra</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Alerta rápida si supera el umbral
        if valor_actual >= umbral_alerta:
            st.warning(f"⚠️ El nivel actual de gas ({valor_actual:,.0f}) supera el umbral configurado ({umbral_alerta:,.0f}).")
        else:
            st.info(f"✅ El nivel actual de gas ({valor_actual:,.0f}) está por debajo del umbral configurado ({umbral_alerta:,.0f}).")

        # --------------------------------------------------
        # Pestañas
        # --------------------------------------------------
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Panorama general",
            "📊 Análisis estadístico",
            "🔍 Filtros y descargas",
            "🗺️ Información del sitio"
        ])

        # ------------- Tab 1: Panorama general -------------
        with tab1:
            st.markdown('<div class="section-title">Evolución del nivel de gas</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="section-subtitle">'
                'Visualiza cómo cambia el nivel de gas a lo largo del tiempo. '
                'Puedes hacer zoom, seleccionar rangos y pasar el cursor sobre el gráfico para ver los valores exactos.'
                '</div>',
                unsafe_allow_html=True
            )

            df_plot = df1.reset_index().rename(columns={"index": "Time"})

            if chart_type == "Línea":
                fig = px.line(
                    df_plot,
                    x="Time",
                    y="nivel_gas",
                    labels={"Time": "Tiempo", "nivel_gas": "Nivel de gas"},
                )
            elif chart_type == "Área":
                fig = px.area(
                    df_plot,
                    x="Time",
                    y="nivel_gas",
                    labels={"Time": "Tiempo", "nivel_gas": "Nivel de gas"},
                )
            else:  # Dispersión
                fig = px.scatter(
                    df_plot,
                    x="Time",
                    y="nivel_gas",
                    labels={"Time": "Tiempo", "nivel_gas": "Nivel de gas"},
                )

            fig.update_layout(
                height=420,
                margin=dict(l=10, r=10, t=10, b=10),
                template="simple_white",
                xaxis_title="Tiempo",
                yaxis_title="Nivel de gas",
                hovermode="x unified"
            )
            fig.update_traces(line_color="#10b981", marker_color="#10b981")  # Verde esmeralda

            st.plotly_chart(fig, use_container_width=True)

            if st.checkbox("Mostrar datos crudos", key="raw_data_tab1"):
                st.dataframe(df1)

        # ------------- Tab 2: Estadísticas -------------
        with tab2:
            st.markdown('<div class="section-title">Resumen estadístico</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="section-subtitle">'
                'Estadísticos básicos del nivel de gas medido por el sensor.'
                '</div>',
                unsafe_allow_html=True
            )

            stats_df = serie.describe().to_frame(name="Nivel de gas")

            col1, col2 = st.columns([1.3, 1])

            with col1:
                st.dataframe(stats_df)

            with col2:
                st.metric("Valor promedio", f"{valor_mean:,.2f}")
                st.metric("Valor máximo", f"{valor_max:,.2f}")
                st.metric("Valor mínimo", f"{valor_min:,.2f}")
                st.metric("Desviación estándar", f"{valor_std:,.2f}")

        # ------------- Tab 3: Filtros y descargas -------------
        with tab3:
            st.markdown('<div class="section-title">Filtros sobre el nivel de gas</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="section-subtitle">'
                'Explora únicamente los registros que cumplan ciertos criterios de valor y exporta los resultados.'
                '</div>',
                unsafe_allow_html=True
            )

            min_value = float(serie.min())
            max_value = float(serie.max())
            mean_value = float(serie.mean())

            if min_value == max_value:
                st.warning(f"⚠️ Todos los valores en el dataset son iguales: {min_value:.2f}")
                st.info("No es posible aplicar filtros cuando no hay variación en los datos.")
                st.dataframe(df1)
            else:
                colf1, colf2 = st.columns(2)

                with colf1:
                    min_val = st.slider(
                        "Valor mínimo (filtrar superiores a…)",
                        min_value,
                        max_value,
                        mean_value,
                        key="min_val_slider"
                    )
                    filtrado_df_min = df1[df1["nivel_gas"] > min_val]
                    st.write(f"Registros con nivel de gas **superior a {min_val:.2f}**:")
                    st.dataframe(filtrado_df_min)

                with colf2:
                    max_val = st.slider(
                        "Valor máximo (filtrar inferiores a…)",
                        min_value,
                        max_value,
                        mean_value,
                        key="max_val_slider"
                    )
                    filtrado_df_max = df1[df1["nivel_gas"] < max_val]
                    st.write(f"Registros con nivel de gas **inferior a {max_val:.2f}**:")
                    st.dataframe(filtrado_df_max)

                st.markdown("#### Descargar datos filtrados (según filtro mínimo)")
                csv = filtrado_df_min.to_csv().encode("utf-8")
                st.download_button(
                    label="💾 Descargar CSV filtrado",
                    data=csv,
                    file_name="nivel_gas_filtrado.csv",
                    mime="text/csv",
                )

        # ------------- Tab 4: Información del sitio -------------
        with tab4:
            st.markdown('<div class="section-title">Ubicación y detalles del sistema de medición</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="section-subtitle">'
                'Información contextual sobre el sensor y el entorno donde se está midiendo el nivel de gas.'
                '</div>',
                unsafe_allow_html=True
            )

            col_info1, col_info2 = st.columns(2)

            with col_info1:
                st.write("### 📍 Ubicación del sensor")
                st.write("**Universidad EAFIT – Medellín, Colombia**")
                st.write("- Latitud: 6.2006")
                st.write("- Longitud: -75.5783")
                st.write("- Altitud: ~1,495 m s. n. m.")
                st.write("- Entorno: Campus universitario")

            with col_info2:
                st.write("### 🧪 Detalles del sistema")
                st.write("- Controlador: ESP32")
                st.write("- Variable medida: Nivel de gas (unidad relativa del sensor)")
                st.write("- Frecuencia de medición: según configuración de Influx/Grafana")
                st.write("- Flujo de datos: Sensor → InfluxDB → Grafana → CSV → Streamlit")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
        st.info("Verifica que el CSV tenga una columna de tiempo ('Time') y una columna con el nivel de gas.")
else:
    st.info("Carga un archivo CSV en la barra lateral para comenzar el análisis.")

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("""
---
Desarrollado para el análisis del **nivel de gas** a partir de datos de sensores urbanos.  
Ubicación: Universidad EAFIT – Medellín, Colombia.
""")
