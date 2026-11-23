# Verificação objetiva do código gerado

O verificador [verificar_saidas.py](../experimentos/verificar_saidas.py) extraiu o primeiro bloco `python` de cada saída, analisou-o com `ast.parse` e, somente quando não encontrou imports externos não aprovados nem operações de sistema, rede ou arquivos, executou o bloco em namespace isolado. Os resultados abaixo são da execução real do verificador.

| Arquivo | Sintaxe | Segurança/execução | Resultado dos asserts |
|---|---|---|---|
| `saidas/cenario_A_1.txt` | passou | executado | passou |
| `saidas/cenario_A_2.txt` | passou | executado | passou |
| `saidas/cenario_B_1.txt` | passou | executado | passou |
| `saidas/cenario_B_2.txt` | passou | executado | falhou: `AssertionError: Teste 2 falhou` |
| `saidas/cenario_C_1.txt` | falhou: `unterminated string literal` na linha 18 por aspa simples não escapada em `Toyota's` | não executado | não aplicável |
| `saidas/cenario_C_2.txt` | passou | não executado: import externo não aprovado `unidecode` | não aplicável |
| `saidas/com_seed/cenario_B_seed42_1.txt` | passou | executado | passou |
| `saidas/com_seed/cenario_B_seed42_2.txt` | passou | executado | passou |
| `saidas/com_seed/cenario_C_seed42_1.txt` | passou | executado | falhou: `AssertionError: Teste 2 falhou` |
| `saidas/com_seed/cenario_C_seed42_2.txt` | passou | executado | falhou: `AssertionError: Teste 2 falhou` |
| `saidas/execucao_prints/cenario_A_print.txt` | passou | executado individualmente | asserts 1, 2 e 3 passaram |
| `saidas/execucao_prints/cenario_B_print.txt` | passou | executado individualmente | asserts 1, 2 e 3 passaram |
| `saidas/execucao_prints/cenario_C_print.txt` | passou | executado individualmente | assert 1 falhou, assert 2 passou, assert 3 falhou |

O teste 2 das saídas C com seed 42 usa `is_palindrome('No ' + '\\u03B1' + ' manna')`. A execução real confirmou `AssertionError`, pois essa string não é um palíndromo após a normalização usada pelo código gerado.

## Execuções usadas nos prints

Os três arquivos em `saidas/execucao_prints/` também foram verificados. O cenário A passou nos três asserts; o cenário B passou nos três asserts; e o cenário C passou na sintaxe, mas teve falha no assert 1, aprovação no assert 2 e falha no assert 3. Embora a saída original do cenário C tenha impresso `Test(s) failed!` por envolver os asserts em `try/except AssertionError`, o verificador removeu o controle agregador apenas para a preparação segura e avaliou cada assert isoladamente. O código do cenário C não executou operações de sistema, rede ou arquivos.

O cenário C sem seed produziu duas saídas diferentes: no C1, o bloco Python abriu e fechou, mas uma string com `Toyota's` não escapou a aspa simples e causou o `SyntaxError`; o texto da explicação posterior ao código foi cortado pelo limite de 400 tokens. No C2, o código importava `unidecode`, que não foi executado pelo verificador por ser uma dependência externa não aprovada para este teste de segurança.
