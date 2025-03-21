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
    "DADOS COMPLETOS": csv_publicado,
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
    "SUB-REGISTRO",
    "DADOS COMPLETOS"
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

# ===================== NOVA ABA: ANÁLISE DE STATUS =====================
if aba_selecionada == "ANÁLISE DE STATUS":
    st.header("📊 Análise Detalhada de Envio e Cumprimento")

    # Preparação dos dados
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')

    municipios_unicos = df['MUNICÍPIO'].dropna().unique()
    municipio_sel = st.sidebar.selectbox("Selecione um Município para análise:", municipios_unicos)

    df_municipio = df[df['MUNICÍPIO'] == municipio_sel]

    # Contagem de registros
    total_envios = df_municipio.shape[0]
    registros_pendentes = 12 - df_municipio['Mês'].nunique()

    st.metric("Total de Envios no Ano", total_envios)
    st.metric("Meses Pendentes", registros_pendentes)

    # Verificar duplicados
    duplicados = df_municipio[df_municipio.duplicated(subset=['Mês', 'Ano'], keep=False)]
    if not duplicados.empty:
        st.warning("⚠️ Foram encontrados registros duplicados para este município.")
        st.dataframe(duplicados)

    # Gráfico de envios por mês
    graf = df_municipio.groupby('Mês').size().reset_index(name='Total Envios')
    chart = alt.Chart(graf).mark_bar().encode(
        x=alt.X('Mês:O', title='Mês'),
        y=alt.Y('Total Envios:Q', title='Total Envios'),
        tooltip=['Mês', 'Total Envios']
    ).properties(title="Envios por Mês")
    st.altair_chart(chart, use_container_width=True)

    # Mostrar detalhes
    st.subheader("📄 Detalhamento dos Envios")
    st.dataframe(df_municipio, use_container_width=True)

# ===================== MOSTRAR DADOS =====================
else:
    st.dataframe(df, height=1200, use_container_width=True)

# ===================== DOWNLOAD COMPLETO =====================
csv_completo = df.to_csv(index=False, encoding='utf-8-sig')
st.sidebar.download_button("📥 Baixar Todos os Dados CSV", data=csv_completo.encode('utf-8-sig'), file_name=f"{aba_selecionada.lower().replace(' ', '_')}.csv", mime='text/csv')
