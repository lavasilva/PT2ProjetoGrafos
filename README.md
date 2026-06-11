# Projeto de Grafos — Parte 2
## Rede de Navegação Wikipedia — Wikispeedia

---

## Sobre o Dataset

Utilizamos o **Wikispeedia dataset** (Stanford SNAP), que registra navegações humanas entre artigos da Wikipedia. No jogo Wikispeedia, jogadores tentavam chegar de um artigo a outro clicando apenas em hiperlinks.

- **Fonte:** https://snap.stanford.edu/data/wikispeedia.html
- **Arquivos utilizados:** `articles.tsv`, `links.tsv`, `categories.tsv`
- **Já incluídos no repositório** em `data/dataset_parte2/`

### Modelagem do Grafo

| Propriedade | Valor |
|---|---|
| Nós | Artigos da Wikipedia (4.604) |
| Arestas | Hiperlinks entre artigos (119.882) |
| Tipo | **Dirigido e ponderado** |
| Peso | `1 / grau_de_saída` do nó origem |

O peso modela a **probabilidade de navegação aleatória** — artigos com poucos links de saída têm arestas mais "valiosas".

---

## Estrutura do Projeto

```
PT2ProjetoGrafos/
├── src/
│   ├── __init__.py
│   ├── __main__.py          # Ponto de entrada: python -m src.cli
│   ├── cli.py               # Interface de linha de comando
│   ├── graph.py             # Estrutura de grafo (lista de adjacência)
│   ├── bfs_dfs.py           # BFS e DFS implementados do zero
│   ├── dijkstra.py          # Dijkstra com heapq (sem libs externas)
│   ├── bellman_ford.py      # Bellman-Ford com detecção de ciclo negativo
│   ├── loader_parte2.py     # Carregamento e construção do grafo Wikispeedia
│   ├── runner_parte2.py     # Orquestrador principal da Parte 2
│   ├── metrics.py           # Tempo, memória e formatação de resultados
│   └── visualizations.py   # Gráficos matplotlib + grafo interativo D3.js
├── tests/
│   └── test_algorithms.py   # 19 testes pytest
├── data/
│   └── dataset_parte2/      # articles.tsv, links.tsv, categories.tsv
├── out/                     # Saídas geradas automaticamente pelo CLI
├── requirements.txt
└── README.md
```

---

## Instalação

```bash
pip install -r requirements.txt
```

---

## Como Executar

### Rodar todos os algoritmos e gerar todas as saídas

```powershell
# Na raiz do projeto
python -m src.cli --dataset ./data/dataset_parte2/ --alg ALL --out ./out/
```

> O processo leva ~40–60s na primeira execução (ForceAtlas2 com 500 iterações para o layout do grafo). As saídas ficam em `out/`.

### Rodar os testes

```powershell
python -m pytest tests/ -v
```

---

## Saídas Geradas (`out/`)

| Arquivo | Descrição |
|---|---|
| `grafo_interativo.html` | **Entrega principal** — dashboard interativo completo, abre direto no navegador |
| `parte2_report.json` | Resultados de todos os algoritmos, tempos e tabela de desempenho |
| `degree_distribution.png` | Distribuição de graus de saída |
| `top_hubs_ranking.png` | Ranking dos 15 artigos com maior grau de saída |
| `category_distribution.png` | Distribuição de artigos por categoria temática |
| `in_out_degree_distribution.png` | Comparação de graus de entrada e saída em escala log |
| `degree_in_out_scatter.png` | Dispersão entrada × saída para identificar hubs |
| `weight_distribution.png` | Distribuição dos pesos `1/grau_saída` |
| `performance_bars.png` | Tempo médio por algoritmo |
| `comparison_lines.png` | Tempo por execução individual |
| `bfs_layers.png` | Nós descobertos por camada BFS |
| `dfs_edge_classes.png` | Classificação de arestas no DFS |
| `dijkstra_paths.png` | Distância ponderada versus saltos |
| `bellman_ford_scenarios.png` | Cenários de Bellman-Ford com pesos negativos |
| `distance_heatmap.png` | Heatmap de distâncias Dijkstra entre pares |

---

## `grafo_interativo.html` — Funcionalidades

O arquivo `out/grafo_interativo.html` é um **dashboard autocontido** (sem dependências externas além de D3.js via CDN). Abre diretamente no navegador.

