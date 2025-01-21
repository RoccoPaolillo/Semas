import sys
import random
import turtle
import threading
import queue
import networkx as nx
import matplotlib.pyplot as plt
import numpy
import random
import os
import csv
import pandas as pd
import re
import math
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# Coda per inviare richieste di query
query_queue = queue.Queue()

# Coda per restituire i risultati delle query
result_queue = queue.Queue()

sys.path.insert(0, "../lib")

from phidias.Lib import *
from phidias.Agent import *
from phidias.Types import *

import configparser
from owlready2 import *
from front_end_mas import *  # SHIFT


config = configparser.ConfigParser()
config.read('config_mas.ini')

# ONTOLOGY section
FILE_NAME = config.get('ONTOLOGY', 'FILE_NAME')
ONTO_NAME = config.get('ONTOLOGY', 'ONTO_NAME')

# REASONING Section
REASONING_ACTIVE = config.getboolean('REASONING', 'ACTIVE')
REASONER = config.get('REASONING', 'REASONER').split(",")
PREFIXES = config.get('REASONING', 'PREFIXES').split(",")
PREFIX = " ".join(PREFIXES)
PREFIX = PREFIX + f"PREFIX {ONTO_NAME}: <http://test.org/{FILE_NAME}#> "

# BDI-CLASSES Section
ENTITIES = config.get('CLASSES', 'Entities').split(",")

# Properties
BELIEFS = config.get('CLASSES', 'PHI-Beliefs').split(",")
REACTORS = config.get('CLASSES', 'PHI-Reactors').split(",")
DESIRES = config.get('CLASSES', 'PHI-Desires').split(",")
INTENTIONS = config.get('CLASSES', 'PHI-Intentions').split(",")

PROPERTIES = config.get('CLASSES', 'Properties').split(",")
DATAS = config.get('CLASSES', 'Data').split(",")

# ---------------------------------------------------------------------
# Ontology section
# ---------------------------------------------------------------------

try:
    my_onto = get_ontology(FILE_NAME).load()
    print("\nLoading worlds "+FILE_NAME+"...")
except IOError:
    my_onto = get_ontology("http://test.org/"+FILE_NAME)
    print("\nCreating new "+FILE_NAME+" file...")

    print("\nPlease Re-Run Semas.")
    my_onto.save(file=FILE_NAME, format="rdfxml")
    exit()


# instances name/instances dictionary
dict_ent = {}
# properties name/properites dictionary
dict_prop = {}


# Phidias belief containing OWL triples
class TRIPLE(Belief):
    pass


with my_onto:

    class ENTITY(Thing):
        pass

    class BELIEF(Thing):
        pass

    class REACTOR(Thing):
        pass

    class DESIRE(Thing):
        pass

    class INTENTION(Thing):
        pass

    # Declaring Owlready DataProperties
    for i in range(len(DATAS)):
        globals()[DATAS[i].strip()] = type(DataProperty)
        dict_prop[DATAS[i].strip()] = DATAS[i].strip()

    # Declaring Owlready ObjectProperties
    for i in range(len(PROPERTIES)):
        globals()[PROPERTIES[i].strip()] = type(PROPERTIES[i].strip(), (ObjectProperty,), {})
        istanza = globals()[PROPERTIES[i].strip()]()
        dict_prop[PROPERTIES[i].strip()] = istanza


# Declaring Phidias belief from OWL
for i in range(len(BELIEFS)):
    # creating subclasses BELIEFS
    new_belief = types.new_class(BELIEFS[i].strip(), (BELIEF,))

    globals()[BELIEFS[i].strip()] = type(BELIEFS[i].strip(), (Belief,), {})
    istanza = globals()[BELIEFS[i].strip()]()

for i in range(len(REACTORS)):
    # creating subclasses BELIEFS
    new_belief = types.new_class(REACTORS[i].strip(), (REACTOR,))

    globals()[REACTORS[i].strip()] = type(REACTORS[i].strip(), (Reactor,), {})
    istanza = globals()[REACTORS[i].strip()]()

