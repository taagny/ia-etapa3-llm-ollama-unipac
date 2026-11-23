import json
import requests

# URL do endpoint local do Ollama
url = "http://localhost:11434/api/generate"

# Configuração do payload (corpo da requisição)
payload = {
    "model": "qwen2.5-coder:7b",  # Substitua pelo modelo baixado no seu Ollama
    "prompt": (
        "Escreva um algoritmo de ordenação Bubble Sort em C bem documentado."
    ),
    "options": {
        "temperature": 0.2,  # Baixa temperatura para maior precisão lógica
        "top_p": 0.9,  # Corte dinâmico de probabilidade
        "num_predict": 300,  # Limite máximo de tokens gerados
    },
    "stream": True,  # Crucial para receber token por token em tempo real
}

try:
    # Dispara a requisição mantendo a conexão aberta (stream=True)
    response = requests.post(url, json=payload, stream=True)
    response.raise_for_status()

    print("--- Iniciando Geração do Modelo (Streaming) ---\n")

    # Itera sobre cada linha (chunk) recebida no fluxo
    for chunk in response.iter_lines():
        if chunk:
            # Decodifica o JSON retornado pelo Ollama
            data = json.loads(chunk.decode("utf-8"))

            # Extrai o texto do token atual e imprime sem quebra de linha
            token_text = data.get("response", "")
            print(token_text, end="", flush=True)

            # Verifica se o modelo concluiu a geração
            if data.get("done", False):
                print("\n\n--- Geração Concluída ---")
                print(
                    f"Total de tokens avaliados: {data.get('eval_count', 0)}"
                )

except requests.exceptions.ConnectionError:
    print(
        "Erro: Não foi possível conectar ao Ollama. Verifique se o serviço está rodando localmente (ollama serve)."
    )
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")