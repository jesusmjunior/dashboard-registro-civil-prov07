import streamlit as st
import pandas as pd
import altair as alt

# ===================== CONFIGURAÇÃO =====================
st.set_page_config(
    page_title="Dashboard Registro Civil - Provimento 07",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard Registro Civil - Provimento 07")

# ===================== LINKS DAS ABAS (CSV) =====================
sheet_id = "1k_aWceBCN_V0VaRJa1Jw42t6hfrER4T4bE2fS88mLDI"
base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet="

sheet_urls = {
    "Respostas ao formulário 2": f"{base_url}Respostas%20ao%20formul%C3%A1rio%202",
    "QUANTITATIVO (2024 E 2025)": f"{base_url}QUANTITATIVO%20(2024%20E%202025)"
}

# ===================== FUNÇÃO: Carregar Dados =====================
@st.cache_data(ttl=3600)
def carregar_planilha(aba):
    df = pd.read_csv(sheet_urls[aba])
    origem = "Planilha Pública Online (CSV)"
    return df, origem

# ===================== LOAD DATA =====================
st.sidebar.header("📂 Seleção de Aba")
abas_selecionadas = list(sheet_urls.keys())
aba_selecionada = st.sidebar.radio("Selecione uma aba:", abas_selecionadas)

df, origem = carregar_planilha(aba_selecionada)
st.caption(f"Fonte dos dados: {origem}")

# ===================== ABA 1: Respostas ao formulário 2 =====================
if aba_selecionada == "Respostas ao formulário 2":
    st.header("📝 Respostas ao Formulário 2")

    col1, col2 = st.sidebar.columns(2)
    municipios = col1.multiselect(
        "Município:", df["MUNICÍPIO"].dropna().unique(), default=df["MUNICÍPIO"].dropna().unique()
    )
    anos = col2.multiselect(
        "Ano:", df["Ano"].dropna().unique(), default=df["Ano"].dropna().unique()
    )

    df_filtrado = df[(df["MUNICÍPIO"].isin(municipios)) & (df["Ano"].isin(anos))]

    st.metric("Total de Registros", df_filtrado.shape[0])
    st.metric("Total Municípios", df_filtrado["MUNICÍPIO"].nunique())

    st.dataframe(df_filtrado, use_container_width=True)

    if not df_filtrado.empty:
        # Gráfico Pizza Distribuição por Município
        pie_data = df_filtrado["MUNICÍPIO"].value_counts().reset_index()
        pie_data.columns = ["Município", "Total"]
        pie_chart = alt.Chart(pie_data).mark_arc().encode(
            theta=alt.Theta(field="Total", type="quantitative"),
            color=alt.Color(field="Município", type="nominal"),
            tooltip=['Município', 'Total']
        ).properties(title="Distribuição por Município")
        st.altair_chart(pie_chart, use_container_width=True)

        # Gráfico Barras Nascimentos e Registros
        bar_data = df_filtrado.groupby("MUNICÍPIO")[['NASCIMENTOS (QTDE)', 'REGISTROS (QTDE)']].sum().reset_index()
        bar_chart = alt.Chart(bar_data).transform_fold(
            ["NASCIMENTOS (QTDE)", "REGISTROS (QTDE)"], as_=["Tipo", "Total"]
        ).mark_bar().encode(
            x=alt.X("MUNICÍPIO:N", sort='-y'),
            y="Total:Q",
            color="Tipo:N",
            tooltip=['MUNICÍPIO', 'Tipo', 'Total']
        ).properties(title="Nascimentos x Registros por Município")
        st.altair_chart(bar_chart, use_container_width=True)

    # Download CSV
    csv = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button(
        label="📥 Baixar CSV",
        data=csv.encode('utf-8-sig'),
        file_name="respostas_formulario2_filtrado.csv",
        mime='text/csv'
    )

# ===================== ABA 2: QUANTITATIVO (2024 E 2025) =====================
elif aba_selecionada == "QUANTITATIVO (2024 E 2025)":
    st.header("📊 Quantitativo (2024 e 2025)")

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    st.metric("Total de Registros", df.shape[0])

    st.dataframe(df, use_container_width=True)

    # Gráfico Barras Nascimentos x Registros Totais
    try:
        soma_nascimentos = df['NASCIMENTOS (QTDE)'].sum()
        soma_registros = df['REGISTROS (QTDE)'].sum()
        bar_df = pd.DataFrame({
            'Tipo': ['NASCIMENTOS (QTDE)', 'REGISTROS (QTDE)'],
            'Total': [soma_nascimentos, soma_registros]
        })
        bar_chart = alt.Chart(bar_df).mark_bar().encode(
            x='Tipo:N',
            y='Total:Q',
            tooltip=['Tipo', 'Total']
        ).properties(title="Total Nascimentos x Registros")
        st.altair_chart(bar_chart, use_container_width=True)
    except Exception:
        st.warning("Não foi possível gerar gráfico para esta aba.")

    # Download CSV
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button(
        label="📥 Baixar CSV",
        data=csv.encode('utf-8-sig'),
        file_name="quantitativo_2024_2025.csv",
        mime='text/csv'
    )

# ===================== FINAL =====================
st.success("✅ Dashboard carregado com sucesso!")