for i in range(len(DESIRES)):
    # creating subclasses DESIRES
    new_belief = types.new_class(DESIRES[i].strip(), (DESIRE,))

    globals()[DESIRES[i].strip()] = type(DESIRES[i].strip(), (Procedure,), {})
    istanza = globals()[DESIRES[i].strip()]()

for i in range(len(INTENTIONS)):
    # creating subclasses INTENTIONS
    new_belief = types.new_class(INTENTIONS[i].strip(), (INTENTION,))

    globals()[INTENTIONS[i].strip()] = type(INTENTIONS[i].strip(), (Reactor,), {})
    istanza = globals()[INTENTIONS[i].strip()]()



# ---------------------------------------------------------------------
# System procedures section
# ---------------------------------------------------------------------


# Ontology intialization
class init(Procedure): pass
# Import OWL triples
class load(Procedure): pass
# Turning triples to beliefs
class pre_process(Procedure): pass
# report measures
class report(Procedure): pass
# report only for universities
class reportuniv(Procedure): pass
# report affil
class reportaffil(Procedure): pass
# plot centrality
class plotmeasurecn(Procedure): pass
# plot clustering
class plotmeasurecl(Procedure): pass
# plot betweeness
class plotmeasurebt(Procedure): pass

class initWorld(Action):
    """World entities initialization"""
    def execute(self):

        # Entities
        for i in range(len(ENTITIES)):
            # creating subclasses ENTITY
            entity = types.new_class(ENTITIES[i].strip(), (ENTITY,))

            ENT_INDS = config.get('INDIVIDUALS', ENTITIES[i].strip()).split(",")

            # creating ENTITY individuals
            for j in range(len(ENT_INDS)):
                new_entity = entity(ENT_INDS[j].strip())
                dict_ent[ENT_INDS[j].strip()] = new_entity

        print("BELIEFS: ", BELIEFS)

        for i in range(len(BELIEFS)):
            BDI_INDS = config.get('INDIVIDUALS', BELIEFS[i].strip()).split(" & ")

            for j in range(len(BDI_INDS)):
                triple = BDI_INDS[j].strip()

                print("BELIEFS: ", BELIEFS)
                print("BDI_INDS: ", BDI_INDS)
                print("triple: ", triple)

                subject = triple.split(",")[0][1:].strip()
                prop = triple.split(",")[1].strip()
                object = triple.split(",")[2][:-1].strip()

                getattr(dict_ent[subject], prop).append(dict_ent[object])



class declareRules(Action):
    """assert an SWRL rule"""
    def execute(self):
        number_of_rules = int(config.get('SWRL', 'NUMBER_OF_RULES'))
        with my_onto:
           rule = Imp()

           print(f"\nAdding the following {number_of_rules} rules to ontology: ")
           for i in range(number_of_rules):
               rule_str = config.get('SWRL', 'RULE'+str(i+1))
               print(f"Rule {str(i+1)}: {rule_str}")
               rule.set_as_rule(rule_str)



class saveOnto(Action):
    """Creating a subclass of the class Verb"""
    def execute(self):
        with my_onto:
            #sync_reasoner_pellet()
            my_onto.save(file=FILE_NAME, format="rdfxml")
            print("Ontology saved.")



