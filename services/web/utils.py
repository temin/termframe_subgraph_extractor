import subprocess
import networkx as nx
import itertools

from fuzzywuzzy import fuzz, process


def best_matching_nodes(g, node, k=5):
    return [n for n, s in process.extract(node, list(g.nodes), limit=k, scorer=fuzz.QRatio)]


def extract_subgraph(g, nodes, k=2, ignoreDirection=False, fuzzySearch=True):
    if fuzzySearch:
        matched_nodes = [node for node in nodes if node in g.nodes]
        unmatched_nodes = [node for node in nodes if node not in g.nodes]
        all_nodes = list(g.nodes)
        for node in unmatched_nodes:
            best_match, score = process.extract(node, all_nodes, limit=1, scorer=fuzz.QRatio)[0]
            matched_nodes.append(best_match)
        nodes = matched_nodes
    else:
        nodes = [node for node in nodes if node in g.nodes]

    if ignoreDirection:
        ug = nx.Graph(g.copy())
    all_neighbours = set(nodes)
    fromnodes = nodes
    for i in range(k):
        neighbours = set(itertools.chain.from_iterable([ug.neighbors(node) for node in fromnodes]))  # - set(fromnodes)
        if not neighbours:
            break
        all_neighbours.update(neighbours)
        fromnodes = neighbours

    result = g.subgraph(all_neighbours).copy()
    for i, node in enumerate(result.nodes):
        result.nodes[node]['id'] = i+1
    return result


def graph2json(g):
    nlist = []
    for node in g.nodes:
        nlist.append({'id': g.nodes[node]['id'],
                      'label': node,
                      'group': g.nodes[node]['group']})
    elist = []
    for edge in g.edges:
        fr = edge[0]
        to = edge[1]
        elist.append({'from': g.nodes[fr]['id'],
                      'to': g.nodes[to]['id'],
                      'label': g.edges[edge]['label']})
    return {'nodes': nlist, 'edges': elist}


def visualize_graphviz(g, path, output='pdf'):
    dotfile = path + '.dot'
    nx.drawing.nx_pydot.write_dot(g, dotfile)
    subprocess.call(['dot', '-T{}'.format(output), dotfile, '-o', '{}.{}'.format(path, output)])  # , cwd=outdir)


def export_dot(g, path):
    dotfile = path + '.dot'
    nx.drawing.nx_pydot.write_dot(g, dotfile)
