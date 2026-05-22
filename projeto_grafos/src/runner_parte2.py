import os
import sys
import json
import random

from src.graph import Graph
from src.bfs_dfs import bfs, dfs
from src.dijkstra import dijkstra, reconstruct_path
from src.bellman_ford import bellman_ford, reconstruct_path_bf
from src.loader_parte2 import build_graph, inject_negative_weights, save_report
from src.metrics import (
    run_timed,
    describe_graph,
    format_bfs_result,
    format_dfs_result,
    format_dijkstra_result,
    format_bf_result,
    build_performance_table,
    save_json,
)
from src.visualizations import (
    plot_degree_distribution,
    plot_performance_bars,
    plot_distance_heatmap,
    plot_algorithm_comparison_lines,
    export_graph_sample_pyvis,
)

PREFERRED_SOURCES = [
    "United_States", "Science", "Africa",
    "Europe", "Mathematics", "Philosophy",
    "Brazil", "Music", "Film",
]

PREFERRED_PAIRS = [
    ("United_States", "Africa"),
    ("Science", "Philosophy"),
    ("Mathematics", "Music"),
    ("Europe", "Brazil"),
    ("Film", "Science"),
]


def pick_nodes(graph, preferred, n):
    result = [p for p in preferred if p in graph.nodes]
    if len(result) < n:
        extras = [
            node for node in sorted(graph.nodes, key=lambda u: -graph.degree(u))
            if node not in result
        ]
        result += extras[: n - len(result)]
    return result[:n]