### Aba: Grafo Completo
- Todos os 4.604 artigos renderizados em Canvas com layout ForceAtlas2
- Nós coloridos por categoria temática (Science, Geography, People, History…)
- **Clique simples** num nó: expande os 30 vizinhos mais conectados com arestas
- **Duplo clique**: expande todas as conexões do nó
- Filtro por categoria com chips coloridos
- Busca de artigo com autocomplete (ordenado por relevância)
- Zoom e pan com level-of-detail (labels aparecem conforme zoom aumenta)

### Aba: Ego-Graph
- Exploração por expansão progressiva a partir de qualquer artigo
- Simulação de física D3 para layout orgânico
- Clique destaca conexões, duplo clique expande vizinhos
- Filtro por categoria preservando o nó central
- Centralização automática ao explorar

### Aba: Caminho Mínimo
- Dijkstra rodando no browser sobre os 4.604 nós
- Busca origem e destino com autocomplete
- Resultado com distância ponderada, número de saltos e lista de artigos
- Pan/zoom automático para centralizar o caminho
- Nós do caminho coloridos por categoria com borda branca neon

### Aba: Análises
8 visualizações dos resultados dos algoritmos, organizadas em 3 categorias. Cada uma abre em modal com gráfico e três seções de insight (O que está sendo mostrado / Insight principal / Por que este tipo de gráfico).

| Visualização | Tipo |
|---|---|
| Distribuição de Graus de Saída | Exploratória |
| Artigos por Categoria | Exploratória |
| BFS — Nós por Camada (3 fontes) | Exploratória |
| Top 15 Hubs por Grau | Explanatória |
| Desempenho Comparativo | Explanatória |
| DFS — Classificação de Arestas | Adicional |
| Dijkstra — Custo Ponderado e Saltos | Adicional |
| Bellman-Ford — 3 Cenários | Adicional |

**Dashboard Analítico**: modal com KPIs globais, tabela de caminhos mínimos e comparativo de desempenho.

---

## Algoritmos Implementados

Todos implementados do zero, sem bibliotecas de algoritmos de grafos.

| Algoritmo | Complexidade | Casos cobertos |
|---|---|---|
| BFS | O(V + E) | 3 fontes distintas, relato de camadas por profundidade |
| DFS | O(V + E) | 3 fontes, detecção de ciclos, classificação de arestas (tree/back/forward/cross) |
| Dijkstra | O((V+E) log V) | 5 pares origem-destino, rejeita pesos negativos |
| Bellman-Ford | O(V · E) | pesos normais, peso negativo sem ciclo, ciclo negativo detectado |

---

## Pesos Negativos — Justificativa

O grafo Wikispeedia tem pesos naturalmente positivos (`1/grau_saída`). Para atender o requisito do Bellman-Ford:

- **Cenário 1 — peso negativo sem ciclo:** uma aresta recebe peso `-0.5`, simulando um atalho privilegiado de navegação. Executado em grafo controlado de 5 nós.
- **Cenário 2 — ciclo negativo detectado:** subgrafo dirigido com 3 nós e arestas `-1.0` formando A→B→C→A. O algoritmo detecta e sinaliza corretamente na iteração V da relaxação.

Ambos os casos são documentados no `parte2_report.json` com o campo `"scenario"`.

---

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.12 | Algoritmos, CLI, geração de saídas |
| matplotlib | Gráficos estáticos (`.png`) |
| ForceAtlas2 (`fa2`) + scipy | Layout do grafo interativo |
| D3.js v7 (CDN) | Canvas rendering, zoom/pan, simulação de física |
| pytest | 19 testes unitários dos algoritmos |

## Declaração de Uso de IA - Parte 2

A IA foi utilizada na definição de soluções para o desenvolvimento do grafo_interativo.html, dado o nível de complexidade técnica pelo volume do dataset: 4.604 nós e 119.882 arestas. As abordagens iniciais simplesmente não funcionaram como desejávamos; pyvis gerava 100 nós estáticos, D3 com SVG travava o browser, simulação de física no browser deixava os nós sobrepostos. Cada tentativa exigiu um novo pivô, na qual a IA nos ajudou a conhecer novas tecnologias e abordagens como solução.

Fomos auxiliados pela IA na compreensão do ForceAtlas2, na configuração dos seus parâmetros e na decisão de rodar o layout em Python antes de gerar o HTML, em vez de no browser. Também foi usada para resolver os problemas técnicos específicos de visualizar um grafo denso: sobreposição de nós, level-of-detail por zoom e arestas fantasmas no ego-graph.

