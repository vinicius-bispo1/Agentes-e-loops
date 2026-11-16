import os  # Permite ler variáveis de ambiente do sistema.
from fastapi import FastAPI  # Importa a classe usada para criar a API.
from pydantic import BaseModel  # Importa a classe-base para validar os dados recebidos.
from dotenv import load_dotenv  # Importa a função que carrega variáveis do arquivo .env.
from google import genai  # Importa o cliente da API do Google Gemini.
from google.genai import types  # Importa os tipos de configuração usados pelo Gemini.


load_dotenv()  # Carrega as variáveis definidas no arquivo .env para o ambiente.


app = FastAPI()  # Cria a aplicação FastAPI que receberá as requisições HTTP.


client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")  # Obtém a chave da API sem gravá-la no código.
)  # Inicializa o cliente usado para enviar solicitações ao Gemini.


MODEL = "gemini-3.5-flash-lite"  # Define o modelo do Gemini que será consultado.


# Define uma base de dados fictícia usada para simular a consulta de pedidos.
PEDIDOS = {
    "12345": {  # Usa o número do pedido como chave para encontrá-lo.
        "status": "Enviado",  # Informa o status atual do pedido.
        "previsao_entrega": "18/11/2026"  # Informa a data prevista de entrega.
    }  # Finaliza os dados do pedido de exemplo.
}  # Finaliza a base simulada de pedidos.


class ChatRequest(BaseModel):
    mensagem: str  # Declara que a requisição deve conter uma mensagem textual.


# Define a ferramenta que o Gemini pode chamar para consultar um pedido.
def consultar_pedido(pedido_id: str) -> dict:
    # Esta docstring descreve a ferramenta para o Gemini e documenta seu argumento.
    """Consulta o status e a previsão de entrega de um pedido.


    Args:
        pedido_id: Número do pedido.
    """
    return PEDIDOS.get(  # Procura o pedido e retorna o valor padrão se não existir.
        pedido_id,  # Usa o identificador recebido para localizar o pedido.
        {"erro": "Pedido não encontrado"}  # Informa quando o identificador não existe.
    )  # Devolve os dados encontrados ou a mensagem de erro.


@app.post("/agente")  # Registra a função abaixo como endpoint HTTP POST em /agente.
def executar_agente(request: ChatRequest):  # Define o endpoint que recebe mensagens do chat.
    # Envia a mensagem ao Gemini e disponibiliza a função de consulta como ferramenta.
    response = client.models.generate_content(
        model=MODEL,  # Seleciona o modelo definido acima.
        contents=request.mensagem,  # Passa ao modelo a mensagem recebida na requisição.
        config=types.GenerateContentConfig(
            tools=[consultar_pedido]  # Registra a função que o Gemini pode chamar.
        )  # Finaliza a configuração das ferramentas disponíveis.
    )  # Executa a solicitação e guarda a resposta do Gemini.

    return {
        "resposta": response.text  # Retorna ao cliente o texto produzido pelo Gemini.
    }  # Finaliza o objeto JSON enviado na resposta HTTP.
