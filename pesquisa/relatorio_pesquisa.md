# Das RNNs aos LLMs

**Nome:** [INSIRA SEU NOME AQUI]  
**Curso:** Ciência da Computação  
**Disciplina:** Inteligência Artificial  
**Instituição:** UNIPAC Barbacena  
**Professor:** Felipe Roncalli de Paula Carneiro  
**Data:** 12/11/2026

## Introdução

Este relatório apresenta a transição das redes neurais recorrentes para os modelos de linguagem de grande porte, destacando os gargalos de processamento, o mecanismo de atenção e as etapas de construção e alinhamento de um LLM.

## 1. O gargalo sequencial das RNNs

Uma rede neural recorrente (RNN) processa uma sequência mantendo um estado oculto que é atualizado a cada instante. Uma forma compacta de representar essa atualização é

\[
h_t = f(W_h \cdot h_{t-1} + W_x \cdot x_t + b),
\]

em que `x_t` é a entrada no instante `t`, `h_{t-1}` é o estado anterior, `W_h` e `W_x` são matrizes de pesos, `b` é o viés e `f` é uma função não linear. O ponto central é que o cálculo de `h_t` só pode começar depois que `h_{t-1}` estiver pronto. Assim, mesmo que os tokens da sequência estejam disponíveis ao mesmo tempo, os estados precisam ser produzidos em ordem.

Esse encadeamento impõe aproximadamente `O(n)` passos sequenciais para uma sequência de comprimento `n`. A dimensão da sequência, portanto, não pode ser paralelizada livremente durante o treinamento: o passo 2 espera o passo 1, o passo 3 espera o passo 2 e assim por diante. Há paralelismo em outras dimensões, como nos exemplos do lote e nos neurônios, mas ele não elimina a barreira temporal da recorrência.

O efeito prático é uma utilização baixa ou irregular das GPUs. Milhares de núcleos podem permanecer ociosos enquanto aguardam a conclusão de uma pequena atualização de estado, em vez de executar uma grande matriz de tokens simultaneamente. Quanto maior a sequência, mais evidente fica essa ociosidade e maior é a latência acumulada.

Além do gargalo de paralelização, RNNs podem sofrer com gradientes que desaparecem ou explodem durante o treinamento. Isso dificulta aprender relações entre posições muito distantes: a informação precisa atravessar muitos passos recorrentes e pode perder força ou tornar o ajuste instável. Esses problemas ajudam a explicar por que arquiteturas capazes de tratar muitos tokens em paralelo se tornaram tão importantes.

## 2. A quebra de paradigma dos Transformers

O artigo *Attention Is All You Need*, de Vaswani et al. (2017), propôs uma arquitetura baseada em atenção, sem depender de recorrência nem de convoluções para organizar a sequência. Essa mudança foi também uma mudança de engenharia: durante o treinamento, os tokens de uma sequência podem ser processados simultaneamente por operações matriciais altamente paralelizáveis. O hardware passa a trabalhar com blocos maiores e mais regulares, favorecendo escala, throughput e treinamento distribuído.

No mecanismo de Self-Attention, cada posição calcula quanto deve considerar as demais posições da mesma sequência. Em vez de transmitir informação apenas de `t-1` para `t`, uma palavra pode consultar diretamente todas as outras em uma camada. Isso facilita relações de longo alcance e reduz a dependência de uma cadeia temporal durante o treinamento. A arquitetura tornou viáveis famílias como BERT e GPT e, em escala maior, os atuais modelos de linguagem de grande porte.

Como a recorrência deixou de fornecer uma ordem implícita, o Transformer precisa receber informação posicional. Ela pode ser incorporada por codificações posicionais adicionadas aos embeddings ou por representações posicionais aprendidas. Sem esse sinal, a atenção trataria a entrada de maneira insuficientemente sensível à posição de cada token.

Essa vantagem tem uma contrapartida: a atenção normalmente compara cada posição com todas as outras, o que produz custo de tempo e memória `O(n²)` em relação ao comprimento `n` da sequência. Ainda assim, a possibilidade de paralelizar o treinamento e de modelar dependências diretamente tornou o compromisso muito mais favorável para a construção de modelos em grande escala.

## 3. A mecânica de Query, Key e Value

O Self-Attention pode ser entendido como uma busca contextual. A **Query (Q)** representa o que a posição atual procura no contexto; a **Key (K)** funciona como uma etiqueta ou descrição que cada posição oferece para ser comparada com a busca; e o **Value (V)** contém o conteúdo informacional que será recuperado quando uma posição for considerada relevante. Para cada embedding `X`, a camada produz essas três representações por projeções aprendidas: `Q = XW_Q`, `K = XW_K` e `V = XW_V`.

A operação é definida por

\[
\operatorname{Attention}(Q,K,V) = \operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V.
\]

O produto escalar `QK^T` mede a compatibilidade entre a busca e cada chave. A divisão por `√d_k` evita que os valores cresçam demais quando a dimensão das chaves aumenta. O `softmax` transforma os escores em pesos positivos cuja soma é 1, e a multiplicação final produz uma soma ponderada dos Values.

### Mini-exemplo numérico

Considere uma Query `Q = [1, 0]`, duas Keys `K₁ = [1, 0]` e `K₂ = [0, 1]`, e Values `V₁ = [2, 0]` e `V₂ = [0, 4]`. Como `d_k = 2`, os escores antes da escala são `QK^T = [1, 0]`. Após dividir por `√2`, obtemos aproximadamente `[0,7071, 0]`.

O softmax resulta em

`peso₁ = exp(0,7071) / (exp(0,7071) + exp(0)) ≈ 0,6698`

`peso₂ = exp(0) / (exp(0,7071) + exp(0)) ≈ 0,3302`.

Logo, a saída é `0,6698 · [2, 0] + 0,3302 · [0, 4] = [1,3396, 1,3208]`. O primeiro Value contribui mais porque sua Key é mais compatível com a Query. Em uma arquitetura real, a **Multi-Head Attention** repete essa ideia em várias cabeças, permitindo que cada uma aprenda relações diferentes.

## 4. A linha de montagem de um LLM