def run_parte2(data_dir, out_dir, alg=None, source=None, target=None):
    os.makedirs(out_dir, exist_ok=True)

    print("=== Construindo grafo Wikispeedia ===")
    graph, _, _, article_categories = build_graph(data_dir)

    nodes_list = list(graph.nodes)
    if not nodes_list:
        print("Grafo vazio. Verifique os arquivos em data/dataset_parte2/")
        sys.exit(1)

    bfs_sources = pick_nodes(graph, PREFERRED_SOURCES, 3)

    dijk_pairs = [
        (u, v) for u, v in PREFERRED_PAIRS if u in graph.nodes and v in graph.nodes
    ]
    top_nodes = [
        n for n in sorted(graph.nodes, key=lambda u: -graph.degree(u))
    ]
    while len(dijk_pairs) < 5 and len(top_nodes) >= 2:
        u, v = top_nodes.pop(0), top_nodes.pop(0)
        if (u, v) not in dijk_pairs:
            dijk_pairs.append((u, v))

    bf_src = bfs_sources[0]
    bf_tgt = bfs_sources[1] if len(bfs_sources) > 1 else nodes_list[1]

    graph_info = describe_graph(graph)
    print(json.dumps(graph_info, indent=2, default=str))

    performance_log = []
    report = {
        "dataset": "Wikispeedia — Wikipedia Navigation Links",
        "graph_description": graph_info,
        "bfs": [],
        "dfs": [],
        "dijkstra": [],
        "bellman_ford": [],
    }

    print("\n=== BFS ===")
    for src in bfs_sources:
        res, t, mem = run_timed(bfs, graph, src, track_memory=True)
        fmt = format_bfs_result(res, src)
        fmt["time_s"] = t
        fmt["mem_kb"] = mem
        report["bfs"].append(fmt)
        performance_log.append({"algorithm": "BFS", "task": f"source={src}", "time_s": t, "mem_kb": mem})
        print(f"BFS {src}: {res['visited_count']} nós, {len(res['layers'])} camadas, {t:.4f}s")

    print("\n=== DFS ===")
    for src in bfs_sources:
        res, t, mem = run_timed(dfs, graph, src, track_memory=True)
        fmt = format_dfs_result(res, src)
        fmt["time_s"] = t
        fmt["mem_kb"] = mem
        report["dfs"].append(fmt)
        performance_log.append({"algorithm": "DFS", "task": f"source={src}", "time_s": t, "mem_kb": mem})
        print(f"DFS {src}: ciclo={res['has_cycle']}, {res['visited_count']} nós, {t:.4f}s")

    print("\n=== Dijkstra ===")
    distance_matrix = {}
    sample_labels = []
    for u, v in dijk_pairs[:5]:
        try:
            res, t, mem = run_timed(dijkstra, graph, u, v, track_memory=True)
            path = reconstruct_path(res["parent"], u, v)
            fmt = format_dijkstra_result(res["dist"], res["parent"], u, v, path)
            fmt["time_s"] = t
            fmt["mem_kb"] = mem
            report["dijkstra"].append(fmt)
            performance_log.append({"algorithm": "Dijkstra", "task": f"{u}->{v}", "time_s": t, "mem_kb": mem})
            if u not in distance_matrix:
                distance_matrix[u] = {}
                sample_labels.append(u)
            distance_matrix[u][v] = res["dist"].get(v, float("inf"))
            print(f"Dijkstra {u}->{v}: dist={fmt['distance']}, path_len={fmt['path_length']}, {t:.4f}s")
        except ValueError as e:
            print(f"  AVISO Dijkstra: {e}")

    print("\n=== Bellman-Ford (pesos normais) ===")
    res, t, mem = run_timed(bellman_ford, graph, bf_src, track_memory=True)
    path = reconstruct_path_bf(res["parent"], bf_src, bf_tgt)
    fmt = format_bf_result(res, bf_src, bf_tgt, path)
    fmt["time_s"] = t
    fmt["mem_kb"] = mem
    fmt["scenario"] = "normal_weights"
    report["bellman_ford"].append(fmt)
    performance_log.append({"algorithm": "Bellman-Ford", "task": f"{bf_src}->{bf_tgt}", "time_s": t, "mem_kb": mem})
    print(f"BF {bf_src}->{bf_tgt}: dist={fmt['distance']}, neg_cycle={fmt['has_negative_cycle']}, {t:.4f}s")

    print("\n=== Bellman-Ford (peso negativo sem ciclo negativo) ===")
    import copy
    g_neg = copy.deepcopy(graph)
    inject_negative_weights(g_neg, [(bf_src, bf_tgt)], bonus=-0.5)
    res_neg, t, mem = run_timed(bellman_ford, g_neg, bf_src, track_memory=True)
    path_neg = reconstruct_path_bf(res_neg["parent"], bf_src, bf_tgt)
    fmt_neg = format_bf_result(res_neg, bf_src, bf_tgt, path_neg)
    fmt_neg["time_s"] = t
    fmt_neg["mem_kb"] = mem
    fmt_neg["scenario"] = "negative_weight_no_cycle"
    fmt_neg["injected_edge"] = f"{bf_src}->{bf_tgt} w=-0.5"
    report["bellman_ford"].append(fmt_neg)
    performance_log.append({"algorithm": "Bellman-Ford", "task": f"neg_no_cycle_{bf_src}->{bf_tgt}", "time_s": t, "mem_kb": mem})
    print(f"BF neg {bf_src}->{bf_tgt}: dist={fmt_neg['distance']}, neg_cycle={fmt_neg['has_negative_cycle']}, {t:.4f}s")

    print("\n=== Bellman-Ford (ciclo negativo detectado) ===")
    cycle_g = Graph(directed=True)
    a, b, c = bfs_sources[0], bfs_sources[1], bfs_sources[2] if len(bfs_sources) >= 3 else nodes_list[2]
    cycle_g.add_edge(a, b, -1.0)
    cycle_g.add_edge(b, c, -1.0)
    cycle_g.add_edge(c, a, -1.0)
    res_cycle, t, mem = run_timed(bellman_ford, cycle_g, a, track_memory=True)
    fmt_cycle = {
        "scenario": "negative_cycle_detected",
        "nodes_in_cycle": [a, b, c],
        "injected_edges": [f"{a}->{b}", f"{b}->{c}", f"{c}->{a}"],
        "has_negative_cycle": res_cycle["has_negative_cycle"],
        "time_s": t,
        "mem_kb": mem,
    }
    report["bellman_ford"].append(fmt_cycle)
    performance_log.append({"algorithm": "Bellman-Ford", "task": "neg_cycle_detection", "time_s": t, "mem_kb": mem})
    print(f"BF ciclo negativo detectado: {res_cycle['has_negative_cycle']}, {t:.4f}s")

    report["performance_table"] = build_performance_table(performance_log)
    save_report(report, out_dir)

    print("\n=== Gerando visualizações ===")
    plot_degree_distribution(graph, out_dir)
    plot_performance_bars(performance_log, out_dir)
    plot_algorithm_comparison_lines(performance_log, out_dir)
    if sample_labels:
        plot_distance_heatmap(distance_matrix, sample_labels, out_dir)
    export_graph_sample_pyvis(graph, out_dir, article_categories=article_categories)

    print(f"\n=== Parte 2 concluída. Saídas em {out_dir} ===")
    return report