class assert_beliefs_triples(Action):
    """create sparql query from MST"""
    def execute(self):

        q = PREFIX + f" SELECT ?subj ?prop ?obj" + " WHERE { "
        q = q + f"?subj ?prop ?obj. ?subj rdf:type/rdfs:subClassOf* {ONTO_NAME}:ENTITY. ?obj rdf:type/rdfs:subClassOf* {ONTO_NAME}:ENTITY." + "}"

        my_world = owlready2.World()
        my_world.get_ontology(FILE_NAME).load()  # path to the owl file is given here

        if REASONING_ACTIVE:
            # sync_reasoner_pellet(my_world, infer_property_values = True, infer_data_property_values = True)
            sync_reasoner_hermit(my_world, infer_property_values=True)
            # sync_reasoner_hermit(my_world)

        graph = my_world.as_rdflib_graph()
        result = list(graph.query(q))

        for res in result:

            subj = str(res).split(",")[0]
            subj = subj.split("#")[1][:-2]

            prop = str(res).split(",")[1]
            prop = prop.split("#")[1][:-2]

            obj = str(res).split(",")[2]
            obj = obj.split("#")[1][:-3]

            self.assert_belief(TRIPLE(subj, prop, obj))


# ---------------------------------------------------------------------
# Agent section
# ---------------------------------------------------------------------

# Thread che esegue le query SPARQL
def query_thread():
    my_world = owlready2.World()
    my_world.get_ontology(FILE_NAME).load()  # path to the owl file

    while True:
        q, result_event = query_queue.get()  # Ottieni la query e l'evento di sincronizzazione

        if q is None:  # Esci dal ciclo quando ricevi None
            break

        graph = my_world.as_rdflib_graph()
        result = list(graph.query(q))  # Esegui la query
        result_queue.put(result)  # Inserisci il risultato nella coda dei risultati
        result_event.set()  # Notifica che il risultato è pronto


# Avvia il thread delle query
query_thread_instance = threading.Thread(target=query_thread)
query_thread_instance.start()

# agents entities are in the config_mas.ini, but we don't actually use here, the function is to add as the following if needed

def get_scholars_names():
    scholars = []
    q = PREFIX + f" SELECT ?subj" + " WHERE { "
    q = q + f"?subj rdf:type {ONTO_NAME}:Scholar." + "}"

    result_event = threading.Event()  # Evento per sincronizzare il risultato
    query_queue.put((q, result_event))  # Invia la query al thread dedicato

    result_event.wait()  # Aspetta che il risultato sia pronto

    result = result_queue.get()  # Ottieni il risultato dalla coda

    for res in result:
        subj = str(res).split(",")[0]
        subj = subj.split("#")[1][:-2]
        scholars.append(subj)
    
    return scholars

def get_universities_names():
    universities = []
    q = PREFIX + f" SELECT ?subj" + " WHERE { "
    q = q + f"?subj rdf:type {ONTO_NAME}:University." + "}"

    result_event = threading.Event()  # Evento per sincronizzare il risultato
    query_queue.put((q, result_event))  # Invia la query al thread dedicato

    result_event.wait()  # Aspetta che il risultato sia pronto

    result = result_queue.get()  # Ottieni il risultato dalla coda

    for res in result:
        subj = str(res).split(",")[0]
        subj = subj.split("#")[1][:-2]
        universities.append(subj)
    
    return universities

def get_fields_names():
    fields = []
    q = PREFIX + f" SELECT ?subj" + " WHERE { "
    q = q + f"?subj rdf:type {ONTO_NAME}:Field." + "}"

    result_event = threading.Event()  # Evento per sincronizzare il risultato
    query_queue.put((q, result_event))  # Invia la query al thread dedicato

    result_event.wait()  # Aspetta che il risultato sia pronto

    result = result_queue.get()  # Ottieni il risultato dalla coda

    for res in result:
        subj = str(res).split(",")[0]
        subj = subj.split("#")[1][:-2]
        fields.append(subj)
    
    return fields

def get_newcomers_names():
    newcomers = []
    q = PREFIX + f" SELECT ?subj" + " WHERE { "
    q = q + f"?subj rdf:type {ONTO_NAME}:Newcomers." + "}"

    result_event = threading.Event()  # Evento per sincronizzare il risultato
    query_queue.put((q, result_event))  # Invia la query al thread dedicato

    result_event.wait()  # Aspetta che il risultato sia pronto

    result = result_queue.get()  # Ottieni il risultato dalla coda

    for res in result:
        subj = str(res).split(",")[0]
        subj = subj.split("#")[1][:-2]
        newcomers.append(subj)
    
    return newcomers

