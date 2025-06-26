import time
from actions_mas import *
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------
# PHIDIAS rules variable declaration
# ---------------------------------------------------------------------

def_vars("X", "Y", "D", "H", "Z", "L", "M", "A", "D", "W","S","U","T", "P")

# ---------------------------------------------------------------------
# Agents section
# ---------------------------------------------------------------------

# agents are in config_mas.ini but not actually used, I left for now
agents = get_agents_names()[1:]
scholars = get_scholars_names()[1:]
universities = get_universities_names()[1:]
newcomers = get_newcomers_names()[1:]
categories = get_categories_names()[1:]

#if len(agents)==0:
#   print("\nWARNING: Agents list is empty. Please initialize the ontology with init() from the eShell then restart.")
#else:
#   print("Agents list: ", agents)

if len(agents) == 0:
   print("\nWARNING: Agents list is empty. Please initialize the ontology with init() from the eShell, then restart Semas.")
else:
   print("Agents list: ", agents)


def create_agents(class_name):
    def main(self):
        # MoveAndCompleteJob intention
        load() >> [show_line("\nAsserting all OWL 2 triples beliefs...\n"), assert_beliefs_triples(), show_line("\nTurning triples beliefs into Semas beliefs...\n"), pre_process()]
        
        pre_process() / TRIPLE(X, "coAuthorWith", Y) >> [-TRIPLE(X, "coAuthorWith", Y), +CoAuthorship(X, Y), co_authorshiplink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "hasAffiliationWith", Y) >> [-TRIPLE(X, "hasAffiliationWith", Y), +Affiliation(X, Y), affiliationlink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "isTopAuthorIn", Y) >> [-TRIPLE(X, "isTopAuthorIn", Y), +TopAuthorship(X, Y), topauthorlink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "selectedFor", Y) >> [-TRIPLE(X, "selectedFor", Y), +Selectionship(X, Y), selectforlink(X,Y), pre_process()]
        
        send(A, X,L) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A), +AGT(A), +COMMUNICATE(X,L)]
        
        +COMMUNICATE(X,L) / AGT(A) >> [-AGT(A), +COMMUNICATE(X,L)[{'to': A}]]
        +COMMUNICATE(X,L)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(W, X,L), pre_process()]

        +COMMUNICATEMAIN(Z,U) / AGT(A) >> [-AGT(A), +COMMUNICATEMAIN(Z,U)[{'to': A}]]
        +COMMUNICATEMAIN(Z,U)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(Z,"hasAffiliationWith",U), pre_process()]
        
        DesireGoalFor(U) / (Affiliation(Z,U)) >> [show_line("found match ",Z), -Affiliation(Z,U), DesireGoalFor(U), +Affiliation(Z,U)]

        +Testkb(U) / (Affiliation(Z,U)) >> [show_line("found match ",Z), -Affiliation(Z,U) ,Testkb(U) ]

     #   sendDelete(A, X,L) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A), +AGT(A), +COMMUNICATE(X)]
     #   +COMMUNICATE(X,L) / AGT(A) >> [-AGT(A) ]# , +COMMUNICATE(X,L)[{'to': A}]]
     #   +COMMUNICATE(X,L)[{'from': W}] >> [show_line("received belief from ", W), -TRIPLE(W, X,L), pre_process()]
#        send(A, X,L) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A), +AGT(A), +COMMUNICATE(X,L)]
        
#        +COMMUNICATE(X,L) / AGT(A) >> [-AGT(A), +COMMUNICATE(X,L)[{'to': A}]]
#        +COMMUNICATE(X,L)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(X,L,W)]

    return type(class_name, (Agent,), {"main": main})

def create_custom_agent(class_name):
    def main(self):
        # Custom intention
        +COMMUNICATE(X,L)[{'from': A}] >> [show_line("\nReceived belief COMMUNICATE(",X,") from ", A), +TRIPLE(X,L,A), +COMMUNICATE(X)[{'to': 'main'}]]

    return type(class_name, (Agent,), {"main": main})

# General agents from OWL
for i in range(len(agents)):
    globals()[agents[i]] = create_agents(agents[i])

for i in range(len(agents)):
    instance = globals()[agents[i]]()

