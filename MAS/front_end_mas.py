import time
from actions_mas import *

# ---------------------------------------------------------------------
# PHIDIAS rules variable declaration
# ---------------------------------------------------------------------

def_vars("X", "Y", "D", "H", "Z", "L", "M", "A", "D", "W","S","U")

# ---------------------------------------------------------------------
# Agents section
# ---------------------------------------------------------------------

agents = get_agents_names()[1:]
scholars = get_scholars_names()[1:]
universities = get_universities_names()[1:]
newcomers = get_newcomers_names()[1:]

if len(agents)==0:
   print("\nWARNING: Agents list is empty. Please initialize the ontology with init() from the eShell then restart.")
else:
   print("Agents list: ", agents)



def create_agents(class_name):
    def main(self):
        # MoveAndCompleteJob intention
#         +TASK(X, Y, A)[{'from': M}] >> [show_line("\n",A," is moving to (", X, ",", Y, "), received task from ", M), move_turtle(A, X, Y), +COMM("DONE")[{'to': 'main'}]]
         +TASK(X)[{'from': M}] >> [pubby(X), +COMM("DONE")[{'to': 'main'}]]



#        +NETNEW(X, Y)[{'from': M}] >> [show_line(create_link(X,Y))[{'to': 'main'}]]
    # Creiamo una nuova classe con il metodo 'main' definito sopra
    return type(class_name, (Agent,), {"main": main})

for i in range(len(agents)):
    # class_name = f"{ID_PREFIX}{i+1}"
    globals()[agents[i]] = create_agents(agents[i])

# Ora puoi creare istanze delle nuove classi e chiamare il loro metodo main
for i in range(len(agents)):
    # class_name = f"{ID_PREFIX}{i+1}"
    instance = globals()[agents[i]]()
    instance.main()
    
for i in range(len(scholars)):
    # class_name = f"{ID_PREFIX}{i+1}"
    globals()[scholars[i]] = create_agents(scholars[i])

# Ora puoi creare istanze delle nuove classi e chiamare il loro metodo main
for i in range(len(scholars)):
    # class_name = f"{ID_PREFIX}{i+1}"
    instance = globals()[scholars[i]]()
    instance.main()

# ---------------------------------------------------------------------
# Agent 'main'
# ---------------------------------------------------------------------

class main(Agent):
    def main(self):

        # World initialization
        init() >> [show_line("\nInitialiting Ontology...\n"), initWorld(), declareRules(), saveOnto()]

        # Importing related triples
        load() >> [show_line("\nAsserting all OWL 2 triples beliefs...\n"), assert_beliefs_triples(), show_line("\nTurning triples beliefs into Semas beliefs...\n"), turn()]
#        turn() / TRIPLE(X, "hasLedger",Z) >> [-TRIPLE(X,"hasLedger",Z), +LEDGER(X,"0"), AssignId(X), turn()]

# FOSSR DAYS        
        turn() / TRIPLE(X, "coAuthorWith", Y) >> [-TRIPLE(X, "coAuthorWith", Y), +CoAuthorship(X, Y), co_authorshiplink(X,Y), turn()]
        turn() / TRIPLE(X, "hasAffiliationWith", Y) >> [-TRIPLE(X, "hasAffiliationWith", Y), +Affiliation(X, Y), affiliationlink(X,Y), turn()]
        turn() / TRIPLE(X, "isTopAuthorIn", Y) >> [-TRIPLE(X, "isTopAuthorIn", Y), +TopAuthorship(X, Y), topauthorlink(X,Y), turn()]
        turn() / TRIPLE(X, "selectedFor", Y) >> [-TRIPLE(X, "selectedFor", Y), +Selectionship(X, Y), selectforlink(X,Y) , turn()]
# FOSSR DAYS

        # desires
        setup() / WORKTIME(W) >> [show_line("Setup worktime again...\n"), load(), -WORKTIME(W), +WORKTIME(0)]
        setup() >> [show_line("Setup worktime...\n"), +WORKTIME(0), +MAX_WORK_TIME(Max_Work_Time), +MAX_WORKDAY_TIME(Max_WorkDay_Time), +REST_TIME(Rest_Time)]
