import time
from actions_mas import *
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------
# PHIDIAS rules variable declaration
# ---------------------------------------------------------------------

def_vars("X", "Y", "D", "H", "Z", "L", "M", "A", "D", "W","S","U")

# ---------------------------------------------------------------------
# Agents section
# ---------------------------------------------------------------------

# agents are in config_mas.ini but not actually used, I left for now

scholars = get_scholars_names()[1:]
universities = get_universities_names()[1:]
newcomers = get_newcomers_names()[1:]
categories = get_categories_names()[1:]

#if len(agents)==0:
#   print("\nWARNING: Agents list is empty. Please initialize the ontology with init() from the eShell then restart.")
#else:
#   print("Agents list: ", agents)

# ---------------------------------------------------------------------
# Agent 'main'
# ---------------------------------------------------------------------

class main(Agent):
    def main(self):

        # World initialization
        init() >> [show_line("\nInitialiting Ontology...\n"), initWorld(), declareRules(), saveOnto()]

        # Importing related triples
        load() >> [show_line("\nAsserting all OWL 2 triples beliefs...\n"), assert_beliefs_triples(), show_line("\nTurning triples beliefs into Semas beliefs...\n"), pre_process()]
      
        pre_process() / TRIPLE(X, "isAffiliated", Y) >> [-TRIPLE(X, "isAffiliated", Y), +IsAffiliated(X, Y), pre_process()]
        pre_process() / TRIPLE(X, "coAuthorWith", Y) >> [-TRIPLE(X, "coAuthorWith", Y), +CoAuthorship(X, Y), co_authorshiplink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "hasAffiliationWith", Y) >> [-TRIPLE(X, "hasAffiliationWith", Y), +Affiliation(X, Y), affiliationlink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "isTopAuthorIn", Y) >> [-TRIPLE(X, "isTopAuthorIn", Y), +TopAuthorship(X, Y), topauthorlink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "selectedFor", Y) >> [-TRIPLE(X, "selectedFor", Y), +Selectionship(X, Y), selectforlink(X,Y), pre_process()]
        pre_process() / TRIPLE(X, "hasInterest", Y) >> [-TRIPLE(X, "hasInterest", Y), +HasInterest(X, Y), pre_process()]

#        DesireGoalFor(X) / (Selectionship(S,U) & TopAuthorship(Y, X) & Affiliation(Y, U)) >> [show_line("Direct match found at ",U,".\n"), -TopAuthorship(Y, X), +ProposeCoauthorship(Y, X), +AcceptOffer(S,X,U),  DesireGoalFor(X)]
#        DesireGoalFor(X) / (Selectionship(S,U) & TopAuthorship(Y, X) & CoAuthorship(Z, Y)  & Affiliation(Z, U)) >> [show_line("Indirect match found at ",U,".\n"), -CoAuthorship(Z, Y), +coauthorIndirect(Z, U,Y,X), +AcceptOffer(S,X,U), DesireGoalFor(X)]

#        DesireGoalFor(X) / (Selectionship(S,U) & TopAuthorship(Y, X) & CoAuthorship(Z, Y)  & Affiliation(Z, U)) >> [show_line("Indirect match found at ",U,".\n"),  -CoAuthorship(Z, Y), +coauthorIndirect(Z, U,Y,X), +AcceptOffer(S,X,U), DesireGoalFor(X)]
        DesireGoalForDir(X) / (IsAffiliated(S, D) & HasInterest(S,X) & Selectionship(S,U) & TopAuthorship(Y, X) & Affiliation(Y, U)) >> [show_line("Direct match found at ",U,".\n"), -TopAuthorship(Y, X),  +AcceptOffer2(S,X,U), -IsAffiliated(S,D),  DesireGoalForDir(X)]
        DesireGoalForIndir(X) / (IsAffiliated(S, D) & HasInterest(S,X) & Selectionship(S,U) & TopAuthorship(Y, X) & CoAuthorship(Z, Y)  & Affiliation(Z, U)) >> [show_line("Indirect match found at ",U,".\n"),  -CoAuthorship(Z, Y), +AcceptOffer(S,X,U), -IsAffiliated(S,D), DesireGoalForIndir(X)]
            

        report() >> [measures()]
        reportuniv() >> [measuresuniv()]
        plotmeasurecn(X) >> [plot_centrality(X)]
        plotmeasurecl(X) >> [plot_clustering(X)]
        plotmeasurebt(X) >> [plot_betweeness(X)]
        
        
        +coauthorIndirect(Z, U,Y,X) >> [show_line(Z," at ", U, " is co-author with ",Y,", a top-author in the field of ",X,".\n")]
        +ProposeCoauthorship(Y,X) >> [show_line("Propose co-authorship with ",Y," as top-author in the field of ",X,".\n")]
        +AcceptOffer(S,X,U) >> [show_line(S," should accept offer from University ",U," with co-authors of top-authors in field of ",X,".\n"),-TRIPLE(S, "hasAffiliationWith", U), +Affiliation(S,U), new_affiliation(S,U), pre_process()]
        +AcceptOffer2(S,X,U) >> [show_line(S," should accept offer from University ",U," with top-authors in field ",X,".\n"),-TRIPLE(S, "hasAffiliationWith", U), +Affiliation(S,U), new_affiliation(S,U), pre_process()]
#        +DeleteSelection(S,A) >> [-TRIPLE(S, "selectedFor", A),-Selectionship(S,A), pre_process()]
        
main().start()