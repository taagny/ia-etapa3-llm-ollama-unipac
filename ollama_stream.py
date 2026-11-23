"""Gera texto localmente com streaming pela API do Ollama."""

import json

import requests


URL = "http://localhost:11434/api/generate"
PAYLOAD = {
    "model": "qwen2.5-coder:7b",
    "prompt": "Escreva um algoritmo de ordenação Bubble Sort em C bem documentado.",
    "options": {
        "temperature": 0.2,
        "top_p": 0.9,
        "num_predict": 300,
    },
    "stream": True,
}


try:
    response = requests.post(URL, json=PAYLOAD, stream=True, timeout=None)
    response.raise_for_status()

    print("--- Iniciando geração do modelo (streaming) ---\n")
    for chunk in response.iter_lines():
        if not chunk:
            continue

        data = json.loads(chunk.decode("utf-8"))
        print(data.get("response", ""), end="", flush=True)

        if data.get("done", False):
            print("\n\n--- Geração concluída ---")
            print(f"Total de tokens avaliados: {data.get('eval_count', 0)}")

except requests.exceptions.ConnectionError:
    print(
        "Erro: não foi possível conectar ao Ollama. "
        "Verifique se o serviço está rodando localmente (ollama serve)."
    )
except Exception as error:
    print(f"Ocorreu um erro inesperado: {error}")
