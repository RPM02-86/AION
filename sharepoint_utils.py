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
