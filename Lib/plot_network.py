from pyvis.network import Network
import networkx as nx
import pandas as pd

# create edgelist to plot network graph
def plot_network(filename, edges):
    # convert edges (dict) to pandas dataframe
    df_network = {'Source':[],
                  'Target':[]}

    for tgt in list(edges.keys()):
        df_network['Source'].append(edges[tgt])
        df_network['Target'].append(tgt)

    df_network = pd.DataFrame(df_network)
    # save edges as csv
    df_network.to_csv(filename + '.csv', index=False)

    # plot & save network graph as html
    G = nx.from_pandas_edgelist(df_network, source='Source', target='Target')
    net = Network('100vh', '100vw')
    net.from_nx(G)
    net.show(filename + '.html')