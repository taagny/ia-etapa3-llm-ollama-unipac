# Registro dos testes de hiperparâmetros

## Ambiente

Os testes foram executados localmente com Ollama `0.40.17`, usando o modelo `qwen2.5-coder:7b`. O comando `ollama show` registrou arquitetura `qwen2`, 7,6B parâmetros e quantização `Q4_K_M`. Após uma geração mínima, `ollama ps` registrou `100% GPU`, contexto 4096 e runner `llamacpp`. O registro completo está em [setup_ambiente.txt](../experimentos/setup_ambiente.txt).

Prompt único: [prompt_teste.txt](../experimentos/prompt_teste.txt).

## Parâmetros e resultados

| Cenário | Execuções | Temperature | Top-P | Num-predict | Seed | `eval_count` | Resultado observado |
|---|---:|---:|---:|---:|---:|---:|---|
| A | 2 | 0.0 | 0.9 | 400 | 42 | 257 e 257 | Mesma resposta nas duas execuções |
| B com seed | 2 | 0.9 | 0.9 | 400 | 42 | 385 e 385 | Mesma resposta nas duas execuções |
| B sem seed | 2 | 0.9 | 0.9 | 400 | ausente | 400 e 400 | Respostas diferentes |
| C com seed | 2 | 1.5 | 0.9 | 400 | 42 | 348 e 348 | Mesma resposta nas duas execuções; erro lógico no teste 2 |
| C sem seed | 2 | 1.5 | 1.0 | 400 | ausente | 400 e 400 | Respostas diferentes; uma saída teve erro de sintaxe por aspa não escapada e outra teve dependência não aprovada |

As execuções antigas B/C com seed 42 estão em [saidas/com_seed/](../saidas/com_seed/). As novas execuções sem seed estão em [saidas/](../saidas/). As respostas foram comparadas desconsiderando o cabeçalho de metadados, que contém durações diferentes.

## Reprodutibilidade com seed

Com o mesmo prompt, modelo, parâmetros e `seed 42`, A, B e C produziram a mesma resposta nas duas execuções correspondentes. Isso documenta reprodutibilidade neste ambiente. A seed não torna uma resposta correta: nas duas saídas C com seed, o código passou na sintaxe, mas falhou no segundo assert.

## Cenário B — `temperature=0.9`, `top_p=0.9`

As duas execuções sem seed foram diferentes, embora ambas tenham atingido o limite de 400 tokens. Uma saída usou `re.sub` para limpar a string; a outra usou `str.maketrans` e incluiu uma explicação diferente. Na verificação objetiva, o primeiro código passou nos asserts, enquanto o segundo falhou em `AssertionError: Teste 2 falhou`.

O cenário B apresentou variação estocástica controlada, mas também mostrou que uma resposta plausível pode conter um teste lógico incorreto. O uso sem seed é adequado para observar essa variação; a avaliação precisa verificar o código, não apenas a fluidez da explicação.

## Cenário C — `temperature=1.5`, `top_p=1.0`

As duas execuções sem seed foram diferentes. No C1, o bloco `python` abriu e fechou corretamente, mas falhou em `ast.parse` com `unterminated string literal` na linha 18 porque uma string delimitada por aspas simples continha a aspa de `Toyota's` sem escape: `'"A Toyota's a Toyota" deveria ser True ...'`. O texto da explicação posterior ao código foi cortado pelo limite de 400 tokens. O C2 tentou usar `unidecode`, apresentou código e testes inconsistentes e não foi executado pelo verificador porque esse import externo não foi aprovado para a execução segura.

Não houve colapso total em texto aleatório: as respostas ainda apresentaram intenção de código e explicação. Houve, porém, degradação observável na completude, na coerência dos testes e na executabilidade. Portanto, o resultado real foi variação elevada com erros lógicos e sintáticos, não uma conclusão de que toda saída em T=1.5 colapsa.

Nas duas saídas C com seed 42, o código era sintaticamente válido, mas o teste `is_palindrome('No ' + '\\u03B1' + ' manna')` falhou com `AssertionError`. A string usada nesse teste não é um palíndromo após a normalização implementada.

## Verificação objetiva do código

O procedimento e os resultados completos estão em [verificacao_codigo_gerado.md](verificacao_codigo_gerado.md). Resumo:

| Grupo | Sintaxe | Asserts |
|---|---|---|
| A1 e A2 | passaram | passaram |
| B sem seed 1 | passou | passou |
| B sem seed 2 | passou | falhou no teste 2 |
| C sem seed 1 | falhou por bloco truncado | não executado |
| C sem seed 2 | passou | não executado por import externo `unidecode` |
| B com seed 42 (duas execuções) | passaram | passaram |
| C com seed 42 (duas execuções) | passaram | falharam no teste 2 |

## Como temperatura e Top-P influenciam a saída

Se os logits do próximo token são `z_i`, a distribuição usada na amostragem pode ser escrita como `p_i = softmax(z_i / T)`. Com temperatura baixa, as diferenças entre logits são ampliadas depois da divisão e a distribuição fica mais concentrada nos tokens mais prováveis. Com temperatura maior, a distribuição fica mais plana e tokens menos prováveis podem ser escolhidos, aumentando a diversidade e também o risco de desvios.

O Top-P ordena os tokens por probabilidade e mantém o menor conjunto cuja probabilidade acumulada atinge o valor escolhido. Com `top_p=0.9`, a cauda menos provável é descartada; com `top_p=1.0`, essa restrição de núcleo fica liberada. Assim, temperatura altera a distribuição antes da seleção, enquanto Top-P limita o conjunto final de candidatos.

## Espaço para capturas

- [capturas/print_setup.png](../capturas/print_setup.png) — print do setup.
- [capturas/print_cenarios.png](../capturas/print_cenarios.png) — print dos cenários.
