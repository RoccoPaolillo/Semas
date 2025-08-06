import time
from actions_mas import *
import warnings
import random

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
#        load_subj(X, Y) >> [show_line("\nAsserting all OWL 2 beliefs related to ",X," (subj) and ",Y," from triple-store...\n"), assert_beliefs_triples_subj(X, Y), pre_process()]
#        load_obj(X, Y) >> [show_line("\nAsserting all OWL 2 beliefs related to ",X," (obj) and ",Y," from triple-store...\n"), assert_beliefs_triples_obj(X, Y), pre_process()]
        pre_process() / TRIPLE(X, "coAuthorWith", Y) >> [-TRIPLE(X, "coAuthorWith", Y), +CoAuthorship(X, Y), +CoAuthorship(Y, X), co_authorshiplink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "hasAffiliationWith", Y) >> [-TRIPLE(X, "hasAffiliationWith", Y), +Affiliation(X, Y), affiliationlink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "isTopAuthorIn", Y) >> [-TRIPLE(X, "isTopAuthorIn", Y), +TopAuthorship(X, Y), topauthorlink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "selectedFor", Y) >> [-TRIPLE(X, "selectedFor", Y), +Selectionship(X, Y), selectforlink(X,Y), pre_process()]
        
        send(A, H,L) >> [show_line("Sending belief COMMUNICATE(",H,") to agent ", A), +AGT(A), +COMMUNICATE(H,L)]
        send_ownselectionship(A,A) / (Selectionship(A,Y)) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A, " "),  +AGT(A), -Selectionship(A,Y) , +COMMUNICATESEL(A,Y), send_ownselectionship(A,A), +Selectionship(A,Y)]
        send_ownaffiliation(A,A) / (Affiliation(A,Y)) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A, " "),  +AGT(A), -Affiliation(A,Y) , +COMMUNICATEOWNAFF(A,Y), send_ownaffiliation(A,A), +Affiliation(A,Y)]
        send_owncoauthor(A,A) / (CoAuthorship(A,Y)) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A, " "),  +AGT(A), -CoAuthorship(A,Y) , +COMMUNICATEOWNCOAUTH(A,Y), send_owncoauthor(A,A), +CoAuthorship(A,Y)]

        #        send_all(A) >>  [show_line("Sending belief COMMUNICATE(",X,") to agent ", A),  +AGT(A), CommunicateOwn(A)]


        +COMMUNICATE(H,L) / AGT(A) >> [-AGT(A), +COMMUNICATE(H,L)[{'to': A}]]
        +COMMUNICATE(H,L)[{'from': S}] >> [show_line("received belief from ", S),  UpdateMain(S) , +TRIPLE(S, H,L), pre_process()   ]

#        CommunicateSelf(A) / Selectionship(A,Y) >> [+AGT(A), +COMMUNICATEOWN(A,Y)]
        +COMMUNICATESEL(A,Y) / AGT(A) >> [+COMMUNICATESEL(A,Y)[{'to': A}]]
        +COMMUNICATESEL(A,Y)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(A,"selectedFor",Y), pre_process()]

        +COMMUNICATEOWNAFF(A,Y) / AGT(A) >> [+COMMUNICATEOWNAFF(A,Y)[{'to': A}]]
        +COMMUNICATEOWNAFF(A,Y)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(A,"hasAffiliationWith",Y), pre_process()]

        +COMMUNICATEOWNCOAUTH(A,Y) / AGT(A) >> [+COMMUNICATEOWNCOAUTH(A,Y)[{'to': A}]]
        +COMMUNICATEOWNCOAUTH(A,Y)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(A,"coAuthorWith",Y), pre_process()]
#        +COMMUNICATEOWN(A,Y) / AGT(A) >> [-AGT(A), +COMMUNICATEOWN(A,Y)[{'to': A}],+COMMUNICATEOWN(A,Y)]
#        +COMMUNICATEOWN(A,Y) / (AGT(A) & Selectionship(A,Y) )>> [-AGT(A), +COMMUNICATEOWN(A,Y)[{'to': A}]]
#        +COMMUNICATEOWN(A,Y)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(A,"selectedFor",Y), pre_process()]

