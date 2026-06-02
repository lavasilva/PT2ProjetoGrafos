import json
import os
from collections import Counter

import streamlit as st


st.set_page_config(
    page_title="Wikispeedia - Grafo de Navegação Wikipedia",
    page_icon="🔎",
    layout="wide",
)

st.title("Rede de Navegação Wikipedia - Wikispeedia")
st.markdown("**Parte 2 do Projeto de Grafos** - BFS, DFS, Dijkstra e Bellman-Ford")

DATA_DIR = "./data/dataset_parte2"
OUT_DIR = "./out"


@st.cache_resource(show_spinner="Construindo grafo Wikispeedia...")
def get_graph():
    from src.loader_parte2 import build_graph

    graph, _, _, article_categories = build_graph(DATA_DIR)
    return graph, article_categories


def load_report():
    path = os.path.join(OUT_DIR, "parte2_report.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def show_image_if_exists(filename, caption):
    path = os.path.join(OUT_DIR, filename)
    if os.path.exists(path):
        st.image(path, caption=caption, use_container_width=True)


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Grafo e Dataset",
        "BFS / DFS",
        "Dijkstra",
        "Bellman-Ford",
        "Desempenho",
        "Dashboard",
    ]
)

with tab1:
    st.header("Descrição do Dataset e do Grafo")
    st.markdown(
        """
        **Wikispeedia** é um dataset de navegação entre artigos da Wikipedia.
        Cada nó é um artigo e cada aresta dirigida representa um hiperlink de um artigo para outro.
        O peso de cada aresta é `1 / grau_de_saída`, representando a probabilidade de seguir aquele link.
        """
    )

    if not os.path.isdir(DATA_DIR):
        st.warning(
            f"Dataset não encontrado em `{DATA_DIR}`. Coloque os arquivos "
            "`articles.tsv`, `links.tsv` e `categories.tsv` nesse diretório."
        )
    else:
        if st.button("Carregar / Recarregar Grafo"):
            st.cache_resource.clear()

        try:
            graph, _ = get_graph()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Nós (artigos)", graph.num_nodes())
            col2.metric("Arestas (links)", graph.num_edges())
            col3.metric("Tipo", "Dirigido")
            col4.metric("Ponderado", "Sim (1/grau)")

            st.subheader("Distribuição de Graus de Saída")
            import pandas as pd

            degrees = [graph.degree(u) for u in graph.nodes]
            counter = Counter(degrees)
            df_deg = pd.DataFrame(
                sorted(counter.items())[:50],
                columns=["Grau", "Frequência"],
            ).set_index("Grau")
            st.bar_chart(df_deg)

            st.subheader("Top 20 Artigos por Grau de Saída")
            top20 = sorted(graph.nodes, key=lambda u: -graph.degree(u))[:20]
            df_top = pd.DataFrame(
                {"Artigo": top20, "Grau de saída": [graph.degree(u) for u in top20]}
            )
            st.dataframe(df_top, use_container_width=True)
        except Exception as exc:
            st.error(f"Erro ao carregar grafo: {exc}")

    show_image_if_exists("degree_distribution.png", "Distribuição de graus")
    show_image_if_exists("in_out_degree_distribution.png", "Graus de entrada e saída")
    show_image_if_exists("degree_in_out_scatter.png", "Relação entre grau de entrada e saída")
    show_image_if_exists("weight_distribution.png", "Distribuição dos pesos das arestas")

    interactive_path = os.path.join(OUT_DIR, "grafo_interativo.html")
    if os.path.exists(interactive_path):
        st.subheader("Visualização Interativa do Grafo")
        with open(interactive_path, "r", encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=700, scrolling=True)

