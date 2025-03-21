import streamlit as st
import pandas as pd

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

# ===================== LINKS DAS ABAS =====================
sheet_id = "1k_aWceBCN_V0VaRJa1Jw42t6hfrER4T4bE2fS88mLDI"

# IMPORTANTE: Usar export direto + gid certo para cada aba:
sheet_urls = {
    "RESPOSTAS AO FORMULÁRIO CAIXA DE ENTRADA": f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0",
    "QUANTITATIVO (2024 E 2025)": f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1644302156",
    "DADOS FILTRADOS DA CAIXA DE ENTRADA": f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1519697321",
    "DADOS DE RECEBIMENTO DO FORMULÁRIO POR MUNICÍPIO": f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=812030272",
    "STATUS DE RECEBIMENTO": f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1842981742",
    "GRAPH SITE": f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1341836627",
    "DADOS ORGANIZADOS": f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=667723113"
}

# Sub-registro separado
subregistro_sheet_id = "1UD1B9_5_zwd_QD0drE1fo3AokpE6EDnYTCwywrGkD-Y"
sheet_urls["SUB-REGISTRO"] = f"https://docs.google.com/spreadsheets/d/{subregistro_sheet_id}/export?format=csv&gid=0"

# ===================== FUNÇÃO: Carregar Dados =====================
@st.cache_data(ttl=3600)
def carregar_planilha(aba):
    df = pd.read_csv(sheet_urls[aba], low_memory=False, dtype=str)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    origem = "Exportação Completa Google Sheets"
    return df, origem

# ===================== LOAD DATA =====================
st.sidebar.header("📂 COGEX NRC 2025- PROV 07 - DADOS DO FORMULÁRIO")
abas_selecionadas = list(sheet_urls.keys())
aba_selecionada = st.sidebar.radio("Selecione uma aba:", abas_selecionadas)

df, origem = carregar_planilha(aba_selecionada)
st.caption(f"Fonte dos dados: {origem}")

# ===================== MOSTRAR TODAS AS LINHAS =====================
st.dataframe(df, height=1200, use_container_width=True)

# ===================== DOWNLOAD COMPLETO DOS DADOS =====================
csv_completo = df.to_csv(index=False, encoding='utf-8-sig')
st.sidebar.download_button("📥 Baixar Todos os Dados CSV", data=csv_completo.encode('utf-8-sig'), file_name=f"{aba_selecionada.lower().replace(' ', '_')}.csv", mime='text/csv')
