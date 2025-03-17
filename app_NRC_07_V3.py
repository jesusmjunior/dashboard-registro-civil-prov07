import streamlit as st
import pandas as pd
import altair as alt

# ===================== CONFIGURAÇÃO =====================
st.set_page_config(
    page_title="CORREGEDORIA DO FORO EXTRAJUDICIAL NRC 2025",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== CABEÇALHO COM IMAGEM E TÍTULO =====================
col1, col2 = st.columns([6, 1])  # Espaço maior à esquerda

with col1:
    st.title("📊 Relatório de Registro Civil - Unidade Interligada PROV 07 2021 22/02/2021 - CORREGEDORIA DO FORO EXTRAJUDICIAL NRC 2025")
    st.subheader("📄 DADOS DO FORMULÁRIO OBRIGATÓRIO DAS UNIDADES INTERLIGADAS - PROV 07")

with col2:
    st.image("https://raw.githubusercontent.com/jesusmjunior/dashboard-registro-civil-prov07/main/CGX.png", width=120)

# ===================== AVISO UNIDADE INTERLIGADA =====================
st.warning("🚨 **ATENÇÃO! UNIDADE INTERLIGADA!**\n\nAcesse e preencha/atualize seus dados do Provimento 07/2021.", icon="⚠️")
st.markdown("[📝 **Clique aqui para acessar o Formulário Obrigatório**](https://forms.gle/vETZAjAStN3F9YHx9)")

# ===================== RESUMO DO PROVIMENTO =====================
with st.expander("ℹ️ Sobre o Provimento 07/2021 - Clique para detalhes"):
    st.markdown("""
**Resumo do Provimento CGJ:**

A instalação de unidades interligadas em hospitais é obrigatória, independentemente do número de partos. Os registros de nascimento e óbito são feitos nessas unidades com livro próprio. Os serviços devem enviar relatório mensal até o dia 10 via [Formulário Online](https://forms.gle/vETZAjAStN3F9YHx9), sob pena de sanções administrativas.

**Desembargador José Jorge Figueiredo dos Anjos**  
Corregedor-Geral da Justiça (Biênio 2024-2026)
""")
# ===================== LINKS DAS ABAS (CSV) =====================
sheet_id = "1k_aWceBCN_V0VaRJa1Jw42t6hfrER4T4bE2fS88mLDI"
base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet="

# ID da planilha SUB-REGISTRO separada
subregistro_sheet_id = "1UD1B9_5_zwd_QD0drE1fo3AokpE6EDnYTCwywrGkD-Y"
subregistro_base_url = f"https://docs.google.com/spreadsheets/d/{subregistro_sheet_id}/gviz/tq?tqx=out:csv&sheet=subregistro"

sheet_urls = {
    "RESPOSTAS AO FORMULÁRIO CAIXA DE ENTRADA": f"{base_url}Respostas%20ao%20formul%C3%A1rio%202",
    "QUANTITATIVO (2024 E 2025)": f"{base_url}QUANTITATIVO%20(2024%20E%202025)",
    "DADOS FILTRADOS DA CAIXA DE ENTRADA": f"{base_url}(N%C3%83O%20ALTERE%20OS%20FILTROS%20OU%20DADOS)",
    "DADOS DE RECEBIMENTO DO FORMULÁRIO POR MUNICÍPIO": f"{base_url}P%C3%A1gina11",
    "STATUS DE RECEBIMENTO": f"{base_url}STATUS%20DE%20RECEBIMENTO",
    "GRAPH SITE": f"{base_url}GRAPH%20SITE",
    "DADOS ORGANIZADOS": f"{base_url}DADOS%20ORGANIZADOS",
    "SUB-REGISTRO": subregistro_base_url  # Nova aba incluída
}

# ===================== FUNÇÃO: Carregar Dados =====================
@st.cache_data(ttl=3600)
def carregar_planilha(aba):
    df = pd.read_csv(sheet_urls[aba])
    origem = "Planilha Pública Online (CSV)"
    return df, origem

# ===================== LOAD DATA =====================
st.sidebar.header("📂 COGEX NRC 2025- PROV 07 - DADOS DO FORMULÁRIO")
abas_selecionadas = list(sheet_urls.keys())
aba_selecionada = st.sidebar.radio("Selecione uma aba:", abas_selecionadas)

df, origem = carregar_planilha(aba_selecionada)
st.caption(f"Fonte dos dados: {origem}")

# ===================== Função para gráficos padrão =====================
def gerar_grafico_barras(df_filtrado, grupo, colunas_sum, titulo):
    bar_data = df_filtrado.groupby(grupo)[colunas_sum].sum().reset_index()
    bar_data_melt = bar_data.melt(id_vars=grupo, var_name='Tipo', value_name='Total')
    bar_chart = alt.Chart(bar_data_melt).mark_bar().encode(
        x=alt.X(f"{grupo}:N", sort='-y'),
        y="Total:Q",
        color="Tipo:N",
        tooltip=[grupo, 'Tipo', 'Total']
    ).properties(title=titulo)
    st.altair_chart(bar_chart, use_container_width=True)
# ===================== ABA: RESPOSTAS AO FORMULÁRIO CAIXA DE ENTRADA =====================
if aba_selecionada == "RESPOSTAS AO FORMULÁRIO CAIXA DE ENTRADA":
    st.header("📝 Respostas ao Formulário 2")

    col1, col2 = st.sidebar.columns(2)
    municipios = col1.multiselect("Município:", df["MUNICÍPIO"].dropna().unique(), default=df["MUNICÍPIO"].dropna().unique())
    anos = col2.multiselect("Ano:", df["Ano"].dropna().unique(), default=df["Ano"].dropna().unique())

    df_filtrado = df[(df["MUNICÍPIO"].isin(municipios)) & (df["Ano"].isin(anos))]

    st.metric("Total de Registros", df_filtrado.shape[0])
    st.metric("Total Municípios", df_filtrado["MUNICÍPIO"].nunique())

    st.dataframe(df_filtrado, use_container_width=True)

    if not df_filtrado.empty:
        gerar_grafico_barras(df_filtrado, "MUNICÍPIO", ['NASCIMENTOS (QTDE)', 'REGISTROS (QTDE)'], "Nascimentos x Registros por Município")

    csv = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button("📥 Baixar CSV", data=csv.encode('utf-8-sig'), file_name="respostas_formulario2.csv", mime='text/csv')

# ===================== ABA: QUANTITATIVO (2024 E 2025) =====================
elif aba_selecionada == "QUANTITATIVO (2024 E 2025)":
    st.header("📊 Quantitativo (2024 e 2025)")
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    st.metric("Total de Registros", df.shape[0])
    st.dataframe(df, use_container_width=True)

    try:
        soma_nascimentos = df['NASCIMENTOS (QTDE)'].sum()
        soma_registros = df['REGISTROS (QTDE)'].sum()
        bar_df = pd.DataFrame({'Tipo': ['NASCIMENTOS (QTDE)', 'REGISTROS (QTDE)'], 'Total': [soma_nascimentos, soma_registros]})
        bar_chart = alt.Chart(bar_df).mark_bar().encode(x='Tipo:N', y='Total:Q', tooltip=['Tipo', 'Total']).properties(title="Total Nascimentos x Registros")
        st.altair_chart(bar_chart, use_container_width=True)
    except Exception:
        st.warning("Não foi possível gerar gráfico para esta aba.")

    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button("📥 Baixar CSV", data=csv.encode('utf-8-sig'), file_name="quantitativo_2024_2025.csv", mime='text/csv')

# ===================== ABA: DADOS FILTRADOS DA CAIXA DE ENTRADA =====================
elif aba_selecionada == "DADOS FILTRADOS DA CAIXA DE ENTRADA":
    st.header("📋 DADOS FILTRADOS DA CAIXA DE ENTRADA")

    municipios = st.sidebar.multiselect("Município:", df["MUNICÍPIO"].dropna().unique(), default=df["MUNICÍPIO"].dropna().unique())
    df_filtrado = df[df["MUNICÍPIO"].isin(municipios)]

    st.metric("Total de Registros", df_filtrado.shape[0])
    st.dataframe(df_filtrado, use_container_width=True)

    gerar_grafico_barras(df_filtrado, "MUNICÍPIO", ['NASCIMENTOS (QTDE)', 'REGISTROS (QTDE)'], "Nascimentos x Registros por Município")

    csv = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button("📥 Baixar CSV", data=csv.encode('utf-8-sig'), file_name="filtros_ou_dados.csv", mime='text/csv')

# ===================== ABA: DADOS DE RECEBIMENTO DO FORMULÁRIO POR MUNICÍPIO =====================
elif aba_selecionada == "DADOS DE RECEBIMENTO DO FORMULÁRIO POR MUNICÍPIO":
    st.header("📄 Dados de Recebimento do Formulário por Município")

    municipios = st.sidebar.multiselect("Município:", df["MUNICÍPIO"].dropna().unique(), default=df["MUNICÍPIO"].dropna().unique())
    df_filtrado = df[df["MUNICÍPIO"].isin(municipios)]

    st.metric("Total de Registros", df_filtrado.shape[0])
    st.dataframe(df_filtrado, use_container_width=True)

    gerar_grafico_barras(df_filtrado, "MUNICÍPIO", ['NASCIMENTOS (QTDE)', 'REGISTROS (QTDE)'], "Nascimentos x Registros por Município")

    csv = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button("📥 Baixar CSV", data=csv.encode('utf-8-sig'), file_name="pagina11.csv", mime='text/csv')
# ===================== ABA: STATUS DE RECEBIMENTO =====================
elif aba_selecionada == "STATUS DE RECEBIMENTO":
    st.header("📄 Status de Recebimento")

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    municipios = st.sidebar.multiselect("Município:", df["MUNICÍPIO"].dropna().unique(), default=df["MUNICÍPIO"].dropna().unique())
    anos = st.sidebar.multiselect("Ano:", df["Ano"].dropna().unique(), default=df["Ano"].dropna().unique())
    cumprimento = st.sidebar.multiselect("Cumprimento Prazo Prov 07:", df["CUMPRIMENTO DE PRAZO PROV 07 2021"].dropna().unique(), default=df["CUMPRIMENTO DE PRAZO PROV 07 2021"].dropna().unique())

    df_filtrado = df[(df["MUNICÍPIO"].isin(municipios)) & (df["Ano"].isin(anos)) & (df["CUMPRIMENTO DE PRAZO PROV 07 2021"].isin(cumprimento))]

    st.metric("Total de Registros", df_filtrado.shape[0])
    st.dataframe(df_filtrado, use_container_width=True)

    if not df_filtrado.empty:
        gerar_grafico_barras(df_filtrado, "MUNICÍPIO", ['NASCIMENTOS (QTDE)', 'REGISTROS (QTDE)'], "Nascimentos x Registros por Município")

    csv = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button("📥 Baixar CSV", data=csv.encode('utf-8-sig'), file_name="status_recebimento.csv", mime='text/csv')

# ===================== ABA: PIORES ÍNDICES SUB-REGISTRO =====================
elif aba_selecionada == "PIORES ÍNDICES SUB-REGISTRO":
    st.header("⚠️ Municípios com Piores Índices de Sub-registro IBGE")

    # URL direto da aba "subregistro"
    sub_url = "https://docs.google.com/spreadsheets/d/1UD1B9_5_zwd_QD0drE1fo3AokpE6EDnYTCwywrGkD-Y/gviz/tq?tqx=out:csv&sheet=subregistro"

    df_sub = pd.read_csv(sub_url)
    df_sub.columns = df_sub.columns.str.strip()

    # Limpar e ordenar pelos piores índices
    df_sorted = df_sub[['Nome Município', 'Sub-registro IBGE(1)']].sort_values(by='Sub-registro IBGE(1)', ascending=False)

    st.metric("Total de Municípios", df_sorted.shape[0])
    st.dataframe(df_sorted, use_container_width=True)

    # Gráfico TOP 10 Piores
    import altair as alt
    chart = alt.Chart(df_sorted.head(10)).mark_bar().encode(
        x=alt.X('Sub-registro IBGE(1):Q', title='Índice de Sub-registro (%)'),
        y=alt.Y('Nome Município:N', sort='-x'),
        color=alt.value('#d62728'),
        tooltip=['Nome Município', 'Sub-registro IBGE(1)']
    ).properties(title='Top 10 Municípios com Piores Índices de Sub-registro')
    st.altair_chart(chart, use_container_width=True)

    # Download CSV
    csv = df_sorted.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button("📥 Baixar CSV Sub-registro", data=csv.encode('utf-8-sig'), file_name="piores_indices_subregistro.csv", mime='text/csv')

# ===================== ABA: GRAPH SITE =====================
elif aba_selecionada == "GRAPH SITE":
    st.header("📈 Nascimentos x Registros - Graph Site")

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.strip()  # Remove espaços extras

    if not df.empty and {'Ano/Mês', 'NASCIMENTOS (QTDE)', 'SUM de REGISTROS (QTDE)'}.issubset(df.columns):
        st.dataframe(df, use_container_width=True)

        # Ajusta formato dos dados
        df_melt = df.melt(id_vars='Ano/Mês', value_vars=['NASCIMENTOS (QTDE)', 'SUM de REGISTROS (QTDE)'],
                          var_name='Tipo', value_name='Total')

        # Área preenchida
        area = alt.Chart(df_melt).mark_area(opacity=0.3).encode(
            x=alt.X('Ano/Mês:N', sort=None),
            y='Total:Q',
            color=alt.Color('Tipo:N', scale=alt.Scale(scheme='set1')),
            tooltip=['Ano/Mês', 'Tipo', 'Total']
        )

        # Linha conectando
        line = alt.Chart(df_melt).mark_line().encode(
            x='Ano/Mês:N',
            y='Total:Q',
            color='Tipo:N'
        )

        # Pontos marcados
        points = alt.Chart(df_melt).mark_point(filled=True).encode(
            x='Ano/Mês:N',
            y='Total:Q',
            color='Tipo:N'
        )

        # Combinação final
        grafico = (area + line + points).properties(title="📊 Nascimentos x Registros por Ano/Mês")
        st.altair_chart(grafico, use_container_width=True)

        # Download CSV
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.sidebar.download_button("📥 Baixar CSV", data=csv.encode('utf-8-sig'), file_name="graph_site.csv", mime='text/csv')

    else:
        st.warning("⚠️ Colunas necessárias não encontradas para gerar gráfico.")
# ===================== ABA: DADOS ORGANIZADOS =====================
elif aba_selecionada == "DADOS ORGANIZADOS":
    st.header("📑 Dados Organizados")

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.strip()

    if not df.empty and 'MUNICÍPIOS' in df.columns:
        municipios = st.sidebar.multiselect("Município:", df["MUNICÍPIOS"].dropna().unique(), default=df["MUNICÍPIOS"].dropna().unique())
        df_filtrado = df[df["MUNICÍPIOS"].isin(municipios)]
    else:
        df_filtrado = df

    st.metric("Total de Registros", df_filtrado.shape[0])
    st.dataframe(df_filtrado, use_container_width=True)

    csv = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button("📥 Baixar CSV", data=csv.encode('utf-8-sig'), file_name="dados_organizados.csv", mime='text/csv')
# ===================== ABA: SUB-REGISTRO =====================
elif aba_selecionada == "SUB-REGISTRO":
    st.header("⚠️ Índices de Sub-registro IBGE por Município - DATA SET ORGANIZADO 17/04/2024")

    # Limpar colunas
    df.columns = df.columns.str.strip()

    # Ordenar pelos piores índices de sub-registro
    df_sorted = df[['Nome Município', 'Sub-registro IBGE(1)']].sort_values(by='Sub-registro IBGE(1)', ascending=False)

    st.metric("Total de Municípios", df_sorted.shape[0])
    st.dataframe(df_sorted, use_container_width=True)

    # Gráfico TOP 10 Piores
    chart = alt.Chart(df_sorted.head(10)).mark_bar().encode(
        x=alt.X('Sub-registro IBGE(1):Q', title='Índice de Sub-registro (%)'),
        y=alt.Y('Nome Município:N', sort='-x'),
        color=alt.value('#d62728'),
        tooltip=['Nome Município', 'Sub-registro IBGE(1)']
    ).properties(title='Top 10 Municípios com Piores Índices de Sub-registro')
    st.altair_chart(chart, use_container_width=True)

    # Download CSV
    csv = df_sorted.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button("📥 Baixar Sub-registro CSV", data=csv.encode('utf-8-sig'), file_name="subregistro.csv", mime='text/csv')

# ===================== FINAL =====================
st.success("✅ Dashboard carregado com sucesso!Todo os Direitos Reservados! COGEX - NRC 2025")
