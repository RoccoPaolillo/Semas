import networkx as nx
import matplotlib.pyplot as plt
import numpy
import random
import os
import csv
import pandas as pd
os.chdir("C:/Users/rocpa/OneDrive/Desktop/ROME_CNR/FOSSRdaysOct24")


# from a csv, build the graph with edges

dflink = pd.read_csv('links.csv', delimiter = ";") # dataframe links
G = nx.Graph() # empty graph
G = nx.from_pandas_edgelist(dflink, create_using=G) # adding info from df to empty graph
G.add_node("Stefano") # here to add manualy isolated nodes
G.add_node("Mandy")

# from csv, attributes of nodes

df = pd.read_csv('nodes.csv', delimiter = ";")  # dataframe nodes

for node in G.nodes():  # to add attribute color to nodes extracting from the dataframe
    G.nodes[node]["color"] = df[(df.node == node)]["color"].item()

# features for the layout of the graph

colors = [node[1]['color'] for node in G.nodes(data=True)] # color of nodes
pos = nx.spring_layout(G, seed=numpy.random.seed(1229)) # seed for having stable configuration

# to plot the graph
plt.clf() 
nx.draw(G, node_color=colors, with_labels=True, node_shape="o", font_color='black', node_size = 1000,
        edge_color = "black",
        pos=pos)
plt.show()

# Here some adding and deleting links, run and then re-run nx.draw()
# These would be the DUTY() to run together with changes in triplets when executing the desire in semas_mas

G.add_edges_from([("Stefano","UNITO")])
G.remove_edges_from([("Stefano","UNITO")])
G.add_edges_from([("Stefano","UNIBO")])
G.remove_edges_from([("Stefano","UNIBO")])

