import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Set wide layout and title
st.set_page_config(
    page_title="Analítica de Violencias - Puebla Corredor Centro-Oriente",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for professional look and feel
st.markdown("""
<style>
    .reportview-container {
        background: #f8f9fa;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #d9534f;
        margin-bottom: 15px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
    }
    .metric-label {
        font-size: 14px;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .title-banner {
        background: linear-gradient(135deg, #4A0E17 0%, #1A0508 100%);
        padding: 25px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# Helper function to clean text artifacts
def clean_text(text):
    if not isinstance(text, str):
        return text
    replacements = {
        "Ã¡": "á",
        "Ã©": "é",
        "Ã­": "í",
        "Ã³": "ó",
        "Ãº": "ú",
        "Ã±": "ñ",
        "Ã\xad": "í",
        "polí\xadtica": "política",
        "polí­tica": "política",
        "TrÃ¡fico": "Tráfico",
        "trÃ¡fico": "tráfico",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

# Coordinates for the 18 municipalities of the Corredor Centro-Oriente, Puebla, México
COORDINATES = {
    'Acajete': {'lat': 19.1023, 'lon': -97.9507},
    'Acatzingo': {'lat': 18.9806, 'lon': -97.7844},
    'Amozoc': {'lat': 19.0431, 'lon': -98.0414},
    'Atzitzintla': {'lat': 18.9000, 'lon': -97.3300},
    'Chalchicomula de Sesma': {'lat': 18.9861, 'lon': -97.4439},
    'Esperanza': {'lat': 18.8578, 'lon': -97.3750},
    'General Felipe Ángeles': {'lat': 19.0117, 'lon': -97.6800},
    'Guadalupe Victoria': {'lat': 19.2894, 'lon': -97.3144},
    'Cañada Morelos': {'lat': 18.7333, 'lon': -97.4167},
    'Palmar de Bravo': {'lat': 18.8356, 'lon': -97.6217},
    'Quecholac': {'lat': 18.9531, 'lon': -97.6594},
    'Los Reyes de Juárez': {'lat': 18.9500, 'lon': -97.8333},
    'San Salvador el Seco': {'lat': 19.1333, 'lon': -97.6333},
    'San Salvador Huixcolotla': {'lat': 18.9022, 'lon': -97.7719},
    'Tecamachalco': {'lat': 18.8822, 'lon': -97.7275},
    'Tepeaca': {'lat': 18.9667, 'lon': -97.9000},
    'Tlachichuca': {'lat': 19.1056, 'lon': -97.4208},
    'Tochtepec': {'lat': 18.8367, 'lon': -97.8314}
}

# 1. Loading data safely with caching
@st.cache_data
def load_data():
    # Read matrix, dropping completely empty rows
    df = pd.read_csv('Matriz_de_Violencias-CorredorCentroOriente.csv')
    df = df.dropna(subset=['ANIO'])
    df['ANIO'] = df['ANIO'].astype(int)
    df['CVE_MUN'] = df['CVE_MUN'].astype(int)
    df['POBLACION'] = df['POBLACION'].astype(int)
    
    # Fill NaN values in crime metrics with 0
    crime_cols = [c for c in df.columns if c.startswith('D') or c.startswith('TASA_')]
    df[crime_cols] = df[crime_cols].fillna(0)
    
    # Clean up municipal names if there are any encoding artifacts
    df['NOMGEO'] = df['NOMGEO'].apply(clean_text)
    
    return df

@st.cache_data
def load_dictionary():
    dict_df = pd.read_csv('Diccionario_Datos_Matriz.csv')
    # Clean string columns in the dictionary
    for col in ['Delito_asociado', 'Categoria_de_violencia', 'Descripcion', 'Observaciones']:
        dict_df[col] = dict_df[col].apply(clean_text)
    return dict_df

# Load the datasets
try:
    df_raw = load_data()
    dict_raw = load_dictionary()
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.stop()

# Build title and header
st.markdown("""
<div class="title-banner">
    <h1 style="margin:0; font-size:32px;">Plataforma de Análisis de Violencias</h1>
    <p style="margin:5px 0 0 0; font-size:16px; opacity:0.9;">
        Corredor Centro-Oriente, Estado de Puebla, México • Periodo 2015 - 2024
    </p>
</div>
""", unsafe_allow_html=True)

# 2. Sidebar Filters Setup
st.sidebar.markdown("## ⚙️ Panel de Filtros")

# Year Selector
available_years = sorted(df_raw['ANIO'].unique().tolist())
selected_years = st.sidebar.multiselect(
    "Seleccionar Años:",
    options=available_years,
    default=available_years,
    help="Filtre los datos para uno o más años en el periodo de estudio."
)

# Municipality Selector
available_muns = sorted(df_raw['NOMGEO'].unique().tolist())
selected_muns = st.sidebar.multiselect(
    "Seleccionar Municipios:",
    options=available_muns,
    default=available_muns,
    help="Filtre o compare municipios específicos del Corredor."
)

# Metric Selector
metric_option = st.sidebar.radio(
    "Métrica de Análisis:",
    options=["Casos Absolutos (Frecuencia)", "Tasas por 100,000 Habitantes"],
    index=1,
    help="Casos Absolutos muestra la frecuencia pura. Las tasas permiten la comparación justa normalizando diferencias poblacionales."
)
is_rate = metric_option == "Tasas por 100,000 Habitantes"

# Category Selector
categories_available = [cat for cat in dict_raw['Categoria_de_violencia'].unique() if cat != 'No aplica']
selected_category = st.sidebar.selectbox(
    "Categoría de Violencia:",
    options=categories_available,
    index=0,
    help="Filtre los indicadores por su ámbito de vulneración social."
)

# Filter Data according to user choices
filtered_df = df_raw.copy()
if selected_years:
    filtered_df = filtered_df[filtered_df['ANIO'].isin(selected_years)]
if selected_muns:
    filtered_df = filtered_df[filtered_df['NOMGEO'].isin(selected_muns)]

# Map category to specific columns from dictionary
category_dictionary = dict_raw[dict_raw['Categoria_de_violencia'] == selected_category]
crimes_list = category_dictionary['Delito_asociado'].dropna().unique().tolist()

# Construct crime mapping (Delito -> (Absolute_Col, Rate_Col, Description))
crime_mapping = {}
for crime in crimes_list:
    crime_rows = category_dictionary[category_dictionary['Delito_asociado'] == crime]
    
    # Grab the field name that starts with D and has digits (absolute)
    abs_cols = crime_rows[crime_rows['Campo'].str.match(r'^D\d+$', na=False)]['Campo'].values
    # Grab the field name that starts with TASA_ (rate)
    rate_cols = crime_rows[crime_rows['Campo'].str.match(r'^TASA_D\d+$', na=False)]['Campo'].values
    
    if len(abs_cols) > 0 and len(rate_cols) > 0:
        crime_mapping[crime] = {
            'abs_col': abs_cols[0],
            'rate_col': rate_cols[0],
            'desc': crime_rows['Descripcion'].values[0]
        }

# Get list of columns to analyze based on selection (absolute or rate)
active_cols_map = {crime: (info['rate_col'] if is_rate else info['abs_col']) for crime, info in crime_mapping.items()}
active_cols = list(active_cols_map.values())

# Show warning if no filters are selected
if not selected_years or not selected_muns:
    st.warning("⚠️ Por favor, seleccione al menos un Año y un Municipio en el panel de control lateral.")
    st.stop()

# Pre-calculate aggregated values for KPI cards
# Sum of cases or mean of rates
total_population = filtered_df.groupby('ANIO')['POBLACION'].sum().max() # peak population analyzed
if is_rate:
    # Weighted rate or average rate? Typically average rate in selection or sum of cases / population * 100k.
    # To be precise, let's compute the total rates or average rate. Let's calculate the sum of all absolute crimes
    # of this category, divided by total population, multiplied by 100,000 as the global rate! That is statistically correct.
    total_abs_cases = 0
    for crime, info in crime_mapping.items():
        total_abs_cases += filtered_df[info['abs_col']].sum()
    global_rate = (total_abs_cases / filtered_df['POBLACION'].sum() * 100000) if filtered_df['POBLACION'].sum() > 0 else 0
else:
    total_abs_cases = 0
    for crime, info in crime_mapping.items():
        total_abs_cases += filtered_df[info['abs_col']].sum()

# Identify Municipal Crítico
municipal_totals = filtered_df.groupby('NOMGEO')[active_cols].sum().sum(axis=1)
if len(municipal_totals) > 0:
    critical_municipality = municipal_totals.idxmax()
    critical_value = municipal_totals.max()
else:
    critical_municipality = "N/A"
    critical_value = 0

# Identify Delito Prevalente
crime_totals = filtered_df[active_cols].sum()
if len(crime_totals) > 0:
    reverse_cols_map = {v: k for k, v in active_cols_map.items()}
    prevalent_col = crime_totals.idxmax()
    prevalent_crime = reverse_cols_map.get(prevalent_col, "N/A")
    prevalent_value = crime_totals.max()
else:
    prevalent_crime = "N/A"
    prevalent_value = 0

# 3. Create Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Resumen y Mapa", 
    "📈 Tendencia Temporal", 
    "📊 Estructura y Comparativa", 
    "📋 Datos y Diccionario"
])

# ==================== TAB 1: RESUMEN Y MAPA ====================
with tab1:
    st.subheader("Análisis Situacional Geográfico")
    st.markdown("""
    Esta sección ofrece un panorama espacial de la categoría seleccionada dentro del corredor de Puebla. 
    El mapa interactivo y el ranking municipal permiten identificar focos rojos de atención.
    """)
    
    # KPI metrics row
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    
    with col_kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Población de Referencia</div>
            <div class="metric-value">{total_population:,.0f} hab.</div>
            <p style='margin:0; font-size:12px; color:#95a5a6;'>Población máxima del conjunto</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_kpi2:
        if is_rate:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #e74c3c;">
                <div class="metric-label">Tasa General Agregada</div>
                <div class="metric-value">{global_rate:,.2f}</div>
                <p style='margin:0; font-size:12px; color:#95a5a6;'>Casos por cada 100k hab.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #e74c3c;">
                <div class="metric-label">Casos Acumulados</div>
                <div class="metric-value">{total_abs_cases:,.0f} delitos</div>
                <p style='margin:0; font-size:12px; color:#95a5a6;'>Suma total en periodo</p>
            </div>
            """, unsafe_allow_html=True)
            
    with col_kpi3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #f39c12;">
            <div class="metric-label">Municipio Crítico</div>
            <div class="metric-value">{critical_municipality}</div>
            <p style='margin:0; font-size:12px; color:#95a5a6;'>{critical_value:,.2f} {'tasas ac. ' if is_rate else 'casos sumados'}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_kpi4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #3498db;">
            <div class="metric-label">Delito Prevalente</div>
            <div class="metric-value" style="font-size: 18px; line-height: 1.2; padding-top: 5px;">{prevalent_crime}</div>
            <p style='margin:0; font-size:12px; color:#95a5a6;'>{prevalent_value:,.2f} {'tasas ac.' if is_rate else 'casos sumados'}</p>
        </div>
        """, unsafe_allow_html=True)

    # Map and Ranking Row
    col_map, col_ranking = st.columns([3, 2])
    
    # Prepare Map Data
    map_agg = filtered_df.groupby('NOMGEO')[active_cols].sum().sum(axis=1).reset_index()
    map_agg.columns = ['NOMGEO', 'valor']
    
    # Join with Coordinates
    map_data = []
    for m_name in map_agg['NOMGEO'].unique():
        if m_name in COORDINATES:
            val = map_agg[map_agg['NOMGEO'] == m_name]['valor'].values[0]
            map_data.append({
                'Municipio': m_name,
                'Valor': val,
                'lat': COORDINATES[m_name]['lat'],
                'lon': COORDINATES[m_name]['lon']
            })
    map_df = pd.DataFrame(map_data)
    
    with col_map:
        st.subheader("Geolocalización del Fenómeno (Puebla)")
        if not map_df.empty:
            # Create interactive scatter mapbox
            fig_map = px.scatter_mapbox(
                map_df,
                lat="lat",
                lon="lon",
                size="Valor",
                color="Valor",
                color_continuous_scale=px.colors.sequential.Reds,
                hover_name="Municipio",
                hover_data={"lat": False, "lon": False, "Valor": ":,.2f"},
                zoom=8.8,
                center={"lat": 19.0, "lon": -97.6},
                mapbox_style="open-street-map",
                height=500
            )
            fig_map.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0},
                coloraxis_colorbar=dict(title="Métrica" if not is_rate else "Tasa Acum.")
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No hay datos geográficos disponibles para la selección actual.")
            
    with col_ranking:
        st.subheader("Ranking de Municipios")
        ranking_sorted = map_agg.sort_values(by="valor", ascending=True)
        
        fig_ranking = px.bar(
            ranking_sorted,
            x="valor",
            y="NOMGEO",
            orientation="h",
            color="valor",
            color_continuous_scale=px.colors.sequential.OrRd,
            labels={"valor": "Valor Acumulado", "NOMGEO": "Municipio"},
            text_auto='.2f' if is_rate else ',.0f',
            height=500
        )
        fig_ranking.update_layout(
            showlegend=False,
            margin={"r":10,"t":20,"l":10,"b":10},
            xaxis_title=metric_option,
            yaxis_title=None,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_ranking, use_container_width=True)

# ==================== TAB 2: TENDENCIA TEMPORAL ====================
with tab2:
    st.subheader("Evolución Histórica de las Violencias")
    st.markdown("""
    Este gráfico permite observar la trayectoria de cada delito bajo la categoría seleccionada. 
    Es de gran utilidad para verificar si las políticas de seguridad o eventos socioeconómicos han tenido un impacto en la incidencia.
    """)
    
    # Process line chart data
    temporal_df = filtered_df.groupby('ANIO')[active_cols].sum().reset_index()
    
    # Pivot columns back to rows for clean plotting
    melted_temp = temporal_df.melt(id_vars=['ANIO'], value_vars=active_cols, var_name='Campo_Col', value_name='Valor')
    
    # Map field code back to crime name
    reverse_cols_map = {v: k for k, v in active_cols_map.items()}
    melted_temp['Delito'] = melted_temp['Campo_Col'].map(reverse_cols_map)
    
    fig_line = px.line(
        melted_temp,
        x="ANIO",
        y="Valor",
        color="Delito",
        markers=True,
        labels={"ANIO": "Año de Registro", "Valor": "Valor Registrado", "Delito": "Tipo de Delito"},
        title=f"Tendencia Histórica: {selected_category} ({metric_option})",
        color_discrete_sequence=px.colors.qualitative.Dark24,
        height=550
    )
    
    fig_line.update_layout(
        xaxis=dict(tickmode='linear', tick0=2015, dtick=1),
        margin={"r":20,"t":50,"l":20,"b":50},
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Multi-variable stacked area chart
    st.subheader("Composición Acumulada Anual")
    fig_area = px.area(
        melted_temp,
        x="ANIO",
        y="Valor",
        color="Delito",
        labels={"ANIO": "Año de Registro", "Valor": "Valor Acumulado", "Delito": "Tipo de Delito"},
        title="Participación de cada delito en el tiempo",
        color_discrete_sequence=px.colors.qualitative.Dark24,
        height=450
    )
    fig_area.update_layout(
        xaxis=dict(tickmode='linear', tick0=2015, dtick=1),
        margin={"r":20,"t":40,"l":20,"b":50},
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_area, use_container_width=True)

# ==================== TAB 3: ESTRUCTURA Y COMPARATIVA ====================
with tab3:
    st.subheader("Composición y Comparación Municipal")
    
    col_comp_left, col_comp_right = st.columns([1, 1])
    
    with col_comp_left:
        st.subheader("Distribución de Delitos en la Categoría")
        st.markdown("¿Cuáles son los delitos que más pesan porcentualmente dentro de la categoría seleccionada?")
        
        # Treemap data
        total_by_crime = melted_temp.groupby('Delito')['Valor'].sum().reset_index()
        
        fig_tree = px.treemap(
            total_by_crime,
            path=['Delito'],
            values='Valor',
            color='Valor',
            color_continuous_scale=px.colors.sequential.Peach,
            labels={'Delito': 'Delito Asociado', 'Valor': 'Volumen Acumulado'},
            height=450
        )
        fig_tree.update_layout(margin={"r":10,"t":20,"l":10,"b":10})
        st.plotly_chart(fig_tree, use_container_width=True)
        
    with col_comp_right:
        st.subheader("Comparador Inteligente de Municipios")
        st.markdown("Seleccione dos municipios de Puebla para contrastar su nivel de vulnerabilidad:")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            mun_a = st.selectbox("Municipio A:", options=available_muns, index=0)
        with col_m2:
            # default to second municipality if available
            mun_b = st.selectbox("Municipio B:", options=available_muns, index=min(2, len(available_muns)-1))
            
        # Extract data for both selected municipalities
        comp_df = df_raw[df_raw['NOMGEO'].isin([mun_a, mun_b])]
        if selected_years:
            comp_df = comp_df[comp_df['ANIO'].isin(selected_years)]
            
        comp_agg = comp_df.groupby(['NOMGEO'])[active_cols].mean() if is_rate else comp_df.groupby(['NOMGEO'])[active_cols].sum()
        comp_agg = comp_agg.reset_index().melt(id_vars=['NOMGEO'], value_vars=active_cols, var_name='Campo_Col', value_name='Valor')
        comp_agg['Delito'] = comp_agg['Campo_Col'].map(reverse_cols_map)
        
        fig_comp = px.bar(
            comp_agg,
            x="Delito",
            y="Valor",
            color="NOMGEO",
            barmode="group",
            labels={"Valor": "Tasa Media" if is_rate else "Casos Sumados", "Delito": "Delito", "NOMGEO": "Municipio"},
            title=f"Contraste Directo: {mun_a} vs {mun_b}",
            color_discrete_map={mun_a: "#c0392b", mun_b: "#2980b9"},
            height=400
        )
        fig_comp.update_layout(
            xaxis_tickangle=-45,
            margin={"r":10,"t":40,"l":10,"b":80},
            legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # --- NUEVA SECCIÓN: HALLAZGOS ---
        st.subheader("💡 Hallazgos Clave")
        
        # Calcular totales para comparar
        total_mun_a = comp_df[comp_df['NOMGEO'] == mun_a][active_cols].sum().sum()
        total_mun_b = comp_df[comp_df['NOMGEO'] == mun_b][active_cols].sum().sum()
        
        if total_mun_a > total_mun_b:
            diferencia = ((total_mun_a - total_mun_b) / total_mun_b * 100) if total_mun_b > 0 else 100
            st.markdown(f"**{mun_a}** presenta una incidencia mayor que **{mun_b}**, con una diferencia aproximada del **{diferencia:.1f}%** en la categoría seleccionada.")
        elif total_mun_b > total_mun_a:
            diferencia = ((total_mun_b - total_mun_a) / total_mun_a * 100) if total_mun_a > 0 else 100
            st.markdown(f"**{mun_b}** presenta una incidencia mayor que **{mun_a}**, con una diferencia aproximada del **{diferencia:.1f}%** en la categoría seleccionada.")
        else:
            st.markdown(f"Ambos municipios, **{mun_a}** y **{mun_b}**, presentan niveles de incidencia similares en la categoría seleccionada.")
        # ---------------------------------

# ==================== TAB 4: DATOS Y DICCIONARIO ====================
with tab4:
    st.subheader("Gobernanza y Transparencia de Datos")
    
    st.markdown("""
    En esta sección puede auditar las fuentes, explorar las descripciones formales de los delitos, 
    consultar las fórmulas empleadas para el cálculo de tasas y descargar los datos crudos filtrados.
    """)
    
    st.subheader("Diccionario Metodológico del Tablero")
    
    # Allow filtering dictionary
    search_dict = st.text_input("🔍 Buscar en el Diccionario de Datos (por delito, categoría o campo):", "")
    
    dict_display = dict_raw.copy()
    if search_dict:
        dict_display = dict_display[
            dict_display['Campo'].str.contains(search_dict, case=False, na=False) |
            dict_display['Delito_asociado'].str.contains(search_dict, case=False, na=False) |
            dict_display['Categoria_de_violencia'].str.contains(search_dict, case=False, na=False) |
            dict_display['Descripcion'].str.contains(search_dict, case=False, na=False)
        ]
        
    st.dataframe(
        dict_display[['Campo', 'Delito_asociado', 'Categoria_de_violencia', 'Descripcion', 'Formula_o_origen', 'Observaciones']],
        use_container_width=True,
        hide_index=True
    )
    
    st.subheader("Datos Consultados en la Matriz")
    st.markdown(f"Registros resultantes de los filtros seleccionados (Total de renglones: `{len(filtered_df)}`):")
    
    # Columns to show in table
    columns_to_show = ['CVE_MUN', 'NOMGEO', 'ANIO', 'POBLACION'] + active_cols
    
    st.dataframe(
        filtered_df[columns_to_show].sort_values(by=['ANIO', 'NOMGEO']),
        use_container_width=True,
        hide_index=True
    )
    
    # Download Button
    csv_data = filtered_df[columns_to_show].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Tabla en Formato CSV",
        data=csv_data,
        file_name=f"Matriz_Violencias_Puebla_Filtrada.csv",
        mime="text/csv",
        help="Descargue los registros actualmente visualizados para análisis externo."
    )