def get_categories_names():
    categories = []
    q = PREFIX + f" SELECT ?subj" + " WHERE { "
    q = q + f"?subj rdf:type {ONTO_NAME}:Cattegories." + "}"

    result_event = threading.Event()  # Evento per sincronizzare il risultato
    query_queue.put((q, result_event))  # Invia la query al thread dedicato

    result_event.wait()  # Aspetta che il risultato sia pronto

    result = result_queue.get()  # Ottieni il risultato dalla coda

    for res in result:
        subj = str(res).split(",")[0]
        subj = subj.split("#")[1][:-2]
        categories.append(subj)
    
    return categories

scholars = get_scholars_names()[1:]
universities = get_universities_names()[1:]
newcomers = get_newcomers_names()[1:]
fields = get_fields_names()[1:]
categories = get_categories_names()[1:]

# Funzione per terminare il thread in sicurezza
def stop_query_thread():
    query_queue.put((None, None))  # Invia un segnale di terminazione
    query_thread_instance.join()  # Aspetta che il thread termini



# ---------------------------------------------------------------------
# Network section
# ---------------------------------------------------------------------


class new_affiliation(Action):
    def execute(self,arg0,arg1):
        node_1 = str(arg0).split("'")[3]
        node_2 = str(arg1).split("'")[3]
        G.add_edge(node_1, node_2, color = "orange", weight = 4, label = "affil", edgestyle = "solid") # str(arg3).split()[0])
        NG.add_edge(node_1, node_2, color = "orange", weight = 4, label = "affil", edgestyle = "solid") # str(arg3).split()[0])
        vis_network()
        
class co_authorshiplink(Action):
    def execute(self,arg0,arg1):
        node_1 = str(arg0).split("'")[3]
        node_2 = str(arg1).split("'")[3]
        G.add_edge(node_1, node_2, color = "blue", weight = 2, label = "coauthor", edgestyle = "dashed") # str(arg3).split()[0])
        vis_network()
        
class affiliationlink(Action):
    def execute(self,arg0,arg1):
        node_1 = str(arg0).split("'")[3]
        node_2 = str(arg1).split("'")[3]
        G.add_edge(node_1, node_2, color = "red", weight = 2, label = "affil", edgestyle = "dotted") # str(arg3).split()[0])
        NG.add_edge(node_1, node_2, color = "red", weight = 2, label = "affil", edgestyle = "dotted") # str(arg3).split()[0])
        vis_network()
        
class topauthorlink(Action):
    def execute(self,arg0,arg1):
        node_1 = str(arg0).split("'")[3]
        node_2 = str(arg1).split("'")[3]
        G.add_edge(node_1, node_2, color = "purple", weight = 2, label = "topauthor", edgestyle = "dashdot") # str(arg3).split()[0])
        vis_network()
        
class selectforlink(Action):
    def execute(self,arg0,arg1):
        node_1 = str(arg0).split("'")[3]
        node_2 = str(arg1).split("'")[3]
        G.add_edge(node_1, node_2, color = "lightgrey", weight = 4,  edgestyle = "dashed" ) #, label  = "selected") # str(arg3).split()[0])
        vis_network()
        
G = nx.Graph()

G.add_nodes_from(universities)
G.add_nodes_from(fields)
G.add_nodes_from(scholars)
G.add_nodes_from(newcomers)

NG = nx.Graph()
NG.add_nodes_from(universities)

# color nodes
color_map = ['orange' if node in newcomers else 'white' for node in G] 
# position nodes
# pos = nx.spring_layout(G , seed=numpy.random.seed(5581), scale = 8) # k = 300, iterations = 70)  # 15495 #5581 # 1933
pos = nx.spring_layout(G , seed=numpy.random.seed(15489), scale = 8) # k = 300, iterations = 70)  # 5578 15490

