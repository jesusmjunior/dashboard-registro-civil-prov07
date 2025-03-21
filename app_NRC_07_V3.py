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
col1, col2 = st.columns([6, 1])

with col1:
    st.title("📊 Relatório de Registro Civil - Unidade Interligada PROV 07 2021 22/02/2021 - CORREGEDORIA DO FORO EXTRAJUDICIAL NRC 2025")
    st.subheader("📄 DADOS DO FORMULÁRIO OBRIGATÓRIO DAS UNIDADES INTERLIGADAS - PROV 07")

with col2:
    st.image("https://raw.githubusercontent.com/jesusmjunior/dashboard-registro-civil-prov07/main/CGX.png", width=120)

# ===================== AVISO =====================
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

# ===================== LINKS DAS ABAS =====================
sheet_id = "1k_aWceBCN_V0VaRJa1Jw42t6hfrER4T4bE2fS88mLDI"
base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet="

subregistro_sheet_id = "1UD1B9_5_zwd_QD0drE1fo3AokpE6EDnYTCwywrGkD-Y"
subregistro_base_url = f"https://docs.google.com/spreadsheets/d/{subregistro_sheet_id}/gviz/tq?tqx=out:csv&sheet=subregistro"

csv_publicado = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtKiqlosLL5_CJgGom7BlWpFYExhLTQEjQT_Pdgnv3uEYMlWPpsSeaxfjqy0IxTluVlKSpcZ1IoXQY/pub?output=csv"

sheet_urls = {
    "RESPOSTAS AO FORMULÁRIO CAIXA DE ENTRADA": f"{base_url}Respostas%20ao%20formul%C3%A1rio%202",
    "QUANTITATIVO (2024 E 2025)": f"{base_url}QUANTITATIVO%20(2024%20E%202025)",
    "DADOS FILTRADOS DA CAIXA DE ENTRADA": f"{base_url}(N%C3%83O%20ALTERE%20OS%20FILTROS%20OU%20DADOS)",
    "DADOS DE RECEBIMENTO DO FORMULÁRIO POR MUNICÍPIO": f"{base_url}P%C3%A1gina11",
    "STATUS DE RECEBIMENTO": f"{base_url}STATUS%20DE%20RECEBIMENTO",
    "GRAPH SITE": f"{base_url}GRAPH%20SITE",
    "DADOS ORGANIZADOS": f"{base_url}DADOS%20ORGANIZADOS",
    "SUB-REGISTRO": subregistro_base_url,
    "ANÁLISE DE STATUS": f"{base_url}Respostas%20ao%20formul%C3%A1rio%202"  # NOVA ABA baseada na aba RESPOSTAS
}

# ===================== FUNÇÃO: Carregar Dados =====================
@st.cache_data(ttl=3600)
def carregar_planilha(aba):
    df = pd.read_csv(sheet_urls[aba], low_memory=False, dtype=str)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    origem = "Planilha Pública Online (CSV)"
    return df, origem

# ===================== LOAD DATA =====================
st.sidebar.header("📂 COGEX NRC 2025- PROV 07 - DADOS DO FORMULÁRIO")
abas_selecionadas = list(sheet_urls.keys())
aba_selecionada = st.sidebar.radio("Selecione uma aba:", abas_selecionadas)

df, origem = carregar_planilha(aba_selecionada)
st.caption(f"Fonte dos dados: {origem}")

# ===================== APLICAR FILTROS =====================
abas_com_filtros = [
    "RESPOSTAS AO FORMULÁRIO CAIXA DE ENTRADA",
    "DADOS FILTRADOS DA CAIXA DE ENTRADA",
    "DADOS DE RECEBIMENTO DO FORMULÁRIO POR MUNICÍPIO",
    "STATUS DE RECEBIMENTO",
    "DADOS ORGANIZADOS",
    "SUB-REGISTRO"
]

