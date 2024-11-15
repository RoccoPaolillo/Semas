import sys
import random
import turtle
import threading
import queue
import networkx as nx
#import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy
import random
import os
import csv
import pandas as pd
import re

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
from front_end_mas import *

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
# Non-ontological rendering variables
# ---------------------------------------------------------------------

# Coordinates spamming range
N = 500

# time-range to get the job done
LOWER_BOUND = 0
UPPER_BOUND = 3

# Breakdown of steps
STEP_BREAKDOWN = 50

# Pause between steps
STEP_DURATIN = 0.005

# Worker-Turtle dictionary
# dict_turtle = {}
# G = nx.Graph()
# agents = get_agents_names()[1:]
# G.add_nodes_from(agents)
# pos = nx.spring_layout(G, seed=numpy.random.seed(1229))
# agents = get_agents_names()[1:]
# G.add_nodes_from(agents)
# pos = nx.spring_layout(G, seed=231)

# ---------------------------------------------------------------------
# Ontology section
# ---------------------------------------------------------------------

# Max work time for a worker (seconds)
Max_WorkDay_Time = 27
# Max work time for a worker (seconds) - MAX_WORKDAY_TIME must be multiple of MAX_WORK_TIME
Max_Work_Time = 9
# Rest time for a worker (seconds)
Rest_Time = 3
# Timer tick
TICK = 0.1

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


# Funzione per ottenere i nomi degli agenti (inviando la query al thread dedicato)
def get_agents_names():
    agents = []
    q = PREFIX + f" SELECT ?subj" + " WHERE { "
    q = q + f"?subj rdf:type {ONTO_NAME}:Agent." + "}"
    
    result_event = threading.Event()  # Evento per sincronizzare il risultato
    query_queue.put((q, result_event))  # Invia la query al thread dedicato

    result_event.wait()  # Aspetta che il risultato sia pronto

    result = result_queue.get()  # Ottieni il risultato dalla coda

    for res in result:
        subj = str(res).split(",")[0]
        subj = subj.split("#")[1][:-2]
        agents.append(subj)
    
#    agents = list(map(lambda x: re.sub(r'[0-9]', '',x), agents))

    return agents

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
    
#    scholars = list(map(lambda x: re.sub(r'[0-9]', '',x), scholars))

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
    
#    universities = list(map(lambda x: re.sub(r'[0-9]', '',x), universities))

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
    
#    fields = list(map(lambda x: re.sub(r'[0-9]', '',x), fields))

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
    
#    newcomers = list(map(lambda x: re.sub(r'[0-9]', '',x), newcomers))

    return newcomers

agents = get_agents_names()[1:]
scholars = get_scholars_names()[1:]
universities = get_universities_names()[1:]
newcomers = get_newcomers_names()[1:]
fields = get_fields_names()[1:]
newcomers = get_newcomers_names()[1:]

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
class turn(Procedure): pass



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
# Sensors section
# ---------------------------------------------------------------------