#        +COMMUNICATEOWN(A,D) / (AGT(A) & CoAuthorship(A,L))>> [-AGT(A), +COMMUNICATEOWN(A,D)[{'to': A}]]
#        +COMMUNICATEOWN(A,D)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(A, D,L), pre_process()]

        +COMMUNNICATEAFF(Z,U) / AGT(A) >> [-AGT(A), +COMMUNNICATEAFF(Z,U)[{'to': A}]]
        +COMMUNNICATEAFF(Z,U)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(Z,"hasAffiliationWith",U), pre_process()]
        +COMMUNICATECOAUTH(Y,D) / AGT(A) >> [-AGT(A), +COMMUNICATECOAUTH(Y,D)[{'to': A}]]
        +COMMUNICATECOAUTH(Y,D)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(Y,"coAuthorWith",D), pre_process()]
        +COMMUNICATETOPAUTH(Y,D) / AGT(A) >> [ +COMMUNICATETOPAUTH(Y,D)[{'to': A}]]
        +COMMUNICATETOPAUTH(Y,D)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(Y,"isTopAuthorIn",D), pre_process()]
        
        DesireGoalFor(X,D,U) / (Selectionship(S,D) & Selectionship(S,U) & TopAuthorship(Y,X) & CoAuthorship(Z,Y) & Affiliation(Z,U)) >> [-CoAuthorship(Z,Y), +AcceptOffer(U)]
        DesireGoalFor(X,D,U) / (Selectionship(S,D) & Selectionship(S,U) & TopAuthorship(Y,X) & CoAuthorship(Z,Y) & Affiliation(Z,D)) >> [-CoAuthorship(Z,Y), +AcceptOffer(D)]
        DesireGoalFor(X,D,U) / trialtest(0.5) >> [+AcceptOffer(U)]
        DesireGoalFor(X,D,U) >> [+AcceptOffer(D)]
#        DesireGoalFor(X) / (Selectionship(S,D) & Selectionship(S,U)) >> [+AcceptOffer(U)]
        +AcceptOffer(U) >> [show_line("affiliation to delete ", S), +Affiliation(U), send("main","hasAffiliationWith",U)]
        +AcceptOffer(D) >> [show_line("affiliation to delete ", S), +Affiliation(D), send("main","hasAffiliationWith",D)]

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
      
        pre_process() / TRIPLE(X, "coAuthorWith", Y) >> [-TRIPLE(X, "coAuthorWith", Y), +CoAuthorship(X, Y), +CoAuthorship(Y, X), co_authorshiplink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "hasAffiliationWith", Y) >> [-TRIPLE(X, "hasAffiliationWith", Y), +Affiliation(X, Y), affiliationlink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "isTopAuthorIn", Y) >> [-TRIPLE(X, "isTopAuthorIn", Y), +TopAuthorship(X, Y), topauthorlink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "selectedFor", Y) >> [-TRIPLE(X, "selectedFor", Y), +Selectionship(X, Y), selectforlink(X,Y), pre_process()]

     #   DesireGoalFor(X) / (CoAuthorship(Z,Y) & TopAuthorship(Y,X) & Affiliation(Z,U) & Selectionship(S,U) & Affiliation(S,T)) >> [-CoAuthorship(Z,Y), +AcceptOffer(Z,U,Y,X,S,T) , DesireGoalFor(X)]
     #   +AcceptOffer(Z,U,Y,X,S,T) >> [show_line (Z," at University ", U ," is co-author with ",Y," top-author in the topic ", X), -Affiliation(S,T) ,-Selectionship(S,U), +Affiliation(S,U) ]# , DeleteAlternative(S)]

    #    DeleteAlternative(S) / ( Selectionship(S,P)) >> [-Selectionship(S,P) , DeleteAlternative(S)]
        
        
        send(A,H,L) >> [show_line("Sending belief COMMUNICATE(",H,") to agent ", A),  +AGT(A), +COMMUNICATE(H,L)]
