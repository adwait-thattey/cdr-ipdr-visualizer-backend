import networkx as nx
import pandas as pd
# import os
import networkx.algorithms.community as nxcom
from rest_framework import status
from rest_framework.response import Response

from data.views import get_cdr_filtered_queryset
from data.models import CDR

# import matplotlib.pyplot as plt
from rest_framework.views import APIView


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


def get_community_and_importance(data_array, algo='girvan'):
    # output coming in form [6306002228': (3, 0.00027210884353741496)], modify and send
    df = pd.DataFrame(data_array)
    df = df[['from_number', 'to_number', 'duration']]
    df = df.dropna()
    G = get_graph_from_df(df)
    if algo == 'modularity':
        communities = sorted(nxcom.greedy_modularity_communities(G), key=len, reverse=True)
    else:
        try:
            result = nxcom.girvan_newman(G)
            communities = next(result)
        except:
            print('this is fucked up')
            communities = sorted(nxcom.greedy_modularity_communities(G), key=len, reverse=True)
    total_cm = len(communities)
    persons = {}
    com_count = 1
    for cm in communities:
        G_sub = G.subgraph(nodes=list(cm))
        importance = nx.betweenness_centrality(G_sub)
        for node in cm:
            persons[node] = (com_count, importance[node])
        com_count += 1
    return persons, total_cm


def get_n_similar_numbers(data_array, n, algo='girvan'):
    df = pd.DataFrame(data_array)
    df = df[['from_number', 'to_number', 'duration']]
    df = df.dropna()
    G = get_graph_from_df(df)
    if algo == 'modularity':
        communities = sorted(nxcom.greedy_modularity_communities(G), key=len, reverse=True)
    else:
        try:
            result = nxcom.girvan_newman(G)
            communities = next(result)
        except:
            communities = sorted(nxcom.greedy_modularity_communities(G), key=len, reverse=True)
    possible_same = {}
    for cm in communities:
        G_S = G.subgraph(nodes=list(cm))
        all_sub_nodes = G_S.nodes
        for node in all_sub_nodes:
            possible_same[node] = list(set(all_sub_nodes) - set(G_S[node]))[:n]
    # check location and filter
    return possible_same


def get_possible_spammers(data_array, ratio_thresh=0.7, dur_thresh=2):
    df = pd.DataFrame(data_array)
    df = df[['from_number', 'to_number', 'duration', 'call_type']]
    df = df.dropna()
    spammers = []
    global_avg = sum(df['duration'] / len(df))
    for mn in df['from_number'].unique():
        mndf = df[df['from_number'] == mn]
        total = len(mndf)
        mndf = df[df['call_type'] == 'OUT']
        num_out = len(mndf)
        avg_out_dur = sum(mndf['duration']) / len(mndf['duration'])
        if num_out / total > ratio_thresh and global_avg / avg_out_dur > dur_thresh:
            spammers.append(mn)
    return spammers


class CommunityGraphView(APIView):
    def get(self, request):
        cdr_qset = get_cdr_filtered_queryset(request.query_params)

        arr = list(cdr_qset.values_list('from_number', 'to_number', 'duration'))
        d = [{'from_number': i[0], 'to_number': i[1], 'duration': i[2]} for i in arr]

        comm = get_community_and_importance(d)

        return Response(comm, status=status.HTTP_200_OK)
