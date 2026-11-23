"""Gera texto localmente com streaming pela API do Ollama."""

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

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
    parser.add_argument("--saida")
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


def save_response(
    args: argparse.Namespace,
    generated: list[str],
    eval_count: int,
    duration: float,
) -> Path:
    output_dir = Path("saidas")
    output_dir.mkdir(exist_ok=True)
    if args.saida:
        output_path = Path(args.saida)
        if output_path.parent != Path('.'):
            output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "_", args.model)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / (
            f"{safe_model}_t{args.temperature:g}_{timestamp}.txt"
        )
    header = (
        f"Modelo: {args.model}\n"
        f"Temperature: {args.temperature}\n"
        f"Top-P: {args.top_p}\n"
        f"Num-predict: {args.num_predict}\n"
        f"Seed: {args.seed}\n"
        f"Prompt: {load_prompt(args)}\n"
        f"Tokens gerados (eval_count): {eval_count}\n"
        f"Duração (segundos): {duration:.3f}\n"
        "\n--- Resposta ---\n"
    )
    output_path.write_text(header + "".join(generated), encoding="utf-8")
    return output_path


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

    started_at = time.perf_counter()
    generated = []
    eval_count = 0
    try:
        response = requests.post(URL, json=payload, stream=True, timeout=None)
        response.raise_for_status()
        print("--- Iniciando geração do modelo (streaming) ---\n")
        for chunk in response.iter_lines():
            if not chunk:
                continue
            data = json.loads(chunk.decode("utf-8"))
            token_text = data.get("response", "")
            generated.append(token_text)
            print(token_text, end="", flush=True)
            if data.get("done", False):
                eval_count = data.get("eval_count", 0)
                print("\n\n--- Geração concluída ---")
                print(f"Total de tokens avaliados: {eval_count}")

        duration = time.perf_counter() - started_at
        output_path = save_response(args, generated, eval_count, duration)
        print(f"Resposta salva em: {output_path}")
    except requests.exceptions.ConnectionError:
        print(
            "Erro: não foi possível conectar ao Ollama. "
            "Verifique se o serviço está rodando localmente (ollama serve)."
        )
    except requests.exceptions.HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            print(
                f"Erro: o modelo '{args.model}' não está instalado. "
                f"Execute: ollama pull {args.model}"
            )
        else:
            print(f"Erro HTTP ao consultar o Ollama: {error}")
    except json.JSONDecodeError as error:
        print(f"Erro: JSON inválido recebido no stream do Ollama: {error}")
    except KeyboardInterrupt:
        duration = time.perf_counter() - started_at
        if generated:
            output_path = save_response(args, generated, eval_count, duration)
            print(f"\nInterrupção recebida. Resposta parcial salva em: {output_path}")
        else:
            print("\nInterrupção recebida antes de qualquer token ser gerado.")
    except Exception as error:
        print(f"Ocorreu um erro inesperado: {error}")


if __name__ == "__main__":
    main()
