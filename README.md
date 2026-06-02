# Projeto de Grafos — Parte 2
## Rede de Navegação Wikipedia — Wikispeedia

---

## Sobre o Dataset

Utilizamos o **Wikispeedia dataset** (Stanford SNAP), que registra navegações humanas entre artigos da Wikipedia. No jogo Wikispeedia, jogadores tentavam chegar de um artigo a outro clicando apenas em hiperlinks.

- **Fonte:** https://snap.stanford.edu/data/wikispeedia.html
- **Arquivos utilizados:** `articles.tsv`, `links.tsv`, `categories.tsv`
- **Os arquivos já estão incluídos no repositório** em `data/dataset_parte2/`

### Modelagem do Grafo

| Propriedade | Valor |
|---|---|
| Nós | Artigos da Wikipedia (~4.600) |
| Arestas | Hiperlinks entre artigos (~119.000) |
| Tipo | **Dirigido e ponderado** |
| Peso | `1 / grau_de_saída` do nó origem |

O peso modela a **probabilidade de navegação aleatória** por aquele link — artigos com poucos links de saída têm arestas mais "valiosas".

---

## Estrutura do Projeto

```
projeto_grafos/
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
├── out/                     # Saídas geradas automaticamente
├── app_parte2.py            # Dashboard Streamlit
└── requirements.txt
```

---

## Instalação

```bash
pip install -r requirements.txt
```

---

## Como Executar

### Rodar todos os algoritmos e gerar relatório completo
```bash
python -m src.cli --dataset ./data/dataset_parte2/ --alg ALL --out ./out/
```

### Subir o dashboard Streamlit
```bash
python -m streamlit run app_parte2.py
```

### Rodar os testes
```bash
python -m pytest tests/ -v
```

---

## Saídas Geradas (`out/`)

| Arquivo | Descrição |
|---|---|
| `parte2_report.json` | Resultados completos de todos os algoritmos e tabela de desempenho |
| `degree_distribution.png` | Distribuição de graus da rede (escala log) |
| `performance_bars.png` | Tempo médio por algoritmo |
| `comparison_lines.png` | Tempo por execução individual |
| `distance_heatmap.png` | Heatmap de distâncias Dijkstra entre pares |
| `in_out_degree_distribution.png` | Compara graus de entrada e saida em escala log |
| `degree_in_out_scatter.png` | Dispersao entrada x saida para identificar hubs |
| `weight_distribution.png` | Distribuicao dos pesos `1/grau_saida` |
| `bfs_layers.png` | Comportamento do BFS por camadas |
| `dfs_edge_classes.png` | Classificacao de arestas no DFS |
| `dijkstra_paths.png` | Distancia ponderada versus saltos nos caminhos |
| `bellman_ford_scenarios.png` | Cenarios de Bellman-Ford com pesos negativos |
| `avd_interactive_charts.html` | Dashboard HTML interativo com zoom, tooltips e janela deslizante |
| `grafo_interativo.html` | Visualização D3.js interativa — abre direto no navegador |
| `parte2_avd_notes.md` | Notas analiticas para apoiar o PDF tecnico |

O `grafo_interativo.html` pode ser aberto **diretamente no navegador** sem precisar do Streamlit.

### Camada AVD

As visualizacoes seguem as recomendacoes do PDF interdisciplinar:

- cores consistentes por algoritmo em barras e linhas;
- eixos e legendas explicitos para comparabilidade;
- separacao visual entre grafo completo e subgrafo usado no Bellman-Ford;
- heatmap distinguindo distancia infinita de distancia zero;
- graficos de comportamento, nao apenas desempenho: camadas do BFS, classes do DFS e caminhos do Dijkstra;
- discussao de limitacoes visuais em `out/parte2_avd_notes.md`, especialmente densidade, sobreposicao de arestas e limites do peso `1/grau_saida`.

---

## Algoritmos Implementados

Todos implementados do zero, sem bibliotecas de algoritmos de grafos.

| Algoritmo | Complexidade | Casos cobertos |
|---|---|---|
| BFS | O(V + E) | 3 fontes distintas, relato de camadas |
| DFS | O(V + E) | 3 fontes, detecção de ciclos, classificação de arestas |
| Dijkstra | O((V+E) log V) | 5 pares origem-destino, rejeita pesos negativos |
| Bellman-Ford | O(V · E) | pesos normais, peso negativo sem ciclo, ciclo negativo detectado |

---

## Pesos Negativos — Justificativa

O grafo Wikispeedia tem pesos naturalmente positivos (`1/grau_saída`). Para atender o requisito de Bellman-Ford com pesos negativos:

- **Cenário 1 — peso negativo sem ciclo:** uma aresta recebe peso `-0.5`, simulando um "atalho privilegiado" de navegação (ex: link de redirecionamento direto de alta relevância).
- **Cenário 2 — ciclo negativo detectado:** subgrafo dirigido controlado com 3 nós e arestas `-1.0` formando um ciclo A→B→C→A. O algoritmo detecta e sinaliza corretamente.

---

## Visualização React (Grafo Completo)

O app React em `web/` renderiza o grafo completo (~4.600 nós, ~119.000 arestas) usando Canvas + D3.js, com performance muito superior ao Streamlit para esse volume de dados.

### Funcionalidades
- Grafo completo com todos os nós e arestas
- Filtro por categoria (clique na legenda)
- Busca de artigo por nome
- Caminho mínimo entre dois artigos (Dijkstra rodando no browser)
- Hover com tooltip de detalhes
- Zoom, pan e arrastar nós

### Como rodar

**Passo 1 — Exportar o grafo (só precisa fazer uma vez):**
```bash
# Na raiz do projeto
python -m src.export_graph_json ./data/dataset_parte2 ./web/public
```
Isso gera `web/public/graph_data.json`.

**Passo 2 — Instalar dependências do React:**
```bash
cd web
npm install
```

**Passo 3 — Rodar em desenvolvimento:**
```bash
npm run dev
```
Abre em `http://localhost:5173`

**Passo 4 — Build para produção (gera HTML estático):**
```bash
npm run build
```
Os arquivos ficam em `web/dist/` e podem ser abertos diretamente no navegador.
