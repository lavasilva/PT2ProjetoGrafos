import os
import json
from src.loader_parte2 import build_graph

# Mapa de palavras-chave -> categoria legível
# Ordem importa: primeira correspondência ganha
KEYWORD_CATEGORIES = [
    ("Science",     ["biology","chemistry","physics","mathematics","astronomy",
                     "medicine","computer","technology","engineering","science",
                     "geology","ecology","neuroscience","genetics","evolution"]),
    ("History",     ["history","war","battle","empire","ancient","medieval",
                     "century","civilization","revolution","historical","dynasty",
                     "military","colonial","conquest","archaeological"]),
    ("Geography",   ["country","countries","city","capital","island","ocean",
                     "river","mountain","continent","region","territory",
                     "africa","europe","asia","america","australia","geography",
                     "arctic","atlantic","pacific"]),
    ("Politics",    ["politics","government","democracy","election","president",
                     "parliament","constitution","law","treaty","diplomacy",
                     "republic","nation","state","sovereignty","united_nations"]),
    ("Arts",        ["music","film","art","painting","sculpture","literature",
                     "poetry","theater","cinema","photography","architecture",
                     "novel","writer","artist","composer","musician"]),
    ("Religion",    ["religion","christian","islam","buddhism","hinduism",
                     "jewish","theology","church","temple","mosque","bible",
                     "god","faith","spiritual","mythology"]),
    ("Sports",      ["sport","football","soccer","basketball","olympic",
                     "athletics","tennis","cricket","baseball","chess",
                     "swimming","cycling","racing","championship"]),
    ("Philosophy",  ["philosophy","ethics","logic","epistemology","metaphysics",
                     "consciousness","existentialism","marxism","democracy",
                     "theory","social","cultural","anthropology","sociology"]),
    ("Nature",      ["animal","plant","species","mammal","bird","fish","insect",
                     "tree","forest","ecosystem","climate","environment",
                     "dinosaur","evolution","wildlife","nature"]),
    ("People",      ["person","people","biography","born","died","actor",
                     "politician","scientist","inventor","explorer","king",
                     "queen","emperor","pope","general"]),
]


def classify_node(label, wikispeedia_cats):
    text = label.lower().replace("_", " ").replace("%", " ")

    # Primeiro tenta pelo nome do artigo
    for cat, keywords in KEYWORD_CATEGORIES:
        for kw in keywords:
            if kw in text:
                return cat

    # Depois tenta pelas categorias do Wikispeedia
    for wcat in sorted(wikispeedia_cats):
        wcat_lower = wcat.lower()
        for cat, keywords in KEYWORD_CATEGORIES:
            for kw in keywords:
                if kw in wcat_lower:
                    return cat

    return "Other"


def export_for_react(data_dir, out_dir):
    print("=== Exportando grafo completo para React ===")
    graph, _, _, article_categories = build_graph(data_dir)

    max_deg = max((graph.degree(u) for u in graph.nodes), default=1)
    node_list = sorted(graph.nodes)
    node_index = {n: i for i, n in enumerate(node_list)}

    nodes = []
    for i, n in enumerate(node_list):
        wcats = article_categories.get(n, set())
        cat = classify_node(n, wcats)
        nodes.append({
            "id": i,
            "label": n.replace("_", " "),
            "raw": n,
            "degree": graph.degree(n),
            "cat": cat,
            "size": round(4 + 18 * (graph.degree(n) / max_deg), 2),
        })

    edges = []
    for src, tgt, w in graph.edges():
        edges.append({
            "source": node_index[src],
            "target": node_index[tgt],
            "weight": round(w, 6),
        })

    all_cats = sorted(set(n["cat"] for n in nodes))

    # Rank de visibilidade: nós mais conectados têm rank menor (aparecem antes)
    sorted_by_degree = sorted(nodes, key=lambda n: -n["degree"])
    for rank, n in enumerate(sorted_by_degree):
        n["rank"] = rank

    os.makedirs(out_dir, exist_ok=True)
    graph_data = {
        "meta": {
            "num_nodes": len(nodes),
            "num_edges": len(edges),
            "directed": True,
            "categories": all_cats,
        },
        "nodes": nodes,
        "edges": edges,
    }

    path = os.path.join(out_dir, "graph_data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False, separators=(",", ":"))

    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f"Exportado: {path} ({size_mb:.1f} MB)")
    print(f"  {len(nodes)} nós, {len(edges)} arestas")
    print(f"  Categorias: {', '.join(all_cats)}")
    return path


if __name__ == "__main__":
    import sys
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "./data/dataset_parte2"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "./web/public"
    export_for_react(data_dir, out_dir)
