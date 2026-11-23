# Trabalho 3ª Etapa — das RNNs aos LLMs

Projeto acadêmico da disciplina de Inteligência Artificial da UNIPAC Barbacena. O trabalho combina uma pesquisa sobre RNNs, Transformers e a construção de LLMs com experimentos locais de geração usando Ollama, sem depender de API externa.

## Requisitos

- Python 3 instalado;
- Ollama instalado e em execução;
- modelo local `qwen2.5-coder:7b` (quantização observada neste ambiente: `Q4_K_M`);
- pacote Python `requests`.

## Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull qwen2.5-coder:7b
```

O registro do ambiente usado nos testes está em [experimentos/setup_ambiente.txt](experimentos/setup_ambiente.txt).

## Uso do script

O script transmite os tokens em tempo real pela API local `http://localhost:11434/api/generate` e salva a resposta em `saidas/`:

```powershell
python ollama_stream.py `
  --model qwen2.5-coder:7b `
  --prompt "Explique uma busca binária em Python." `
  --temperature 0.2 `
  --top-p 0.9 `
  --num-predict 300 `
  --seed 42 `
  --saida saidas/exemplo.txt
```

Também é possível passar o prompt por arquivo:

```powershell
python ollama_stream.py --model qwen2.5-coder:7b `
  --prompt-file experimentos/prompt_teste.txt `
  --temperature 0.0 --top-p 0.9 --num-predict 400 --seed 42
```

Os argumentos `--temperature`, `--top-p` e `--num-predict` são validados. O arquivo salvo contém modelo, parâmetros, prompt, tokens avaliados, duração e resposta.

## Reprodução dos cenários

Execute duas vezes cada comando, alterando apenas o nome de saída:

```powershell
python ollama_stream.py --model qwen2.5-coder:7b --prompt-file experimentos/prompt_teste.txt --temperature 0.0 --top-p 0.9 --num-predict 400 --seed 42 --saida saidas/cenario_A_1.txt
python ollama_stream.py --model qwen2.5-coder:7b --prompt-file experimentos/prompt_teste.txt --temperature 0.9 --top-p 0.9 --num-predict 400 --saida saidas/cenario_B_1.txt
python ollama_stream.py --model qwen2.5-coder:7b --prompt-file experimentos/prompt_teste.txt --temperature 1.5 --top-p 1.0 --num-predict 400 --saida saidas/cenario_C_1.txt
```

Para a segunda execução de cada cenário, use os nomes `_2.txt`. O registro comentado dos testes está em [relatorio/registro_testes.md](relatorio/registro_testes.md).

Use `--seed 42` quando quiser tornar execuções comparáveis e reproduzíveis, como no cenário A. Omita `--seed` nos cenários B e C quando o objetivo for observar a variação estocástica entre execuções. No cenário C, `--top-p 1.0` libera a cauda completa da distribuição.

## Estrutura

```text
.
├── README.md
├── requirements.txt
├── .gitignore
├── ollama_stream.py
├── pesquisa/relatorio_pesquisa.md
├── experimentos/
│   ├── prompt_teste.txt
│   └── setup_ambiente.txt
├── saidas/
├── relatorio/registro_testes.md
└── capturas/
```

## Entregáveis e pendências manuais

- Relatório teórico: [pesquisa/relatorio_pesquisa.md](pesquisa/relatorio_pesquisa.md).
- Script e saídas reais dos cenários: [ollama_stream.py](ollama_stream.py) e [saidas/](saidas/).
- Nome do aluno preenchido no relatório.
- Adicionar os prints em `capturas/print_setup.png` e `capturas/print_cenarios.png`.
- Conferir as referências marcadas no comentário HTML do relatório.