# custom agent rocco
globals()["rocco"] = create_custom_agent("rocco")
globals()["anna"] = create_custom_agent("anna")
instance = globals()["rocco"]()

for i in range(len(agents)):
    globals()[agents[i]] = create_agents(agents[i])

for i in range(len(agents)):
    instance = globals()[agents[i]]()


# ---------------------------------------------------------------------
# Agent 'main'
# ---------------------------------------------------------------------

class main(Agent):
    def main(self):

        # World initialization
        init() >> [show_line("\nInitialiting Ontology...\n"), initWorld(), declareRules(), saveOnto()]

        # Importing related triples
        load() >> [show_line("\nAsserting all OWL 2 triples beliefs...\n"), assert_beliefs_triples(), show_line("\nTurning triples beliefs into Semas beliefs...\n"), pre_process()]
      
        pre_process() / TRIPLE(X, "coAuthorWith", Y) >> [-TRIPLE(X, "coAuthorWith", Y), +CoAuthorship(X, Y), co_authorshiplink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "hasAffiliationWith", Y) >> [-TRIPLE(X, "hasAffiliationWith", Y), +Affiliation(X, Y), affiliationlink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "isTopAuthorIn", Y) >> [-TRIPLE(X, "isTopAuthorIn", Y), +TopAuthorship(X, Y), topauthorlink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "selectedFor", Y) >> [-TRIPLE(X, "selectedFor", Y), +Selectionship(X, Y), selectforlink(X,Y), pre_process()]

     #   DesireGoalFor(X) / (CoAuthorship(Z,Y) & TopAuthorship(Y,X) & Affiliation(Z,U) & Selectionship(S,U) & Affiliation(S,T)) >> [-CoAuthorship(Z,Y), +AcceptOffer(Z,U,Y,X,S,T) , DesireGoalFor(X)]
     #   +AcceptOffer(Z,U,Y,X,S,T) >> [show_line (Z," at University ", U ," is co-author with ",Y," top-author in the topic ", X), -Affiliation(S,T) ,-Selectionship(S,U), +Affiliation(S,U) ]# , DeleteAlternative(S)]

    #    DeleteAlternative(S) / ( Selectionship(S,P)) >> [-Selectionship(S,P) , DeleteAlternative(S)]
        
        
        send(A, X,L) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A),  +AGT(A), +COMMUNICATE(X,L)]
        sendtriple(A,U) / (Affiliation(Z,U)) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A),  +AGT(A), +COMMUNICATEMAIN(Z,U)]
        
        +COMMUNICATEMAIN(Z,U) / AGT(A) >> [-AGT(A), +COMMUNICATEMAIN(Z,U)[{'to': A}]]
        +COMMUNICATEMAIN(Z,U)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(Z,"hasAffiliationWith",U), pre_process()]

        +COMMUNICATE(X,L) / AGT(A) >> [-AGT(A), +COMMUNICATE(X,L)[{'to': A}]]
        +COMMUNICATE(X,L)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(W, X,L), pre_process()]

        DesireGoalFor(U) / (Affiliation(Z,U)) >> [show_line("found match ",Z), -Affiliation(Z,U), DesireGoalFor(U), +Affiliation(Z,U)]

        +Testkb(U) / (Affiliation(Z,U)) >> [show_line("found match ",Z), -Affiliation(Z,U) ,Testkb(U) ]

     #   sendDelete(A, X,L) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A), +AGT(A), +COMMUNICATE(X)]
     #   +COMMUNICATE(X,L) / AGT(A) >> [-AGT(A), +COMMUNICATE(X,L)[{'to': A}]]
     #   +COMMUNICATE(X,L)[{'from': W}] >> [show_line("received belief from ", W), -TRIPLE(W, X,L), pre_process()]
 

        report() >> [measures()]
        reportuniv() >> [measuresuniv()]
        plotmeasurecn(X) >> [plot_centrality(X)]
        plotmeasurecl(X) >> [plot_clustering(X)]
        plotmeasurebt(X) >> [plot_betweeness(X)]
        


for i in range(len(agents)):
    instance = globals()[agents[i]]()
    instance.start()

main().start()