if aba_selecionada in abas_com_filtros:
    if 'MUNICÍPIO' in df.columns:
        municipios = st.sidebar.selectbox("Filtrar por Município:", ["Choose an option"] + list(df["MUNICÍPIO"].dropna().unique()))
        if municipios != "Choose an option":
            df = df[df["MUNICÍPIO"] == municipios]

    if 'Ano' in df.columns:
        anos = st.sidebar.selectbox("Filtrar por Ano:", ["Choose an option"] + list(df["Ano"].dropna().unique()))
        if anos != "Choose an option":
            df = df[df["Ano"] == anos]

# ===================== MOSTRAR DADOS =====================
else:
    st.dataframe(df, height=1200, use_container_width=True)

# ===================== DOWNLOAD COMPLETO =====================
csv_completo = df.to_csv(index=False, encoding='utf-8-sig')
st.sidebar.download_button("📥 Baixar Todos os Dados CSV", data=csv_completo.encode('utf-8-sig'), file_name=f"{aba_selecionada.lower().replace(' ', '_')}.csv", mime='text/csv')

# ===================== NOVA ABA: ANÁLISE DE STATUS =====================
if aba_selecionada == "ANÁLISE DE STATUS":
    st.header("📊 Análise Detalhada de Envio e Cumprimento")

    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')

    municipios_unicos = df['MUNICÍPIO'].dropna().unique()
    municipio_sel = st.sidebar.selectbox("Selecione um Município para análise:", municipios_unicos)

    anos_unicos = df[df['MUNICÍPIO'] == municipio_sel]['Ano'].dropna().unique()
    ano_sel = st.sidebar.selectbox("Selecione o Ano para análise:", anos_unicos)

    df_municipio = df[(df['MUNICÍPIO'] == municipio_sel) & (df['Ano'] == ano_sel)]

    total_envios = df_municipio.shape[0]
    st.metric("Total de Envios no Ano", total_envios)

    meses_enviados = df_municipio['Mês'].dropna().unique().tolist()
    meses_todos = list(range(1, 13))
    meses_pendentes = sorted(list(set(meses_todos) - set(meses_enviados)))
    st.metric("Meses Pendentes", len(meses_pendentes))
    if meses_pendentes:
        st.warning(f"Meses não enviados: {meses_pendentes}")

    duplicados = df_municipio[df_municipio.duplicated(subset=['Mês', 'Ano'], keep=False)]
    if not duplicados.empty:
        st.warning("⚠️ Foram encontrados registros duplicados para este município e ano.")
        st.dataframe(duplicados)

    # ===== CORREÇÃO DO ERRO AQUI =====
    df_municipio['Carimbo de data/hora'] = pd.to_datetime(df_municipio['Carimbo de data/hora'], errors='coerce')
    df_municipio['Data Limite'] = pd.to_datetime(
        df_municipio['Ano'].fillna(0).astype(int).astype(str) + '-' +
        df_municipio['Mês'].fillna(1).astype(int).astype(str) + '-10',
        errors='coerce'
    )
    df_municipio['Dentro do Prazo'] = df_municipio['Carimbo de data/hora'] <= df_municipio['Data Limite']

    enviados_dentro = df_municipio['Dentro do Prazo'].sum()
    enviados_fora = total_envios - enviados_dentro
    st.metric("Envios Dentro do Prazo", enviados_dentro)
    st.metric("Envios Fora do Prazo", enviados_fora)

    graf = df_municipio.groupby(['Mês', 'Dentro do Prazo']).size().reset_index(name='Total Envios')
    graf['Status'] = graf['Dentro do Prazo'].apply(lambda x: 'Dentro do Prazo' if x else 'Fora do Prazo')

    chart = alt.Chart(graf).mark_bar().encode(
        x=alt.X('Mês:O', title='Mês'),
        y=alt.Y('Total Envios:Q', title='Total Envios'),
        color=alt.Color('Status:N', scale=alt.Scale(domain=['Dentro do Prazo', 'Fora do Prazo'], range=['green', 'red'])),
        tooltip=['Mês', 'Total Envios', 'Status']
    ).properties(title=f"Envios por Mês - {municipio_sel}/{ano_sel}")
    st.altair_chart(chart, use_container_width=True)

    st.subheader("📄 Detalhamento dos Envios")
    st.dataframe(df_municipio, use_container_width=True)
