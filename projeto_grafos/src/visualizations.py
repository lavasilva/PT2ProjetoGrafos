import os
import json
from collections import Counter, defaultdict


def plot_degree_distribution(graph, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não instalado; pulando gráfico de distribuição de graus.")
        return None

    degrees = [graph.degree(u) for u in graph.nodes]
    counter = Counter(degrees)
    x = sorted(counter.keys())
    y = [counter[d] for d in x]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x, y, color="#3B82F6", edgecolor="white", linewidth=0.5)
    ax.set_xlabel("Grau", fontsize=12)
    ax.set_ylabel("Frequência", fontsize=12)
    ax.set_title("Distribuição de Graus — Wikispeedia", fontsize=14)
    ax.set_yscale("log")
    plt.tight_layout()
    path = os.path.join(out_dir, "degree_distribution.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_performance_bars(performance_entries, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    alg_times = {}
    for entry in performance_entries:
        alg = entry["algorithm"]
        t = entry["time_s"]
        if alg not in alg_times:
            alg_times[alg] = []
        alg_times[alg].append(t)

    algs = list(alg_times.keys())
    avg_times = [sum(alg_times[a]) / len(alg_times[a]) for a in algs]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444"]
    bars = ax.bar(algs, avg_times, color=colors[: len(algs)], edgecolor="white")
    ax.set_ylabel("Tempo médio (s)", fontsize=12)
    ax.set_title("Desempenho Médio por Algoritmo", fontsize=14)
    for bar, val in zip(bars, avg_times):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.0001,
            f"{val:.4f}s",
            ha="center", va="bottom", fontsize=9,
        )
    plt.tight_layout()
    path = os.path.join(out_dir, "performance_bars.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_distance_heatmap(distance_matrix, labels, out_dir):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return None

    n = len(labels)
    matrix = []
    for u in labels:
        row = []
        for v in labels:
            d = distance_matrix.get(u, {}).get(v, float("inf"))
            row.append(d if d != float("inf") else 0)
        matrix.append(row)

    arr = np.array(matrix, dtype=float)
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(arr, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(labels, fontsize=8)
    plt.colorbar(im, ax=ax, label="Distância")
    ax.set_title("Heatmap de Distâncias (Dijkstra)", fontsize=13)
    plt.tight_layout()
    path = os.path.join(out_dir, "distance_heatmap.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_algorithm_comparison_lines(performance_entries, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    alg_series = {}
    for entry in performance_entries:
        alg = entry["algorithm"]
        if alg not in alg_series:
            alg_series[alg] = []
        alg_series[alg].append(entry["time_s"])

    fig, ax = plt.subplots(figsize=(9, 5))
    markers = ["o", "s", "^", "D"]
    colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444"]
    for i, (alg, times) in enumerate(alg_series.items()):
        ax.plot(
            range(1, len(times) + 1), times, label=alg,
            marker=markers[i % len(markers)],
            color=colors[i % len(colors)], linewidth=2,
        )
    ax.set_xlabel("Execução #", fontsize=11)
    ax.set_ylabel("Tempo (s)", fontsize=11)
    ax.set_title("Comparação de Tempo por Execução", fontsize=13)
    ax.legend()
    plt.tight_layout()
    path = os.path.join(out_dir, "comparison_lines.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Salvo: {path}")
    return path


def export_graph_sample_pyvis(graph, out_dir, max_nodes=100, article_categories=None):
    # Amostragem diversificada por categoria
    if article_categories:
        cat_nodes = defaultdict(list)
        for node in graph.nodes:
            cats = article_categories.get(node, {"other"})
            top_cat = sorted(cats)[0].split(".")[0].split("/")[0] if cats else "other"
            cat_nodes[top_cat].append(node)

        # Colapsa subcategorias no nível raiz (ex: Geography.Africa -> Geography)
        # e aplica cap de 15% do total para categorias dominantes
        cat_nodes_collapsed = defaultdict(list)
        for node in graph.nodes:
            cats = article_categories.get(node, {"other"})
            root_cat = sorted(cats)[0].split(".")[0].split("/")[0] if cats else "other"
            cat_nodes_collapsed[root_cat].append(node)

        max_per_dominant = max(8, max_nodes // 7)  # no máximo ~14% por categoria
        sampled_set = set()
        # Ordena cats por tamanho crescente — pequenas entram primeiro completas
        sorted_by_size = sorted(cat_nodes_collapsed.items(), key=lambda x: len(x[1]))
        budget = max_nodes
        n_cats = len(sorted_by_size)
        for idx, (cat, members) in enumerate(sorted_by_size):
            remaining_cats = n_cats - idx
            fair_share = max(2, budget // remaining_cats)
            cap = min(fair_share, max_per_dominant)
            top = sorted(members, key=lambda u: -graph.degree(u))[:cap]
            sampled_set.update(top)
            budget = max_nodes - len(sampled_set)
            if budget <= 0:
                break
        # Completa se sobrar espaço
        if len(sampled_set) < max_nodes:
            for node in sorted(graph.nodes, key=lambda u: -graph.degree(u)):
                sampled_set.add(node)
                if len(sampled_set) >= max_nodes:
                    break
    else:
        top_nodes = sorted(graph.nodes, key=lambda u: -graph.degree(u))[:max_nodes // 2]
        sampled_set = set(top_nodes)
        for node in top_nodes:
            for neighbor, _ in list(graph.get_neighbors(node))[:3]:
                if len(sampled_set) >= max_nodes:
                    break
                sampled_set.add(neighbor)

    node_list = list(sampled_set)
    node_index = {n: i for i, n in enumerate(node_list)}
    max_deg = max((graph.degree(n) for n in node_list), default=1)

    # Categoria principal de cada nó
    all_cats = set()
    node_cats = {}
    for n in node_list:
        cats = article_categories.get(n, set()) if article_categories else set()
        top_cat = sorted(cats)[0].split(".")[0].split("/")[0] if cats else "other"
        # Colapsa subcategorias Geography.X -> Geography para coloração consistente
        top_cat = top_cat.split(".")[0]
        node_cats[n] = top_cat
        all_cats.add(top_cat)

    all_cats_list = sorted(all_cats)
    cat_index = {c: i for i, c in enumerate(all_cats_list)}
    n_cats = len(all_cats_list)

    nodes_data = [
        {
            "id": i,
            "label": n,
            "degree": graph.degree(n),
            "size": 5 + 20 * (graph.degree(n) / max_deg),
            "cat": node_cats[n],
            "catIdx": cat_index[node_cats[n]],
            "nCats": n_cats,
        }
        for i, n in enumerate(node_list)
    ]

    edge_count = {n: 0 for n in sampled_set}
    edges_data = []
    for u, v, w in graph.edges():
        if u in sampled_set and v in sampled_set:
            if edge_count[u] < 6 and edge_count[v] < 6:
                edges_data.append({
                    "source": node_index[u],
                    "target": node_index[v],
                    "weight": round(w, 4),
                })
                edge_count[u] += 1
                edge_count[v] += 1

    nodes_json = json.dumps(nodes_data)
    edges_json = json.dumps(edges_data)
    cats_json = json.dumps(all_cats_list)
    directed_js = "true" if graph.directed else "false"
    n_nodes = len(nodes_data)
    n_edges = len(edges_data)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Grafo Wikispeedia</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0f172a; font-family:'Segoe UI',sans-serif; overflow:hidden; }}
  #info {{ position:absolute; top:12px; left:12px; color:#94a3b8; font-size:12px; line-height:1.7; }}
  #info strong {{ color:#e2e8f0; font-size:14px; display:block; margin-bottom:2px; }}
  #legend {{
    position:absolute; top:12px; right:12px; background:#1e293b;
    border:1px solid #334155; border-radius:8px; padding:10px 14px;
    font-size:11px; color:#94a3b8; max-height:80vh; overflow-y:auto;
    max-width:180px;
  }}
  #legend strong {{ color:#e2e8f0; display:block; margin-bottom:6px; font-size:12px; }}
  .legend-item {{ display:flex; align-items:center; gap:6px; margin-bottom:4px; cursor:pointer; }}
  .legend-dot {{ width:10px; height:10px; border-radius:50%; flex-shrink:0; }}
  #tooltip {{
    position:absolute; background:#1e293b; color:#e2e8f0;
    border:1px solid #334155; border-radius:6px;
    padding:8px 12px; font-size:12px; pointer-events:none;
    opacity:0; transition:opacity 0.15s; max-width:220px;
  }}
  #controls {{
    position:absolute; bottom:16px; left:50%; transform:translateX(-50%);
    display:flex; gap:8px;
  }}
  button {{
    background:#1e293b; color:#94a3b8; border:1px solid #334155;
    padding:6px 14px; border-radius:6px; cursor:pointer; font-size:12px;
  }}
  button:hover {{ background:#334155; color:#e2e8f0; }}
  .link {{ stroke:#334155; stroke-opacity:0.5; stroke-width:1px; fill:none; }}
  .link.highlighted {{ stroke-opacity:1; stroke-width:2px; }}
  .link.faded {{ stroke-opacity:0.06; }}
  .node circle {{ cursor:pointer; stroke:#0f172a; stroke-width:1.5px; }}
  .node text {{ pointer-events:none; fill:#cbd5e1; font-size:9px; text-anchor:middle; }}
  .node.faded circle {{ opacity:0.15; }}
  .node.faded text {{ opacity:0.1; }}
</style>
</head>
<body>
<div id="info">
  <strong>🌐 Wikispeedia — Rede de Navegação Wikipedia</strong>
  {n_nodes} artigos &nbsp;·&nbsp; {n_edges} conexões &nbsp;·&nbsp; amostra diversificada por categoria
</div>
<div id="legend"><strong>Categorias</strong></div>
<div id="tooltip"></div>
<svg id="graph" width="100vw" height="100vh">
  <defs>
    <marker id="arrow" viewBox="0 -4 8 8" refX="22" refY="0"
      markerWidth="5" markerHeight="5" orient="auto">
      <path d="M0,-4L8,0L0,4" fill="#475569"/>
    </marker>
  </defs>
</svg>
<div id="controls">
  <button onclick="restart()">↺ Reorganizar</button>
  <button id="pauseBtn" onclick="togglePhysics()">⏸ Pausar</button>
  <button onclick="zoomFit()">⊡ Ajustar tela</button>
  <button onclick="clearFilter()">✕ Limpar filtro</button>
</div>
<script>
const nodesRaw = {nodes_json};
const edgesRaw = {edges_json};
const cats = {cats_json};
const directed = {directed_js};

const W = window.innerWidth, H = window.innerHeight;
const svg = d3.select("#graph");
const container = svg.append("g");
const tooltip = d3.select("#tooltip");

// Paleta de cores por categoria
const colorScale = d3.scaleOrdinal()
  .domain(cats)
  .range([
    "#2dd4bf","#06b6d4","#22d3ee","#34d399","#4ade80",
    "#a3e635","#38bdf8","#67e8f9","#6ee7b7","#86efac",
    "#5eead4","#7dd3fc","#bbf7d0","#99f6e4","#bae6fd",
    "#d9f99d","#a7f3d0","#cffafe","#e0f2fe","#dcfce7"
  ]);

// Legenda
const legend = d3.select("#legend");
cats.forEach(cat => {{
  const item = legend.append("div").attr("class", "legend-item")
    .on("click", () => filterByCategory(cat));
  item.append("div").attr("class", "legend-dot")
    .style("background", colorScale(cat));
  item.append("span").text(cat.replace(/_/g," ").substring(0,22));
}});

svg.call(d3.zoom().scaleExtent([0.05, 6])
  .on("zoom", e => container.attr("transform", e.transform)));

const sim = d3.forceSimulation(nodesRaw)
  .force("link", d3.forceLink(edgesRaw).id(d => d.id).distance(110).strength(0.3))
  .force("charge", d3.forceManyBody().strength(-280).distanceMax(450))
  .force("center", d3.forceCenter(W / 2, H / 2))
  .force("collision", d3.forceCollide(d => d.size + 8))
  .alphaDecay(0.022);

const linkSel = container.append("g")
  .selectAll("line")
  .data(edgesRaw).join("line")
  .attr("class", "link")
  .attr("marker-end", directed ? "url(#arrow)" : null);

const nodeSel = container.append("g")
  .selectAll(".node")
  .data(nodesRaw).join("g")
  .attr("class", "node")
  .call(d3.drag()
    .on("start", (e, d) => {{ if (!e.active) sim.alphaTarget(0.2).restart(); d.fx = d.x; d.fy = d.y; }})
    .on("drag",  (e, d) => {{ d.fx = e.x; d.fy = e.y; }})
    .on("end",   (e, d) => {{ if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }}));

nodeSel.append("circle")
  .attr("r", d => d.size)
  .attr("fill", d => colorScale(d.cat))
  .on("mouseover", (event, d) => {{
    tooltip.style("opacity", 1)
      .style("left", (event.pageX + 14) + "px")
      .style("top",  (event.pageY - 14) + "px")
      .html("<strong>" + d.label.replace(/_/g," ") + "</strong><br>" +
            "Categoria: " + d.cat.replace(/_/g," ") + "<br>" +
            "Grau de saída: " + d.degree);
    linkSel
      .classed("highlighted", l => l.source.id === d.id || l.target.id === d.id)
      .classed("faded", l => l.source.id !== d.id && l.target.id !== d.id);
  }})
  .on("mouseout", () => {{
    tooltip.style("opacity", 0);
    linkSel.classed("highlighted", false).classed("faded", false);
  }});

nodeSel.append("text")
  .attr("dy", d => d.size + 11)
  .text(d => d.label.replace(/_/g," ").substring(0, 22));

sim.on("tick", () => {{
  linkSel
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  nodeSel.attr("transform", d => "translate(" + d.x + "," + d.y + ")");
}});

let paused = false;
function togglePhysics() {{
  paused = !paused;
  paused ? sim.stop() : sim.alphaTarget(0.1).restart();
  document.getElementById("pauseBtn").textContent = paused ? "▶ Retomar" : "⏸ Pausar";
}}
function restart() {{ sim.alpha(0.9).alphaTarget(0).restart(); }}
function zoomFit() {{
  svg.transition().duration(700)
    .call(d3.zoom().transform, d3.zoomIdentity.translate(W*0.1, H*0.1).scale(0.8));
}}
function filterByCategory(cat) {{
  nodeSel.classed("faded", d => d.cat !== cat);
  linkSel.classed("faded", l => l.source.cat !== cat && l.target.cat !== cat);
}}
function clearFilter() {{
  nodeSel.classed("faded", false);
  linkSel.classed("faded", false);
}}
</script>
</body>
</html>"""

    path = os.path.join(out_dir, "grafo_interativo.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Salvo: {path}")
    return path