with tab2:
    st.header("BFS e DFS")
    report = load_report()

    if report is None:
        st.info(
            "Execute `python -m src.cli --dataset ./data/dataset_parte2/ --alg ALL --out ./out/` "
            "para gerar o relatório."
        )
    else:
        st.subheader("BFS - Exploração em Camadas")
        for entry in report.get("bfs", []):
            with st.expander(f"BFS | Fonte: {entry['source']}"):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Nós visitados", entry["visited_count"])
                col2.metric("Camadas", entry["num_layers"])
                col3.metric("Tempo (s)", f"{entry['time_s']:.4f}")
                col4.metric("Memória (KB)", entry.get("mem_kb", "-"))
                st.write("**Tamanho por camada:**", entry["layer_sizes"])
                st.write("**Ordem de visita (amostra):**", entry["order_sample"])

        st.subheader("DFS - Exploração em Profundidade")
        for entry in report.get("dfs", []):
            with st.expander(f"DFS | Fonte: {entry['source']}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Nós visitados", entry["visited_count"])
                col2.metric("Ciclo detectado", "Sim" if entry["has_cycle"] else "Não")
                col3.metric("Tempo (s)", f"{entry['time_s']:.4f}")
                st.write("**Classificação de arestas:**", entry["edge_class_counts"])

    show_image_if_exists("bfs_layers.png", "BFS: alcance por camadas")
    show_image_if_exists("dfs_edge_classes.png", "DFS: classificação de arestas")

    st.subheader("Busca Interativa")
    try:
        graph, _ = get_graph()
        nodes_sorted = sorted(graph.nodes)
        src_bfs = st.selectbox("Artigo de origem", nodes_sorted, key="bfs_src")
        alg_choice = st.radio("Algoritmo", ["BFS", "DFS"], horizontal=True)
        if st.button("Executar", key="run_bfs_dfs"):
            from src.bfs_dfs import bfs, dfs
            from src.metrics import run_timed

            if alg_choice == "BFS":
                res, t, _ = run_timed(bfs, graph, src_bfs, track_memory=True)
                st.success(
                    f"Visitados: {res['visited_count']} | Camadas: {len(res['layers'])} | Tempo: {t:.4f}s"
                )
                st.write(
                    "Primeiras camadas:",
                    {k: v[:8] for k, v in list(res["layers"].items())[:5]},
                )
            else:
                res, t, _ = run_timed(dfs, graph, src_bfs, track_memory=True)
                st.success(
                    f"Visitados: {res['visited_count']} | Ciclo: {res['has_cycle']} | Tempo: {t:.4f}s"
                )
                st.write("Classificação de arestas:", res["edge_class_counts"])
    except Exception as exc:
        st.warning(f"Grafo não carregado: {exc}")

with tab3:
    st.header("Dijkstra - Caminho Mínimo entre Artigos")
    report = load_report()

    if report:
        rows = []
        for entry in report.get("dijkstra", []):
            distance = entry["distance"]
            rows.append(
                {
                    "Origem": entry["source"],
                    "Destino": entry["target"],
                    "Distância": round(distance, 6) if distance != float("inf") else "∞",
                    "Saltos no caminho": entry["path_length"],
                    "Tempo (s)": entry["time_s"],
                }
            )
        if rows:
            import pandas as pd

            st.dataframe(pd.DataFrame(rows), use_container_width=True)

        for entry in report.get("dijkstra", []):
            if entry.get("path"):
                with st.expander(f"{entry['source']} -> {entry['target']}"):
                    st.write(" -> ".join(entry["path"]))

    show_image_if_exists("distance_heatmap.png", "Heatmap de distâncias")
    show_image_if_exists("dijkstra_paths.png", "Dijkstra: distância ponderada vs saltos")

    st.subheader("Busca Interativa")
    try:
        graph, _ = get_graph()
        nodes_sorted = sorted(graph.nodes)
        col1, col2 = st.columns(2)
        src_d = col1.selectbox("Origem", nodes_sorted, key="dijk_src")
        tgt_d = col2.selectbox("Destino", nodes_sorted, index=1, key="dijk_tgt")
        if st.button("Calcular caminho mínimo", key="run_dijkstra"):
            from src.dijkstra import dijkstra, reconstruct_path
            from src.metrics import run_timed

            try:
                res, t, _ = run_timed(dijkstra, graph, src_d, tgt_d)
                path = reconstruct_path(res["parent"], src_d, tgt_d)
                dist = res["dist"].get(tgt_d, float("inf"))
                if dist == float("inf"):
                    st.warning("Destino inalcançável a partir desta origem.")
                else:
                    st.success(f"Distância: {dist:.6f} | Tempo: {t:.4f}s")
                    if path:
                        st.write("**Caminho:**", " -> ".join(path))
            except ValueError as exc:
                st.error(str(exc))
    except Exception as exc:
        st.warning(f"Grafo não carregado: {exc}")