#        send_all(A,A) / (CoAuthorship(A,Y)) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A, " " ,Z),  +AGT(A), -CoAuthorship(A,Y) , +COMMUNICATEOWN(A,Y), send_all(A,A), +CoAuthorship(A,Y)]
#        send_all(A) >>  [show_line("Sending belief COMMUNICATE(",X,") to agent ", A),  +AGT(A), CommunicateOwn(A)]
        send_ownselectionship(A,A) / (Selectionship(A,Y)) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A, " "),  +AGT(A), -Selectionship(A,Y) , +COMMUNICATESEL(A,Y), send_ownselectionship(A,A), +Selectionship(A,Y)]
        send_ownaffiliation(A,A) / (Affiliation(A,Y)) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A, " "),  +AGT(A), -Affiliation(A,Y) , +COMMUNICATEOWNAFF(A,Y), send_ownaffiliation(A,A), +Affiliation(A,Y)]
        send_owncoauthor(A,A) / (CoAuthorship(A,Y)) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A, " "),  +AGT(A), -CoAuthorship(A,Y) , +COMMUNICATEOWNCOAUTH(A,Y), send_owncoauthor(A,A), +CoAuthorship(A,Y)]


        sendaffiliation(A,U) / (Affiliation(Z,U)) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A, " " ,Z),  +AGT(A), -Affiliation(Z,U) ,   +COMMUNNICATEAFF(Z,U), sendaffiliation(A,U), +Affiliation(Z,U)]
        sendcoauthor(A,D) / (CoAuthorship(Y,D)) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A, " " ,Y),  +AGT(A), -CoAuthorship(Y,D) ,   +COMMUNICATECOAUTH(Y,D), sendcoauthor(A,D), +CoAuthorship(Y,D)]
        sendtopauthor(A,D) / (TopAuthorship(Y,D)) >> [show_line("Sending belief COMMUNICATE(",X,") to agent ", A, " " ,Y),  +AGT(A), -TopAuthorship(Y,D) ,   +COMMUNICATETOPAUTH(Y,D), sendtopauthor(A,D), +TopAuthorship(Y,D)]
     
        +COMMUNICATESEL(A,Y) / AGT(A) >> [+COMMUNICATESEL(A,Y)[{'to': A}]]
        +COMMUNICATESEL(A,Y)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(A,"selectedFor",Y), pre_process()]

        +COMMUNICATEOWNAFF(A,Y) / AGT(A) >> [+COMMUNICATEOWNAFF(A,Y)[{'to': A}]]
        +COMMUNICATEOWNAFF(A,Y)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(A,"hasAffiliationWith",Y), pre_process()]

        +COMMUNICATEOWNCOAUTH(A,Y) / AGT(A) >> [+COMMUNICATEOWNCOAUTH(A,Y)[{'to': A}]]
        +COMMUNICATEOWNCOAUTH(A,Y)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(A,"coAuthorWith",Y), pre_process()]


     
     #   ComunicationTriple(A,U) / (Affiliation(Z,U)) >> [-AGT(A), +COMMUNNICATEAFF(Z,U)[{'to': A}]]
     #   +COMMUNNICATEAFF(Z,U) / AGT(A) >> [-AGT(A), +COMMUNNICATEAFF(Z,U)[{'to': A}]]
        +COMMUNNICATEAFF(Z,U) / AGT(A) >> [ +COMMUNNICATEAFF(Z,U)[{'to': A}]]
        +COMMUNNICATEAFF(Z,U)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(Z,"hasAffiliationWith",U), pre_process()]
        +COMMUNICATECOAUTH(Y,D) / AGT(A) >> [ +COMMUNICATECOAUTH(Y,D)[{'to': A}]]
        +COMMUNICATECOAUTH(Y,D)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(Y,"coAuthorWith",D), pre_process()]
        +COMMUNICATETOPAUTH(Y,D) / AGT(A) >> [ +COMMUNICATETOPAUTH(Y,D)[{'to': A}]]
        +COMMUNICATETOPAUTH(Y,D)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(Y,"isTopAuthorIn",D), pre_process()]


        +COMMUNICATE(H,L) / AGT(A) >> [-AGT(A), +COMMUNICATE(H,L)[{'to': A}]]
        +COMMUNICATE(H,L)[{'from': S}] >> [show_line("received belief from ", S),  UpdateMain(S) , +TRIPLE(S,H,L), pre_process()   ]

