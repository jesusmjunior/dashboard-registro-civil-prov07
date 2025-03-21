import streamlit as st
import pandas as pd

# ===================== CONFIGURAÇÃO =====================
st.set_page_config(
    page_title="CORREGEDORIA NRC 2025",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== FUNÇÃO: Carregar Dados =====================
@st.cache_data(ttl=3600)
def carregar_planilha(url):
    df = pd.read_csv(url, low_memory=False, dtype=str)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['Carimbo de data/hora'] = pd.to_datetime(df['Carimbo de data/hora'], errors='coerce')
    df['Ano'] = df['Carimbo de data/hora'].dt.year
    df['Mês'] = df['Carimbo de data/hora'].dt.month
    df['Mês Nome'] = df['Carimbo de data/hora'].dt.strftime('%B')
    return df

# ===================== LINKS DAS ABAS =====================
sheet_id = "1k_aWceBCN_V0VaRJa1Jw42t6hfrER4T4bE2fS88mLDI"
base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet="

sheet_urls = {
    "DADOS RECEBIDOS": f"{base_url}Respostas%20ao%20formul%C3%A1rio%202"
}

# ===================== LOAD DATA =====================
st.sidebar.header("📂 Dados NRC 2025")
aba = st.sidebar.radio("Selecione:", list(sheet_urls.keys()))
df = carregar_planilha(sheet_urls[aba])

st.title("📊 Relatório Registro Civil - NRC 2025")

# ===================== SELETORES =====================
municipios = df['MUNICÍPIO'].dropna().unique()
municipio_sel = st.sidebar.selectbox("Município:", municipios)

df_municipio = df[df['MUNICÍPIO'] == municipio_sel]

anos = df_municipio['Ano'].dropna().unique()
ano_sel = st.sidebar.selectbox("Ano:", anos)

df_municipio_ano = df_municipio[df_municipio['Ano'] == ano_sel]

# ===================== ANÁLISE DOS MESES =====================
meses_enviados = df_municipio_ano['Mês'].dropna().astype(int).unique().tolist()
meses_todos = list(range(1, 13))
meses_pendentes = sorted(list(set(meses_todos) - set(meses_enviados)))

# ===================== EXIBIR STATUS COM EMOJI =====================
if meses_pendentes:
    nomes_pendentes = [pd.to_datetime(f'2020-{m}-01').strftime('%B') for m in meses_pendentes]
    st.error(f"🤖 Município: **{municipio_sel}** | Ano: **{ano_sel}**\n\n🔴 Meses pendentes: {nomes_pendentes}")
    st.markdown("<div style='font-size:50px;'>🤖🚩</div>", unsafe_allow_html=True)
else:
    st.success(f"🤖 Município: **{municipio_sel}** | Ano: **{ano_sel}**\n\n✅ Todos os meses enviados!")
    st.markdown("<div style='font-size:50px;'>🤖🎉</div>", unsafe_allow_html=True)

# ===================== TABELA DETALHADA =====================
st.subheader("📄 Detalhamento Completo dos Envios")
st.dataframe(df_municipio_ano, use_container_width=True)

# ===================== DOWNLOAD DETALHADO =====================
csv_detalhe = df_municipio_ano.to_csv(index=False, encoding='utf-8-sig')
st.sidebar.download_button("📥 Baixar Detalhamento CSV", data=csv_detalhe.encode('utf-8-sig'), file_name=f"detalhamento_{municipio_sel}_{ano_sel}.csv", mime='text/csv')
