import streamlit as st
import pandas as pd
import altair as alt

# ===================== CONFIGURAÇÃO =====================
st.set_page_config(
    page_title="CORREGEDORIA DO FORO EXTRAJUDICIAL NRC 2025",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== FUNÇÃO PADRONIZADA PARA COMPLETAR CAMPOS =====================
def preencher_ano_mes(df):
    if 'Carimbo de data/hora' in df.columns:
        df['Carimbo de data/hora'] = pd.to_datetime(df['Carimbo de data/hora'], errors='coerce')
        df['Ano'] = df['Carimbo de data/hora'].dt.year
        df['Mês'] = df['Carimbo de data/hora'].dt.month
        df['Mês Nome'] = df['Carimbo de data/hora'].dt.strftime('%B')
    return df

# ===================== CABEÇALHO COM IMAGEM E TÍTULO =====================
col1, col2 = st.columns([6, 1])

with col1:
    st.title("\U0001F4CA Relatório de Registro Civil - Unidade Interligada PROV 07 2021 22/02/2021 - CORREGEDORIA DO FORO EXTRAJUDICIAL NRC 2025")
    st.subheader("\U0001F4C4 DADOS DO FORMULÁRIO OBRIGATÓRIO DAS UNIDADES INTERLIGADAS - PROV 07")

with col2:
    st.image("https://raw.githubusercontent.com/jesusmjunior/dashboard-registro-civil-prov07/main/CGX.png", width=120)

st.warning("\U0001F6A8 **ATENÇÃO! UNIDADE INTERLIGADA!**\n\nAcesse e preencha/atualize seus dados do Provimento 07/2021.", icon="⚠️")
st.markdown("[\U0001F4DD **Clique aqui para acessar o Formulário Obrigatório**](https://forms.gle/vETZAjAStN3F9YHx9)")

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

sheet_urls = {
    "RESPOSTAS AO FORMULÁRIO CAIXA DE ENTRADA": f"{base_url}Respostas%20ao%20formul%C3%A1rio%202",
    "QUANTITATIVO (2024 E 2025)": f"{base_url}QUANTITATIVO%20(2024%20E%202025)",
    "DADOS FILTRADOS DA CAIXA DE ENTRADA": f"{base_url}(N%C3%83O%20ALTERE%20OS%20FILTROS%20OU%20DADOS)",
    "DADOS DE RECEBIMENTO DO FORMULÁRIO POR MUNICÍPIO": f"{base_url}P%C3%A1gina11",
    "STATUS DE RECEBIMENTO": f"{base_url}STATUS%20DE%20RECEBIMENTO",
    "GRAPH SITE": f"{base_url}GRAPH%20SITE",
    "DADOS ORGANIZADOS": f"{base_url}DADOS%20ORGANIZADOS",
    "SUB-REGISTRO": subregistro_base_url,
    "ANÁLISE DE STATUS": f"{base_url}Respostas%20ao%20formul%C3%A1rio%202"
}

# ===================== FUNÇÃO: Carregar Dados =====================
@st.cache_data(ttl=3600)
def carregar_planilha(aba):
    df = pd.read_csv(sheet_urls[aba], low_memory=False, dtype=str)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = preencher_ano_mes(df)
    origem = "Planilha Pública Online (CSV)"
    return df, origem

# ===================== LOAD DATA =====================
st.sidebar.header("\U0001F4C2 COGEX NRC 2025- PROV 07 - DADOS DO FORMULÁRIO")
abas_selecionadas = list(sheet_urls.keys())
aba_selecionada = st.sidebar.radio("Selecione uma aba:", abas_selecionadas)

df, origem = carregar_planilha(aba_selecionada)
st.caption(f"Fonte dos dados: {origem}")

# ===================== MOSTRAR DADOS =====================
st.dataframe(df, height=1000, use_container_width=True)

# ===================== DOWNLOAD COMPLETO =====================
csv_completo = df.to_csv(index=False, encoding='utf-8-sig')
st.sidebar.download_button("\U0001F4E5 Baixar Todos os Dados CSV", data=csv_completo.encode('utf-8-sig'), file_name=f"{aba_selecionada.lower().replace(' ', '_')}.csv", mime='text/csv')

# ===================== CHECAR MESES PENDENTES COM ROBOZINHO =====================
if 'MUNICÍPIO' in df.columns and 'Carimbo de data/hora' in df.columns:
    st.header("\U0001F916 Análise de Pendência por Unidade")
    municipios_unicos = df['MUNICÍPIO'].dropna().unique()
    municipio_sel = st.selectbox("Selecione um Município:", municipios_unicos)

    anos_unicos = df[df['MUNICÍPIO'] == municipio_sel]['Ano'].dropna().unique()
    ano_sel = st.selectbox("Selecione o Ano:", anos_unicos)

    df_municipio = df[(df['MUNICÍPIO'] == municipio_sel) & (df['Ano'] == int(ano_sel))]

    meses_enviados = df_municipio['Mês'].dropna().astype(int).unique().tolist()
    meses_todos = list(range(1, 13))
    meses_pendentes = sorted(list(set(meses_todos) - set(meses_enviados)))

    if meses_pendentes:
        nomes_pendentes = [pd.to_datetime(f'2020-{m}-01').strftime('%B') for m in meses_pendentes]
        st.error(f"🤖 Município **{municipio_sel}** - Ano **{ano_sel}**\n\n🔴 Meses pendentes: {nomes_pendentes}")
        st.markdown("<div style='font-size:50px;'>🤖🚩</div>", unsafe_allow_html=True)
    else:
        st.success(f"🤖 Município **{municipio_sel}** - Ano **{ano_sel}**\n\n✅ Todos os meses enviados!")
        st.markdown("<div style='font-size:50px;'>🤖🎉</div>", unsafe_allow_html=True)

    # Verificar duplicados
    duplicados = df_municipio[df_municipio.duplicated(subset=['Mês'], keep=False)]
    if not duplicados.empty:
        st.warning("⚠️ Foram encontrados registros duplicados:")
        st.dataframe(duplicados[['Carimbo de data/hora', 'MUNICÍPIO', 'Mês', 'Mês Nome']], use_container_width=True)