#        CommunicateSelf(A) / Selectionship(A,Y) >> [+AGT(A), +COMMUNICATEOWN(A,Y)]
#        +COMMUNICATEOWN(A,Y) / AGT(A) >> [+COMMUNICATEOWN(A,Y)[{'to': A}]]
#        +COMMUNICATEOWN(A,Y)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(A,"coAuthorWith",Y), pre_process()]

#        +COMMUNICATEOWN(A,Y) / AGT(A) >> [-AGT(A), +COMMUNICATEOWN(A,Y)[{'to': A}],+COMMUNICATEOWN(A,Y)]
#        +COMMUNICATEOWN(A,Y) / (AGT(A) & Selectionship(A,Y) )>> [-AGT(A), +COMMUNICATEOWN(A,Y)[{'to': A}]]
#        +COMMUNICATEOWN(A,Y)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(A,"selectedFor",Y), pre_process()]

#        +COMMUNICATEOWN(A,D) / (AGT(A) & CoAuthorship(A,L))>> [-AGT(A), +COMMUNICATEOWN(A,D)[{'to': A}]]
#        +COMMUNICATEOWN(A,D)[{'from': W}] >> [show_line("received belief from ", W), +TRIPLE(A, D,L), pre_process()]

        DesireGoalFor(X,D,U) / (Selectionship(S,D) & Selectionship(S,U) & TopAuthorship(Y,X) & CoAuthorship(Z,Y) & Affiliation(Z,U)) >> [-CoAuthorship(Z,Y), +AcceptOffer(U)]
        DesireGoalFor(X,D,U) / (Selectionship(S,D) & Selectionship(S,U) & TopAuthorship(Y,X) & CoAuthorship(Z,Y) & Affiliation(Z,D)) >> [-CoAuthorship(Z,Y), +AcceptOffer(D)]
        DesireGoalFor(X,D,U) / trialtest(0.5) >> [+AcceptOffer(U)]
        DesireGoalFor(X,D,U) >> [+AcceptOffer(D)]
#        DesireGoalFor(X) / (Selectionship(S,D) & Selectionship(S,U)) >> [+AcceptOffer(U)]
        +AcceptOffer(U) >> [show_line("affiliation to delete ", S), +Affiliation(U), send("main","hasAffiliationWith",U)]
        +AcceptOffer(D) >> [show_line("affiliation to delete ", S), +Affiliation(D), send("main","hasAffiliationWith",D)]

        +Testkb(U) / (Affiliation(Z,U)) >> [show_line("found match ",Z), -Affiliation(Z,U) ,Testkb(U) ]
#        +UpdateMain(W) / ((Selectionship(W,D) & Affiliation(W,D)) & Affiliation(W,U) & Selectionship(W,Y)) >> [-Selectionship(W,Y), -Affiliation(W,U), -Selectionship(W,D),  deletelink(W,U), deletelink(W,Y), affiliationlink(W,D) ] #deletelink(W,D),
        UpdateMain(S) / Selectionship(S,P)  >> [-Selectionship(S,P), deletelink(S,P), UpdateMain(S) ] #deletelink(W,D),
        UpdateMain(S) / Affiliation(S,P)  >> [-Affiliation(S,P), deletelink(S,P), UpdateMain(S) ] #deletelink(W,D),

#        +UpdateMain(W,D,U,H) / ( (Affiliation(W,U) & Selectionship(W,U)) & Affiliation(W,H) & Selectionship(W,D)) >> [-Affiliation(W,H), -Selectionship(W,D), -Selectionship(W,U), deletelink(W,H), deletelink(W,D), deletelink(W,U), affiliationlink(W,U) ] #, deletelink(W,T), deletelink(W,Y), affiliationlink(W,T) ]
#        +UpdateMain(W,D,U,H) / ( (Affiliation(W,D) & Selectionship(W,D)) & Affiliation(W,H) & Selectionship(W,U)) >> [-Affiliation(W,H), -Selectionship(W,U), -Selectionship(W,D), deletelink(W,H), deletelink(W,U), deletelink(W,D), affiliationlink(W,D) ]
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