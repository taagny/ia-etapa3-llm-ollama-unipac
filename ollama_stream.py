"""Gera texto localmente com streaming pela API do Ollama."""

import argparse
import json
import sys

import requests


URL = "http://localhost:11434/api/generate"
PROMPT_PADRAO = "Escreva um algoritmo de ordenação Bubble Sort em C bem documentado."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera texto usando o Ollama local.")
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    prompt_group = parser.add_mutually_exclusive_group()
    prompt_group.add_argument("--prompt")
    prompt_group.add_argument("--prompt-file")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.9, dest="top_p")
    parser.add_argument("--num-predict", type=int, default=300, dest="num_predict")
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    if args.temperature < 0:
        parser.error("--temperature deve ser maior ou igual a 0")
    if not 0 < args.top_p <= 1:
        parser.error("--top-p deve estar entre 0 e 1")
    if args.num_predict <= 0:
        parser.error("--num-predict deve ser maior que 0")
    return args


def load_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        with open(args.prompt_file, encoding="utf-8") as prompt_file:
            return prompt_file.read()
    return args.prompt or PROMPT_PADRAO


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    payload = {
        "model": args.model,
        "prompt": load_prompt(args),
        "options": {
            "temperature": args.temperature,
            "top_p": args.top_p,
            "num_predict": args.num_predict,
        },
        "stream": True,
    }
    if args.seed is not None:
        payload["options"]["seed"] = args.seed

    try:
        response = requests.post(URL, json=payload, stream=True, timeout=None)
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


if __name__ == "__main__":
    main()
