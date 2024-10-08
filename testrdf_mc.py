# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 15:01:44 2024

@author: rocpa
"""

import rdflib
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt
import os

os.chdir("C:/Users/rocpa/OneDrive/Desktop/ROME_CNR/FOSSRdaysOct24")

g = rdflib.Graph()
result = g.parse("6701393010.nt")


G = rdflib_to_networkx_multidigraph(result)

pos = nx.spring_layout(G, scale=2)
edge_labels = nx.get_edge_attributes(G, 'r')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
nx.draw(G, with_labels=True)

#if not in interactive mode for 
plt.show()

# Per identificare una persona specific (provato)
agostinelli = rdflib.URIRef("http://fossr.eu/kg/data/authors/6701393010")

if (agostinelli, rdflib.namespace.RDF.type, g.FOAF.Person) in g:
    print("This graph knows that Agostinelli is a person!")






