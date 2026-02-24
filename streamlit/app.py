import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Inmobiliario", layout="wide")

# ==============================
# CARGAR DATOS
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("cucutaventacasas.csv")
    return df

df_original = load_data()
df = df_original.copy()

st.title("📊 Dashboard Inmobiliario Interactivo")

# ==============================
# SELECCIÓN DE COLUMNAS VISIBLES
# ==============================
st.sidebar.header("⚙️ Configuración")

columnas_seleccionadas = st.sidebar.multiselect(
    "Selecciona columnas visibles",
    df.columns,
    default=df.columns.tolist()
)

df = df[columnas_seleccionadas]

# ==============================
# FILTROS DINÁMICOS
# ==============================
st.sidebar.header("🔎 Filtros")

for col in df.columns:
    if df[col].dtype == "object":
        valores = st.sidebar.multiselect(
            f"{col}",
            options=df[col].dropna().unique(),
            default=df[col].dropna().unique()
        )
        df = df[df[col].isin(valores)]

    elif df[col].dtype in ["int64", "float64"]:

        min_val = float(df[col].min())
        max_val = float(df[col].max())

        st.sidebar.markdown(f"**{col}**")

        min_input = st.sidebar.number_input(
            f"{col} mínimo",
            value=min_val,
            step=1.0
        )

        max_input = st.sidebar.number_input(
            f"{col} máximo",
            value=max_val,
            step=1.0
        )

        df = df[(df[col] >= min_input) & (df[col] <= max_input)]

# ==============================
# KPIs
# ==============================
st.subheader("📌 Indicadores")

col1, col2, col3 = st.columns(3)

numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

if numeric_cols:
    metrica_kpi = st.selectbox("Selecciona métrica KPI", numeric_cols)

    col1.metric("Total registros", len(df))
    col2.metric("Suma", f"{df[metrica_kpi].sum():,.0f}")
    col3.metric("Promedio", f"{df[metrica_kpi].mean():,.2f}")
else:
    st.warning("No hay columnas numéricas disponibles para KPIs.")

# ==============================
# GRÁFICO DINÁMICO
# ==============================
st.subheader("📈 Visualización Dinámica")

if len(numeric_cols) > 0:
    col_x = st.selectbox("Eje X (categoría)", df.columns)
    col_y = st.selectbox("Eje Y (métrica)", numeric_cols)

    tipo_agregacion = st.selectbox(
        "Tipo de cálculo",
        ["Suma", "Promedio", "Conteo"]
    )

    if tipo_agregacion == "Suma":
        df_group = df.groupby(col_x)[col_y].sum().reset_index()
    elif tipo_agregacion == "Promedio":
        df_group = df.groupby(col_x)[col_y].mean().reset_index()
    else:
        df_group = df.groupby(col_x)[col_y].count().reset_index()

    fig = px.bar(df_group, x=col_x, y=col_y)
    st.plotly_chart(fig, use_container_width=True)

# ==============================
# TABLA FILTRADA
# ==============================
st.subheader("📋 Datos Filtrados")

st.dataframe(df, use_container_width=True)

# ==============================
# DESCARGAR DATOS
# ==============================
csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Descargar datos filtrados",
    csv,
    "datos_filtrados.csv",
    "text/csv"
)