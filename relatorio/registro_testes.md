# Registro dos testes de hiperparâmetros

## Ambiente

Os testes foram executados localmente com Ollama `0.40.17`, usando o modelo `qwen2.5-coder:7b`. O comando `ollama show` registrou arquitetura `qwen2`, 7,6B parâmetros e quantização `Q4_K_M`. Após uma geração mínima, `ollama ps` registrou o modelo com `100% GPU`, contexto 4096 e runner `llamacpp`. O registro completo está em [setup_ambiente.txt](../experimentos/setup_ambiente.txt).

Prompt único: [prompt_teste.txt](../experimentos/prompt_teste.txt).

## Parâmetros e resultados

| Cenário | Execuções | Temperature | Top-P | Num-predict | Seed | `eval_count` | Comparação da resposta |
|---|---:|---:|---:|---:|---:|---:|---|
| A | 2 | 0.0 | 0.9 | 400 | 42 | 257 em ambas | Idênticas após remover o cabeçalho de metadados |
| B | 2 | 0.9 | 0.9 | 400 | 42 | 385 em ambas | Idênticas após remover o cabeçalho de metadados |
| C | 2 | 1.5 | 0.9 | 400 | 42 | 348 em ambas | Idênticas após remover o cabeçalho de metadados |

Os arquivos completos estão em [cenario_A_1.txt](../saidas/cenario_A_1.txt), [cenario_A_2.txt](../saidas/cenario_A_2.txt), [cenario_B_1.txt](../saidas/cenario_B_1.txt), [cenario_B_2.txt](../saidas/cenario_B_2.txt), [cenario_C_1.txt](../saidas/cenario_C_1.txt) e [cenario_C_2.txt](../saidas/cenario_C_2.txt). Os hashes dos arquivos completos do cenário A foram diferentes porque o cabeçalho registra durações diferentes; a comparação do trecho de resposta foi idêntica.

## Cenário A — `temperature=0.0`

Trecho real: “Aqui está uma função em Python que verifica se uma string é um palíndromo...” seguido de uma implementação com `re.sub`, reversão por `[::-1]` e três `assert`.

As duas respostas foram idênticas e terminaram com 257 tokens avaliados. Esse é o comportamento determinístico observado neste teste. A implementação, contudo, remove caracteres fora de `a-zA-Z0-9`; portanto, a alegação de ignorar acentos não é plenamente atendida para letras acentuadas. O registro descreve o que foi gerado, sem considerar a saída automaticamente correta.

## Cenário B — `temperature=0.9`, `top_p=0.9`

Trecho real: “Claro! Aqui está uma função em Python...” seguido de uma função chamada `é_palíndromo`, usando `char.isalnum()` e três `assert`.

As duas execuções foram idênticas, com 385 tokens avaliados. Portanto, não foi observada variação entre as duas amostras porque o mesmo `seed 42` foi usado. A resposta ficou mais longa e incluiu uma explicação da função. Como ponto técnico, `isalnum()` mantém letras acentuadas, mas o código não realiza normalização explícita de acentos; isso deve ser conferido antes de considerar o requisito totalmente satisfeito.

## Cenário C — `temperature=1.5`

Trecho real: a resposta começou diretamente com um bloco `python`, usando `re.sub(r'[\W_]', '', s).lower()` e três `assert`, incluindo um exemplo com `\u03B1`.

As duas execuções foram idênticas, com 348 tokens avaliados. Não houve colapso sintático: a saída permaneceu legível e apresentou código e explicação. Também não foi observada variação entre as execuções por causa do `seed 42`. Há, porém, um ponto de atenção: a explicação sobre a expressão regular contém uma descrição inconsistente (`[^\W_]` em um trecho, enquanto o código usa `[\W_]`), e o teste em grego não demonstra sozinho a remoção de acentos.

## Como temperatura e Top-P influenciam a saída

Se os logits do próximo token são `z_i`, a distribuição usada na amostragem pode ser escrita como

`p_i = softmax(z_i / T)`.

Com temperatura baixa, as diferenças entre logits são ampliadas depois da divisão e a distribuição fica mais concentrada nos tokens mais prováveis. Com temperatura maior, a distribuição fica mais plana e tokens menos prováveis podem ser escolhidos, aumentando a diversidade e também o risco de desvios. Em `T=0.0`, o Ollama tratou o cenário como determinístico nesta execução.

O Top-P faz uma segunda restrição: ordena os tokens por probabilidade e mantém o menor conjunto cuja probabilidade acumulada atinge `p=0.9`. A amostragem ocorre dentro desse núcleo, descartando a cauda menos provável. Assim, temperatura altera a distribuição antes da seleção, enquanto Top-P limita o conjunto final de candidatos.

## Espaço para capturas

- `[capturas/print_setup.png](../capturas/print_setup.png)` — inserir print do setup.
- `[capturas/print_cenarios.png](../capturas/print_cenarios.png)` — inserir print dos cenários.
