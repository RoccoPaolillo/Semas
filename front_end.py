from phidias.Lib import *
from actions import *
from phidias.Types import *

# ---------------------------------------------------------------------
# PHIDIAS rules variable declaration
# ---------------------------------------------------------------------

def_vars('X', 'Y', 'Z', 'U','S','P','T')

# Ontology intialization
class init(Procedure): pass

# Processing beliefs
class load_subj(Procedure): pass
class load_obj(Procedure): pass

# Import OWL triples
class pre_process(Procedure): pass

class REST(Belief): pass


# World initialization (only for local usage ontologies)
init() >> [show_line("\nInitialiting Ontology...\n"), initWorld(), declareRules(), saveOnto()]
load() >> [show_line("\nAsserting all OWL 2 beliefs...\n"), assert_beliefs_local_triples(), pre_process()]

# Importing all related triples
# Importing filtered triples
load_subj(X, Y) >> [show_line("\nAsserting all OWL 2 beliefs related to ",X," (subj) and ",Y," from triple-store...\n"), assert_beliefs_triples_subj(X, Y), pre_process()]
load_obj(X, Y) >> [show_line("\nAsserting all OWL 2 beliefs related to ",X," (obj) and ",Y," from triple-store...\n"), assert_beliefs_triples_obj(X, Y), pre_process()]



# Starting RESTful flask service
start_rest() >> [show_line("\nStarting RESTful service...\n"), +REST("ACTIVE"), start_rest_service()]

# Only after get_triple() | pre_process()
pre_process() / TRIPLE(X, "coAuthorWith", Y) >> [-TRIPLE(X, "coAuthorWith", Y), +CoAuthorship(X, Y), pre_process()]
pre_process() / TRIPLE(X, "hasAffiliationWith", Y) >> [-TRIPLE(X, "hasAffiliationWith", Y), +Affiliation(X, Y), pre_process()]
pre_process() / TRIPLE(X, "isTopAuthorIn", Y) >> [-TRIPLE(X, "isTopAuthorIn", Y), +ConsiderTopAuthor(X, Y), pre_process()]
pre_process() / TRIPLE(X, "selectedFor", Y) >> [-TRIPLE(X, "selectedFor", Y), +Selectionship(X, Y), pre_process()]
pre_process() >> [show_line("\nAsserting triples ended.\n")]

BeTopAuthorship(X) >> [show_line("\nPlanning to be top-author in ",X,"..."), load_obj("acad:isTopAuthorIn", X), FindRelated(), Publicationship(X)]

FindRelated() / ConsiderTopAuthor(X, Y) >> [-ConsiderTopAuthor(X, Y), +TopAuthorship(X, Y), show_line("\nFinding triples related with ",X,"..."), load_subj("acad:hasAffiliationWith", X), load_subj("acad:coAuthorWith", X), load_obj("acad:coAuthorWith", X), FindRelated()]

FindRelated() >> [show_line("\nRelated triples retrived."), ]

# comment in case of no Selectionship handling (fig. 9, 10, 11)
Publicationship(X) / (CoAuthorship(Z, Y) & TopAuthorship(Y, X) & Affiliation(Z, U) & Selectionship(S,U) & Affiliation(S,T)) >> [-CoAuthorship(Z, Y), +ProposeCoauthorship(Z,U,Y,X,S,T),Publicationship(X)]
+ProposeCoauthorship(Z,U,Y,X,S,T) >> [show_line(Z, " at Organization ", U, " is co-author with ", Y, " top-author in the topic ", X, "\n"), -Affiliation(S,T) ,-Selectionship(S,U), +Affiliation(S,U), DeleteAlternative(S)] 
DeleteAlternative(S) / (Selectionship(S,P)) >> [-Selectionship(S,P), DeleteAlternative(S)]

# Prompt shell (figure 4 case study)

# BeTopAuthorship('http://fossr.eu/kg/data/topics/2003') ----> Finance
# BeTopAuthorship('http://fossr.eu/kg/data/topics/2214') ----> Media Technology
# Assert in shell to handle Selectionshìp beliefs:
# +Selectionship('http://fossr.eu/kg/data/authors/57201117401','http://fossr.eu/kg/data/organizations/60000481') ---> Università degli Studi di Padova
# +Selectionship('http://fossr.eu/kg/data/authors/57201117401','http://fossr.eu/kg/data/organizations/105937250') ---> Università degli Studi di Milano Statale
# load_subj("acad:hasAffiliationWith", 'http://fossr.eu/kg/data/authors/57201117401')
# authors/57201117401 has affiliation from KG time 0 with "http://fossr.eu/kg/data/organizations/60024690" --> "University of Ferrara"
