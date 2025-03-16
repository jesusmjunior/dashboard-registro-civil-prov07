import streamlit as st
import pandas as pd
import altair as alt

# ===================== CONFIGURAÇÃO =====================
st.set_page_config(
    page_title="Dashboard Registro Civil - Provimento 07",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("\U0001F4CA Dashboard Registro Civil - Provimento 07")

# ===================== FUNÇÃO: Carregar Dados =====================
@st.cache_data(ttl=3600)
def carregar_planilha():
    sheet_url = "https://docs.google.com/spreadsheets/d/1k_aWceBCN_V0VaRJa1Jw42t6hfrER4T4bE2fS88mLDI/export?format=xlsx"
    df_dict = pd.read_excel(sheet_url, sheet_name=None)
    origem = "Planilha Online"
    return df_dict, origem

# ===================== LOAD DATA =====================
st.sidebar.header("\U0001F4C2 Seleção de Aba")
dados, origem = carregar_planilha()
abas_selecionadas = ["Respostas ao formulário 2", "QUANTITATIVO (2024 E 2025)"]
aba_selecionada = st.sidebar.radio("Selecione uma aba:", abas_selecionadas)

st.caption(f"Fonte dos dados: {origem}")
df = dados[aba_selecionada]

# ===================== ABA 1: Respostas ao formulário 2 =====================
if aba_selecionada == "Respostas ao formulário 2":
    st.header("\U0001F4DD Respostas ao Formulário 2")

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
        label="\U0001F4E5 Baixar CSV",
        data=csv.encode('utf-8-sig'),
        file_name="respostas_formulario2_filtrado.csv",
        mime='text/csv'
    )

# ===================== ABA 2: QUANTITATIVO (2024 E 2025) =====================
elif aba_selecionada == "QUANTITATIVO (2024 E 2025)":
    st.header("\U0001F4C8 Quantitativo (2024 e 2025)")

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
        label="\U0001F4E5 Baixar CSV",
        data=csv.encode('utf-8-sig'),
        file_name="quantitativo_2024_2025.csv",
        mime='text/csv'
    )

# ===================== FINAL =====================
st.success("\u2705 Dashboard carregado com sucesso!")
