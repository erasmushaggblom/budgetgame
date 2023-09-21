import pygame
import random
import asyncio
from urllib import request, parse
import json

class BudgetGame(): #create class for the game; class includes internal variables that are tracked throughout the game
    def __init__(self):
        pygame.init()
        self.satisfaction_standard_high = 90
        self.satisfaction_standard_low = 50
        self.performance_standard_high = 90
        self.performance_standard_low = 50
        self.stress_standard_high = 70
        self.stress_standard_low = 20
        self.learning_standard_high = 90
        self.learning_standard_low = 50
        self.first_time = True  
        self.click_summary = True #the choice to use clicks instead of time to advance the school summary screen
        self.agency_count = 0
        self.caption1 = False
        self.caption2 = False
        self.caption3 = False
        self.caption4 = False
        self.caption5 = False
        self.caption6 = False
        self.caption7 = True
        self.caption8 = False
        self.roundinterval = 0
        self.summaryinterval = 10
        self.roundtimer = 300
        self.roundtime = 5
        self.clock = pygame.time.Clock()
        self.time = 0
        self.intervaltime = 0
        self.window_height = 720
        self.window_width = 1080
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        self.agency_labels = []
        self.agencies = []
        self.agency_stats = {} #monitors the budget, staff and functional equipment for each agency
        self.staff_stats = {} #monitors the staff happiness etc for each agency
        self.student_stats = {} #monitors the student satisfaction, learning outcomes etc for each agency
        self.budget_standard = 15000
        self.total_budget = self.budget_standard #initial budget set to 10000 euros
        self.menu_buttons = [] #buttons for the agency menu
        self.budget_options = {} #budget action options
        self.agency_feedback = {} #player feedback in the agencies
        self.events = {} #dictionary containing possible events
        self.radius = 49.5 #radius of agency buttons
        self.radius2 = 30 #radius of round selection
        self.board = [] #list containing separated elements of the game board
        self.arial = pygame.font.SysFont("bahnschrift", 16) #fonts for text shown to players, four fonts in use currently
        self.arial2 = pygame.font.SysFont("bahnschrift", 14)
        self.calibri = pygame.font.SysFont("calibri", 13)
        self.calibri2 = pygame.font.SysFont("calibri", 10)
        self.agency = "null" #base agency, used if none is selected to avoid errors
        self.agency_stats["null"] = "null" #base agency stats
        self.click_counter = 0 #tracks how many times the player has clicked
        self.agency_events = {} #dictionary containing events that have occurred for each agency
        self.clicked_anything = False #checks if something has been clicked
        self.participant = 1 #participant number
        self.main_menu_action = False #checks if main menu button has been clicked
        self.scripts = {} #dictionary containing the scripts chosen in a given round
        self.agency_status = {} #dictionary checking for input-based events
        self.roundstandard = 10 #how many rounds are played
        self.round_number = 1 #tracks the number of rounds
        self.roundclicked = 2 #tracks the number of times the player has chosen to advance the round
        self.script_events = [0, 0] #list of events that have occurred in the current round
        self.score = 0 #player score
        self.score_last = 0
        self.score_total = [0]
        self.agency_scores = {} #score for each agency
        self.agency_round_results = {}
        self.intro_style = "text" #choose "video" or "text"
        self.start = True #condition for showing the instruction screen first
        self.agencynames = []
        self.endrankings = False
        self.insummary = False
        self.instruction_2 = False
        self.information = False
        self.summary = False
        self.agency_summary = False
        self.agency_summary_2 = False
        self.show_agencies = False
        self.show_effects = False
        self.show_event_effects = False
        self.show_main_menu = False
        self.show_feedback = False
        self.roundover = False
        self.historical = False
        self.history_information = False
        self.rankings = False
        self.roundsummary1 = False
        self.roundsummary2 = False
        self.roundsummary3 = False
        self.roundsummary4 = False
        self.roundsummary5 = False
        self.roundsummary6 = False
        self.roundsummary7 = False
        self.show_budget_options = False
        self.postgame = False
        self.vidintro = True
        self.show_vid = True
        self.show_rankings = False
        self.choice = "null"
        self.roundchoice = "null"
        self.effects_choice = "null"
        self.button_effects = {}
        self.black = (0, 0, 0, 255)
        self.gold = (255, 215, 0, 255)
        self.tan = (210, 180, 140, 255)
        self.orange = (255, 165, 0, 255)
        self.crimson = (220, 20, 60, 255)
        self.lightslateblue = (132, 112, 255, 255)
        self.cadetblue2 = (142, 229, 238, 255)
        self.dodgerblue = (30, 144, 255, 255)
        self.lightsteelblue = (176, 196, 222, 255)
        self.navyblue = (0, 0, 128, 255)
        self.cornflowerblue = (100, 149, 237, 255)
        self.royalblue3 = (58, 95, 205, 255)
        self.tomato = (255, 99, 71, 255)
        self.forestgreen = (34, 139, 34, 255)
        self.green = (0, 255, 0, 255)
        self.darkolivegreen3 = (162, 205, 90, 255)
        self.gainsboro = (220, 220, 220, 255)
        self.white = (255, 255, 255, 255)
        self.purple = (160, 32, 240, 255)
        self.schoolranking = [0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ]
        self.historical_rankings = []
        self.ranking_schools = ["School 1", "School 2", "School 3", "School 4", "School 5", "School 6", "School 7", "School 8", "School 9", "School 10", "School 11", "School 12", "School 13", "School 14", "School 15", "School 16", "School 17", "School 18", "School 19", "School 20"]
        self.possible_events = ["Talent show", "Sports fair", "Science fair", "Basketball game", "Football game", "Cook-off", "Bake sale", "Quiz", "School exchange", "Writing workshop", "Dance performance", "Musical performance", "Holiday celebration", "Independence party", "Museum visit", "Treasure hunt", "Charity run", "School party"] #names for possible events

    def baseconditions(self):
        if self.first_time == True:
            self.roundtime = self.time
        self.agency = "null"
        self.roundchoice = "null"
        self.insummary = False
        self.endrankings = False
        self.start = False #condition for showing the instruction screen first
        self.instruction_2 = False
        self.information = False
        self.summary = False
        self.agency_summary = False
        self.agency_summary_2 = False
        self.show_agencies = True
        self.show_effects = False
        self.show_event_effects = False
        self.show_main_menu = True
        self.show_feedback = True
        self.roundover = False
        self.historical = False
        self.history_information = False
        self.roundsummary1 = False
        self.roundsummary2 = False
        self.roundsummary3 = False
        self.roundsummary4 = False
        self.roundsummary5 = False
        self.roundsummary6 = False
        self.roundsummary7 = False
        self.show_budget_options = False
        self.postgame = False
        self.show_vid = False
        self.main_menu_action = False
        self.caption1 = True
        self.caption2 = False
        self.caption3 = False
        self.caption4 = False
        self.caption5 = False
        self.caption6 = False
        self.caption7 = False
        self.caption8 = False
        self.first_time = False
        self.rankings = False
        self.show_rankings = False


    def baseconditions_video(self):
        if self.first_time == True:
            self.roundtime = self.time
        self.insummary = False
        self.start = False #condition for showing the instruction screen first
        self.instruction_2 = False
        self.information = False
        self.summary = False
        self.agency_summary = False
        self.agency_summary_2 = False
        self.show_agencies = False
        self.show_effects = False
        self.show_event_effects = False
        self.show_main_menu = False
        self.show_feedback = False
        self.roundover = False
        self.roundsummary1 = False
        self.roundsummary2 = False
        self.roundsummary3 = False
        self.roundsummary4 = False
        self.roundsummary5 = False
        self.roundsummary6 = False
        self.roundsummary7 = False
        self.show_budget_options = False
        self.postgame = False
        self.show_vid = False
        self.main_menu_action = False
        self.caption1 = False
        self.caption2 = False
        self.caption3 = False
        self.caption4 = False
        self.caption5 = False
        self.caption6 = False
        self.caption7 = False
        self.caption8 = False
        self.first_time = False



    def base_scripts(self): #scripts set to none
        self.scripts[0] = []
        self.scripts[1] = []
    
    def choose_random_scripts(self, amount: int): #chooses random events at the end of the round
        list1 = []
        list2 = []
        while True:
            number = random.randrange(0, 29)
            if number not in list1:
                list1.append(number)
            if len(list1) == amount:
                break
        for i in list1:
            list2.append(self.scripts[1][i])
        return list2

    def run_random_scripts(self): #runs chosen random scripts
        list1 = []
        for e in self.agencies:
            agency = e[0]
            scripts = self.choose_random_scripts(3)
            for i in scripts:
                effects = []
                for u in i:
                    for q in i[u]:
                        singleeffects = self.execute_script(q, agency)
                        effects.append(singleeffects)
                    list1.append((agency, i[u][0]))
                    self.agency_events[agency].append((u, self.round_number, effects, 1))
        self.script_events[1] = list1

    def run_input_scripts(self): #runs input scripts based on given conditions
        list1 = []
        for e in self.agencies:
            agency = e[0]
            self.check_input_scripts(agency)
            for i in self.agency_status[agency]:
                for u in i:
                    if u != False:
                        for e in self.scripts[0]:
                            for t in e:
                                if u == t:
                                    effects = []
                                    for q in e[u]:
                                        singleeffects = self.execute_script(q, agency)
                                        effects.append(singleeffects)
                                    list1.append((agency, e[u][0]))
                                    self.agency_events[agency].append((u, self.round_number, effects, 0))

        self.script_events[0] = list1

        
    def advance_game_round(self): #advances to the next round of the game
        if self.roundclicked > self.round_number:
            self.add_to_score()
            self.run_random_scripts()
            self.run_input_scripts()
            self.round_number += 1
            for i in self.agencies:
                self.staff_stats[i[0]][0] = self.staff_stats[i[0]][3] #change current values to predicted values
                self.staff_stats[i[0]][1] = self.staff_stats[i[0]][4]
                self.staff_stats[i[0]][2] = self.staff_stats[i[0]][5]
                self.student_stats[i[0]][0] = self.student_stats[i[0]][6]
                self.student_stats[i[0]][1] = self.student_stats[i[0]][7]
                self.student_stats[i[0]][2] = self.student_stats[i[0]][8]
                self.student_stats[i[0]][3] = self.student_stats[i[0]][9]
                self.student_stats[i[0]][4] = self.student_stats[i[0]][10]
                self.student_stats[i[0]][5] = self.student_stats[i[0]][11]
            self.adjust_total_budget(self.budget_standard)
            for i in self.agencies:
                self.adjust_agency_budget(i[0], 1000)
            self.adjust_ranking()
            self.historical_rankings.append(self.schoolranking)




    def check_score(self): #checks the current player score
        list1 = []
        numbers = []
        for i in self.student_stats:
            numbers.append(self.student_stats[i][6])
            numbers.append(self.student_stats[i][7])
            numbers.append(self.student_stats[i][8])
            numbers.append(self.student_stats[i][9])
            numbers.append(self.student_stats[i][10])
            numbers.append(self.staff_stats[i][3])
            numbers.append(self.staff_stats[i][4])
            number = int(sum(numbers)/len(numbers))
            self.agency_scores[i] = number
            list1.append(number)
        self.score = int((sum(list1))/len(self.agencies))

        if self.round_number == 1:
            self.score_total = [self.score]

    def add_to_score(self):
        temp_scores = []
        self.score_last = self.score
        for i in self.agency_scores:
            temp_scores.append((i, self.agency_scores[i]))
        self.agency_round_results[self.round_number] = temp_scores

        if self.round_number >1:
            self.score_total.append(self.score)

    def add_script(self, script: list): #adds a script to the list of possible ones
        key = script[0]
        key2 = script[1]
        add = script[2:]
        dict1 = {}
        dict1[key2] = add
        self.scripts[key].append(dict1)
    
    def create_scripts(self): #creates the input and random scripts; these can be manually adjusted, as can their effects
        self.add_script([0, "poor learning results (math)", "The students had poor learning results in math", ("decrease agency budget", 200), ("decrease staff satisfaction", 0), ("decrease staff performance", 0), ("increase staff stress",0 ), ("decrease staff", 1), ("cancel event", 1), ("increase equipment", 500), ("increase student stress", 0)])
        self.add_script([0, "poor learning results (reading)", "The students had poor learning results in reading", ("decrease agency budget", 200), ("decrease staff satisfaction", 0), ("decrease staff performance", 0), ("increase staff stress", 0), ("decrease staff", 1), ("cancel event", 1), ("increase equipment", 500), ("increase student stress", 0)])
        self.add_script([0, "poor learning results (science)", "The students had poor learning results in science", ("decrease agency budget", 200), ("decrease staff satisfaction", 0), ("decrease staff performance", 0), ("increase staff stress", 0), ("decrease staff", 1), ("cancel event", 1), ("increase equipment", 500), ("increase student stress", 0)])
        self.add_script([0, "poor learning results (overall)", "The students had poor overall learning results", ("decrease agency budget", 800), ("decrease staff satisfaction", 0), ("decrease staff performance", 0), ("increase staff stress", 0), ("decrease staff", 1), ("cancel event", 1), ("increase equipment", 1500), ("increase student stress", 0)])
        self.add_script([0, "not within budget", "The school was not within its budget", ("increase staff stress", 0), ("increase student stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease staff performance", 0)])
        self.add_script([0, "within budget", "The school was within its budget", ("decrease staff stress", 0), ("decrease student stress", 0), ("increase staff satisfaction", 0), ("increase student satisfaction", 0), ("increase staff performance", 0)])
        self.add_script([0, "good learning results (math)", "The students had good learning results in math", ("increase agency budget", 200), ("increase staff satisfaction", 0), ("increase staff performance", 0), ("decrease staff stress", 0), ("increase staff", 1), ("plan event", 1), ("decrease equipment", 500), ("decrease student stress", 0)])
        self.add_script([0, "good learning results (reading)", "The students had good learning results in reading ", ("increase agency budget", 200), ("increase staff satisfaction", 0), ("increase staff performance", 0), ("decrease staff stress", 0), ("increase staff", 1), ("plan event", 1), ("decrease equipment", 500), ("decrease student stress", 0)])
        self.add_script([0, "good learning results (science)", "The students had good learning results in science", ("increase agency budget", 200), ("increase staff satisfaction", 0), ("increase staff performance", 0), ("decrease staff stress", 0), ("increase staff", 1), ("plan event", 1), ("decrease equipment", 500), ("decrease student stress", 0)])
        self.add_script([0, "good learning results (overall)", "The students had good overall learning results", ("increase agency budget", 800), ("increase staff satisfaction", 0), ("increase staff performance", 0), ("decrease staff stress", 0), ("increase staff", 1), ("plan event", 1), ("decrease equipment", 1500), ("decrease student stress", 0)])
        self.add_script([0, "high staff stress", "The staff had high stress", ("decrease staff satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([0, "low staff stress", "The staff had low stress", ("increase staff satisfaction", 0), ("decrease staff stress", 0), ("increase staff performance", 0), ("increase staff", 5), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0)])
        self.add_script([0, "high staff satisfaction", "The staff had high satisfaction", ("increase staff satisfaction", 0), ("decrease staff stress", 0), ("increase staff performance", 0), ("increase staff", 5), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0)])
        self.add_script([0, "low staff performance", "The staff had low performance", ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([0, "high staff performance", "The staff had high performance", ("decrease staff stress", 0), ("increase staff satisfaction", 0), ("increase staff", 5), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0)])
        self.add_script([0, "high student satisfaction", "The students had high satisfaction", ("decrease student stress", 0), ("increase student satisfaction", 0), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0)])
        self.add_script([0, "low student stress", "The students had low stress", ("decrease student stress", 0), ("increase student satisfaction", 0), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0)])
        self.add_script([0, "high student stress", "The students had high stress", ("increase student stress", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([0, "low student satisfaction", "The students had low satisfaction", ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([0, "low staff satisfaction", "The staff had low satisfaction", ("increase student stress", 0), ("decrease student satisfaction", 0), ("decrease staff", 5), ("decrease staff performance", 0)])
        self.add_script([0, "not enough events", "There were no events organised at the school", ("decrease student satisfaction", 0), ("increase student stress", 0), ("decrease staff stress", 0), ("decrease staff satisfaction", 0)])
        self.add_script([0, "enough events", "There were enough events organised at the school", ("increase student satisfaction", 0), ("decrease student stress", 0), ("increase staff stress", 0), ("increase staff satisfaction", 0)])
        self.add_script([0, "understaffed", "The school was understaffed", ("decrease student satisfaction", 0), ("increase student stress", 0), ("decrease staff stress", 0), ("decrease staff satisfaction", 0)])
        self.add_script([0, "staffed", "The school had enough staff", ("increase student satisfaction", 0), ("decrease student stress", 0), ("increase staff stress", 0), ("increase staff satisfaction", 0)])
        self.add_script([0, "insufficient equipment", "The school did not have enough equipment", ("decrease staff satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0), ("decrease student satisfaction", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([0, "enough equipment", "The school had enough equipment", ("increase staff satisfaction", 0), ("decrease staff stress", 0), ("increase staff performance", 0), ("increase student satisfaction", 0), ("increase staff", 5), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0)])
        self.add_script([1, "misuse of funds", "The school leadership misused school funds", ("decrease agency budget", 5000), ("decrease staff satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0), ("decrease student satisfaction", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "improper conduct", "An employee behaved inappropriately", ("decrease agency budget", 5000), ("decrease staff satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0), ("decrease student satisfaction", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "theft (outside)", "A thief broke into the school and stole valuables", ("decrease agency budget", 5000), ("decrease staff satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0), ("decrease student satisfaction", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "theft (inside)", "An employee stole valuables", ("decrease agency budget", 5000), ("decrease staff satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0), ("decrease student satisfaction", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "bullying (students)", "A student complained about bullying", ("increase student stress", 0), ("increase student stress", 0), ("decrease student satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase staff stress", 0)])
        self.add_script([1, "bullying (staff)", "A staff member complained about bullying", ("increase staff stress", 0), ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0)])
        self.add_script([1, "alumni grant", "A school alumni made a donation", ("increase agency budget", 10000), ("increase staff performance", 0), ("increase staff satisfaction", 0), ("decrease staff stress", 0)])
        self.add_script([1, "alumni complaint", "An alumni complained about school results", ("decrease staff performance", 0), ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0)])
        self.add_script([1, "flood", "The school was flooded unexpectedly", ("decrease agency budget", 5000), ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("decrease agency equipment", 2000)])
        self.add_script([1, "mold", "Mold was found in the school walls", ("decrease agency budget", 5000), ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0)])
        self.add_script([1, "broken windows", "The school windows were broken", ("decrease agency budget", 1000), ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("increase student stress", 0), ("decrease agency equipment", 1000)])
        self.add_script([1, "illness (flu)", "A flu epidemic went through the school", ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "illness (noro)", "A norovirus epidemic went through the school", ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "student injury (limb)", "A student broke their arm", ("increase staff stress", 0), ("increase student stress", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([1, "student injury (concussion)", "A student got a concussion", ("increase staff stress", 0), ("increase student stress", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([1, "staff injury (limb)", "A staff member broke their arm", ("increase staff stress", 0), ("increase student stress", 0), ("decrease staff performance", 0), ("decrease staff satisfaction", 0)])
        self.add_script([1, "staff injury (concussion)", "A staff member got a concussion", ("increase staff stress", 0), ("increase student stress", 0), ("decrease staff performance", 0), ("decrease staff satisfaction", 0)])
        self.add_script([1, "outbreak (lice)", "A lice outbreak occurred at the school", ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "earthquake", "An earthquake damaged the school building", ("decrease agency budget", 5000), ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("decrease agency equipment", 2000)])
        self.add_script([1, "equipment breakage", "Some equipment broke during a lesson", ("increase staff stress", 0), ("increase student stress", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("decrease staff performance", 0)])
        self.add_script([1, "equipment donation", "An alumni donated additional equipment", ("decrease staff stress", 0), ("decrease student stress", 0), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0), ("increase staff performance", 0)])
        self.add_script([1, "external evaluation", "An external evaluation of the school was conducted", ("increase staff stress", 0), ("increase staff performance", 0), ("increase student stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0)])
        self.add_script([1, "inter-school competition", "A sports competition with another school was held", ("decrease agency budget", 1000), ("increase staff stress", 0), ("decrease student stress", 0), ("increase student satisfaction", 0), ("increase staff satisfaction", 0)])
        self.add_script([1, "state grants", "The state gave the school an educational grant", ("increase agency budget", 5000), ("increase staff satisfaction", 0), ("decrease staff stress", 0), ("increase staff performance", 0)])
        self.add_script([1, "fundraiser (bake sale)", "A bake sale was organised at the school", ("increase agency budget", 2000), ("increase student satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0)])
        self.add_script([1, "fundraiser (sporting event)", "A sporting event was organised at the school", ("increase agency budget", 2000), ("increase student satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0)])
        self.add_script([1, "fundraiser (auction)", "An auction was organised at the school", ("increase agency budget", 2000), ("increase student satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0)])
        self.add_script([1, "pro bono event", "An alumni organised a recreational event", ("increase agency budget", 2000), ("increase student satisfaction", 0), ("decrease staff stress", 0), ("decrease staff performance", 0), ("increase staff satisfaction", 0)])
        self.add_script([1, "outside event cancellation", "State authorities cancelled a recreational event", ("decrease student satisfaction", 0), ("decrease staff stress", 0), ("decrease staff performance", 0), ("decrease staff satisfaction", 0)])

    def script_effects(self):
        rect1 = self.draw_exit("previous")
        x = 100
        y = 50
        text = self.arial.render(f"{self.effects_choice[0]}!", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"This had the following effects:", True, self.black)
        self.window.blit(text, (x+10, y))
        y += 25
        for i in self.effects_choice[1]:
            text = self.arial.render(f"{i}", True, self.black)
            self.window.blit(text, (x+10, y))
            y += 25

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    self.summary_click_forward(3, rect1)

            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit

    def execute_script(self, script, agency): #executes a given script
        effects = []
        if script[0] == "decrease agency budget":
            number = script[1]
            self.adjust_agency_budget(agency, -number)
            effects.append(f"The school budget was decreased by {number}")
        if script[0] == "increase agency budget":
            number = script[1]
            self.adjust_agency_budget(agency, number)
            effects.append(f"The school budget for was increased by {number}")
        if script[0] == "decrease staff":
            number = script[1]
            self.adjust_agency_staff(agency, -number)
            effects.append(f"The number of staff declined by {number}")
        if script[0] == "increase staff":
            number = script[1]
            self.adjust_agency_staff(agency, number)
            effects.append(f"The number of staff increased by {number}")
        if script[0] == "plan event":
            number = script[1]
            self.create_agency_event(agency, number, 0)
            effects.append(f"A new event was planned")
        if script[0] == "cancel event":
            number = script[1]
            self.create_agency_event(agency, -number, 0)
            effects.append(f"An event was cancelled")
        if script[0] == "increase equipment":
            amount = script[1]
            self.adjust_agency_equipment(agency, amount)
            effects.append(f"The amount of available equipment increased by {amount}")
        if script[0] == "decrease equipment":
            amount = script[1]
            self.adjust_agency_equipment(agency, -amount)
            effects.append(f"The amount of available equipment decreased by {amount}")
        if script[0] == "decrease staff satisfaction":
            self.adjust_soft_stats("staff satisfaction", agency, -1)
            effects.append(f"Staff satisfaction decreased")
        if script[0] == "increase staff satisfaction":
            self.adjust_soft_stats("staff satisfaction", agency, 1)
            effects.append(f"Staff satisfaction increased")
        if script[0] == "decrease student satisfaction":
            self.adjust_soft_stats("student satisfaction", agency, -1)
            effects.append(f"Student satisfaction decreased")
        if script[0] == "increase student satisfaction":
            self.adjust_soft_stats("student satisfaction", agency, 1)
            effects.append(f"Student satisfaction increased")
        if script[0] == "decrease staff stress":
            self.adjust_soft_stats("staff stress", agency, -1)
            effects.append(f"Staff stress decreased")
        if script[0] == "increase staff stress":
            self.adjust_soft_stats("staff stress", agency, 1)
            effects.append(f"Staff stress increased")
        if script[0] == "decrease student stress":
            self.adjust_soft_stats("student stress", agency, -1)
            effects.append(f"Student stress decreased")
        if script[0] == "increase student stress":
            self.adjust_soft_stats("student stress", agency, 1)
            effects.append(f"Student stress increased")
        if script[0] == "increase student reading":
            self.adjust_soft_stats("student reading", agency, 1)
            effects.append(f"Student reading performance increased")
        if script[0] == "increase student math":
            self.adjust_soft_stats("student math", agency, 1)
            effects.append(f"Student math performance increased")
        if script[0] == "increase student science":
            self.adjust_soft_stats("student science", agency, 1)
            effects.append(f"Student science performance increased")
        if script[0] == "decrease student reading":
            self.adjust_soft_stats("student reading", agency, -1)
            effects.append(f"Student reading performance decreased")
        if script[0] == "decrease student math":
            self.adjust_soft_stats("student math", agency, -1)
            effects.append(f"Student math performance decreased")
        if script[0] == "decrease student science":
            self.adjust_soft_stats("student science", agency, -1)
            effects.append(f"Student science performance decreased")
        if script[0] == "decrease staff performance":
            self.adjust_soft_stats("staff performance", agency, -1)
            effects.append(f"Staff performance decreased")
        if script[0] == "increase staff performance":
            self.adjust_soft_stats("staff performance", agency, 1)
            effects.append(f"Staff performance increased")
        if effects == []:
            effects = script
        return effects

    def check_input_scripts(self, agency): #checks for input conditions to choose scripts
        stats = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

        if self.staff_stats[agency][3] < self.satisfaction_standard_low:
            stats[0] = "low staff satisfaction" #low_staff_satisfaction
        else:
            stats[0] = False
        if self.staff_stats[agency][4] < self.performance_standard_low:
            stats[1] = "low staff performance" #low_staff_performance
        else:
            stats[1] = False
        if self.staff_stats[agency][5] < self.stress_standard_low: #low_staff_stress
            stats[2] = "low staff stress"
        else:
            stats[2] = False
        if self.staff_stats[agency][3] > self.satisfaction_standard_high: #high_staff_satisfaction
            stats[3] = "high staff satisfaction"
        else:
            stats[3] = False
        if self.staff_stats[agency][4] > self.performance_standard_high: #high_staff_performance
            stats[4] = "high staff performance"
        else:
            stats[4] = False
        if self.staff_stats[agency][5] > self.stress_standard_high: #high_staff_stress
            stats[5] = "high staff stress"
        else:
            stats[5] = False
        if self.student_stats[agency][6] < self.satisfaction_standard_low:
            stats[6] = "low student satisfaction" #low_student_satisfaction
        else:
            stats[6] = False
        if self.student_stats[agency][7] < self.learning_standard_low:
            stats[7] = "poor learning results (reading)" #low_student_reading
        else:
            stats[7] = False
        if self.student_stats[agency][8] < self.learning_standard_low: #low_student_math
            stats[8] = "poor learning results (math)"
        else:
            stats[8] = False
        if self.student_stats[agency][9] < self.learning_standard_low:
            stats[9] = "poor learning results (science)" #low_student_science
        else:
            stats[9] = False
        if self.student_stats[agency][10] < self.learning_standard_low:
            stats[10] = "poor learning results (overall)" #low_student_overall
        else:
            stats[10] = False
        if self.student_stats[agency][11] < self.stress_standard_low:
            stats[11] = "low student stress" #low_student_stress
        else:
            stats[11] = False
        if self.student_stats[agency][6] > self.satisfaction_standard_high:
            stats[12] = "high student satisfaction" #high_student_satisfaction
        else:
            stats[12] = False
        if self.student_stats[agency][7] > self.learning_standard_high:
            stats[13] = "good learning results (reading)" #high_student_reading
        else:
            stats[13] = False
        if self.student_stats[agency][8] > self.learning_standard_high: #high_student_math
            stats[14] = "good learning results (math)"
        else:
            stats[14] = False
        if self.student_stats[agency][9] > self.learning_standard_high:
            stats[15] = "good learning results (science)" #high_student_science
        else:
            stats[15] = False
        if self.student_stats[agency][10] > self.learning_standard_high:
            stats[16] = "good learning results (overall)" #high_student_overall
        else:
            stats[16] = False
        if self.student_stats[agency][11] < self.stress_standard_high:
            stats[17] = "high student stress" #high_student_stress
        else:
            stats[17] = False
        if self.agency_stats[agency][5] == "Sufficient equipment":
            stats[18] = "enough equipment" #sufficient_equipment
        else:
            stats[18] = False
        if self.agency_stats[agency][5] == "Equipment shortage":
            stats[19] = "insufficient equipment" #insufficient_equipment
        else:
            stats[19] = False
        if self.agency_stats[agency][6] == "No events planned":
            stats[20] = "not enough events" #no_events
        else:
            stats[20] = False
        if self.agency_stats[agency][6] == "Events planned":
            stats[21] = "enough events" #enough_events
        else:
            stats[21] = False
        if self.agency_stats[agency][7] == "Within budget":
            stats[22] = "within budget" #within_budget
        else:
            stats[22] = False
        if self.agency_stats[agency][7] == "Under budget":
            stats[23] = "not within budget" #outside_budget
        else:
            stats[23] = False
        if self.agency_stats[agency][7] == "Understaffed":
            stats[24] = "understaffed"
        else:
            stats[24] = False
        if self.agency_stats[agency][7] == "Staffed":
            stats[25] = "staffed"
        else:
            stats[25] = False
        self.agency_status[agency] = [stats]


    def increase_click_counter(self): #tracks how many inputs have been made by the player
        mouse_presses = pygame.mouse.get_pressed()
        if mouse_presses[0]:
            self.click_counter += 1

    def increase_round_counter(self): #increases round coounter
        self.roundclicked += 1

    def check_participant_number(self): #checks the number of participants
        count = 0
        words2 = []
        try:
            with open("output_file.txt") as my_file:
                for i in my_file:
                    text = i
                    count += 1
                    if count == 1:
                        break
        except FileNotFoundError:
            return
        words = text.split(" ")
        for i in words:
            words2.append(i.strip())
        participant_number = int(words2[1])
        if self.participant <= participant_number:
            participant_number += 1
            self.participant = participant_number

    def rename_output(self): #renames the output file to an unique name
        filename = f"participant_{self.participant}"
        lines = []
        with open("output_file.txt") as original_file:
            for i in original_file:
                lines.append(i)
        with open(f"{filename}.txt", "w") as new_file:
            for i in lines:
                new_file.write(i)

    def create_output_file(self): #creates the output file, currently as a .txt file
        with open("output_file.txt", "w") as my_file:
            my_file.write(f"Participant {self.participant}")
            my_file.write("\n")

    def add_final_output(self): #adds final notes to the output file
        with open("output_file.txt", "a") as my_file:
            my_file.write(f"total number of clicks: {self.click_counter}")
            my_file.write("\n")

    def post_output(self):
        #POST data string to `url`, return page and headers

        headers={'Content-Type':'application/json'}

        url = "https://europe-west1-budgetgame.cloudfunctions.net/budgetgame_api"

        data = ""

        with open("output_file.txt", "r") as my_file:
            for i in my_file:
                data += i
        # if data is not in bytes, convert to it to utf-8 bytes
        bindata = data if type(data) == bytes else data.encode('utf-8')

        # need Request to pass headers
        req = request.Request(url, bindata, headers)
        resp = request.urlopen(req)


        return resp.read(), resp.getheaders()

    def add_to_output(self, add: str): #records player inputs in the output file
        lines = 0
        with open("output_file.txt", "r") as my_file:
            for i in my_file:
                lines += 1
        if self.click_counter >= lines:
            with open("output_file.txt", "a") as my_file:
                my_file.write("game state: ")
                my_file.write(f"agency stats: {str(self.agency_stats)}")
                my_file.write(f"staff stats: {str(self.staff_stats)}")
                my_file.write(f"student stats: {str(self.student_stats)}")
                my_file.write(f"total budget: {str(self.total_budget)}")
                my_file.write(add)
                my_file.write("\n")

    def add_agency(self, agency: str, initial_budget: float, initial_staff: int, initial_equipment: float, initial_events, staff_status, equipment_status, event_status, budget_status): #add different agencies for budgeting; the game currently allows for up to 7 options at a time for graphical reasons. the input includes an initial budget
        self.agencies.append((agency, initial_budget))
        self.agency_stats[agency] = [initial_budget, initial_staff, initial_equipment, initial_events, staff_status, equipment_status, event_status, budget_status, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        lower_bound = 1
        upper_bound = 7
        count = 0
        self.events[agency] = [1, 2, 3, 4]
        for i in range(4):
            if count < initial_events:
                index = random.randrange(0, 17)
                self.events[agency][i] = (self.possible_events[index], random.randrange(lower_bound, upper_bound))
            else:
                self.events[agency][i] = ("null", random.randrange(lower_bound, upper_bound))
            lower_bound += 7
            upper_bound += 7
            count += 1
        self.budget_options[agency] = []
        self.agency_feedback[agency] = []
        self.adjust_total_budget(-initial_budget) #when adding a new agency, the initial budget is subtracted form the total budget
        self.agency_count += 1
        self.agencynames.append(agency)

    def create_agencies(self): #creates the agencies to be used; the name can be edited to change the labels in the game. With longer names the label code may need to be adjusted. The current form of the code supports up to seven different agencies; more can be added if required but this would require more significant changes to the source code
        self.add_agency("Leaf High", 1000, 0, 1000, 0, "null", "null", "null", "null")
        self.add_agency("Robin High", -2000, 5, 200, 1, "null", "null", "null", "null")
        self.add_agency("Valley Primary", -4000, 10, -300, 2, "null", "null", "null", "null")
        self.add_agency("Seal High", 6000, -5, 400, 3, "null", "null", "null", "null")
        #self.add_agency("West Elementary", -5000, 15, 3000, 0, "null", "null", "null", "null")
        #self.add_agency("Foothill Private", 0, 20, -5000, 3, "null", "null", "null", "null")
        #self.add_agency("Johns Elementary", 3000, 35, 600, 4, "null", "null", "null", "null")
        for i in self.agencies:
            self.agency_events[i[0]] = []

    def create_ranking(self):
        agencies = []
        for i in self.agencies:
            agencies.append(i[0])
        for i in self.ranking_schools:
            if len(agencies) >= 20:
                break
            agencies.append(i)
        self.ranking_schools = agencies
        self.adjust_ranking()


    def adjust_ranking(self):
        agencies = []
        ranking_scores = []
        rangelimit = 0
        for i in self.agencies:
            agencies.append(i[0])
        for i in self.ranking_schools:
            if i in agencies:
                ranking_scores.append((self.agency_scores[i], i))
            if i not in agencies:
                score = random.randrange(rangelimit, 100)
                rangelimit += 5
                ranking_scores.append((score, i))
        self.schoolranking = sorted(ranking_scores)

    def create_agency_stats(self): #creates monitors for agency stats
        for i in self.agencies:
            number = random.randrange(0, 100) #staff satisfaction
            number2 = random.randrange(0, 100) #staff performance
            number3 = random.randrange(0, 100) #staff stress
            self.staff_stats[i[0]] = [number, number2, number3, number, number2, number3] #staff satisfaction, staff performance, staff stress levels followed by predicted values
            number = random.randrange(0, 100) #student satisfaction
            number2 = random.randrange(25, 100) #student reading
            number3 = random.randrange(25, 100) #student math
            number4 = random.randrange(25, 100) #student science
            number5 = int((number2 + number3 + number4)/3) #student overall
            number6 = random.randrange(0, 100) #student stress
            self.student_stats[i[0]] = [number, number2, number3, number4, number5, number6, number, number2, number3, number4, number5, number6] #student satisfaction, student performance (reading), student performance (mathematics), student performance (science), study results (index), student stress levels followed by predicted values
        self.check_status()




    def check_status(self): #checks whether there are issues in the agencies that need to be addressed

        for i in self.agency_stats:
            try:
                if self.agency_stats[i][0] < 0:
                    self.agency_stats[i][7] = "Under budget"
                else:
                    self.agency_stats[i][7] = "Within budget"
                if self.agency_stats[i][1] < 0:
                    self.agency_stats[i][4] = "Understaffed"
                else:
                    self.agency_stats[i][4] = "Staffed"
                if self.agency_stats[i][2] < 0:
                    self.agency_stats[i][5] = "Equipment shortage"
                else:
                    self.agency_stats[i][5] = "Sufficient equipment"
                if self.agency_stats[i][3] == 0:
                    self.agency_stats[i][6] = "No events planned"
                elif self.agency_stats[i][3] > 0:
                    self.agency_stats[i][6] = "Events planned"
                if self.staff_stats[i][3] <= self.satisfaction_standard_low:
                    self.agency_stats[i][8] = "low staff satisfaction" #low_staff_satisfaction
                elif self.staff_stats[i][3] >= self.satisfaction_standard_high:
                    self.agency_stats[i][8] = "high staff satisfaction" #low_staff_satisfaction
                else:
                    self.agency_stats[i][8] = False
                if self.staff_stats[i][4] <= self.performance_standard_low:
                    self.agency_stats[i][9] = "low staff performance" #low_staff_performance
                elif self.staff_stats[i][4] >= self.performance_standard_high:
                    self.agency_stats[i][9] = "high staff performance" #low_staff_performance
                else:
                    self.agency_stats[i][9] = False
                if self.staff_stats[i][5] >= self.stress_standard_high: #high_staff_stress
                    self.agency_stats[i][10] = "high staff stress"
                elif self.staff_stats[i][5] <= self.stress_standard_low: #high_staff_stress
                    self.agency_stats[i][10] = "low staff stress"
                else:
                    self.agency_stats[i][10] = False
                if self.student_stats[i][6] <= self.satisfaction_standard_low:
                    self.agency_stats[i][11] = "low student satisfaction" #low_student_satisfaction
                elif self.student_stats[i][6] >= self.satisfaction_standard_high:
                    self.agency_stats[i][11] = "high student satisfaction" #low_student_satisfaction
                else:
                    self.agency_stats[i][11] = False
                if self.student_stats[i][7] <= self.learning_standard_low:
                    self.agency_stats[i][12] = "poor learning results (reading)" #low_student_reading
                elif self.student_stats[i][7] >= self.learning_standard_high:
                    self.agency_stats[i][12] = "good learning results (reading)" #low_student_reading
                else:
                    self.agency_stats[i][12] = False
                if self.student_stats[i][8] <= self.learning_standard_low: #low_student_math
                    self.agency_stats[i][13] = "poor learning results (math)"
                elif self.student_stats[i][8] >= self.learning_standard_high: #low_student_math
                    self.agency_stats[i][13] = "good learning results (math)"
                else:
                    self.agency_stats[i][13] = False
                if self.student_stats[i][9] <= self.learning_standard_low:
                    self.agency_stats[i][14] = "poor learning results (science)" #low_student_science
                elif self.student_stats[i][9] >= self.learning_standard_high:
                    self.agency_stats[i][14] = "good learning results (science)" #low_student_science
                else:
                    self.agency_stats[i][14] = False
                if self.student_stats[i][10] <= self.learning_standard_low:
                    self.agency_stats[i][15] = "poor learning results (overall)" #low_student_overall
                elif self.student_stats[i][10] >= self.learning_standard_high:
                    self.agency_stats[i][15] = "good learning results (overall)" #low_student_overall
                else:
                    self.agency_stats[i][15] = False
                if self.student_stats[i][11] >= self.stress_standard_high:
                  self.agency_stats[i][16] = "high student stress" #high_student_stress
                elif self.student_stats[i][11] <= self.stress_standard_low:
                  self.agency_stats[i][16] = "low student stress" #high_student_stress
                else:
                    self.agency_stats[i][16] = False
            except TypeError:
                pass



    def add_budget_option(self, agency: str, option: str, cost: float): #add options for budget action the player can take; these can be individually designed per agency
        self.budget_options[agency].append((option, cost))

    def add_agency_feedback(self, agency: str, feedback: str): #adds the desired agency feedback monitors
        self.agency_feedback[agency].append((feedback))


    def create_budget_options(self): #adds the desired budget options through the function above
        for i in self.agencies:
            self.add_budget_option(i[0], "increase funding", 1000)
            self.add_budget_option(i[0], "decrease funding", -1000)
            self.add_budget_option(i[0], "hire staff (5 people)", 600)
            self.add_budget_option(i[0], "conduct external probe", 300)
            self.add_budget_option(i[0], "initiate layoffs (5 people)", -400)
            self.add_budget_option(i[0], "purchase equipment", 1000)
            self.add_budget_option(i[0], "plan event", 700)
            self.add_budget_option(i[0], "cancel upcoming event", -600)
            self.add_budget_option(i[0], "recycle equipment", -500)

    def create_agency_feedback(self):
        for i in self.agencies:
            self.add_agency_feedback(i[0], f"{i[0]} staffing and stress:")
            self.add_agency_feedback(i[0], f"{i[0]} equipment and learning:")
            self.add_agency_feedback(i[0], f"{i[0]} events:")


    def adjust_total_budget(self, amount: float): #change the total budget based on player input and game events
        self.total_budget += amount

    def adjust_agency_budget(self, agency, amount: float): #adjusts budget for a given agency
        self.agency_stats[agency][0] += amount

    def adjust_agency_staff(self, agency: tuple, amount: int): #changes the umber of staff in a given agency
        for i in self.agency_stats:
            if i == agency:
                self.agency_stats[i][1] += amount

    def adjust_agency_equipment(self, agency: tuple, amount: float): #adjusts the amount of equipment available for a given agency
        for i in self.agency_stats:
            if i == agency:
                self.agency_stats[i][2] += amount

    def create_agency_event(self, agency: tuple, number: int, amount): #creates a recreational event for a given agency
        for i in self.agency_stats:
            if i == agency and number > 0 and self.agency_stats[i][3] < 6:
                self.agency_stats[i][3] += number
                self.adjust_agency_budget(agency, -amount)
                listcheck = self.events[agency]
                for u in range(len(listcheck)):
                    if listcheck[u][0] == "null":
                        index = random.randrange(0, 17)
                        self.events[agency][u] = (self.possible_events[index], listcheck[u][1])
                        break

            if i == agency and number < 0 and self.agency_stats[i][3] > 0:
                self.agency_stats[i][3] += number
                self.adjust_agency_budget(agency, -amount)
                listcheck = self.events[agency]
                count = 0
                for u in range(len(listcheck)):
                    if listcheck[u][0] != "null":
                        count += 1
                        if count - 1 == self.agency_stats[i][3]:
                            self.events[agency][u] = ("null", listcheck[u][1])


    def diminishing_returns(self, number, direction): #creates a program where changes at the top and bottom end of the scale have different effects
        added = 0
        if direction > 0:
            if number >= 0:
                added = random.randrange(20, 25)
            if number > 20:
                added = random.randrange(15, 20)
            if number > 40:
                added = random.randrange(10, 15)
            if number > 60:
                added = random.randrange(5, 10)
            if number > 80:
                added = random.randrange(1, 5)
        if direction < 0:
            if number > 0:
                added = random.randrange(-5, 1)
            if number > 20:
                added = random.randrange(-10, -5)
            if number > 40:
                added = random.randrange(-15, -10)
            if number > 60:
                added = random.randrange(-20, -15)
            if number > 80:
                added = random.randrange(-25, -20)
        final = number + added
        if final > 100:
            final = 100
        if final < 0:
            final = 0
        return final

    def adjust_soft_stats(self, stat, agency, direction): #adjusts student and staff-based stats
        if stat == "student satisfaction":
            thing = self.student_stats[agency][6]
            self.student_stats[agency][6] = self.diminishing_returns(thing, direction)
        if stat == "student reading":
            thing = self.student_stats[agency][7]
            self.student_stats[agency][7] = self.diminishing_returns(thing, direction)
            self.student_stats[agency][10] = int((self.student_stats[agency][7]+self.student_stats[agency][8]+self.student_stats[agency][9])/3)
        if stat == "student math":
            thing = self.student_stats[agency][8]
            self.student_stats[agency][8] = self.diminishing_returns(thing, direction)
            self.student_stats[agency][10] = int((self.student_stats[agency][7]+self.student_stats[agency][8]+self.student_stats[agency][9])/3)
        if stat == "student science":
            thing = self.student_stats[agency][9]
            self.student_stats[agency][9] = self.diminishing_returns(thing, direction)
            self.student_stats[agency][10] = int((self.student_stats[agency][7]+self.student_stats[agency][8]+self.student_stats[agency][9])/3)
        if stat == "student stress":
            thing = self.student_stats[agency][11]
            self.student_stats[agency][11] = self.diminishing_returns(thing, direction)
        if stat == "staff satisfaction":
            thing = self.staff_stats[agency][3]
            self.staff_stats[agency][3] = self.diminishing_returns(thing, direction)
        if stat == "staff performance":
            thing = self.staff_stats[agency][4]
            self.staff_stats[agency][4] = self.diminishing_returns(thing, direction)
        if stat == "staff stress":
            thing = self.staff_stats[agency][5]
            self.staff_stats[agency][5] = self.diminishing_returns(thing, direction)
     
    def adjust_agency_stats(self, agency: str, amount: float, action: str, menu: list): #change individual agency stats based on player input and game events
        if action == "increase funding" or action == "decrease funding":
            self.adjust_total_budget(-amount)
            self.adjust_agency_budget(agency, amount)
        if action == "hire staff (5 people)":
            self.adjust_agency_staff(agency, 5)
            self.adjust_agency_budget(agency, -amount)
            self.adjust_soft_stats("student reading", agency, 1)
            self.adjust_soft_stats("student math", agency, 1)
            self.adjust_soft_stats("student science", agency, 1)
            self.adjust_soft_stats("staff performance", agency, 1)
            self.adjust_soft_stats("staff satisfaction", agency, 1)
            self.adjust_soft_stats("staff performance", agency, 1)
            self.adjust_soft_stats("staff stress", agency, -1)
        if action == "conduct external probe":
            self.adjust_agency_budget(agency, -amount)
            self.adjust_soft_stats("staff performance", agency, 1)
            self.adjust_soft_stats("staff stress", agency, 1)
            self.adjust_soft_stats("student reading", agency, 1)
            self.adjust_soft_stats("student math", agency, 1)
            self.adjust_soft_stats("student science", agency, 1)
            self.adjust_soft_stats("student stress", agency, 1)
        if action == "initiate layoffs (5 people)":
            self.adjust_agency_budget(agency, -amount)
            self.adjust_agency_staff(agency, -5)
            self.adjust_soft_stats("student reading", agency, -1)
            self.adjust_soft_stats("student math", agency, -1)
            self.adjust_soft_stats("student science", agency, -1)
            self.adjust_soft_stats("staff performance", agency, -1)
            self.adjust_soft_stats("staff satisfaction", agency, -1)
            self.adjust_soft_stats("staff stress", agency, 1)
        if action == "purchase equipment":
            self.adjust_agency_budget(agency, -amount)
            self.adjust_agency_equipment(agency, amount - 100)
            self.adjust_soft_stats("student reading", agency, 1)
            self.adjust_soft_stats("student math", agency, 1)
            self.adjust_soft_stats("student science", agency, 1)
            self.adjust_soft_stats("staff satisfaction", agency, 1)
            self.adjust_soft_stats("staff performance", agency, 1)
        if action == "recycle equipment":
            self.adjust_agency_budget(agency, -amount)
            self.adjust_agency_equipment(agency, amount * 1.5)
            self.adjust_soft_stats("student reading", agency, -1)
            self.adjust_soft_stats("student math", agency, -1)
            self.adjust_soft_stats("student science", agency, -1)
            self.adjust_soft_stats("staff satisfaction", agency, -1)
            self.adjust_soft_stats("staff performance", agency, -1)
        if action == "plan event":
            self.create_agency_event(agency, 1, amount)
            self.adjust_soft_stats("student satisfaction", agency, 1)
            self.adjust_soft_stats("student stress", agency, -1)
            self.adjust_soft_stats("staff stress", agency, 1)

        if action == "cancel upcoming event":
            self.create_agency_event(agency, -1, amount)
            self.adjust_soft_stats("student satisfaction", agency, -1)
            self.adjust_soft_stats("student stress", agency, 1)
            self.adjust_soft_stats("staff stress", agency, -1)
        self.check_status()
        pygame.display.update(self.board[4])


    def draw_agency_menu(self, menu: list): #draw the main manu for the game (with agency selection options)
        actions = []
        colour = self.forestgreen
        count = 0
        agencies = []
        number = 0  
        for i in self.agencies:
            agencies.append((i[0], number))
            number += 1
        for i in menu:
            name = i[1][0]
            if (self.agency_stats[name][4] == "Understaffed" 
                or self.agency_stats[name][5] == "Equipment shortage" 
                or self.agency_stats[name][6] == "No events planned" 
                or self.agency_stats[name][7] == "Under budget" 
                or self.agency_stats[name][8] == "low staff satisfaction" 
                or self.agency_stats[name][9] == "low staff performance" 
                or self.agency_stats[name][10] == "high staff stress" 
                or self.agency_stats[name][11] == "low student satisfaction" #low_student_satisfaction
                or self.agency_stats[name][12] == "poor learning results (reading)" #low_student_reading
                or self.agency_stats[name][13] == "poor learning results (math)"
                or self.agency_stats[name][14] == "poor learning results (science)" #low_student_science
                or self.agency_stats[name][15] == "poor learning results (overall)" #low_student_overall
                or self.agency_stats[name][16] == "high student stress"):
                colour = self.white
                text = self.calibri2.render("Issues to solve!", True, self.crimson)
                width = text.get_width()
                actions.append((text, (i[0][0]-(width/2), i[0][1]+5)))
            elif (self.agency_stats[name][4] == "Staffed" 
                and self.agency_stats[name][5] == "Sufficient equipment" 
                and self.agency_stats[name][6] == "Events planned" 
                and self.agency_stats[name][7] == "Within budget" 
                and self.agency_stats[name][8] == "high staff satisfaction" 
                and self.agency_stats[name][9] == "high staff performance" 
                and self.agency_stats[name][10] == "low staff stress" 
                and self.agency_stats[name][11] == "high student satisfaction" #low_student_satisfaction
                and self.agency_stats[name][12] == "good learning results (reading)" #low_student_reading
                and self.agency_stats[name][13] == "good learning results (math)"
                and self.agency_stats[name][14] == "good learning results (science)" #low_student_science
                and self.agency_stats[name][15] == "good learning results (overall)" #low_student_overall
                and self.agency_stats[name][16] == "low student stress"):
                colour = self.lightslateblue
                text = self.calibri2.render("All great!", True, self.black)
                width = text.get_width()
                actions.append((text, (i[0][0]-(width/2), i[0][1]+5)))
            else:
                text = self.calibri2.render("No issues!", True, self.black)
                width = text.get_width()
                actions.append((text, (i[0][0]-(width/2), i[0][1]+5)))
            for u in agencies:
                if self.agency == u[0] and u[1] == count:
                    colour = self.gold
            pygame.draw.circle(self.window, colour, i[0], self.radius)
            colour = self.forestgreen
            count += 1

        for i in self.agency_labels: #writes main menu labels
            text = self.calibri.render(i[0], True, self.black) 
            self.window.blit(text, (i[1], i[2]))
        for i in actions:
            self.window.blit(i[0], (i[1][0], i[1][1]))


    def menu_option_1(self): #draws the initial instruction screen for the player
        self.window.fill(self.white)
        x = 50
        y = 75
        text = self.arial.render(f"This is the budget game. In this game, you will be asked to act as a policymaker deciding public schools budgets.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"There are {len(self.agencies)} different schools for which you will be responsible over a period of 10 semesters.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Each school has measures that track the performance, happiness and stress levels of their staff and students.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"The primary aim of the game is to maximise the learning outcomes of the students while staying within your overall budget.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"There are three learning outcomes that are being independently tracked: the students' math, reading and science scores.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Each of the schools has an index tracking its status. There is also an overall learning result index giving you your score.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"The secondary aim of the game is to maintain sufficient levels of happiness among the staff and students.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"As the budget officer, you are in charge of a number of measures by which you can either try to save money or improve outcomes.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"     Hiring new staff will make students and staff happier and perform better, laying off staff will have the opposite effect.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"     Purchasing equipment will improve performance and staff satisfaction, recycling will do the opposite.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"     Organising events will increase student happiness and reduce student stress but add to staff stress.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"     Calling for an external probe will improve performance but increase stress.", True, self.black)
        self.window.blit(text, (x, y))
        y += 75
        rect1 = self.draw_exit("next")
        y += 25


        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    if self.click_box(x, y, rect1) == True:
                        self.add_to_output(f"instruction screen back button clicked")
                        self.start = False
                        self.instruction_2 = True

            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit
            
    def instruction_screen_2(self):
        self.window.fill(self.white)
        x = 50
        y = 75
        text = self.arial.render(f"Schools are required by the school board administration to have sufficient levels of staff, equipment and events.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"The levels of happiness, stress and performanced among the students will all influence each other:", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"     Positive learning results will cause staff and students to be happier and less stressed.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"     Negative learning results will have the opposite effect, and cause some staff to quit their jobs.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"     Not staying within a school's budget will cause staff to become more stressed and decrease performance levels.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"     Low generalised performance will increase stress and decrease learning outcomes, high performance will do the opposite.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"     If no events are organised, students will become unhappy and perform worse; organising events has the opposite effect", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"     If the school is understaffed, both students and staff will perform worse and become unhappy; even more staff will leave.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"There are also a number of random events that may occur to each school; these can have both negative and positive effects.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"The events range from natural disasters to alumni events; they will be automatically generated at the end of each semester.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"You will be able to make budget decisions for each school separately; once you are satisfied, you can advance to the next semester.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"You have up to {int(self.roundtimer/60)} minutes per semester, after which the game will advance to the next semester automatically.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Between semesters, game events will occur and overall and school budgets will be adjusted.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"At any time from the main menu screen, you can return here to read the game instructions.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"You also have the option of looking in more detail at what effects each budget choice has.", True, self.black)
        self.window.blit(text, (x, y))
        y += 75
        text = self.arial.render(f"Have fun playing the game!", True, self.black)
        self.window.blit(text, (x, y))
        rect1 = self.draw_exit("start")
        y += 25
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    if self.click_box(x, y, rect1) == True:
                        self.add_to_output("instruction screen back button clicked")
                        self.baseconditions()

            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit

    def show_postgame(self): #draws a post-game screen
        x = 200
        y = 100
        self.window.fill(self.cadetblue2)
        text = self.arial.render("You have reached the end of the game, thank you for playing!", True, self.black)
        self.window.blit(text, (x, y))
        y += 30
        text = self.arial.render(f"Your score in the game was: {self.score_total[0]} out of 100", True, self.black)
        self.window.blit(text, (x, y))
        y += 30

        text = self.arial.render("Insert additional debrief text here", True, self.black)
        self.window.blit(text, (x, y))
        y += 30
        text = self.arial.render("Click anywhere to exit", True, self.black)
        self.window.blit(text, (x, y))
        y += 30        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.add_final_output()
                    self.rename_output()
                    self.post_output()
                    raise SystemExit
            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit


    def draw_summary_prompts(self, condition): #draws a prompt to select a given agency
        x = 470
        y = 100
        boxheight = 100
        boxwidth = 400
        x2 = 305
        y2 = 100
        rounds = []
        if condition == "historical":
            rect1 = (x, y, boxwidth, boxheight)
            if self.agency == "null":
                pygame.draw.rect(self.window, self.tan, rect1)
            text1 = self.arial.render("Please click on the school you wish", True, self.black)
            self.window.blit(text1, (x+10, y+10))
            text2 = self.arial.render("to see historical performance information on", True, self.black)
            self.window.blit(text2, (x+10, y+40))
            y += boxheight + 50
            rect3 = (x, y, boxwidth, boxheight)
            pygame.draw.rect(self.window, self.tan, rect3)
            text = self.arial.render("Click here to return to main menu", True, self.black)
            self.window.blit(text, (x+10, y+10))
            y = 100
            x = 100
            counter = 1
        if condition == "summary":
            if self.round_number != 1:
                rect1 = (x, y, boxwidth, boxheight)
                if self.agency == "null":
                    pygame.draw.rect(self.window, self.tan, rect1)
                else:
                    pygame.draw.rect(self.window, self.gold, rect1)
                text1 = self.arial.render("Please click on the school you wish", True, self.black)
                self.window.blit(text1, (x+10, y+10))
                text2 = self.arial.render("to receive a summary on", True, self.black)
                self.window.blit(text2, (x+10, y+40))
                y += boxheight + 50
                rect2 = (x, y, boxwidth, boxheight)
                if self.roundchoice == "null":
                    pygame.draw.rect(self.window, self.tan, rect2)
                else:
                    pygame.draw.rect(self.window, self.gold, rect2)
                text1 = self.arial.render("Please click on the semester you wish to get a summary for", True, self.black)
                self.window.blit(text1, (x+10, y+10))
                y += boxheight + 50
                rect3 = (x, y, boxwidth, boxheight)
                pygame.draw.rect(self.window, self.tan, rect3)
                text = self.arial.render("Click here to return to main menu", True, self.black)
                self.window.blit(text, (x+10, y+10))
                y = 100
                x = 100
                counter = 1
                for i in range((self.round_number)-1):
                        if self.roundchoice == counter:
                            pygame.draw.circle(self.window, self.gold, (x2, y2), self.radius2)
                        else:
                            pygame.draw.circle(self.window, self.green, (x2, y2), self.radius2)

                        rounds.append(((x2, y2, self.radius2), counter))
                        textwritten = f"Semester {str(counter)}"
                        text = self.calibri.render(textwritten, True, self.black)
                        text_width, text_height = self.calibri.size(textwritten)
                        self.window.blit(text, (x2-(text_width/2), y2-text_height/2))
                        counter += 1
                        y2 += self.radius2*2 + 10
            else:
                rect1 = (x, y, boxwidth, boxheight)
                pygame.draw.rect(self.window, self.tan, rect1)
                text1 = self.arial.render("No events have occurred in the game yet!", True, self.black)
                self.window.blit(text1, (x+10, y+10))
                y += boxheight*2 + 100
                rect3 = (x, y, boxwidth, boxheight)
                pygame.draw.rect(self.window, self.tan, rect3)
                text = self.arial.render("Click here to return to main menu", True, self.black)
                self.window.blit(text, (x+10, y+10))

        if condition == "rankings":
            rect1 = (x, y, boxwidth, boxheight)
            pygame.draw.rect(self.window, self.tan, rect1)
            text1 = self.arial.render("Please click on the semester you wish", True, self.black)
            self.window.blit(text1, (x+10, y+10))
            text2 = self.arial.render("to see the school ranking for", True, self.black)
            self.window.blit(text2, (x+10, y+40))
            y += boxheight + 50
            rect2 = (x, y, boxwidth, boxheight)
            if self.roundchoice == "null":
                pygame.draw.rect(self.window, self.tan, rect2)
            else:
                pygame.draw.rect(self.window, self.gold, rect2)
            rect3 = (x, y, boxwidth, boxheight)
            pygame.draw.rect(self.window, self.tan, rect3)
            text = self.arial.render("Click here to return to main menu", True, self.black)
            self.window.blit(text, (x+10, y+10))
            y = 100
            x = 100
            counter = 1
            y2 -= 50
            for i in range((self.round_number)):
                    if self.roundchoice == counter:
                        pygame.draw.circle(self.window, self.gold, (x2, y2), self.radius2)
                    else:
                        pygame.draw.circle(self.window, self.green, (x2, y2), self.radius2)
                    rounds.append(((x2, y2, self.radius2), counter))
                    textwritten = f"Semester {str(counter)}"
                    text = self.calibri.render(textwritten, True, self.black)
                    text_width, text_height = self.calibri.size(textwritten)
                    self.window.blit(text, (x2-(text_width/2), y2-text_height/2))
                    counter += 1
                    y2 += self.radius2*2 + 10


        return (rect3, rounds)


    def show_information(self, agency, condition): #shows either performance information or a summary
        if condition == "PI":
            text1 = self.arial.render(f"This is performance information on {agency}", True, self.black)
            text2 = self.arial.render(f"Click anywhere to return to the main menu", True, self.black)
            while True:
                self.window.fill(self.white)
                self.window.blit(text1, (200, 300))
                self.window.blit(text2, (200, 400))
                if self.main_menu_action == False:
                    break
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.increase_click_counter()
                            self.add_to_output("performance information back button clicked")
                            self.main_menu_action = False
                            self.agency = "null"
                    if event.type == pygame.QUIT:
                        self.add_final_output()
                        self.rename_output()
                        self.post_output()
                        raise SystemExit
                pygame.display.update()
        if condition == "summary":
            while True:
                self.window.fill(self.white)
                x = 50
                y = 50
                text1 = self.arial.render(f"This page shows a list of the events that have happened at {agency}:                    Click anywhere to return", True, self.black)
                self.window.blit(text1, (x, y))
                y += 25
                for i in self.agency_events[agency]:
                    text = self.calibri.render(f"{i}", True, self.black)
                    self.window.blit(text, (x, y))
                    y += 25
                    if y > 700:
                        x += 300
                        y = 75
                if self.main_menu_action == False:
                    break
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.increase_click_counter()
                            self.add_to_output("performance information back button clicked")
                            self.main_menu_action = False
                            self.agency = "null"
                    if event.type == pygame.QUIT:
                        self.add_final_output()
                        self.rename_output()
                        self.post_output()
                        raise SystemExit
                pygame.display.update()
            text1 = self.arial.render(f"This is a summary of game events for {agency}", True, self.black)



    def show_budget_effects(self):
        self.window.fill(self.white)
        rect1 = self.draw_exit("previous")
        x = 100
        y = 100
        text = self.arial.render(f"The button you chose for more information was: {self.choice}", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"This choice results in the following effects:", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        if self.choice == "increase funding":
            text = self.arial.render(f"The funds available for the agency are increased by {self.amount} €. This amount is subtracted from the total budget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"This action does not impact other stats.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25           
        if self.choice == "decrease funding":
            text = self.arial.render(f"The funds available for the agency are decreased by {-self.amount} €. This amount is added to the total budget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"This action does not impact other stats.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25   
        if self.choice == "hire staff (5 people)":
            text = self.arial.render(f"5 additional staff members are hired.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"This costs the school {self.amount} €, which is removed from the school budget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"The increased staff results in the following effects on the school metrics:", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"The students receive more attentive teaching, and their performance in each learning outcome improves.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25       
            text = self.arial.render(f"The staff are more able to focus on their work, and their performance improves and satisfaction increases.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25   
            text = self.arial.render(f"The staff are also less overworked, and their stress levels decrease.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
        if self.choice == "conduct external probe":
            text = self.arial.render(f"A third-party evaluator is hired to examine the performance of the school and fix issues.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"This costs the school {self.amount} €, which is removed from the school budget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"The increased scrutiny by the evaluator results in the following effects on the school metrics:", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"The students become more focused on their studies, and each of their learning metrics improve.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25       
            text = self.arial.render(f"The staff are under pressure to work to fix issues, and their performance also increases.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25   
            text = self.arial.render(f"However, the staff and students both also become more stressed by the scrutiny.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
        if self.choice == "purchase equipment":
            text = self.arial.render(f"More equipment is purchased, which is used for teaching activities.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"This costs the school {self.amount} €, which is removed from the school budget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"The additional equipment makes it easier to teach the students, and all learning metrics improve", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"The staff are particularly happy with having more teaching equipment, and both their satisfaction and performance improve.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25       
        if self.choice == "initiate layoffs (5 people)":
            text = self.arial.render(f"5 staff members are layed off to save costs.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"This saves the school {-self.amount} €, which is added to the school budget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"Having less staff available decreases the time students have with teachers, which decreases all learning outcomes.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"The staff are under more pressure, and their overall performance decreases.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25       
            text = self.arial.render(f"The staff also become more stressed by their work and less satisfied.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25   
        if self.choice == "plan event":
            text = self.arial.render(f"An event is organised at the school.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"This costs the school {self.amount} €, which is removed from the school budget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"Organising the event in addition to other work increases staff stress.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"The students look forward to the event, and their satisfaction increases and stress decreases.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25       
        if self.choice == "cancel upcoming event":
            text = self.arial.render(f"An event that has been organised is cancelled to save money", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"This saves the school {-self.amount} €, which is added to the school budget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"Having less activities to manage decreases staff stress.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"The students are dissappointed by the cancelled event, and their satisfaction decreases and stress increases.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
        if self.choice == "recycle equipment":
            text = self.arial.render(f"Some of the equipment at the school is recycled, and some funds are recovered.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"This saves the school {-self.amount} €, which is added to the school budget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"The decreased equipment makes it harder to teach the students, and all learning metrics decline", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"The staff are particularly unhappy with having less teaching equipment, and both their satisfaction and performance decline.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25       


        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    for i in self.budget_buttons:
                        if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                            self.add_to_output(f"budget information back button clicked")
                            self.information = True
                            self.show_effects = False
                            self.choice = "null"

            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit

    def menu_option_2(self, menu_options): #prompts the player to select a budget action for which they will be given more information
        self.agency = "Leaf High"
        self.budget_menu = []
        self.budgeting_labels1 = []
        self.budgeting_labels2 = []
        self.budget_buttons = []
        self.budget_menu = self.create_budgeting_menu(self.agency, "information")
        self.draw_budget_options(self.budget_menu)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    for i in self.budget_buttons:
                        if self.click_box(x, y, i[0]) == True: #checks if a budget option has been clicked
                            self.choice = i[1]
                            self.amount = i[2]
                            self.show_budget_options = False
                            self.add_to_output(f"budget information button {self.choice} clicked")
                    if self.choice == "exit":
                        self.information = False
                        self.main_menu_action = False
                        self.show_agencies = True
                        self.show_main_menu = True
                        self.show_feedback = True
                        self.show_effects = False
                        self.agency = "null"
                    elif self.choice == 1:
                        self.show_effects = False
                    else:
                        self.information = False
                        self.show_effects = True
            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit

    def menu_option_3(self, menu_options): #prompts the player to choose an agency for which they will receive a summary of game events
        self.window.fill(self.white)
        self.draw_game_board()
        self.draw_agency_menu(menu_options)
        summarybuttons = self.draw_summary_prompts("summary")
        rect = summarybuttons[0]
        rounds = summarybuttons[1]
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    if self.click_box(x, y, rect) == True:
                        self.main_menu_action = False
                        self.summary = False
                        self.show_agencies = True
                        self.show_feedback = True
                        self.show_main_menu = True
                        self.roundchoice = "null"
                        self.agency = "null"
                        self.add_to_output("summary back button clicked")
                    if self.round_number > 1:
                        for i in self.menu_buttons:
                            if self.click_circle(x, y, i[0]) == True: #checks if an agency has been clicked
                                agency = i[1]
                                self.add_to_output(f"agency clicked: {agency}")
                                self.agency = agency
                        for i in rounds:
                            if self.click_circle(x, y, i[0]) == True: #checks if a round has been clicked
                                round = i[1]
                                self.add_to_output(f"Sesmester clicked: {round}")
                                self.roundchoice = round
                            
                    if self.agency != "null" and self.roundchoice != "null":
                            self.summary = False
                            self.agency_summary = True
                            self.intervaltime = self.time
                            self.caption1 = False
                            self.caption4 = True
                            self.show_agencies = False

                            


            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit
            
    def draw_exit(self, condition):
        x = 340
        y = 5
        boxheight = 30
        boxwidth = 400
        rect1 = (x, y, boxwidth, boxheight)
        pygame.draw.rect(self.window, self.tan, rect1)
        if condition == "previous":
            text1 = self.arial.render("Click here to return to the menu page", True, self.black)
        if condition == "next":
            text1 = self.arial.render("Click here to continue to the next page", True, self.black)
        if condition == "roundend":
            text1 = self.arial.render("Click here to continue to school rankings", True, self.black)
        if condition == "rankings":
            text1 = self.arial.render("Click here to continue to the main menu", True, self.black)
        if condition == "gameend":
            text1 = self.arial.render("Click here to continue to the postgame", True, self.black)
        if condition == "start":
            text1 = self.arial.render("Click here to continue to the game!", True, self.black)
        self.window.blit(text1, (x+10, y+3))
        return rect1

    def summary_click_forward(self, summary, rect1): #saved code for implementing click-based advancement in the next two functions
        #summary_1
        if summary == 1:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("agency summary back button clicked")
                self.agency_summary = False
                self.agency_summary_2 = True
                self.intervaltime2 = self.time

        #summary_2
        if summary == 2:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("agency summary back button clicked")
                self.agency = "null"
                self.roundchoice = "null"
                self.summary = True
                self.agency_summary_2 = False

        if summary == 3:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("agency summary back button clicked")
                self.agency_summary = True
                self.show_event_effects = False
                self.agency_summary_2 = False

        if summary == 4:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.roundchoice = "null"
                self.add_to_output("rankings back button clicked")
                self.rankings = True
                self.show_rankings = False

        if summary == 5:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.roundchoice = "null"
                self.add_to_output("rankings back button clicked")
                self.roundend()

    def show_agency_summary(self, roundnumber):
        if self.click_summary == True:
            rect1 = self.draw_exit("next")
            self.caption1 = True
            self.caption4 = False
            width = 300
            height = 100
            x = 50
            y = 50
            text = self.arial.render(f"These input-based events occurred at {self.agency} in semester {roundnumber}:", True, self.black)
            self.window.blit(text, (x, y))
            y += 50
            choices = []
            for i in self.agency_events[self.agency]:
                if i[3] == 0:
                    if i[1] == roundnumber:
                        effects = []
                        for u in i[2][1:]:
                            effects.append(f"{u[0]}")
                        eventname = f"{i[2][0]}"
                        effects_choice = (eventname, effects)
                        text = self.arial2.render(eventname, True, self.black)
                        text_width, text_height = self.arial2.size(eventname)
                        box = pygame.Rect(x-10, y-(text_height), width, height)
                        choices.append((box, effects_choice))
                        pygame.draw.rect(self.window, self.tomato, box)
                        self.window.blit(text, (x, y))
                        y += 25
                        text = self.arial2.render(f"Click here to see the effects", True, self.black)
                        self.window.blit(text, (x, y))
                        y += height
                        if y > 720-height:
                            y = 100
                            x += 350



        if self.click_summary == False:
            x = 50
            y = 50
            text = self.arial.render(f"These input-based events occurred at {self.agency} in semester {roundnumber}:", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            for i in self.agency_events[self.agency]:
                if i[3] == 0:
                    if i[1] == roundnumber:
                        text = self.arial2.render(f"{i[2][0]}!", True, self.black)
                        self.window.blit(text, (x, y))
                        y += 25
                        text = self.arial2.render(f"This resulted in the following effects:", True, self.black)
                        self.window.blit(text, (x+10, y))
                        y += 25
                        if y > 720:
                            y = 75
                            x += 350
                        for u in i[2][1:]:
                            text = self.calibri.render(f"{u[0]}", True, self.black)
                            self.window.blit(text, (x+25, y))
                            y += 25
                            if y > 720:
                                y = 75
                                x += 350

            if self.time > self.intervaltime + self.summaryinterval:
                self.agency_summary = False
                self.agency_summary_2 = True
                self.intervaltime2 = self.time
                self.caption4 = False
                self.caption5 = True

        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    if self.click_summary == True:
                        for i in choices:
                            xy = pygame.mouse.get_pos()
                            x = xy[0]
                            y = xy[1]
                            if self.click_box(x, y, i[0]) == True: #checks if a budget option has been clicked
                                self.show_event_effects = True
                                self.effects_choice = i[1]
                                self.add_to_output("agency summary effects button clicked")
                                self.agency_summary = False
                                self.agency_summary_2 = False
                                self.show_event_effects = True
                        self.summary_click_forward(1, rect1)


            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit

    def show_agency_summary_2(self, roundnumber):
        if self.click_summary == True:
            rect1 = self.draw_exit("previous")
            self.caption1 = True
            self.caption5 = False
            width = 300
            height = 100
            x = 50
            y = 50
            text = self.arial.render(f"These random events occurred at {self.agency} in semester {roundnumber}:", True, self.black)
            self.window.blit(text, (x, y))
            y += 50
            choices = []
            for i in self.agency_events[self.agency]:
                if i[3] == 1:
                    if i[1] == roundnumber:
                        effects = []
                        for u in i[2][1:]:
                            effects.append(f"{u[0]}")
                        eventname = f"{i[2][0]}"
                        effects_choice = (eventname, effects)
                        text = self.arial2.render(eventname, True, self.black)
                        text_width, text_height = self.arial2.size(eventname)
                        box = pygame.Rect(x-10, y-(text_height), width, height)
                        choices.append((box, effects_choice))
                        pygame.draw.rect(self.window, self.tomato, box)
                        self.window.blit(text, (x, y))
                        y += 25
                        text = self.arial2.render(f"Click here to see the effects", True, self.black)
                        self.window.blit(text, (x, y))
                        y += height
                        if y > 720-height:
                            y = 100
                            x += 350

        if self.click_summary == False:
            x = 50
            y = 50
            text = self.arial.render(f"These random events occurred at {self.agency} in semester {roundnumber}:", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            for i in self.agency_events[self.agency]:
                if i[3] == 1:
                    if i[1] == roundnumber:
                        text = self.arial2.render(f"{i[2][0]}!", True, self.black)
                        self.window.blit(text, (x, y))
                        y += 25
                        text = self.arial2.render(f"This resulted in the following effects:", True, self.black)
                        self.window.blit(text, (x+10, y))
                        y += 25
                        if y > 720:
                            y = 75
                            x += 350
                        for u in i[2][1:]:
                            text = self.calibri.render(f"{u[0]}", True, self.black)
                            self.window.blit(text, (x+25, y))
                            y += 25
                            if y > 720:
                                y = 75
                                x += 350
            if self.time > self.intervaltime2 + self.summaryinterval:
                self.agency = "null"
                self.roundchoice = "null"
                self.summary = True
                self.agency_summary_2 = False
                self.caption5 = False
                self.caption1 = True

        
        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    if self.click_summary == True:
                        for i in choices:
                            xy = pygame.mouse.get_pos()
                            x = xy[0]
                            y = xy[1]
                            if self.click_box(x, y, i[0]) == True: #checks if a budget option has been clicked
                                self.show_event_effects = True
                                self.effects_choice = i[1]
                                self.add_to_output("agency summary effects button clicked")
                                self.agency_summary = False
                                self.agency_summary_2 = False
                                self.show_event_effects = True
                        self.summary_click_forward(2, rect1)

            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit
            

    def summary_out(self):
        self.roundsummary1 = False
        self.roundsummary2 = False
        self.roundsummary3 = False
        self.roundsummary4 = False
        self.roundsummary5 = False
        self.roundsummary6 = False
        self.roundsummary7 = False

    def menu_option_4(self): #progress to the next round
        if self.roundsummary1 == True:
            self.roundcounter = 0
        boxheight1 = 25
        boxheight2 = 25
        boxheight3 = 50
        boxwidth3 = 400
        boxwidth = 400
        x = 150
        x1 = x-20
        x3 = x + boxwidth + 50
        y = 25
        y1 = y
        texts = []
        self.window.fill(self.white)
        text = self.arial.render(f"These random events occurred at {self.agency} this semester:", True, self.crimson)
        texts.append((text, (300, y)))
        y += 50
        y1 = y-12.5

        for i in self.script_events[1]:
            if i[0] == self.agency:
                text = self.calibri.render(f"{i[1]}", True, self.black)
                texts.append((text, (x, y)))
                y += 15
                boxheight1 += 15
        y += 50

        text = self.arial.render(f"These input-based events occurred at {self.agency} this semester:", True, self.crimson)
        texts.append((text, (300, y)))

        y += 50
        if self.time > self.intervaltime + self.roundinterval:
            text = self.arial.render("Click here to progress to the next summary screen", True, self.black)
            texts.append((text, (x3+10, y+50)))
            progress_button = (x3, y+30, boxwidth3, boxheight1)
            pygame.draw.rect(self.window, self.gold, progress_button)
        else:
            text = self.arial.render(f"Next summary screen available in {int(self.roundinterval+1-(self.time-self.intervaltime))} seconds", True, self.black)
            texts.append((text, (x3+10, y+50)))
            progress_button = (x3, y+30, boxwidth3, boxheight1)
            pygame.draw.rect(self.window, self.gainsboro, progress_button)

        y2 = y-12.5
        for i in self.script_events[0]:
            if i[0] == self.agency:
                text = self.calibri.render(f"{i[1]}", True, self.black)
                texts.append((text, (x, y)))
                y += 15
                boxheight2 += 15

        pygame.draw.rect(self.window, self.tomato, (x1, y1, boxwidth, boxheight1))
        pygame.draw.rect(self.window, self.tomato, (x1, y2, boxwidth, boxheight2))

        for i in self.agency_round_results[self.round_number-1]:
            if i[0] == self.agency:
                score = i[1]

        y += 50
        pygame.draw.rect(self.window, self.tomato, (x1, y, boxwidth, boxheight3))

        text = self.calibri.render(f"Performance score at {self.agency} this semester: {score}", True, self.black)
        self.window.blit(text, (x, y+15))
        y += 75

        pygame.draw.rect(self.window, self.tomato, (x1, y, boxwidth, boxheight3))

        text = self.calibri.render(f"Your overall performance score this semester was: {self.score_last}", True, self.black)
        self.window.blit(text, (x, y+15))


        for i in texts:
            self.window.blit(i[0], i[1])


        pygame.display.update()
        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration


            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    if self.click_box(x, y, progress_button) == True: #checks if a budget option has been clicked

                        if self.time > self.intervaltime + self.roundinterval and self.roundsummary1 == True:
                                    self.roundsummary1 = False
                                    self.roundsummary2 = True
                                    self.intervaltime = self.time
                                    self.roundcounter += 1
                                    if self.roundcounter == self.agency_count:
                                        self.summary_out()
                                        self.roundover = True

                        if self.time > self.intervaltime + self.roundinterval and self.roundsummary2 == True:
                                    self.roundsummary2 = False
                                    self.roundsummary3 = True
                                    self.intervaltime = self.time
                                    self.roundcounter += 1
                                    if self.roundcounter == self.agency_count:
                                        self.summary_out()
                                        self.roundover = True

                        if self.time > self.intervaltime + self.roundinterval and self.roundsummary3 == True:
                                    self.roundsummary3 = False
                                    self.roundsummary4 = True
                                    self.intervaltime = self.time
                                    self.roundcounter += 1
                                    if self.roundcounter == self.agency_count:
                                        self.summary_out()
                                        self.roundover = True


                        if self.time > self.intervaltime + self.roundinterval and self.roundsummary4 == True:
                                    self.roundsummary4 = False
                                    self.roundsummary5 = True
                                    self.intervaltime = self.time
                                    self.roundcounter += 1
                                    if self.roundcounter == self.agency_count:
                                        self.summary_out()
                                        self.roundover = True


                        if self.time > self.intervaltime + self.roundinterval and self.roundsummary5 == True:
                                    self.roundsummary5 = False
                                    self.roundsummary6 = True
                                    self.intervaltime = self.time
                                    self.roundcounter += 1
                                    if self.roundcounter == self.agency_count:
                                        self.summary_out()
                                        self.roundover = True


                        if self.time > self.intervaltime + self.roundinterval and self.roundsummary6 == True:
                                    self.roundsummary6 = False
                                    self.roundsummary7 = True
                                    self.intervaltime = self.time
                                    self.roundcounter += 1
                                    if self.roundcounter == self.agency_count:
                                        self.summary_out()
                                        self.roundover = True

                        if self.time > self.intervaltime + self.roundinterval and self.roundsummary7 == True:
                                    self.roundsummary7 = False
                                    self.intervaltime = self.time
                                    self.roundcounter += 1
                                    if self.roundcounter == self.agency_count:
                                        self.summary_out()
                                        self.roundover = True

    def round_summary(self):
        if self.round_number < 11:
            rect1 = self.draw_exit("roundend")
        else:
            rect1 = self.draw_exit("gameend")

        texts = []
        x = 150
        x1 = x-20
        y = 100
        y1 = y-5

        boxheight3 = 30
        boxwidth3 = 100
        boxwidth = 700
        scores = []
        names = []
        text = self.arial.render(f"Your overall performance score this semester was: {self.score_last} out of 100", True, self.black)
        texts.append((text, (x, y)))
        pygame.draw.rect(self.window, self.dodgerblue, (x1, y1, boxwidth, boxheight3))
        y += 40
        y1 += 40
        for i in self.agency_round_results[self.round_number-1]:
            scores.append(i[1])
            names.append(i[0])
        lowest = min(scores)
        highest = max(scores)
        for i in self.agency_round_results[self.round_number-1]:
            if i[1] == lowest:
                lowest_school = i[0]
            if i[1] == highest:
                highest_school = i[0]
        text = self.arial.render(f"Your lowest performing school this semester was {lowest_school} with a performance score of {lowest}", True, self.black)
        texts.append((text, (x, y)))
        pygame.draw.rect(self.window, self.tomato, (x1, y1, boxwidth, boxheight3))
        y += 40
        y1 += 40
        text = self.arial.render(f"Your highest performing school this semester was {highest_school} with a performance score of {highest}", True, self.black)
        texts.append((text, (x, y)))
        pygame.draw.rect(self.window, self.darkolivegreen3, (x1, y1, boxwidth, boxheight3))
        y += 40
        y1 += 40
        text = self.arial.render(f"Your overall performance score in each semester so far has been:", True, self.black)
        texts.append((text, (x, y)))
        pygame.draw.rect(self.window, self.gainsboro, (x1, y1, boxwidth, boxheight3))
        y += 40
        y1 += 40
        count = 1
        for i in self.score_total:
                text = self.arial.render(f"Semester {count}: {i}", True, self.black)
                texts.append((text, (x+10, y)))
                pygame.draw.rect(self.window, self.gold, (x1+10, y1, boxwidth, boxheight3))
                y += 40
                y1 += 40
                count += 1
        text = self.arial.render(f"Your average performance score in the game so far: {int(sum(self.score_total)/len(self.score_total))}", True, self.black)
        texts.append((text, (x, y)))
        pygame.draw.rect(self.window, self.lightsteelblue, (x1, y1, boxwidth, boxheight3))
        y += 40
        y1 += 40

        for i in texts:
            self.window.blit(i[0], i[1])

        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    if self.click_box(x, y, rect1) == True:
                            self.endrankings = True
                            self.roundover = False
                            self.increase_click_counter()
                            self.add_to_output("Semester summary forward button clicked")
                            self.roundchoice = self.round_number
                            self.show_rankings = True



    def roundend(self):
            self.insummary = False
            self.agency = "null"
            self.main_menu_action = False
            self.show_agencies = True
            self.show_feedback = True
            self.show_main_menu = True
            self.caption1 = True
            self.caption3 = False
            self.roundsummary2 = False
            self.roundtime = self.time
            self.increase_round_counter()
            self.baseconditions()
            if self.round_number == self.roundstandard + 1:
                self.postgame = True
                self.start = False #condition for showing the instruction screen first
                self.instruction_2 = False
                self.information = False
                self.summary = False
                self.agency_summary = False
                self.agency_summary_2 = False
                self.show_agencies = False
                self.show_effects = False
                self.show_event_effects = False
                self.show_main_menu = False
                self.show_feedback = False
                self.show_budget_options = False

    def menu_option_5(self, menu_options): #view historical performance
        self.window.fill(self.white)
        self.draw_game_board()
        self.draw_agency_menu(menu_options)
        summarybuttons = self.draw_summary_prompts("historical")
        rect = summarybuttons[0]
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    if self.click_box(x, y, rect) == True:
                        self.baseconditions()
                        self.add_to_output("summary back button clicked")

                    for i in self.menu_buttons:
                        if self.click_circle(x, y, i[0]) == True: #checks if an agency has been clicked
                            agency = i[1]
                            self.add_to_output(f"agency clicked: {agency}")
                            self.agency = agency
                            
                    if self.agency != "null":
                            self.historical = False
                            self.history_information = True
                            self.show_agencies = False

                            


            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit

    def historical_performance(self, agency):
        self.window.fill(self.white)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    self.add_to_output("historical performance back button clicked")
                    self.baseconditions()

            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit

    def menu_option_6(self, menu_options): #show performance ranking
        self.window.fill(self.white)
        self.draw_game_board()
        self.draw_agency_menu(menu_options)
        summarybuttons = self.draw_summary_prompts("rankings")
        rect = summarybuttons[0]
        rounds = summarybuttons[1]
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    if self.click_box(x, y, rect) == True:
                        self.baseconditions()
                        self.roundchoice = "null"
                        self.agency = "null"
                        self.add_to_output("summary back button clicked")
                    for i in self.menu_buttons:
                        if self.click_circle(x, y, i[0]) == True: #checks if an agency has been clicked
                            agency = i[1]
                            self.add_to_output(f"agency clicked: {agency}")
                            self.agency = agency
                    for i in rounds:
                        if self.click_circle(x, y, i[0]) == True: #checks if a round has been clicked
                            round = i[1]
                            self.add_to_output(f"round clicked: {round}")
                            self.roundchoice = round
                        
                    if self.roundchoice != "null":
                            self.rankings = False
                            self.show_rankings = True
                            self.show_agencies = False

                            


            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit

    def show_performance_rankings(self):
        ranking = self.historical_rankings[self.roundchoice-1]
        if self.endrankings == False:
            rect1 = self.draw_exit("previous")
        if self.endrankings == True:
            rect1 = self.draw_exit("rankings")
        texts = []
        x = 150
        x1 = x-20
        y = 50
        y1 = y-5

        boxheight3 = 25
        boxwidth3 = 100
        boxwidth = 700
        scores = []
        names = []
        count = 1

        agencies = []
        ranking_scores = []
        rangelimit = 0


        text = self.arial2.render(f"This is the school ranking for semester {self.roundchoice} of all schools in the region. Your schools are highlighted.", True, self.black)
        texts.append((text, (x, y)))
        pygame.draw.rect(self.window, self.darkolivegreen3, (x1, y1, boxwidth, boxheight3))
        y += 50
        y1 += 50

        for i in self.agencies:
            agencies.append(i[0])

        for i in ranking:
            if i[1] in agencies:
                colour_box = self.gold
            else:
                colour_box = self.gainsboro 
            text = self.arial2.render(f"Rank {count}: {i[1]}, performance score {i[0]}", True, self.black)
            texts.append((text, (x, y)))
            pygame.draw.rect(self.window, colour_box, (x1, y1, boxwidth, boxheight3))
            y += 30
            y1 += 30
            count += 1


        for i in texts:
            self.window.blit(i[0], i[1])

        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    if self.endrankings == True:
                        self.summary_click_forward(5, rect1)
                    else:
                        self.summary_click_forward(4, rect1)
                    self.add_to_output("Semester summary forward button clicked")

    def menu_option_7(self): #optional function for another menu item (currently removed)
        self.agency = self.agencynames[3]
        self.window.fill(self.white)
        x = 150
        y = 25
        pygame.display.update()
        text = self.arial.render(f"These random events occurred at {self.agency} this semester:", True, self.crimson)
        self.window.blit(text, (300, y))
        y += 25
        for i in self.script_events[1]:
            if i[0] == self.agency:
                text = self.calibri.render(f"{i[1]}", True, self.black)
                self.window.blit(text, (x, y))
                y += 15
        y += 50
        text = self.arial.render(f"These input-based events occurred at {self.agency} this semester:", True, self.crimson)
        self.window.blit(text, (300, y))
        y += 25
        for i in self.script_events[0]:
            if i[0] == self.agency:
                text = self.calibri.render(f"{i[1]}", True, self.black)
                self.window.blit(text, (x, y))
                y += 15
        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    self.add_to_output("menu option 7 back button clicked")
                self.main_menu_action = False
            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit

    def menu_option_8(self): #optional function for another menu item (currently removed)
        self.window.fill(self.white)
        self.agency = self.agencynames[4]
        x = 150
        y = 25
        pygame.display.update()
        text = self.arial.render(f"These random events occurred at {self.agency} this semester:", True, self.crimson)
        self.window.blit(text, (300, y))
        y += 25
        for i in self.script_events[1]:
            if i[0] == self.agency:
                text = self.calibri.render(f"{i[1]}", True, self.black)
                self.window.blit(text, (x, y))
                y += 15
        y += 50
        text = self.arial.render(f"These input-based events occurred at {self.agency} this semester:", True, self.crimson)
        self.window.blit(text, (300, y))
        y += 25
        for i in self.script_events[0]:
            if i[0] == self.agency:
                text = self.calibri.render(f"{i[1]}", True, self.black)
                self.window.blit(text, (x, y))
                y += 15
        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    self.add_to_output("menu option 8 back button clicked")
                self.main_menu_action = False
            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit
            
    def menu_option_9(self): #optional function for another menu item (currently removed)
        self.window.fill(self.white)
        self.agency = self.agencynames[5]
        x = 150
        y = 25
        pygame.display.update()
        text = self.arial.render(f"These random events occurred at {self.agency} this semester:", True, self.crimson)
        self.window.blit(text, (300, y))
        y += 25
        for i in self.script_events[1]:
            if i[0] == self.agency:
                text = self.calibri.render(f"{i[1]}", True, self.black)
                self.window.blit(text, (x, y))
                y += 15
        y += 50
        text = self.arial.render(f"These input-based events occurred at {self.agency} this semester:", True, self.crimson)
        self.window.blit(text, (300, y))
        y += 25
        for i in self.script_events[0]:
            if i[0] == self.agency:
                text = self.calibri.render(f"{i[1]}", True, self.black)
                self.window.blit(text, (x, y))
                y += 15
        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    self.add_to_output("menu option 8 back button clicked")
                self.main_menu_action = False
            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit
            
    def menu_option_10(self): #optional function for another menu item (currently removed)
        self.window.fill(self.white)
        self.agency = self.agencynames[6]
        x = 150
        y = 25
        pygame.display.update()
        text = self.arial.render(f"These random events occurred at {self.agency} this semester:", True, self.crimson)
        self.window.blit(text, (300, y))
        y += 25
        for i in self.script_events[1]:
            if i[0] == self.agency:
                text = self.calibri.render(f"{i[1]}", True, self.black)
                self.window.blit(text, (x, y))
                y += 15
        y += 50
        text = self.arial.render(f"These input-based events occurred at {self.agency} this semester:", True, self.crimson)
        self.window.blit(text, (300, y))
        y += 25
        for i in self.script_events[0]:
            if i[0] == self.agency:
                text = self.calibri.render(f"{i[1]}", True, self.black)
                self.window.blit(text, (x, y))
                y += 15
        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    self.add_to_output("menu option 8 back button clicked")
                self.main_menu_action = False
            if event.type == pygame.QUIT:
                self.add_final_output()
                self.rename_output()
                self.post_output()
                raise SystemExit
            


    def create_game_board(self): #create areas in the game that can be individually updated
        rect1 = pygame.Rect(120, 0, 20, 720) # bar separating left and right screens
        rect2 = pygame.Rect(140, 100, 940, 620) #main game screen
        rect3 = pygame.Rect(140, 0, 415, 100) #total feedback screen
        rect4 = pygame.Rect(555, 0, 525, 100) #agency feedback screen
        rect5 = pygame.Rect(0, 0, 120, 720) #agency menu screen
        self.board.append(rect1)
        self.board.append(rect2)
        self.board.append(rect3)
        self.board.append(rect4)
        self.board.append(rect5)

    def draw_budget_options(self, budget_options: list): #draw the budget action choices and labels
        for i in budget_options:
            pygame.draw.rect(self.window, i[1], i[0])
        for i in self.budgeting_labels1:
            text = self.arial.render(i[0], True, self.black)
            self.window.blit(text, (i[1], i[2]))
        for i in self.budgeting_labels2:
            text = self.calibri.render(i[0], True, (i[3]))
            self.window.blit(text, (i[1], i[2]))
        


    def draw_game_board(self): #draw different game areas
        pygame.draw.rect(self.window, self.purple, self.board[0])
        pygame.draw.rect(self.window, self.white, self.board[1])
        pygame.draw.rect(self.window, self.white, self.board[2])
        pygame.draw.rect(self.window, self.white, self.board[3])
        pygame.draw.rect(self.window, self.navyblue, self.board[4])


    def draw_feedback(self, feedback: tuple, colour: tuple): #draw the monitors for player feedback

        if "null" not in feedback[1]:
            try:
                pygame.draw.rect(self.window, colour, feedback[0])
                text = self.arial.render(feedback[1], True, feedback[2])
                self.window.blit(text, (feedback[0][0]+10, feedback[0][1]+10))
            except TypeError:
                text = self.arial.render(feedback[0], True, feedback[2])
                self.window.blit(text, (feedback[1][0]+10, feedback[1][1]+10))

    def create_game_menu(self): #create a menu for selecting different agencies
        menu_options = []
        y = 55
        x = 60
        for i in self.agencies:
            menu_options.append(((x, y), i))
            self.menu_buttons.append(((x, y, self.radius), i[0]))
            text = i[0]
            text_width, text_height = self.calibri.size(text)
            self.agency_labels.append((text, x-(text_width/2), y-text_height/2))
            y += 100
            y += (7-self.agency_count)*20
        return menu_options

    def update_game_feedback(self): #provides an updating counter which follows the budget available in total and for a given agency
        feedback_monitors = []
        x = 160
        y = 10
        boxheight = 75
        boxwidth = 250
        x2 = 435
        x3 = 710
        if self.total_budget < 0:
            colour = self.crimson
        else:
            colour = self.black
        feedback_monitors.append(((x, y, boxwidth, boxheight), (f"Total budget this semester: {self.total_budget} €"), colour))
        time = int(self.roundtimer+1-(self.time-self.roundtime))
        if time > 10:
            feedback_monitors.append(((x3, y, boxwidth, boxheight), (f"Time left in this semester: {time}"), colour))
        else:
            feedback_monitors.append(((x3, y, boxwidth, boxheight), (f"Auto-progress in {time} seconds"), colour))

        colour = self.black
        if self.agency != "null":
            if self.agency_stats[self.agency][0] < 0:
                colour = self.crimson
            else:
                colour = self.black
            feedback_monitors.append(((x2, y, boxwidth, boxheight), (f"{self.agency} budget this semester: {self.agency_stats[self.agency][0]} €"), colour))
            y += 25
            colour = self.black
            if (self.agency_stats[self.agency][4] == "Understaffed"
                or self.agency_stats[self.agency][5] == "Equipment shortage" 
                or self.agency_stats[self.agency][6] == "No events planned" 
                or self.agency_stats[self.agency][7] == "Under budget" 
                or self.agency_stats[self.agency][8] == "low staff satisfaction" 
                or self.agency_stats[self.agency][9] == "low staff performance" 
                or self.agency_stats[self.agency][10] == "high staff stress" 
                or self.agency_stats[self.agency][11] == "low student satisfaction" #low_student_satisfaction
                or self.agency_stats[self.agency][12] == "poor learning results (reading)" #low_student_reading
                or self.agency_stats[self.agency][13] == "poor learning results (math)"
                or self.agency_stats[self.agency][14] == "poor learning results (science)" #low_student_science
                or self.agency_stats[self.agency][15] == "poor learning results (overall)" #low_student_overall
                or self.agency_stats[self.agency][16] == "high student stress"):                
                feedback_monitors.append((f"There are problems to solve at {self.agency}!", (x, y, boxwidth, boxheight), colour))
            else:
                feedback_monitors.append((f"Everything is fine at {self.agency}!", (x, y, boxwidth, boxheight), colour))
            feedback_monitors.append((f"{self.agency} performance score: {self.agency_scores[self.agency]}/100", (x2, y, boxwidth, boxheight), colour))
        if self.agency == "null":
            feedback_monitors.append(((x2, y, boxwidth, boxheight), f"Current semester: {self.round_number} of 10", colour))
            y += 25
            feedback_monitors.append((f"Your average performance score: {int(sum(self.score_total)/len(self.score_total))}", (x, y, boxwidth, boxheight), colour))
            feedback_monitors.append((f"Current performance score: {self.score}/100", (x2, y, boxwidth, boxheight), colour))
        return feedback_monitors

    def create_main_menu_options(self): #creates the main menu options the player can choose
        self.main_menu_options = []
        self.main_menu_labels = []
        self.main_menu_options.append(("Receive game instructions", 0))
        self.main_menu_options.append(("Receive budget option instructions", 1))
        self.main_menu_options.append(("Receive summary of game events", 2))
        self.main_menu_options.append(("Progress to the next semester", 3))
        self.main_menu_options.append(("View perfomance reports", 4))
        self.main_menu_options.append(("View school rankings", 5))
        #self.main_menu_options.append(("this is a seventh main menu text", 6))
        #self.main_menu_options.append(("this is an eighth main menu text", 7))


    def create_main_menu(self): #creates the main menu based on the selected menu options
        self.main_menu_buttons = []
        self.create_main_menu_options()
        menu_options = []
        x = 160
        y = 150
        boxheight = 100
        boxwidth = 275
        boxwidth2 = 425
        boxheight2 = 300
        count = 0
        for i in self.main_menu_options:
            menu_options.append((x, y, boxwidth, boxheight))
            text = i[0]
            self.main_menu_labels.append((text, x+5, y+5))
            self.main_menu_buttons.append(((x, y, boxwidth, boxheight), count))
            x += boxwidth + 25
            if x + boxwidth > 1080:
                x = 160
                y += boxheight + 25
            count += 1
        menu_options.append((x, y, boxwidth2, boxheight2))
        x += boxwidth2 + 50
        menu_options.append((x, y, boxwidth2, boxheight2))

        return menu_options

    def draw_main_menu(self, menu_options: list): #draws the main menu
        self.main_menu_feedback = []
        count = 0
        for i in menu_options:
            if count < 6:
                pygame.draw.rect(self.window, self.tan, i)
            else:
                pygame.draw.rect(self.window, self.orange, i)
            count += 1

        y = 400
        x = 165
        if self.total_budget >= 0:
            text = "You are within your semester budget!"
        elif self.total_budget < 0:
            text = "You are below your semester budget!"
        self.main_menu_feedback.append((text, x+5, y+5))
        y += 25
        monitor = []
        for i in self.agency_stats:
            try:
                if self.agency_stats[i][7] == "Under budget":
                    monitor.append(i)
            except IndexError:
                pass
        if len(monitor) > 0:
            text = "Schools under budget:"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
            text = " "
            if len(monitor) > 4:
                count = 0
                for i in monitor:
                    text += i + ", "
                    count += 1
                    if count == 4:
                        text = text[:-1]
                        self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                        y += 15
                        text = " "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            if len(monitor) < 5:
                for i in monitor:
                    text += i + ", "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            y += 25
        else:
            text = "All schools are within their budget!"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 25
            text = ""
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
        monitor = []
        for i in self.agency_stats:
            try:
                if self.agency_stats[i][4] == "Understaffed":
                    monitor.append(i)
            except IndexError:
                pass
        if len(monitor) > 0:
            text = "Schools understaffed:"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
            text = " "
            if len(monitor) > 4:
                count = 0
                for i in monitor:
                    text += i + ", "
                    count += 1
                    if count == 4:
                        text = text[:-1]
                        self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                        y += 15
                        text = " "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            if len(monitor) < 5:
                for i in monitor:
                    text += i + ", "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            y += 25
        else:
            text = "All schools are fully staffed!"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 25
            text = ""
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
        monitor = []
        for i in self.agency_stats:
            try:
                if self.agency_stats[i][5] == "Equipment shortage":
                    monitor.append(i)
            except IndexError:
                pass
        if len(monitor) > 0:
            text = "Schools with an equipment shortage:"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
            text = " "
            if len(monitor) > 4:
                count = 0
                for i in monitor:
                    text += i + ", "
                    count += 1
                    if count == 4:
                        text = text[:-1]
                        self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                        y += 15
                        text = " "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            if len(monitor) < 5:
                for i in monitor:
                    text += i + ", "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            y += 25
        else:
            text = "All schools have enough equipment!"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 25
            text = ""
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
        monitor = []
        for i in self.agency_stats:
            try:
                if self.agency_stats[i][6] == "No events planned":
                    monitor.append(i)
            except IndexError:
                pass
        if len(monitor) > 0:
            text = "Schools without events planned:"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
            text = " "
            if len(monitor) > 4:
                count = 0
                for i in monitor:
                    text += i + ", "
                    count += 1
                    if count == 4:
                        text = text[:-1]
                        self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                        y += 15
                        text = " "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            if len(monitor) < 5:
                for i in monitor:
                    text += i + ", "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            y += 25
        else:
            text = "All schools have events planned!"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 25
            text = ""
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
        text = ""
        count = 0
        monitor = []
        for i in self.staff_stats:
            if self.staff_stats[i][5] > self.stress_standard_low:
                monitor.append(i)
        if len(monitor) > 0:
            text = f"Schools with staff stress above {self.stress_standard_low}:"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
            text = " "
            if len(monitor) > 4:
                count = 0
                for i in monitor:
                    text += i + ", "
                    count += 1
                    if count == 4:
                        text = text[:-1]
                        self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                        y += 15
                        text = " "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            if len(monitor) < 5:
                for i in monitor:
                    text += i + ", "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                y += 15
            y += 25
        else:
            text = f"No schools have staff stress above {self.stress_standard_low}!"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 25
            text = ""
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
        y = 400
        x = 635
        text = ""
        count = 0
        monitor = []
        for i in self.staff_stats:
            if self.staff_stats[i][3] < self.satisfaction_standard_high:
                monitor.append(i)
        if len(monitor) > 0:
            text = f"Schools with staff satisfaction below {self.satisfaction_standard_high}:"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 25
            text = " "
            if len(monitor) > 4:
                count = 0
                for i in monitor:
                    text += i + ", "
                    count += 1
                    if count == 4:
                        text = text[:-1]
                        self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                        y += 15
                        text = " "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            if len(monitor) < 5:
                for i in monitor:
                    text += i + ", "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                y += 15
            y += 15
        else:
            text = f"No schools have staff satisfaction below {self.satisfaction_standard_high}!"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
            text = ""
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15

        text = f"Schools with staff performance below {self.performance_standard_high}:"
        text = ""
        count = 0
        monitor = []
        for i in self.staff_stats:
            if self.staff_stats[i][4] < self.performance_standard_high:
                monitor.append(i)
        if len(monitor) > 0:
            text = f"Schools with staff performance below {self.performance_standard_high}:"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 25
            text = " "
            if len(monitor) > 4:
                count = 0
                for i in monitor:
                    text += i + ", "
                    count += 1
                    if count == 4:
                        text = text[:-1]
                        self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                        y += 15
                        text = " "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            if len(monitor) < 5:
                for i in monitor:
                    text += i + ", "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                y += 15
            y += 15
        else:
            text = f"No schools have staff performance below {self.performance_standard_high}!"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
            text = ""
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15

        text = ""
        count = 0
        monitor = []
        for i in self.staff_stats:
            if self.student_stats[i][6] < self.satisfaction_standard_high:
                monitor.append(i)
        if len(monitor) > 0:
            text = f"Schools with student satisfaction below {self.satisfaction_standard_high}:"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 25
            text = " "
            if len(monitor) > 4:
                count = 0
                for i in monitor:
                    text += i + ", "
                    count += 1
                    if count == 4:
                        text = text[:-1]
                        self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                        y += 15
                        text = " "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            if len(monitor) < 5:
                for i in monitor:
                    text += i + ", "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                y += 15
            y += 15
        else:
            text = f"No schools have student satisfaction below {self.satisfaction_standard_high}!"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
            text = ""
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
        text = ""
        count = 0
        monitor = []
        for i in self.staff_stats:
            if self.student_stats[i][10] < self.learning_standard_high:
                monitor.append(i)
        if len(monitor) > 0:
            text = f"Schools with overall learning below {self.learning_standard_high}:"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 25
            text = " "
            if len(monitor) > 4:
                count = 0
                for i in monitor:
                    text += i + ", "
                    count += 1
                    if count == 4:
                        text = text[:-1]
                        self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                        y += 15
                        text = " "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            if len(monitor) < 5:
                for i in monitor:
                    text += i + ", "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                y += 15
            y += 15
        else:
            text = f"No schools have overall learning below {self.learning_standard_high}!"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
            text = ""
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
        text = ""
        count = 0
        monitor = []
        for i in self.staff_stats:
            if self.student_stats[i][11] > self.stress_standard_low:
                monitor.append(i)
        if len(monitor) > 0:
            text = f"Schools with student stress above {self.stress_standard_low}:"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 25
            text = " "
            if len(monitor) > 4:
                count = 0
                for i in monitor:
                    text += i + ", "
                    count += 1
                    if count == 4:
                        text = text[:-1]
                        self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                        y += 15
                        text = " "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
            if len(monitor) < 5:
                for i in monitor:
                    text += i + ", "
                text = text[:-2]
                self.main_menu_feedback.append(((text, x+5, y+10), "calibri"))
                y += 15
            y += 15
        else:
            text = f"No schools have student stress above {self.stress_standard_low}!"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
            text = ""
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
        for i in self.main_menu_labels:
            text = self.arial.render(i[0], True, self.black)
            self.window.blit(text, (i[1], i[2]))
        
        for i in self.main_menu_feedback:
            try:
                text = self.arial.render(i[0], True, self.black)
                self.window.blit(text, (i[1], i[2]))
            except TypeError:
                text = self.calibri.render(i[0][0], True, self.crimson)
                self.window.blit(text, (i[0][1], i[0][2]))
                pass

    def create_budgeting_menu(self, agency: str, condition): #creates the budget action menu based on the selected options

        if condition == "action":
            menu_options = []
            x = 160
            y = 100
            boxheight = 60
            boxwidth = 260
            boxheight2 = 250
            x2 = x + boxwidth + 50
            y2 = 640
            for i in self.budget_options[agency]:
                if i[1] < 0:
                    menu_options.append(((x, y, boxwidth, boxheight), self.cornflowerblue))
                else:
                    menu_options.append(((x, y, boxwidth, boxheight), self.tomato))

                text = (i[0])
                self.budgeting_labels1.append((text, x+5, y+5))
                cost = i[1]
                if cost > 0:
                    action_cost_label = f"Cost: {cost} €"
                else:
                    action_cost_label = f"Money saved: {-cost} €"
                if text == "increase funding":
                    action_cost_label = f"Cost: {cost} €"
                if text == "decrease funding":
                    action_cost_label = f"Money saved: {-cost} €"
                self.budgeting_labels1.append((action_cost_label, x+5, y+30))
                self.budget_buttons.append(((x, y, boxwidth, boxheight), text, cost))
                x += boxwidth + 50
                if x + boxwidth > 1080:
                    x = 160
                    y += boxheight + 25
            
            count = 0
            for i in self.agency_feedback[agency]:
                menu_options.append(((x, y, boxwidth+25, boxheight2), self.gold))
                text = i
                basecolour = self.black
                self.budgeting_labels2.append((text, x+5, y+10, basecolour))
                if count == 0:
                    number = str(self.agency_stats[agency][1])
                    if self.agency_stats[self.agency][4] == "Understaffed":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][4] == "Staffed":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    if float(number) >= 0:
                        text = f"Total staff: {number} (staffed)"
                        self.budgeting_labels2.append((text, x+5, y+30, colour))
                    if float(number) < 0:
                        text = f"Total staff:  {number} (understaffed)"
                        self.budgeting_labels2.append((text, x+5, y+30, colour))
                    text = f"Staff satisfaction: {self.staff_stats[agency][3]}/100"
                    if self.agency_stats[self.agency][8] == "low staff satisfaction":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][8] == "high staff satisfaction":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+80, colour))
                    text = f"Staff performance: {self.staff_stats[agency][4]}/100"
                    if self.agency_stats[self.agency][9] == "low staff performance":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][9] == "high staff performance":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+130, colour))
                    text = f"Staff stress levels: {self.staff_stats[agency][5]}/100"
                    if self.agency_stats[self.agency][10] == "high staff stress":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][10] == "low staff stress":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+180, colour))
                    text = f"Student stress levels: {self.student_stats[agency][11]}/100"
                    if self.agency_stats[self.agency][16] == "high student stress":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][16] == "low student stress":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+230, colour))
                if count == 1:
                    number = str(self.agency_stats[agency][2])
                    if self.agency_stats[self.agency][5] == "Equipment shortage":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][5] == "Sufficient equipment":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    if float(number) > 0:
                        text = f"Total value: {number} € (enough)"
                        self.budgeting_labels2.append((text, x+5, y+30, colour))
                    if float(number) < 0:
                        text = f"Total value: {number} € (shortage)"
                        self.budgeting_labels2.append((text, x+5, y+30, colour))
                    
                    text = f"Student performance (reading): {self.student_stats[agency][7]}/100"
                    if self.agency_stats[self.agency][13] == "poor learning results (reading)":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][12] == "good learning results (reading)":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+80, colour))
                    text = f"Student performance (math): {self.student_stats[agency][8]}/100"
                    if self.agency_stats[self.agency][14] == "poor learning results (math)":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][13] == "good learning results (math)":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+130, colour))
                    text = f"Student performance (science): {self.student_stats[agency][9]}/100"
                    if self.agency_stats[self.agency][15] == "poor learning results (science)":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][14] == "good learning results (science)":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+180, colour))
                    text = f"Student performance (overall): {self.student_stats[agency][10]}/100"
                    if self.agency_stats[self.agency][15] == "poor learning results (overall)":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][15] == "good learning results (overall)":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+230, colour))

                if count == 2:
                    number = int(str(self.agency_stats[agency][3]))
                    if self.agency_stats[self.agency][6] == "No events planned":
                        colour = self.crimson
                        text = f"No events are currently planned!"
                        self.budgeting_labels2.append((text, x+5, y+30, colour))
                    elif self.agency_stats[self.agency][6] == "Events planned":
                        colour = self.forestgreen
                        text = f"Total events planned: {number}"
                        self.budgeting_labels2.append((text, x+5, y+30, colour))
                    text = f"Upcoming events:"
                    self.budgeting_labels2.append((text, x+5, y+55, basecolour))
                    z = 80
                    for i in self.events[agency]:
                        if i[0] != "null":
                            text = f"{i[0]} planned for day {i[1]}"
                            self.budgeting_labels2.append((text, x+5, y+z, self.royalblue3))

                        if i[0] == "null":
                            text = f"No event planned for day {i[1]}"
                            self.budgeting_labels2.append((text, x+5, y+z, self.crimson))
                        z += 25
                    text = f"Student satisfaction: {self.student_stats[agency][6]}"
                    if self.agency_stats[self.agency][11] == "low student satisfaction":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][11] == "high student satisfaction":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+205, colour))
                x += boxwidth + 50
                count += 1
            menu_options.append(((x2, y2, boxwidth, boxheight), (self.tan)))
            text = "Exit to main menu"
            self.budgeting_labels1.append((text, x2+5, y2+5, boxwidth, boxheight))
            self.budget_buttons.append(((x2, y2, boxwidth, boxheight), "exit", "null"))
        
        if condition == "information":
            menu_options = []
            x = 100
            y = 200
            y2 = 640
            boxheight = 60
            boxwidth = 260
            x2 = x + boxwidth + 50

            for i in self.budget_options[agency]:
                if i[1] < 0:
                    menu_options.append(((x, y, boxwidth, boxheight), self.cornflowerblue))
                else:
                    menu_options.append(((x, y, boxwidth, boxheight), self.tomato))
                text = (i[0])
                self.budgeting_labels1.append((text, x+5, y+5))
                cost = i[1]
                if cost > 0:
                    action_cost_label = f"Cost: {cost} €"
                else:
                    action_cost_label = f"Money saved: {-cost} €"
                if text == "increase funding":
                    action_cost_label = f"Cost: {cost} €"
                if text == "decrease funding":
                    action_cost_label = f"Money saved: {-cost} €"
                self.budgeting_labels1.append((action_cost_label, x+5, y+30))
                self.budget_buttons.append(((x, y, boxwidth, boxheight), text, cost))
                x += boxwidth + 50
                if x + boxwidth > 1080:
                    x = 100
                    y += boxheight + 25
            menu_options.append(((x2, y2, boxwidth, boxheight), (self.tan)))
            text = "Exit to main menu"
            self.budgeting_labels1.append((text, x2+5, y2+5, boxwidth, boxheight))
            self.budget_buttons.append(((x2, y2, boxwidth, boxheight), "exit", "null"))
        return menu_options

    def click_circle(self, x: int, y: int, circle: tuple): #checks if a click by the player is in a circle
        circlex = circle[0]
        circley = circle[1]
        radius = circle[2]
        if abs(x - circlex) < radius and abs(y - circley) < radius:
            return True
        return False
            
    def click_box(self, x: int, y: int, box: pygame.rect): #checks if a click by the player is in a rectangle
        points_in_boxx = []
        points_in_boxy = []
        boxx = box[0]
        boxy = box[1]
        boxwidth = box[2]
        boxheight = box[3]
        count = 0
        for i in range(boxwidth):
            points_in_boxx.append(boxx+i)
        for i in range(boxheight):
            points_in_boxy.append(boxy+i)
        for i in points_in_boxx:
            if x == i:
                count += 1
        for i in points_in_boxy:
            if y == i:
                count += 1
        if count == 2:
            return True
        return False  
    



    
    def check_caption(self):
        pygame.display.set_caption(f"Welcome to the budget game!")
        return
        if self.caption1 == True:
            pygame.display.set_caption(f"Time left in this semester: {int(self.roundtimer+1-(self.time-self.roundtime))}")
        elif self.caption2 == True:
            pygame.display.set_caption(f"Time until the next summary screen: {int(self.roundinterval+1-(self.time-self.intervaltime))} seconds")
        elif self.caption3 == True:
            pygame.display.set_caption(f"Time until the next semester: {int(self.roundinterval+1-(self.time-self.intervaltime2))} seconds")
        elif self.caption4 == True:
            pygame.display.set_caption(f"Time until the next summary screen: {int(self.summaryinterval+1-(self.time-self.intervaltime))} seconds")
        elif self.caption5 == True:
            pygame.display.set_caption(f"Time until the game returns to the previous screen: {int(self.summaryinterval+1-(self.time-self.intervaltime2))} seconds")
        elif self.caption6 == True:
            pygame.display.set_caption(f"Time until the game returns to the previous screen: {int(self.summaryinterval+1-(self.time-self.intervaltime))} seconds")
        elif self.caption7 == True:
            pygame.display.set_caption(f"Welcome to the budget game!")
        elif self.caption8 == True:
            pygame.display.set_caption(f"Time until the next semester: {int(self.summaryinterval+1-(self.time-self.intervaltime))} seconds")

    def instruction_video(self):
        return
        self.video = Video("vidmaker.mp4")
        self.video.play()
        self.vidintro = False



game = BudgetGame()
game.check_participant_number()
game.create_agencies()
game.create_game_board()
game.create_budget_options()
game.create_agency_feedback()
game.create_output_file()
game.main_menu_action = True
game.base_scripts()
game.create_scripts()
game.create_agency_stats()
game.check_score()
game.create_ranking()
game.historical_rankings.append(game.schoolranking)
pygame.font.get_fonts()
game.menu_options = game.create_game_menu() #creates the agency selection menu
game.main_menus = game.create_main_menu()
async def main():
    while True:
        game.check_caption()
        game.check_score()
        feedback = game.update_game_feedback()
        game.add_to_output("null input")
        game.window.fill(game.white) #fills the game screen with white
        if game.main_menu_action == False:
            game.draw_game_board()
        if game.start == True and game.intro_style == "video" and game.vidintro == True:
            game.instruction_video()
        if game.start == True and game.intro_style == "text":
            game.menu_option_1()
        if game.show_vid == True and game.intro_style == "video":
            try:
                game.video.draw_to(game.window, (0, 0))
            except TypeError:
                game.baseconditions()
        if game.instruction_2 == True:
            game.instruction_screen_2()
        if game.show_effects == True:
            game.show_budget_effects()
        if game.show_event_effects == True:
            game.script_effects()
        if game.information == True:
            game.menu_option_2(game.menu_options)
        if game.summary == True:
            game.menu_option_3(game.menu_options)
        if game.roundsummary1 == True:
            game.agency = game.agencynames[0]
            game.menu_option_4()
        if game.roundsummary2 == True:
            game.agency = game.agencynames[1]
            game.menu_option_4()
        if game.roundsummary3 == True:
            game.agency = game.agencynames[2]
            game.menu_option_4()
        if game.roundsummary4 == True:
            game.agency = game.agencynames[3]
            game.menu_option_4()
        if game.roundsummary5 == True:
            game.agency = game.agencynames[4]
            game.menu_option_4()
        if game.roundsummary6 == True:
            game.agency = game.agencynames[5]
            game.menu_option_4()
        if game.roundsummary7 == True:
            game.agency = game.agencynames[6]
            game.menu_option_4()
        if game.historical == True:
            game.menu_option_5(game.menu_options)
        if game.rankings == True:
            game.menu_option_6(game.menu_options)
        if game.show_rankings == True:
            game.show_performance_rankings()
        if game.history_information == True:
            game.historical_performance(game.agency)
        if game.show_agencies == True:
            game.check_status()
            game.draw_agency_menu(game.menu_options)
        if game.show_main_menu == True:
            game.draw_main_menu(game.main_menus)
        if game.show_budget_options == True:
            game.draw_budget_options(game.budget_menu)
        if game.agency_summary == True:
            game.show_agency_summary(game.roundchoice)
        if game.agency_summary_2 == True:
            game.show_agency_summary_2(game.roundchoice)
        if game.postgame == True:
            game.show_postgame()
        if game.roundover == True:
            game.round_summary()
        if game.show_feedback == True:
            for i in feedback:
                game.draw_feedback(i, ("cornsilk"))
        if game.first_time == False and game.insummary == False and abs(game.time-game.roundtime)>game.roundtimer and game.round_number < game.roundstandard + 1:
                game.baseconditions()                
                game.increase_click_counter()
                game.add_to_output("automatic progression to next round")
                game.main_menu_action = True
                game.instruction_2 = False
                game.information = False
                game.summary = False
                game.agency_summary = False
                game.agency_summary_2 = False
                game.show_agencies = False
                game.show_effects = False
                game.show_event_effects = False
                game.show_main_menu = False
                game.show_feedback = False
                game.roundsummary1 = False
                game.roundsummary2 = False
                game.show_budget_options = False
                game.choice = 3
                game.advance_game_round()
                game.roundsummary1 = True
                game.intervaltime = game.time
                game.caption1 = False
                game.caption7 = True
                game.insummary = True
    
                

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    if game.agency != "null":
                        for i in game.menu_buttons:
                            if game.click_circle(x, y, i[0]) == True: #checks if an agency has been clicked
                                if game.summary == False:
                                    game.show_main_menu = False
                                    game.show_budget_options = True
                                game.agency = i[1]
                                feedback = game.update_game_feedback()
                                game.add_to_output(f"agency {game.agency} clicked")
                        for i in game.budget_buttons:
                            if game.click_box(x, y, i[0]) == True: #checks if a budget option has been clicked
                                option = i[1]
                                cost = i[2]
                                if game.agency_stats[game.agency][3] == 0:
                                    game.adjust_agency_stats(game.agency, cost, option, game.menu_options)
                                    game.add_to_output(f"budget option {option} clicked (events at zero)")
                                else:
                                    game.adjust_agency_stats(game.agency, cost, option, game.menu_options)
                                    game.add_to_output(f"budget option {option} clicked")
                                    
                                if option == "exit":
                                    game.show_budget_options = False
                                    game.show_main_menu = True
                                    game.agency = "null"
                                    
                    for i in game.menu_buttons:
                        if game.click_circle(x, y, i[0]) == True and game.show_budget_options != True: #checks if an agency has been clicked
                            if game.summary == False:
                                game.show_main_menu = False
                                game.show_budget_options = True
                            game.agency = i[1]
                            feedback = game.update_game_feedback()
                            game.add_to_output(f"agency {game.agency} clicked")
                            
                    if game.show_main_menu == True:
                        for i in game.main_menu_buttons:
                            if game.click_box(x, y, i[0]) == True:
                                game.show_agencies = False
                                game.show_budget_options = False
                                game.show_main_menu = False
                                game.show_feedback = False
                                game.main_menu_action = True
                                game.choice = i[1]
                    
                    if game.main_menu_action == True:
                        if game.choice == 0:
                            game.add_to_output("menu option 1 clicked")
                            game.start = True
                            game.show_vid = True
                            game.vidintro = True
                        if game.choice == 1:
                            game.add_to_output("menu option 2 clicked")
                            game.information = True
                        if game.choice == 2:
                            game.add_to_output("menu option 3 clicked")
                            game.summary = True
                            game.show_agencies = True
                        if game.choice == 3:
                            game.baseconditions()
                            game.choice = "null"
                            game.add_to_output("menu option 4 clicked")
                            game.main_menu_action = True
                            game.instruction_2 = False
                            game.information = False
                            game.summary = False
                            game.agency_summary = False
                            game.agency_summary_2 = False
                            game.show_agencies = False
                            game.show_effects = False
                            game.show_event_effects = False
                            game.show_main_menu = False
                            game.show_feedback = False
                            game.roundsummary1 = False
                            game.roundsummary2 = False
                            game.show_budget_options = False
                            game.advance_game_round()
                            game.roundsummary1 = True
                            game.insummary = True
                            game.intervaltime = game.time
                            game.caption1 = False
                            game.caption7 = True
                        if game.choice == 4:
                            game.add_to_output("menu option 5 clicked")
                            game.historical = True
                        if game.choice == 5:
                            game.add_to_output("menu option 6 clicked")
                            game.rankings = True

            if event.type == pygame.QUIT:
                game.add_final_output()
                game.rename_output()
                game.post_output()
                raise SystemExit

        game.budget_menu = []
        try:
            game.budgeting_labels1 = []
            game.budgeting_labels2 = []
            game.budget_buttons = []
            game.budget_menu = game.create_budgeting_menu(game.agency, "action")
        except KeyError:
            pass
        game.clock.tick(60)
        game.time += 1/60
        pygame.display.update()
        await asyncio.sleep(0)
asyncio.run(main())