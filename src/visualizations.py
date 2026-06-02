import os
import json
from collections import Counter, defaultdict


ALGORITHM_COLORS = {
    "BFS": "#2563EB",
    "DFS": "#059669",
    "Dijkstra": "#D97706",
    "Bellman-Ford": "#DC2626",
}

EDGE_CLASS_COLORS = {
    "tree": "#2563EB",
    "back": "#DC2626",
    "forward": "#D97706",
    "cross": "#64748B",
}


def _style_axes(ax):
    ax.grid(axis="y", color="#E5E7EB", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _save_fig(fig, out_dir, filename):
    path = os.path.join(out_dir, filename)
    fig.tight_layout()
    try:
        fig.savefig(path, dpi=160, bbox_inches="tight")
    except PermissionError:
        stem, ext = os.path.splitext(filename)
        path = os.path.join(out_dir, f"{stem}_avd{ext}")
        fig.savefig(path, dpi=160, bbox_inches="tight")
    return path


def plot_degree_distribution(graph, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib nao instalado; pulando grafico de distribuicao de graus.")
        return None

    degrees = [graph.degree(u) for u in graph.nodes]
    counter = Counter(degrees)
    x = sorted(counter.keys())
    y = [counter[d] for d in x]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x, y, color="#2563EB", edgecolor="white", linewidth=0.5)
    ax.set_xlabel("Grau de saida", fontsize=12)
    ax.set_ylabel("Frequencia (escala log)", fontsize=12)
    ax.set_title("Distribuicao de Graus de Saida - Wikispeedia", fontsize=14)
    ax.set_yscale("log")
    _style_axes(ax)
    path = _save_fig(fig, out_dir, "degree_distribution.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def _directed_degrees(graph):
    out_degrees = {u: graph.degree(u) for u in graph.nodes}
    in_degrees = {u: 0 for u in graph.nodes}
    for u, v, _ in graph.edges():
        in_degrees.setdefault(u, 0)
        in_degrees[v] = in_degrees.get(v, 0) + 1
    return in_degrees, out_degrees


def plot_in_out_degree_distribution(graph, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    in_degrees, out_degrees = _directed_degrees(graph)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    for ax, values, title, color in [
        (axes[0], out_degrees.values(), "Grau de Saida", "#2563EB"),
        (axes[1], in_degrees.values(), "Grau de Entrada", "#059669"),
    ]:
        counter = Counter(values)
        x = sorted(counter.keys())
        y = [counter[d] for d in x]
        ax.bar(x, y, color=color, edgecolor="white", linewidth=0.4)
        ax.set_title(title)
        ax.set_xlabel("Grau")
        ax.set_yscale("log")
        _style_axes(ax)
    axes[0].set_ylabel("Frequencia (escala log)")
    fig.suptitle("Distribuicao de Grau em Grafo Dirigido", fontsize=14)
    path = _save_fig(fig, out_dir, "in_out_degree_distribution.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_degree_scatter(graph, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    in_degrees, out_degrees = _directed_degrees(graph)
    xs = [out_degrees[u] for u in graph.nodes]
    ys = [in_degrees.get(u, 0) for u in graph.nodes]
    sizes = [10 + min(out_degrees[u] + in_degrees.get(u, 0), 250) * 0.25 for u in graph.nodes]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(xs, ys, s=sizes, color="#2563EB", alpha=0.35, edgecolors="none")
    ax.set_title("Relacao entre Grau de Saida e Entrada")
    ax.set_xlabel("Grau de saida")
    ax.set_ylabel("Grau de entrada")
    _style_axes(ax)
    path = _save_fig(fig, out_dir, "degree_in_out_scatter.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_weight_distribution(graph, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    weights = [w for _, _, w in graph.edges()]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(weights, bins=40, color="#7C3AED", edgecolor="white", linewidth=0.5)
    ax.set_title("Distribuicao dos Pesos das Arestas")
    ax.set_xlabel("Peso = 1 / grau de saida")
    ax.set_ylabel("Quantidade de arestas")
    _style_axes(ax)
    path = _save_fig(fig, out_dir, "weight_distribution.png")
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
        alg_times.setdefault(alg, []).append(entry["time_s"])

    algs = [a for a in ALGORITHM_COLORS if a in alg_times]
    avg_times = [sum(alg_times[a]) / len(alg_times[a]) for a in algs]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(algs, avg_times, color=[ALGORITHM_COLORS[a] for a in algs], edgecolor="white")
    ax.set_ylabel("Tempo medio (s)", fontsize=12)
    ax.set_title("Desempenho Medio por Algoritmo", fontsize=14)
    for bar, val in zip(bars, avg_times):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{val:.4f}s",
                ha="center", va="bottom", fontsize=9)
    _style_axes(ax)
    fig.text(
        0.02, 0.01,
        "Obs.: Bellman-Ford foi medido em subgrafo controlado por custo O(V*E).",
        fontsize=9, color="#475569"
    )
    path = _save_fig(fig, out_dir, "performance_bars.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_distance_heatmap(distance_matrix, labels, out_dir):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return None

    all_labels = list(labels)
    for u, row in distance_matrix.items():
        if u not in all_labels:
            all_labels.append(u)
        for v in row:
            if v not in all_labels:
                all_labels.append(v)

    n = len(all_labels)
    matrix = []
    masked_positions = []
    for i, u in enumerate(all_labels):
        row_values = []
        for j, v in enumerate(all_labels):
            d = distance_matrix.get(u, {}).get(v, float("inf"))
            if d == float("inf"):
                row_values.append(float("nan"))
                masked_positions.append((i, j))
            else:
                row_values.append(d)
        matrix.append(row_values)

    arr = np.array(matrix, dtype=float)
    positive = arr[np.isfinite(arr) & (arr > 0)]
    vmin = float(positive.min()) if positive.size else None
    vmax = float(positive.max()) if positive.size else None
    fig, ax = plt.subplots(figsize=(8, 7))
    cmap = plt.cm.coolwarm.copy()
    cmap.set_bad(color="#E5E7EB")
    im = ax.imshow(arr, cmap=cmap, aspect="auto", vmin=vmin, vmax=vmax)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(all_labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(all_labels, fontsize=8)
    for i, j in masked_positions:
        ax.text(j, i, "inf", ha="center", va="center", fontsize=7, color="#64748B")
    fig.colorbar(im, ax=ax, label="Distancia ponderada (positivas normalizadas)")
    ax.set_title("Heatmap de Distancias entre Pares (Dijkstra)", fontsize=13)
    path = _save_fig(fig, out_dir, "distance_heatmap.png")
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
        alg_series.setdefault(entry["algorithm"], []).append(entry["time_s"])

    fig, ax = plt.subplots(figsize=(9, 5))
    markers = {"BFS": "o", "DFS": "s", "Dijkstra": "^", "Bellman-Ford": "D"}
    for alg in [a for a in ALGORITHM_COLORS if a in alg_series]:
        times = alg_series[alg]
        ax.plot(
            range(1, len(times) + 1), times, label=alg,
            marker=markers.get(alg, "o"), color=ALGORITHM_COLORS[alg], linewidth=2,
        )
    ax.set_xlabel("Tarefa dentro do algoritmo", fontsize=11)
    ax.set_ylabel("Tempo (s)", fontsize=11)
    ax.set_title("Comparacao de Tempo por Tarefa", fontsize=13)
    ax.legend()
    _style_axes(ax)
    fig.text(
        0.02, 0.01,
        "Cada ponto representa uma fonte, par origem-destino ou cenario de teste.",
        fontsize=9, color="#475569"
    )
    path = _save_fig(fig, out_dir, "comparison_lines.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_bfs_layers(bfs_entries, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    if not bfs_entries:
        return None

    labels = [entry["source"] for entry in bfs_entries]
    max_layer = max(max(map(int, entry["layer_sizes"].keys())) for entry in bfs_entries)
    x = range(len(labels))
    bottoms = [0] * len(labels)
    palette = ["#DBEAFE", "#93C5FD", "#60A5FA", "#3B82F6", "#2563EB", "#1D4ED8", "#1E40AF", "#1E3A8A"]

    fig, ax = plt.subplots(figsize=(10, 5))
    for layer in range(max_layer + 1):
        vals = [entry["layer_sizes"].get(str(layer), entry["layer_sizes"].get(layer, 0)) for entry in bfs_entries]
        ax.bar(x, vals, bottom=bottoms, label=f"Camada {layer}", color=palette[layer % len(palette)], edgecolor="white")
        bottoms = [b + v for b, v in zip(bottoms, vals)]

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("Nos visitados")
    ax.set_title("BFS: Alcance por Camadas")
    ax.legend(ncol=4, fontsize=8)
    _style_axes(ax)
    path = _save_fig(fig, out_dir, "bfs_layers.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_dfs_edge_classes(dfs_entries, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    if not dfs_entries:
        return None

    labels = [entry["source"] for entry in dfs_entries]
    classes = ["tree", "back", "forward", "cross"]
    x = range(len(labels))
    bottoms = [0] * len(labels)

    fig, ax = plt.subplots(figsize=(9, 5))
    for cls in classes:
        vals = [entry["edge_class_counts"].get(cls, 0) for entry in dfs_entries]
        ax.bar(x, vals, bottom=bottoms, label=cls, color=EDGE_CLASS_COLORS[cls], edgecolor="white")
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("Arestas classificadas")
    ax.set_title("DFS: Classificacao de Arestas por Fonte")
    ax.legend()
    _style_axes(ax)
    path = _save_fig(fig, out_dir, "dfs_edge_classes.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_dijkstra_paths(dijkstra_entries, out_dir):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return None

    if not dijkstra_entries:
        return None

    labels = [f"{e['source']} -> {e['target']}" for e in dijkstra_entries]
    distances = [0 if e["distance"] == float("inf") else e["distance"] for e in dijkstra_entries]
    hops = [(e.get("path_length") or 1) - 1 for e in dijkstra_entries]
    x = np.arange(len(labels))
    width = 0.38

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax2 = ax1.twinx()
    bars1 = ax1.bar(x - width / 2, distances, width, label="Distancia ponderada", color=ALGORITHM_COLORS["Dijkstra"])
    bars2 = ax2.bar(x + width / 2, hops, width, label="Saltos", color="#64748B")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax1.set_ylabel("Distancia ponderada")
    ax2.set_ylabel("Saltos no caminho")
    ax1.set_title("Dijkstra: Custo Ponderado vs Quantidade de Saltos")
    ax1.bar_label(bars1, fmt="%.3f", fontsize=8, padding=2)
    ax2.bar_label(bars2, fmt="%d", fontsize=8, padding=2)
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    _style_axes(ax1)
    ax2.spines["top"].set_visible(False)
    path = _save_fig(fig, out_dir, "dijkstra_paths.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_bellman_ford_scenarios(bf_entries, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    if not bf_entries:
        return None

    labels = []
    times = []
    colors = []
    for entry in bf_entries:
        scenario = entry.get("scenario", "cenario")
        labels.append(scenario.replace("_", "\n"))
        times.append(entry.get("time_s", 0))
        colors.append("#DC2626" if entry.get("has_negative_cycle") else ALGORITHM_COLORS["Bellman-Ford"])

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, times, color=colors, edgecolor="white")
    ax.set_ylabel("Tempo (s)")
    ax.set_title("Bellman-Ford: Cenarios de Peso Negativo")
    ax.bar_label(bars, labels=[f"{v:.4f}s" for v in times], fontsize=9, padding=3)
    _style_axes(ax)
    path = _save_fig(fig, out_dir, "bellman_ford_scenarios.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def export_interactive_avd_charts(graph, report, performance_entries, distance_matrix, labels, out_dir):
    in_degrees, out_degrees = _directed_degrees(graph)

    def distribution(values):
        counter = Counter(values)
        return [
            {"label": str(k), "value": int(counter[k]), "x": k}
            for k in sorted(counter)
        ]

    def finite_or_none(value):
        return None if value == float("inf") else value

    alg_times = {}
    for entry in performance_entries:
        alg_times.setdefault(entry["algorithm"], []).append(entry["time_s"])
    perf_avg = [
        {"label": alg, "value": sum(alg_times[alg]) / len(alg_times[alg]), "color": ALGORITHM_COLORS[alg]}
        for alg in ALGORITHM_COLORS
        if alg in alg_times
    ]
    perf_series = [
        {
            "label": alg,
            "color": ALGORITHM_COLORS[alg],
            "points": [{"x": i + 1, "y": value} for i, value in enumerate(alg_times.get(alg, []))],
        }
        for alg in ALGORITHM_COLORS
        if alg in alg_times
    ]

    bfs_layers = []
    for entry in report.get("bfs", []):
        for layer, count in entry["layer_sizes"].items():
            bfs_layers.append({
                "label": f"{entry['source']} | C{layer}",
                "value": count,
                "group": entry["source"],
            })

    dfs_classes = []
    for entry in report.get("dfs", []):
        for cls, count in entry["edge_class_counts"].items():
            dfs_classes.append({
                "label": f"{entry['source']} | {cls}",
                "value": count,
                "color": EDGE_CLASS_COLORS.get(cls, "#64748B"),
            })

    dijkstra_dist = []
    dijkstra_hops = []
    for entry in report.get("dijkstra", []):
        label = f"{entry['source']} -> {entry['target']}"
        dijkstra_dist.append({"label": label, "value": finite_or_none(entry["distance"])})
        dijkstra_hops.append({"label": label, "value": max((entry.get("path_length") or 1) - 1, 0)})

    bf_scenarios = [
        {
            "label": entry.get("scenario", "cenario").replace("_", " "),
            "value": entry.get("time_s", 0),
            "color": "#DC2626" if entry.get("has_negative_cycle") else "#991B1B",
        }
        for entry in report.get("bellman_ford", [])
    ]

    heatmap = []
    heatmap_labels = list(labels)
    for y_label in heatmap_labels:
        for x_label in heatmap_labels:
            value = distance_matrix.get(y_label, {}).get(x_label, float("inf"))
            heatmap.append({
                "x": x_label,
                "y": y_label,
                "value": finite_or_none(value),
            })

    chart_data = {
        "degreeOut": distribution(out_degrees.values()),
        "degreeIn": distribution(in_degrees.values()),
        "weights": distribution(round(w, 3) for _, _, w in graph.edges()),
        "scatter": [
            {
                "x": out_degrees[node],
                "y": in_degrees.get(node, 0),
                "label": node,
                "size": min(out_degrees[node] + in_degrees.get(node, 0), 250),
            }
            for node in graph.nodes
        ],
        "perfAvg": perf_avg,
        "perfSeries": perf_series,
        "bfsLayers": bfs_layers,
        "dfsClasses": dfs_classes,
        "dijkstraDist": dijkstra_dist,
        "dijkstraHops": dijkstra_hops,
        "bfScenarios": bf_scenarios,
        "heatmap": heatmap,
        "heatmapLabels": heatmap_labels,
    }
    data_json = json.dumps(chart_data, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Graficos Interativos AVD - Wikispeedia</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: #0b0f16; color: #e5e7eb;
    font-family: Segoe UI, Arial, sans-serif;
  }}
  header {{ padding: 18px 28px 8px; }}
  h1 {{ margin: 0; font-size: 24px; }}
  .subtitle {{ color: #94a3b8; margin-top: 6px; font-size: 13px; }}
  .grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(520px, 1fr));
    gap: 18px; padding: 18px 28px 32px;
  }}
  .card {{
    background: #111821; border: 1px solid #263241; border-radius: 8px;
    padding: 14px 16px 12px; min-height: 420px;
  }}
  .wide {{ grid-column: 1 / -1; }}
  .card-head {{ display: flex; justify-content: space-between; gap: 12px; align-items: center; }}
  h2 {{ margin: 0 0 8px; font-size: 18px; }}
  .controls {{ display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }}
  button {{
    background: #1f2937; color: #d1d5db; border: 1px solid #374151;
    border-radius: 6px; padding: 5px 9px; cursor: pointer; font-size: 12px;
  }}
  button:hover {{ background: #334155; }}
  input[type=range] {{ width: 150px; }}
  svg {{ width: 100%; height: 340px; display: block; overflow: visible; }}
  .axis {{ stroke: #526071; stroke-width: 1; }}
  .gridline {{ stroke: #273241; stroke-width: 1; }}
  .tick {{ fill: #cbd5e1; font-size: 11px; }}
  .label {{ fill: #e5e7eb; font-size: 12px; }}
  .note {{ color: #94a3b8; font-size: 12px; margin-top: 8px; }}
  #tooltip {{
    position: fixed; pointer-events: none; opacity: 0; z-index: 20;
    background: #020617; color: #e5e7eb; border: 1px solid #334155;
    border-radius: 6px; padding: 8px 10px; font-size: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
  }}
</style>
</head>
<body>
<header>
  <h1>Graficos Interativos AVD - Wikispeedia</h1>
  <div class="subtitle">Use zoom, reset e janela deslizante para reduzir poluicao visual em distribuicoes densas.</div>
</header>
<main class="grid">
  <section class="card wide" data-chart="bars-window" data-key="degreeOut" data-title="Distribuicao de Graus de Saida" data-x-label="Grau de saida" data-y-label="Frequencia" data-color="#7cc7ff"></section>
  <section class="card" data-chart="bars-window" data-key="degreeIn" data-title="Distribuicao de Graus de Entrada" data-x-label="Grau de entrada" data-y-label="Frequencia" data-color="#34d399"></section>
  <section class="card" data-chart="scatter" data-key="scatter" data-title="Grau de Saida x Grau de Entrada" data-x-label="Grau de saida" data-y-label="Grau de entrada"></section>
  <section class="card" data-chart="bars-window" data-key="weights" data-title="Distribuicao dos Pesos" data-x-label="Peso da aresta" data-y-label="Frequencia" data-color="#c084fc"></section>
  <section class="card" data-chart="bars" data-key="perfAvg" data-title="Tempo Medio por Algoritmo" data-x-label="Algoritmo" data-y-label="Tempo medio (s)"></section>
  <section class="card" data-chart="lines" data-key="perfSeries" data-title="Tempo por Tarefa" data-x-label="Tarefa" data-y-label="Tempo (s)"></section>
  <section class="card" data-chart="bars-window" data-key="bfsLayers" data-title="BFS: Camadas por Fonte" data-x-label="Fonte e camada" data-y-label="Nos visitados" data-color="#60a5fa"></section>
  <section class="card" data-chart="bars-window" data-key="dfsClasses" data-title="DFS: Classificacao de Arestas" data-x-label="Fonte e classe" data-y-label="Arestas"></section>
  <section class="card" data-chart="group-bars" data-title="Dijkstra: Distancia x Saltos" data-x-label="Par origem-destino" data-y-label="Valor"></section>
  <section class="card" data-chart="bars" data-key="bfScenarios" data-title="Bellman-Ford: Cenarios" data-x-label="Cenario" data-y-label="Tempo (s)"></section>
  <section class="card wide" data-chart="heatmap" data-key="heatmap" data-title="Heatmap de Distancias Dijkstra" data-x-label="Destino" data-y-label="Origem"></section>
</main>
<div id="tooltip"></div>
<script>
const DATA = {data_json};
const tooltip = document.getElementById("tooltip");
const state = {{}};

function showTip(event, html) {{
  tooltip.innerHTML = html;
  tooltip.style.left = `${{event.clientX + 12}}px`;
  tooltip.style.top = `${{event.clientY + 12}}px`;
  tooltip.style.opacity = 1;
}}
function hideTip() {{ tooltip.style.opacity = 0; }}
function fmt(v) {{
  if (v === null || v === undefined || Number.isNaN(v)) return "inf";
  if (Math.abs(v) < 0.01 && v !== 0) return v.toFixed(5);
  if (Math.abs(v) < 1) return v.toFixed(4);
  return String(Math.round(v * 1000) / 1000);
}}
function shortLabel(value, max=18) {{
  const text = String(value ?? "");
  return text.length > max ? text.slice(0, max - 1) + "…" : text;
}}
function niceStep(maxValue, ticks=5) {{
  if (!Number.isFinite(maxValue) || maxValue <= 0) return 1;
  const raw = maxValue / ticks;
  const power = Math.pow(10, Math.floor(Math.log10(raw)));
  const fraction = raw / power;
  const niceFraction = fraction <= 1 ? 1 : fraction <= 2 ? 2 : fraction <= 5 ? 5 : 10;
  return niceFraction * power;
}}
function niceMax(maxValue, ticks=5) {{
  const step = niceStep(maxValue, ticks);
  return Math.ceil(maxValue / step) * step;
}}
function makeSvg(section) {{
  section.innerHTML = `
    <div class="card-head">
      <h2>${{section.dataset.title}}</h2>
      <div class="controls"></div>
    </div>
    <svg></svg>
    <div class="note"></div>`;
  return {{
    controls: section.querySelector(".controls"),
    svg: section.querySelector("svg"),
    note: section.querySelector(".note")
  }};
}}
function dims(svg) {{
  const w = svg.clientWidth || 700, h = 340;
  return {{w, h, l: 74, r: 24, t: 18, b: 82, iw: w - 98, ih: h - 100}};
}}
function drawAxes(svg, d, yMax, labels={{}}, yTicks=5) {{
  const maxNice = niceMax(yMax, yTicks);
  const step = niceStep(yMax, yTicks);
  svg.insertAdjacentHTML("beforeend", `<line class="axis" x1="${{d.l}}" y1="${{d.t}}" x2="${{d.l}}" y2="${{d.t+d.ih}}"/><line class="axis" x1="${{d.l}}" y1="${{d.t+d.ih}}" x2="${{d.l+d.iw}}" y2="${{d.t+d.ih}}"/>`);
  for (let val=0; val<=maxNice + step * 0.5; val += step) {{
    const y = d.t + d.ih - (val / maxNice) * d.ih;
    svg.insertAdjacentHTML("beforeend", `<line class="gridline" x1="${{d.l}}" y1="${{y}}" x2="${{d.l+d.iw}}" y2="${{y}}"/><text class="tick" x="${{d.l-8}}" y="${{y+4}}" text-anchor="end">${{fmt(val)}}</text>`);
  }}
  if (labels.y) {{
    svg.insertAdjacentHTML("beforeend", `<text class="label" transform="translate(18,${{d.t+d.ih/2}}) rotate(-90)" text-anchor="middle">${{labels.y}}</text>`);
  }}
  if (labels.x) {{
    svg.insertAdjacentHTML("beforeend", `<text class="label" x="${{d.l+d.iw/2}}" y="${{d.h-8}}" text-anchor="middle">${{labels.x}}</text>`);
  }}
  return maxNice;
}}
function visibleWindow(key, total, base=50) {{
  if (!state[key]) state[key] = {{start: 0, size: Math.min(base, total)}};
  const s = state[key];
  s.size = Math.max(5, Math.min(s.size, total));
  s.start = Math.max(0, Math.min(s.start, Math.max(0, total - s.size)));
  return s;
}}
function addWindowControls(ui, key, total, render) {{
  const s = visibleWindow(key, total);
  ui.controls.innerHTML = `
    <button data-act="out">- zoom</button>
    <button data-act="in">+ zoom</button>
    <button data-act="reset">reset</button>
    <input type="range" min="0" max="${{Math.max(0,total-s.size)}}" value="${{s.start}}">
  `;
  ui.controls.querySelectorAll("button").forEach(btn => btn.onclick = () => {{
    if (btn.dataset.act === "in") s.size = Math.max(5, Math.floor(s.size * 0.65));
    if (btn.dataset.act === "out") s.size = Math.min(total, Math.ceil(s.size * 1.55));
    if (btn.dataset.act === "reset") {{ s.start = 0; s.size = Math.min(50, total); }}
    render();
  }});
  ui.controls.querySelector("input").oninput = e => {{ s.start = Number(e.target.value); render(); }};
}}
function barChart(section, rows, opts={{}}) {{
  const ui = makeSvg(section);
  const key = section.dataset.key || section.dataset.title;
  const color = section.dataset.color || opts.color || "#7cc7ff";
  const windowed = section.dataset.chart === "bars-window";
  function render() {{
    const d = dims(ui.svg);
    ui.svg.innerHTML = "";
    const source = rows.filter(r => r.value !== null && r.value !== undefined);
    const s = windowed ? visibleWindow(key, source.length) : {{start: 0, size: source.length}};
    const data = source.slice(s.start, s.start + s.size);
    const yMax = Math.max(...data.map(r => r.value), 1);
    const yScaleMax = drawAxes(ui.svg, d, yMax, {{x: section.dataset.xLabel, y: section.dataset.yLabel}});
    const gap = Math.max(2, Math.min(8, d.iw / Math.max(data.length, 1) * 0.18));
    const bw = Math.max(4, d.iw / Math.max(data.length, 1) - gap);
    data.forEach((row, i) => {{
      const x = d.l + i * (bw + gap);
      const h = (row.value / yScaleMax) * d.ih;
      const y = d.t + d.ih - h;
      const fill = row.color || color;
      ui.svg.insertAdjacentHTML("beforeend", `<rect x="${{x}}" y="${{y}}" width="${{bw}}" height="${{h}}" fill="${{fill}}" rx="2"></rect>`);
      const rect = ui.svg.lastElementChild;
      rect.onmousemove = e => showTip(e, `<b>${{row.label ?? row.x}}</b><br>Valor: ${{fmt(row.value ?? row.y)}}`);
      rect.onmouseleave = hideTip;
      const labelStep = data.length <= 14 ? 1 : data.length <= 32 ? 2 : data.length <= 60 ? 5 : 0;
      if (labelStep && i % labelStep === 0) {{
        ui.svg.insertAdjacentHTML("beforeend", `<text class="tick" transform="translate(${{x+bw/2}},${{d.t+d.ih+20}}) rotate(-35)" text-anchor="end">${{shortLabel(row.label ?? row.x, 16)}}</text>`);
      }}
    }});
    ui.note.textContent = windowed ? `Mostrando ${{data.length}} de ${{source.length}} pontos. Use zoom e o controle deslizante para limpar a leitura.` : "";
    if (windowed) addWindowControls(ui, key, source.length, render);
  }}
  render();
}}
function lineChart(section, series) {{
  const ui = makeSvg(section);
  ui.controls.innerHTML = `<button>reset</button>`;
  function render() {{
    const d = dims(ui.svg);
    ui.svg.innerHTML = "";
    const maxX = Math.max(...series.flatMap(s => s.points.map(p => p.x)), 1);
    const maxY = Math.max(...series.flatMap(s => s.points.map(p => p.y)), 1);
    const yScaleMax = drawAxes(ui.svg, d, maxY, {{x: section.dataset.xLabel, y: section.dataset.yLabel}});
    series.forEach(s => {{
      const pts = s.points.map(p => [d.l + (p.x - 1) / Math.max(maxX - 1, 1) * d.iw, d.t + d.ih - p.y / yScaleMax * d.ih]);
      const path = pts.map((p,i) => `${{i ? "L" : "M"}}${{p[0]}},${{p[1]}}`).join(" ");
      ui.svg.insertAdjacentHTML("beforeend", `<path d="${{path}}" fill="none" stroke="${{s.color}}" stroke-width="3"/>`);
      pts.forEach((p, i) => {{
        ui.svg.insertAdjacentHTML("beforeend", `<circle cx="${{p[0]}}" cy="${{p[1]}}" r="5" fill="${{s.color}}"></circle>`);
        const c = ui.svg.lastElementChild;
        c.onmousemove = e => showTip(e, `<b>${{s.label}}</b><br>Tarefa: ${{i+1}}<br>Tempo: ${{fmt(s.points[i].y)}}s`);
        c.onmouseleave = hideTip;
      }});
    }});
    for (let xVal = 1; xVal <= maxX; xVal++) {{
      const x = d.l + (xVal - 1) / Math.max(maxX - 1, 1) * d.iw;
      ui.svg.insertAdjacentHTML("beforeend", `<text class="tick" x="${{x}}" y="${{d.t+d.ih+18}}" text-anchor="middle">${{xVal}}</text>`);
    }}
  }}
  ui.controls.querySelector("button").onclick = render;
  render();
}}
function scatterChart(section, rows) {{
  const ui = makeSvg(section);
  ui.controls.innerHTML = `<button data-z="1.4">+ zoom</button><button data-z="0.7">- zoom</button><button data-z="0">reset</button>`;
  const key = section.dataset.key;
  if (!state[key]) state[key] = {{zoom: 1}};
  function render() {{
    const d = dims(ui.svg);
    ui.svg.innerHTML = "";
    const xMax = Math.max(...rows.map(r => r.x), 1) / state[key].zoom;
    const yMax = Math.max(...rows.map(r => r.y), 1) / state[key].zoom;
    const yScaleMax = drawAxes(ui.svg, d, yMax, {{x: section.dataset.xLabel, y: section.dataset.yLabel}});
    const xScaleMax = niceMax(xMax, 5);
    const xStep = niceStep(xMax, 5);
    for (let val=0; val<=xScaleMax + xStep * 0.5; val += xStep) {{
      const x = d.l + (val / xScaleMax) * d.iw;
      ui.svg.insertAdjacentHTML("beforeend", `<line class="gridline" x1="${{x}}" y1="${{d.t}}" x2="${{x}}" y2="${{d.t+d.ih}}"/><text class="tick" x="${{x}}" y="${{d.t+d.ih+18}}" text-anchor="middle">${{fmt(val)}}</text>`);
    }}
    rows.filter(r => r.x <= xMax && r.y <= yMax).forEach(r => {{
      const x = d.l + r.x / xScaleMax * d.iw;
      const y = d.t + d.ih - r.y / yScaleMax * d.ih;
      const radius = 3 + Math.min(r.size, 250) / 90;
      ui.svg.insertAdjacentHTML("beforeend", `<circle cx="${{x}}" cy="${{y}}" r="${{radius}}" fill="#60a5fa" opacity="0.45"></circle>`);
      const c = ui.svg.lastElementChild;
      c.onmousemove = e => showTip(e, `<b>${{r.label}}</b><br>Saida: ${{r.x}}<br>Entrada: ${{r.y}}`);
      c.onmouseleave = hideTip;
    }});
    ui.note.textContent = "Zoom filtra a area visivel para separar melhor os pontos proximos.";
  }}
  ui.controls.querySelectorAll("button").forEach(btn => btn.onclick = () => {{
    const z = Number(btn.dataset.z);
    state[key].zoom = z ? Math.max(1, Math.min(12, state[key].zoom * z)) : 1;
    render();
  }});
  render();
}}
function groupedDijkstra(section) {{
  const rows = DATA.dijkstraDist.map((r, i) => [
    {{label: `${{r.label}} | dist`, value: r.value, color: "#D97706", kind: "distancia"}},
    {{label: `${{DATA.dijkstraHops[i].label}} | saltos`, value: DATA.dijkstraHops[i].value, color: "#64748B", kind: "saltos"}}
  ]).flat();
  barChart(section, rows, {{color: "#D97706"}});
}}
function heatmapChart(section) {{
  const ui = makeSvg(section);
  ui.controls.innerHTML = `<button>reset</button>`;
  function render() {{
    const d = dims(ui.svg);
    ui.svg.innerHTML = "";
    const labels = DATA.heatmapLabels;
    const vals = DATA.heatmap.map(r => r.value).filter(v => v !== null && v > 0);
    const min = Math.min(...vals, 0);
    const max = Math.max(...vals, 1);
    const cw = d.iw / labels.length;
    const ch = d.ih / labels.length;
    ui.svg.insertAdjacentHTML("beforeend", `<text class="label" transform="translate(18,${{d.t+d.ih/2}}) rotate(-90)" text-anchor="middle">${{section.dataset.yLabel}}</text><text class="label" x="${{d.l+d.iw/2}}" y="${{d.h-8}}" text-anchor="middle">${{section.dataset.xLabel}}</text>`);
    DATA.heatmap.forEach(cell => {{
      const xi = labels.indexOf(cell.x), yi = labels.indexOf(cell.y);
      let color = "#273241";
      if (cell.value !== null) {{
        if (cell.value === 0) {{
          color = "#f8fafc";
        }} else {{
          const intensity = Math.max(0, Math.min(1, (cell.value - min) / Math.max(max - min, 0.000001)));
          const r = Math.round(59 + 196 * intensity);
          const g = Math.round(130 - 90 * intensity);
          const b = Math.round(246 - 150 * intensity);
          color = `rgb(${{r}},${{g}},${{b}})`;
        }}
      }}
      ui.svg.insertAdjacentHTML("beforeend", `<rect x="${{d.l+xi*cw}}" y="${{d.t+yi*ch}}" width="${{cw-2}}" height="${{ch-2}}" fill="${{color}}"></rect>`);
      const rect = ui.svg.lastElementChild;
      rect.onmousemove = e => showTip(e, `<b>${{cell.y}} -> ${{cell.x}}</b><br>Distancia: ${{fmt(cell.value)}}`);
      rect.onmouseleave = hideTip;
    }});
    labels.forEach((label, i) => {{
      ui.svg.insertAdjacentHTML("beforeend", `<text class="tick" x="${{d.l-8}}" y="${{d.t+i*ch+ch/2+4}}" text-anchor="end">${{shortLabel(label, 16)}}</text><text class="tick" transform="translate(${{d.l+i*cw+cw/2}},${{d.t+d.ih+18}}) rotate(-35)" text-anchor="end">${{shortLabel(label, 16)}}</text>`);
    }});
    const legendX = d.l + d.iw - 180;
    const legendY = d.t - 4;
    for (let i=0; i<80; i++) {{
      const intensity = i / 79;
      const r = Math.round(59 + 196 * intensity);
      const g = Math.round(130 - 90 * intensity);
      const b = Math.round(246 - 150 * intensity);
      ui.svg.insertAdjacentHTML("beforeend", `<rect x="${{legendX+i*2}}" y="${{legendY}}" width="2" height="8" fill="rgb(${{r}},${{g}},${{b}})"></rect>`);
    }}
    ui.svg.insertAdjacentHTML("beforeend", `<text class="tick" x="${{legendX}}" y="${{legendY+22}}">${{fmt(min)}}</text><text class="tick" x="${{legendX+160}}" y="${{legendY+22}}" text-anchor="end">${{fmt(max)}}</text>`);
    ui.note.textContent = "Azul indica menor distancia ponderada; vermelho indica maior. Celulas escuras indicam pares inalcançaveis no sentido dirigido.";
  }}
  ui.controls.querySelector("button").onclick = render;
  render();
}}
document.querySelectorAll("[data-chart]").forEach(section => {{
  const type = section.dataset.chart;
  const key = section.dataset.key;
  if (type === "bars" || type === "bars-window") barChart(section, DATA[key]);
  if (type === "lines") lineChart(section, DATA[key]);
  if (type === "scatter") scatterChart(section, DATA[key]);
  if (type === "group-bars") groupedDijkstra(section);
  if (type === "heatmap") heatmapChart(section);
}});
window.addEventListener("resize", () => document.querySelectorAll("[data-chart]").forEach(section => {{
  const type = section.dataset.chart, key = section.dataset.key;
  if (type === "bars" || type === "bars-window") barChart(section, DATA[key]);
  if (type === "lines") lineChart(section, DATA[key]);
  if (type === "scatter") scatterChart(section, DATA[key]);
  if (type === "group-bars") groupedDijkstra(section);
  if (type === "heatmap") heatmapChart(section);
}}));
</script>
</body>
</html>"""
    path = os.path.join(out_dir, "avd_interactive_charts.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Salvo: {path}")
    return path


def export_graph_sample_pyvis(graph, out_dir, max_nodes=100, article_categories=None):
    if article_categories:
        cat_nodes_collapsed = defaultdict(list)
        for node in graph.nodes:
            cats = article_categories.get(node, {"other"})
            root_cat = sorted(cats)[0].split(".")[0].split("/")[0] if cats else "other"
            cat_nodes_collapsed[root_cat].append(node)

        max_per_dominant = max(8, max_nodes // 7)
        sampled_set = set()
        sorted_by_size = sorted(cat_nodes_collapsed.items(), key=lambda x: len(x[1]))
        budget = max_nodes
        n_cats = len(sorted_by_size)
        for idx, (_, members) in enumerate(sorted_by_size):
            remaining_cats = n_cats - idx
            fair_share = max(2, budget // remaining_cats)
            cap = min(fair_share, max_per_dominant)
            top = sorted(members, key=lambda u: -graph.degree(u))[:cap]
            sampled_set.update(top)
            budget = max_nodes - len(sampled_set)
            if budget <= 0:
                break
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

    all_cats = set()
    node_cats = {}
    for n in node_list:
        cats = article_categories.get(n, set()) if article_categories else set()
        top_cat = sorted(cats)[0].split(".")[0].split("/")[0] if cats else "other"
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
  .node text {{ pointer-events:none; fill:#cbd5e1; font-size:9px; text-anchor:middle; opacity:0; transition:opacity .15s; }}
  .node.faded circle {{ opacity:0.15; }}
  .node.faded text {{ opacity:0.1; }}
</style>
</head>
<body>
<div id="info">
  <strong>Wikispeedia - Rede de Navegacao Wikipedia</strong>
  {n_nodes} artigos &nbsp;|&nbsp; {n_edges} conexoes &nbsp;|&nbsp; amostra diversificada por categoria
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
  <button onclick="restart()">Reorganizar</button>
  <button id="pauseBtn" onclick="togglePhysics()">Pausar</button>
  <button onclick="zoomFit()">Ajustar tela</button>
  <button onclick="clearFilter()">Limpar filtro</button>
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
const colorScale = d3.scaleOrdinal()
  .domain(cats)
  .range(["#2dd4bf","#06b6d4","#34d399","#f59e0b","#f87171",
    "#c084fc","#fb923c","#4ade80","#e879f9","#94a3b8"]);

const legend = d3.select("#legend");
cats.forEach(cat => {{
  const item = legend.append("div").attr("class", "legend-item")
    .on("click", () => filterByCategory(cat));
  item.append("div").attr("class", "legend-dot").style("background", colorScale(cat));
  item.append("span").text(cat.replace(/_/g," ").substring(0,22));
}});

let currentZoom = 1;
svg.call(d3.zoom().scaleExtent([0.05, 8])
  .on("zoom", e => {{
    currentZoom = e.transform.k;
    container.attr("transform", e.transform);
    updateLabelVisibility();
  }}));

const sim = d3.forceSimulation(nodesRaw)
  .force("link", d3.forceLink(edgesRaw).id(d => d.id).distance(d => 100 + Math.min(120, d.weight * 900)).strength(0.22))
  .force("charge", d3.forceManyBody().strength(-360).distanceMax(560))
  .force("center", d3.forceCenter(W / 2, H / 2))
  .force("collision", d3.forceCollide(d => d.size + 16))
  .alphaDecay(0.022);

const linkSel = container.append("g").selectAll("line")
  .data(edgesRaw).join("line")
  .attr("class", "link")
  .attr("marker-end", directed ? "url(#arrow)" : null);

const nodeSel = container.append("g").selectAll(".node")
  .data(nodesRaw).join("g").attr("class", "node")
  .call(d3.drag()
    .on("start", (e, d) => {{ if (!e.active) sim.alphaTarget(0.2).restart(); d.fx = d.x; d.fy = d.y; }})
    .on("drag",  (e, d) => {{ d.fx = e.x; d.fy = e.y; }})
    .on("end",   (e, d) => {{ if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }}));

nodeSel.append("circle")
  .attr("r", d => d.size)
  .attr("fill", d => colorScale(d.cat))
  .on("mouseover", (event, d) => {{
    d3.select(event.currentTarget.parentNode).select("text").style("opacity", 1);
    tooltip.style("opacity", 1)
      .style("left", (event.pageX + 14) + "px")
      .style("top",  (event.pageY - 14) + "px")
      .html("<strong>" + d.label.replace(/_/g," ") + "</strong><br>" +
            "Categoria: " + d.cat.replace(/_/g," ") + "<br>" +
            "Grau de saida: " + d.degree);
    linkSel.classed("highlighted", l => l.source.id === d.id || l.target.id === d.id)
      .classed("faded", l => l.source.id !== d.id && l.target.id !== d.id);
  }})
  .on("mouseout", () => {{
    tooltip.style("opacity", 0);
    linkSel.classed("highlighted", false).classed("faded", false);
    updateLabelVisibility();
  }});

nodeSel.append("text")
  .attr("dy", d => d.size + 11)
  .text(d => d.label.replace(/_/g," ").substring(0, 22));

function updateLabelVisibility() {{
  nodeSel.select("text")
    .style("opacity", d => {{
      if (currentZoom >= 2.1) return 1;
      if (currentZoom >= 1.2 && d.degree >= 40) return 1;
      if (d.degree >= 100) return 0.95;
      return 0;
    }});
  linkSel
    .style("stroke-opacity", currentZoom >= 1.6 ? 0.45 : 0.18)
    .style("stroke-width", currentZoom >= 1.8 ? 1.2 : 0.8);
}}
updateLabelVisibility();

sim.on("tick", () => {{
  linkSel.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  nodeSel.attr("transform", d => "translate(" + d.x + "," + d.y + ")");
}});

let paused = false;
function togglePhysics() {{
  paused = !paused;
  paused ? sim.stop() : sim.alphaTarget(0.1).restart();
  document.getElementById("pauseBtn").textContent = paused ? "Retomar" : "Pausar";
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