#        work() >> [show_line("Starting task detection...\n"), Timer(Max_Work_Time).start(), TaskDetect().start(), show_line("Workers on duty...")]
        work() >> [show_line("Starting task detection...\n"), Timer(Max_Work_Time).start(), TaskDetect().start(), show_line("Workers on duty...")]

        # AssignJob intentions
        +TASK(X, Y) / (AGT(A, D) & DUTY(D)) >> [show_line("assigning job to ",A), -DUTY(D), +TASK(X, Y, A)[{'to': A}]]

        # ReceiveCommunication intentions
        +COMM(X)[{'from': W}] / LEDGER(W, H) >> [show_line("received job done comm from ", W), -LEDGER(W, H), UpdateLedger(W, H)]

        # Pause work intentions - check if the whole working time belief WORKTIME is greater-equal than MAX_WORKDAY_TIME
        +TIMEOUT("ON") / (WORKTIME(X) & MAX_WORKDAY_TIME(Y) & geq(X,Y)) >> [show_line("\nWorkers are very tired. Finishing working day.\n"), TaskDetect().stop(), stopwork()]

        # End work intentions - Add the MAX_WORK_TIME quantity (during the pause) to the whole working time belief WORKTIME
        +TIMEOUT("ON") / (WORKTIME(X) & MAX_WORK_TIME(Y)) >> [show_line("\nWorkers are tired, they need some rest.\n"), TaskDetect().stop(), -WORKTIME(X), UpdateWorkTime(X, Y), noduty()]
        noduty() / (AGT(A, D) & DUTY(D)) >> [show_line("Putting agent" , A, " to rest..."), -DUTY(D), noduty()]
        noduty() / REST_TIME(X) >> [rest(X), work()]

        # Stop work intention
        stopwork() / ((AGT(A, D) & DUTY(D))) >> [show_line("\n-------------------------> Stopping ", A), -DUTY(D), stopwork()]
        stopwork() >> [show_line("\nAll workers were stopped. Starting payment process."), pay()]

        # pay desires
        pay() / LEDGER(Z, H) >> [show_line("\nSending payment to ",Z, " for ",H," tasks..."), -LEDGER(Z, H), pay()]
        pay() >> [show_line("\nPayments completed.")]
        
#        netty() / (CoAuthorship(X, Y)) >> [co_authorshiplink(X,Y), netty()]
#        netty() / (Affiliation(X, Y)) >> [affiliationlink(X,Y), netty()]
#        netty() / (TopAuthorship(X, Y)) >> [topauthorlink(X,Y), netty()]
#        netty() / (Selectionship(X, Y)) >> [selectforlink(X,Y), netty()]
#        newlink() >> [new_affiliation()]
        
        pubby(X) >> [DesireGoalFor(X)]        
        
#        SelectUniversity(X) / (Selectionship(S,U) & CoAuthorship(Z, Y) & TopAuthorship(Y, X) & Affiliation(Z, U)) >> [show_line("Indirect match found at ",U,".\n"), -CoAuthorship(Z, Y), +AcceptOffer(S,X,U), SelectUniversity(X)]
#        DesireGoalFor(X) / (Selectionship(S,U) & CoAuthorship(Z, Y) & TopAuthorship(Y, X) & Affiliation(Z, U)) >> [show_line("Indirect match found at ",U,".\n"), -CoAuthorship(Z, Y), +coauthorIndirect(Z, Y,X), +AcceptOffer(S,X,U), DesireGoalFor(X)]
#        DesireGoalFor(X) / (Selectionship(S,U) & CoAuthorship(Z, Y) & TopAuthorship(Y, X) & Affiliation(Z, U)) >> [show_line("Indirect match found at ",U,".\n"), -CoAuthorship(Z, Y), +coauthorIndirect(Z, Y,X), +AcceptOffer(S,X,U), DesireGoalFor(X)]
        DesireGoalFor(X) / (Selectionship(S,U) & CoAuthorship(Z, Y) & TopAuthorship(Y, X) & Affiliation(Z, U)) >> [show_line("Indirect match found at ",U,".\n"), -CoAuthorship(Z, Y), +coauthorIndirect(Z, U,Y,X), +AcceptOffer(S,X,U), DesireGoalFor(X)]

        DesireGoalFor(X) / (Selectionship(S,U) & TopAuthorship(Y, X) & Affiliation(Y, U)) >> [show_line("Direct match found at ",U,".\n"), -TopAuthorship(Y, X), +ProposeCoauthorship(Y, X), +AcceptOffer(S,X,U), DesireGoalFor(X)]


        +coauthorIndirect(X,U,Z, Y) >> [show_line(X," at ", U, " is co-author with ",Z,", a top-author in the field of ",Y,".\n")]
        +ProposeCoauthorship(X,Y) >> [show_line("Propose co-authorship with ",X," as top-author in the field of ",Y,".\n")]
        +AcceptOffer(S,X,U) >> [show_line(S," should accept offer from University ",U," with co-authors of top-authors in field of ",X,".\n"),-TRIPLE(S, "hasAffiliationWith", U), +Affiliation(S,U), new_affiliation(S,U), turn()]


# for i in range(len(agents)):
#   instance = globals()[agents[i]]()
#    instance.start()

main().start()