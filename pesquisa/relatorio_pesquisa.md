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

## 3. A mecânica de Query, Key e Value

## 4. A linha de montagem de um LLM