class measures(Action):
    def execute(self):
        print(nx.degree_centrality(NG))
        df = pd.DataFrame.from_dict(data=nx.degree_centrality(NG), orient='index')
        print(NG)
#        print(df.head())
        df.to_csv('dict_file.csv', header=False)
        
class measuresuniv(Action):
    def execute(self):
        all_edges = []
#        centrality_index = ()
        print("Univ-Catania,", len( NG.edges("Univ-Catania")))
        print("Univ-Bologna, ",len( NG.edges("Univ-Bologna")))
        print("Univ-Turin, ",len( NG.edges("Univ-Turin")))
        print("Univ-Messina, ",len( NG.edges("Univ-Messina")))
        
        for edgeuniv in universities:
            all_edges.append(len( NG.edges(edgeuniv)))
        print(all_edges)
        print(sum(all_edges))
        
        def centralityindex(x):
            return len(NG.edges(str(x)))/sum(all_edges)
       
        centrality_index = dict(zip(universities,list(map(centralityindex, universities))))
        names = list(centrality_index.keys())
        values = list(centrality_index.values())
        plt.rcParams["figure.figsize"] = (6, 3)
        plt.bar(range(len(centrality_index)), values, tick_label=names)
#        plt.xticks(rotation=30)
        plt.title("Centrality Universities")
        plt.show()
#v        plt.savefig('centralityuniv.png')
        
        print(centrality_index)
        print("Univ-Catania_centrality,", len( NG.edges("Univ-Catania"))/sum(all_edges))
        print("Univ-Bologna_centrality, ",len( NG.edges("Univ-Bologna"))/sum(all_edges))
        print("Univ-Turin_centrality, ",len( NG.edges("Univ-Turin"))/sum(all_edges))
        print("Univ-Messina_centrality, ",len( NG.edges("Univ-Messina"))/sum(all_edges))
        
class plot_centrality(Action):
    def execute(self,arg0):
        dct = nx.degree_centrality(G)
        dctsub = {k: v for k, v in dct.items() if k in str(arg0)}
        names = list(dctsub.keys())
        values = list(dctsub.values())
        plt.bar(range(len(dctsub)), values, tick_label=names)
        plt.xticks(rotation=30)
        plt.title("Centrality")
        plt.show()

class plot_clustering(Action):
    def execute(self,arg0):
        dct = nx.clustering(G)
        dctsub = {k: v for k, v in dct.items() if k in str(arg0)}
        names = list(dctsub.keys())
        values = list(dctsub.values())
        plt.bar(range(len(dctsub)), values, tick_label=names)
        plt.xticks(rotation=30)
        plt.title("Clustering")
        plt.show()
        
class plot_betweeness(Action):
    def execute(self,arg0):
        dct = nx.betweenness_centrality(G)
        dctsub = {k: v for k, v in dct.items() if k in str(arg0)}
        names = list(dctsub.keys())
        values = list(dctsub.values())
        plt.bar(range(len(dctsub)), values, tick_label=names)
        plt.xticks(rotation=30)
        plt.title("Betweeness")
        plt.show()

def vis_network():
    
        colors_edges = nx.get_edge_attributes(G,"color").values()
        edges = G.edges()
        weights_edges = [G[u][v]['weight'] for u,v in edges]   
        plt.clf()
        warnings.filterwarnings("ignore")
        nx.draw(G,with_labels=True, node_color=color_map , edge_color = colors_edges, width = weights_edges ,  pos = pos,
                font_size = 18)
        nx.draw_networkx_edge_labels(G, edge_labels=nx.get_edge_attributes(G,'label'), 
                                     label_pos= 0.7,  pos = pos,
                                     font_size = 14) 
        plt.show()
        

# Avviare il thread del network
ntw_thread = threading.Thread(target=vis_network)
ntw_thread.daemon = True
ntw_thread.start()