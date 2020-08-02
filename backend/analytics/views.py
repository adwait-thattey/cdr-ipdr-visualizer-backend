from django.shortcuts import render
import networkx as nx
import pandas as pd
# import os
import networkx.algorithms.community as nxcom


# Create your views here.
def get_graph_from_df(df):
    G = nx.Graph()
    G.add_nodes_from(list(df['from_number']))
    G.add_nodes_from(list(df['to_number']))
    weights = {}
    mn = list(df['from_number'])
    on = list(df['to_number'])
    dur = list(df['duration'])
    for i in range(len(mn)):
        if (mn[i], on[i]) in weights:
            weights[(mn[i], on[i])] += dur[i]
        else:
            weights[(mn[i], on[i])] = dur[i]
    weight_list = []
    for k, v in weights.items():
        weight_list.append((k[0], k[1], v))
    for i in weight_list:
        G.add_edge(i[0], i[1], weight=i[2])
    return G


def get_community_and_importance(data_array, algo='modularity'):
    df = pd.DataFrame(data_array)
    df = df[['from_number', 'to_number', 'duration']]
    df = df.dropna()

    G = get_graph_from_df(df)
    print(G.edges)
    if algo == 'modularity':
        communities = sorted(nxcom.greedy_modularity_communities(G), key=len, reverse=True)
    else:
        result = nxcom.girvan_newman(G)
        print(list(result))
        communities = next(result)
    total_cm = len(communities)
    persons = {}
    com_count = 1
    for cm in communities:
        G_sub = G.subgraph(nodes=list(cm))
        importance = nx.betweenness_centrality(G_sub)
        for node in cm:
            persons[node] = (com_count, importance[node])
    return persons, total_cm

