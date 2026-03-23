pip install Office365-REST-Python-Client
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
import pandas as pd
import io

def ler_arquivo_sharepoint(
    site_url: str,
    relative_folder: str,
    nome_arquivo: str,
    usuario: str,
    senha: str,
) -> pd.DataFrame:
    """
    Lê um CSV ou Excel armazenado em uma pasta do SharePoint e devolve um DataFrame.
    """
    # Cria o contexto autenticado
    ctx = ClientContext(site_url).with_credentials(UserCredential(usuario, senha))

    # Monta o caminho completo dentro do site
    caminho_completo = f"{relative_folder}/{nome_arquivo}"

    # Faz o download do arquivo como stream de bytes
    response = ctx.web.get_file_by_server_relative_url(caminho_completo).download().execute_query()
    conteudo = io.BytesIO(response.content)

    # Detecta o tipo de arquivo
    if nome_arquivo.lower().endswith(".csv"):
        df = pd.read_csv(conteudo)
    elif nome_arquivo.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(conteudo)
    else:
        raise ValueError("Formato de arquivo não suportado (use .csv ou .xlsx)")

    return df
# Configurações – você pode colocar no .streamlit/secrets.toml ou em st.secrets
SITE_URL = "https://lapoasis.sharepoint.com/sites/OASIS"
PASTA = "https://lapoasis.sharepoint.com/:x:/s/OASIS/IQAg693YO9jpQJPS79HCqFFLAQgLKMn2B-mhoGORLL8FSLc?e=HQUvNd"   # caminho relativo ao site
ARQUIVO = "historico_os.xlsx"
USUARIO = st.secrets["renato.oliveira@oasis.ind.br"]
SENHA   = st.secrets["Ro.Lap@2023"]

# Carrega os dados reais diretamente do SharePoint
df_real = ler_arquivo_sharepoint(SITE_URL, PASTA, ARQUIVO, USUARIO, SENHA)
@st.cache_data(ttl=3600)  # 1 hora de validade
def obter_dados_sharepoint():
    return ler_arquivo_sharepoint(...)