with tab4:
    st.header("Bellman-Ford - Pesos Negativos e Ciclos")
    report = load_report()

    if report:
        for entry in report.get("bellman_ford", []):
            scenario = entry.get("scenario", "")
            label = {
                "normal_weights": "Pesos normais",
                "negative_weight_no_cycle": "Peso negativo sem ciclo negativo",
                "negative_cycle_detected": "Ciclo negativo detectado",
            }.get(scenario, scenario)

            with st.expander(label):
                if scenario == "negative_cycle_detected":
                    st.error(f"Ciclo negativo detectado: {entry['has_negative_cycle']}")
                    st.write("Nós do ciclo:", entry.get("nodes_in_cycle"))
                    st.write("Arestas injetadas:", entry.get("injected_edges"))
                    st.metric("Tempo (s)", entry["time_s"])
                else:
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Origem", entry.get("source", ""))
                    col2.metric("Destino", entry.get("target", ""))
                    distance = entry.get("distance", float("inf"))
                    col3.metric(
                        "Distância",
                        f"{distance:.6f}" if distance != float("inf") else "∞",
                    )
                    col4.metric(
                        "Ciclo negativo",
                        "Sim" if entry["has_negative_cycle"] else "Não",
                    )
                    st.metric("Tempo (s)", entry["time_s"])
                    if entry.get("path"):
                        st.write("Caminho:", " -> ".join(entry["path"]))
                    if entry.get("injected_edge"):
                        st.info(f"Aresta injetada com peso negativo: `{entry['injected_edge']}`")

    show_image_if_exists("bellman_ford_scenarios.png", "Bellman-Ford: cenários de teste")

    st.subheader("Busca Interativa")
    try:
        graph, _ = get_graph()
        nodes_sorted = sorted(graph.nodes)
        col1, col2 = st.columns(2)
        src_bf = col1.selectbox("Origem", nodes_sorted, key="bf_src")
        tgt_bf = col2.selectbox("Destino", nodes_sorted, index=1, key="bf_tgt")
        inject_neg = st.checkbox("Injetar aresta negativa entre origem e destino (w=-0.5)")
        if st.button("Executar Bellman-Ford", key="run_bellman_ford"):
            from src.bellman_ford import bellman_ford, reconstruct_path_bf
            from src.loader_parte2 import inject_negative_weights
            from src.metrics import run_timed

            import copy

            g_copy = copy.deepcopy(graph)
            if inject_neg:
                inject_negative_weights(g_copy, [(src_bf, tgt_bf)], bonus=-0.5)
                st.info(f"Aresta `{src_bf} -> {tgt_bf}` com peso -0.5 injetada.")
            res, t, _ = run_timed(bellman_ford, g_copy, src_bf)
            path = reconstruct_path_bf(res["parent"], src_bf, tgt_bf)
            dist = res["dist"].get(tgt_bf, float("inf"))
            if res["has_negative_cycle"]:
                st.error("Ciclo negativo detectado.")
            elif dist == float("inf"):
                st.warning("Destino inalcançável.")
            else:
                st.success(f"Distância: {dist:.6f} | Tempo: {t:.4f}s")
                if path:
                    st.write("Caminho:", " -> ".join(path))
    except Exception as exc:
        st.warning(f"Grafo não carregado: {exc}")

with tab5:
    st.header("Desempenho Comparativo")
    report = load_report()

    show_image_if_exists("performance_bars.png", "Tempo médio por algoritmo")
    show_image_if_exists("comparison_lines.png", "Comparação por tarefa")

    if report and report.get("performance_table"):
        import pandas as pd

        df_perf = pd.DataFrame(report["performance_table"])
        st.subheader("Tabela de Desempenho")
        st.dataframe(df_perf, use_container_width=True)

    st.subheader("Discussão Crítica")
    st.markdown(
        """
        **BFS** encontra o caminho com menor número de saltos entre artigos. É adequado quando
        o objetivo é medir quantos cliques separam dois temas, sem considerar pesos.

        **DFS** explora cadeias profundas de links. Em grafos dirigidos como este, ajuda a
        detectar ciclos de referência e classificar arestas em `tree`, `back`, `forward` e `cross`.

        **Dijkstra** usa pesos não negativos (`1/grau_de_saída`) e calcula caminhos de menor custo
        no modelo escolhido. Ele não deve ser usado quando houver pesos negativos.

        **Bellman-Ford** suporta pesos negativos e detecta ciclos negativos, mas é mais caro
        computacionalmente. Por isso, no projeto ele é executado em cenários controlados.

        **Limites do modelo de pesos:** usar `1/grau_de_saída` favorece artigos especializados
        e pode reduzir a relevância de hubs generalistas, como `United_States`.
        """
    )

with tab6:
    st.header("Dashboard")

    interactive_charts_path = os.path.join(OUT_DIR, "avd_interactive_charts.html")
    if os.path.exists(interactive_charts_path):
        st.subheader("Gráficos Interativos AVD")
        with open(interactive_charts_path, "r", encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=900, scrolling=True)
    else:
        st.info(
            "Execute `python -m src.cli --dataset ./data/dataset_parte2/ --alg ALL --out ./out/` "
            "para gerar o dashboard interativo."
        )

    interactive_graph_path = os.path.join(OUT_DIR, "grafo_interativo.html")
    if os.path.exists(interactive_graph_path):
        st.subheader("Grafo Interativo")
        with open(interactive_graph_path, "r", encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=700, scrolling=True)

    avd_notes_path = os.path.join(OUT_DIR, "parte2_avd_notes.md")
    if os.path.exists(avd_notes_path):
        st.subheader("Notas Analíticas AVD - Parte 2")
        with open(avd_notes_path, "r", encoding="utf-8") as f:
            st.markdown(f.read())
