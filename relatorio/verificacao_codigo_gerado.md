# Verificação objetiva do código gerado

O verificador [verificar_saidas.py](../experimentos/verificar_saidas.py) extraiu o primeiro bloco `python` de cada saída, analisou-o com `ast.parse` e, somente quando não encontrou imports externos não aprovados nem operações de sistema, rede ou arquivos, executou o bloco em namespace isolado. Os resultados abaixo são da execução real do verificador.

| Arquivo | Sintaxe | Segurança/execução | Resultado dos asserts |
|---|---|---|---|
| `saidas/cenario_A_1.txt` | passou | executado | passou |
| `saidas/cenario_A_2.txt` | passou | executado | passou |
| `saidas/cenario_B_1.txt` | passou | executado | passou |
| `saidas/cenario_B_2.txt` | passou | executado | falhou: `AssertionError: Teste 2 falhou` |
| `saidas/cenario_C_1.txt` | falhou: `unterminated string literal` na linha 18 | não executado | não aplicável |
| `saidas/cenario_C_2.txt` | passou | não executado: import externo não aprovado `unidecode` | não aplicável |
| `saidas/com_seed/cenario_B_seed42_1.txt` | passou | executado | passou |
| `saidas/com_seed/cenario_B_seed42_2.txt` | passou | executado | passou |
| `saidas/com_seed/cenario_C_seed42_1.txt` | passou | executado | falhou: `AssertionError: Teste 2 falhou` |
| `saidas/com_seed/cenario_C_seed42_2.txt` | passou | executado | falhou: `AssertionError: Teste 2 falhou` |

O teste 2 das saídas C com seed 42 usa `is_palindrome('No ' + '\\u03B1' + ' manna')`. A execução real confirmou `AssertionError`, pois essa string não é um palíndromo após a normalização usada pelo código gerado.

O cenário C sem seed produziu duas saídas diferentes: a primeira continha um bloco Python truncado e sintaticamente inválido; a segunda importava `unidecode`, que não foi executado pelo verificador por ser uma dependência externa não aprovada para este teste de segurança.