class TaskDetect(Sensor):

    def on_start(self):
        # Starting task detection
       self.running = True

    def on_restart(self):
        # Re-Starting task detection
        self.do_restart = True

    def on_stop(self):
        #Stopping task detection
        self.running = False

    def sense(self):
        while self.running:
           time.sleep(TICK)

           pos_x = random.randint(-N // 2, N // 2)
           pos_y = random.randint(-N // 2, N // 2)
           print(f"Generating task on position ({pos_x}, {pos_y})...")
           self.assert_belief(TASK())



class Timer(Sensor):

    def on_start(self, uTimeout):
        evt = threading.Event()
        self.event = evt
        self.timeout = uTimeout()
        self.do_restart = False


    def on_restart(self, uTimeout):
        self.do_restart = True
        self.event.set()

    def on_stop(self):
        self.do_restart = False
        self.event.set()

    def sense(self):
        while True:
            time.sleep(self.timeout)
            self.event.clear()
            if self.do_restart:
                self.do_restart = False
                continue
            elif self.stopped:
                self.assert_belief(TIMEOUT("ON"))
                return
            else:
                return




# Funzione per terminare il thread in sicurezza
def stop_query_thread():
    query_queue.put((None, None))  # Invia un segnale di terminazione
    query_thread_instance.join()  # Aspetta che il thread termini



class rest(Action):
    """resting for few seconds"""
    def execute(self, arg):
      rest_time = int(str(arg).split("'")[2][1:-1])
      print(f"\nresting for {rest_time} seconds...")

      for t in dict_turtle:
          dict_turtle[t].color("red")

      time.sleep(rest_time)

      for t in dict_turtle:
          dict_turtle[t].color("black")



class UpdateLedger(Action):
    """Update completed jobs"""
    def execute(self, arg1, arg2):

      agent = str(arg1).split("'")[3]
      jobs = int(str(arg2).split("'")[3])
      jobs = jobs + 1
      print(f"Updating {agent} ledger: {jobs}")
      self.assert_belief(LEDGER(agent, str(jobs)))
      self.assert_belief(DUTY(int(agent[-1:])))


class UpdateWorkTime(Action):
    """Update completed jobs"""
    def execute(self, arg1, arg2):

        arg1_num = str(arg1).split("'")[2][1:-1]
        arg2_num = str(arg2).split("'")[2][1:-1]
        arg_num_tot = int(arg1_num)+int(arg2_num)
        print("WORKTIME: ",arg_num_tot)
        self.assert_belief(WORKTIME(arg_num_tot))


class AssignId(Action):
    """Intialize duty flag with ID"""
    def execute(self, arg):
        entity = str(arg).split("'")[3]

        self.assert_belief(DUTY(int(entity[-1:])))
        self.assert_belief(AGT(entity, int(entity[-1:])))



# ---------------------------------------------------------------------
# Turtle section
# ---------------------------------------------------------------------


class move_turtle(Action):
    """moving turtle to coordinates (x,y)"""
    def execute(self, arg0, arg1, arg2):
        id_turtle = str(arg0).split("'")[3]

        pos_x = str(arg1).split("'")[2]
        pos_y = str(arg2).split("'")[2]

        pos_x = int(pos_x[1:-1])
        pos_y = int(pos_y[1:-1])

        # Recupera la posizione attuale
        current_x, current_y = dict_turtle[id_turtle].position()

        # Calcola la distanza da percorrere su ciascun asse
        delta_x = (pos_x - current_x) / STEP_BREAKDOWN
        delta_y = (pos_y - current_y) / STEP_BREAKDOWN

        for step in range(STEP_BREAKDOWN):
            # Sposta la tartaruga di una piccola quantità
            current_x += delta_x
            current_y += delta_y
            dict_turtle[id_turtle].goto(current_x, current_y)

            # Rallenta il movimento
            time.sleep(STEP_DURATIN)  # Regola il tempo di pausa per modificare la velocità

        # Pausa finale casuale (se necessaria)
        rnd = random.uniform(LOWER_BOUND, UPPER_BOUND)
        time.sleep(rnd)



# def turtle_thread_func():
#    wn = turtle.Screen()
#    wn.title("Workers jobs assignment")

#    agents = get_agents_names()[1:]

#    for i in range(len(agents)):
#       dict_turtle[agents[i]] = turtle.Turtle()

#    wn.mainloop()
   
# class network_init(Action):
#     def execute(self):
#        dflink = pd.read_csv('links.csv', delimiter = ";") # dataframe links
         # empty graph
#         G.remove_edges_from(list(G.edges()))
#         agents = get_agents_names()[1:]
#         G.add_nodes_from(agents)
#         pos = nx.spring_layout(G, seed=231)
#        pos = nx.spring_layout(G, seed=numpy.random.seed(1229))
#         vis_network()
#        plt.clf() 
#        nx.draw(G,with_labels=True)
#        plt.show()
        
class new_affiliation(Action):
    def execute(self,arg0,arg1):
        node_1 = str(arg0).split("'")[3]
        node_2 = str(arg1).split("'")[3]
        G.add_edge(node_1, node_2, color = "orange", weight = 4, label = "affil") # str(arg3).split()[0])
        vis_network()
        
class co_authorshiplink(Action):
    def execute(self,arg0,arg1):
        node_1 = str(arg0).split("'")[3]
        node_2 = str(arg1).split("'")[3]
        G.add_edge(node_1, node_2, color = "lightgrey", weight = 2, label = "coauthor") # str(arg3).split()[0])
        vis_network()
        
class affiliationlink(Action):
    def execute(self,arg0,arg1):
        node_1 = str(arg0).split("'")[3]
        node_2 = str(arg1).split("'")[3]
        G.add_edge(node_1, node_2, color = "lightgrey", weight = 2, label = "affil") # str(arg3).split()[0])
        vis_network()
        
class topauthorlink(Action):
    def execute(self,arg0,arg1):
        node_1 = str(arg0).split("'")[3]
        node_2 = str(arg1).split("'")[3]
        G.add_edge(node_1, node_2, color = "lightgrey", weight = 2, label = "topauthor") # str(arg3).split()[0])
        vis_network()
        
class selectforlink(Action):
    def execute(self,arg0,arg1):
        node_1 = str(arg0).split("'")[3]
        node_2 = str(arg1).split("'")[3]
        G.add_edge(node_1, node_2, color = "darkgrey", weight = 4, label  = "selected") # str(arg3).split()[0])
        vis_network()
        
G = nx.Graph()

# G.add_nodes_from(agents)
G.add_nodes_from(universities)
G.add_nodes_from(fields)
G.add_nodes_from(agents)
G.add_nodes_from(newcomers)

# color_map = ['red' if node in universities else 'green' if node in fields else 'orange' if node in newcomers else "cyan" for node in G] 
color_map = ['orange' if node in newcomers else 'white' for node in G] 


#colors_edges = nx.get_edge_attributes(G,"color").values()
# color_map = ['red' if node in universities elif 'green' if node in fields else "blue" for node in G] 

# color_map = []

# for node in G:
#     if node in universities:
#         node.color_map = "red"
#     elif node in fields:
#         node.color_map = "green"
#     else:
#         node.color_map = "blue"
        
        
        
        
#             else 'violet' for node in G]  G.nodes[node]["color"]

#df = pd.read_csv('nodes.csv', delimiter = ";")  # dataframe nodes
#G.from_pandas_dataframe(df)
# for node in G.nodes():  # to add attribute color to nodes extracting from the dataframe
#    G.nodes[node]["color"] = df[(df.node == node)]["color"].item()

# features for the layout of the graph

# colors = [node[1]['color'] for node in G.nodes(data=True)] # color of nodes

pos = nx.spring_layout(G, seed=numpy.random.seed(15495)) # 12495
# G = nx.relabel_nodes(G, lambda x: ''.join([i for i in x if not i.isdigit()]))

def vis_network():
#        wm = plt.get_current_fig_manager() 
#        wm.window.attributes('-topmost', 1)
#        wm.window.attributes('-topmost', 0)
#        plt.gcf().canvas.get_tk_widget().focus_force() 
        colors_edges = nx.get_edge_attributes(G,"color").values()
        edges = G.edges()
        weights_edges = [G[u][v]['weight'] for u,v in edges]# nx.get_edge_attributes(G,'weight').values()        
        plt.clf()
#        fig = plt.figure()
        nx.draw(G,with_labels=True, node_color=color_map , edge_color = colors_edges, width = weights_edges , pos = pos,
                font_size = 20)
        nx.draw_networkx_edge_labels(G, edge_labels=nx.get_edge_attributes(G,'label'), label_pos=0.7, pos = pos,
                                     font_size = 17) # edge_color = colors_edges,  pos = pos)
#        fig.canvas.manager.window.attributes('-topmost', 1)
        plt.show()


# Avviare il thread del network
ntw_thread = threading.Thread(target=vis_network)
ntw_thread.daemon = True
ntw_thread.start()