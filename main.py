import pygame
import random
import asyncio
import urllib
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request
import json
import uuid
import js
import os
import io
import webbrowser
import datetime
import uuid



class RequestHandler:
    """
    WASM compatible request handler
    auto-detects emscripten environment and sends requests using JavaScript Fetch API
    """

    GET = "GET"
    POST = "POST"
    _js_code = ""
    _init = False

    def __init__(self):
        self.is_emscripten = sys.platform == "emscripten"
        if not self._init:
            self.init()
        self.debug = True
        self.result = None
        if not self.is_emscripten:
            try:
                import requests

                self.requests = requests
            except ImportError:
                pass

    def init(self):
        if self.is_emscripten:
            self._js_code = """
    window.Fetch = {}
    // generator functions for async fetch API
    // script is meant to be run at runtime in an emscripten environment
    // Fetch API allows data to be posted along with a POST request
    window.Fetch.POST = function * POST (url, data)
    {
    // post info about the request
    console.log('POST: ' + url + 'Data: ' + data);
    var request = new Request(url, {headers: {'Accept': 'application/json','Content-Type': 'application/json'},
        method: 'POST',
        body: data});
    var content = 'undefined';
    fetch(request)
    .then(resp => resp.text())
    .then((resp) => {
        console.log(resp);
        content = resp;
    })
    .catch(err => {
        // handle errors
        console.log("An Error Occurred:")
        console.log(err);
    });
    while(content == 'undefined'){
        yield;
    }
    yield content;
    }
    // Only URL to be passed
    // when called from python code, use urllib.parse.urlencode to get the query string
    window.Fetch.GET = function * GET (url)
    {
    console.log('GET: ' + url);
    var request = new Request(url, { method: 'GET' })
    var content = 'undefined';
    fetch(request)
    .then(resp => resp.text())
    .then((resp) => {
        console.log(resp);
        content = resp;
    })
    .catch(err => {
        // handle errors
        console.log("An Error Occurred:");
        console.log(err);
    });
    while(content == 'undefined'){
        // generator
        yield;
    }

    yield content;
    }
            """
            try:
                platform.window.eval(self._js_code)
            except AttributeError:
                self.is_emscripten = False

    @staticmethod
    def read_file(file):
        # synchronous reading of file intended for evaluating on initialization
        # use async functions during runtime
        with open(file, "r") as f:
            data = f.read()
        return data

    @staticmethod
    def print(*args, default=True):
        try:
            for i in args:
                platform.window.console.log(i)
        except AttributeError:
            pass
        except Exception as e:
            return e
        if default:
            print(*args)

    async def get(self, url, params=None, doseq=False):
        # await asyncio.sleep(5)
        if params is None:
            params = {}
        if self.is_emscripten:
            query_string = urlencode(params, doseq=doseq)
            await asyncio.sleep(0)
            content = await platform.jsiter(platform.window.Fetch.GET(url + "?" + query_string))
            if self.debug:
                self.print(content)
            self.result = content
        else:
            self.result = self.requests.get(url, params).text
        return self.result

    # def get(self, url, params=None, doseq=False):
    #     return await self._get(url, params, doseq)

    async def post(self, url, data=None):
        if data is None:
            data = {}
        if self.is_emscripten:
            await asyncio.sleep(0)
            content = await platform.jsiter(platform.window.Fetch.POST(url, json.dumps(data)))
            if self.debug:
                self.print(content)
            self.result = content
        else:
            self.result = self.requests.post(
                url, data, headers={"Accept": "application/json", "Content-Type": "application/json"}
            ).text
        return self.result

    # def post(self, url, data=None):
    #     return await self._post(url, data)

class BudgetGame(): #create class for the game; class includes internal variables that are tracked throughout the game
    def __init__(self): #inititate the class
        pygame.init()
        self.output_tracker = 0
        self.treatment = False #condition to select participants for treatment condition
        self.satisfaction_standard_high = 90 #standard to trigger high satisfaction event
        self.satisfaction_standard_low = 20 #standard to trigger low satisfaction event
        self.satisfaction_standard_mid = 70 #standard to trigger mid satisfaction event
        self.performance_standard_high = 90 #standard to trigger high performance event
        self.performance_standard_low = 20 #standard to trigger low performance event
        self.performance_standard_mid = 70 #standard to trigger mid performance event
        self.stress_standard_high = 90 #standard to trigger high stress event
        self.stress_standard_low = 20 #standard to trigger low stress event
        self.stress_standard_mid = 40 #standard to trigger mid stress event
        self.learning_standard_high = 90 #standard to trigger high learning event
        self.learning_standard_low = 20 #standard to trigger low learning event
        self.learning_standard_mid = 70 #standard to trigger mid learning event
        self.first_time = True #condition for starting the game for the first time
        self.agency_count = 0 #how many agencies are in the game
        self.roundinterval = 3 #how long is the timer for round summaries in seconds
        self.summaryinterval = 10 #how long is the timer for eventg summaries in seconds (currently obsolete)
        self.roundtimer = 300 #how much time do players have in the game in seconds per round
        self.roundtime = 5 #time in a given round
        self.clock = pygame.time.Clock() #function to advance time
        self.time = 0 #total time in the game
        self.intervaltime = 0 #time for given timers
        self.window_height = 720 #height of game window
        self.window_width = 1080 #width of game window
        self.window = pygame.display.set_mode((self.window_width, self.window_height)) #game window
        self.agency_labels = [] #labels used in agency menu
        self.agencies = [] #list of agencies used in the game
        self.news_archive = {} #dictionary of news reprots in the game
        self.agency_stats = {} #monitors the budget, staff and functional equipment for each agency
        self.staff_stats = {} #monitors the staff happiness etc for each agency
        self.student_stats = {} #monitors the student satisfaction, learning outcomes etc for each agency
        self.initial_budget = 15000 #starting budget
        self.budget_standard = 15000 #change in total budget per round
        self.total_budget = self.initial_budget #total budget
        self.menu_buttons = [] #buttons for the agency menu
        self.budget_options = {} #budget action options
        self.agency_feedback = {} #player feedback in the agencies
        self.events = {} #dictionary containing possible events
        self.radius = 55 #radius of agency buttons
        self.radius2 = 40 #radius of round selection
        self.board = [] #list containing separated elements of the game board
        self.arial = pygame.font.SysFont("calibri", 14) #fonts for text shown to players, four fonts in use currently
        self.arial2 = pygame.font.SysFont("calibri", 13)
        self.arial3 = pygame.font.SysFont("calibri", 24)
        self.arial4 = pygame.font.SysFont("calibri", 20)
        self.calibri = pygame.font.SysFont("calibri", 15)
        self.calibri2 = pygame.font.SysFont("calibri", 10)
        self.report = None #currently chosen news report
        self.agency = "null" #base agency, used if none is selected to avoid errors
        self.agency_stats["null"] = "null" #base agency stats
        self.click_counter = 0 #tracks how many times the player has clicked
        self.agency_events = {} #dictionary containing events that have occurred for each agency
        self.clicked_anything = False #checks if something has been clicked
        self.participant = 1 #participant number
        self.main_menu_action = False #checks if main menu button has been clicked
        self.scripts = {} #dictionary containing the scripts chosen in a given round
        self.agency_status = {} #dictionary checking for input-based events
        self.roundstandard = 5 #how many rounds are played
        self.round_number = 1 #tracks the number of rounds
        self.roundclicked = 2 #tracks the number of times the player has chosen to advance the round
        self.script_events = [0, 0] #list of events that have occurred in the current round
        self.score = 0 #player score
        self.score_last = 0 #performance score in most recent round
        self.score_total = [0] #list of scores from each round
        self.reportchoice = [] #list of reports in the game
        self.agency_scores = {} #score for each agency
        self.agency_round_results = {} #score for an agency at the end of a round
        self.intro_style = "text" #style of instructions used
        self.start = False #condition for showing the instruction screen first
        self.agencynames = [] #names of agencies in game
        self.endrankings = False #final agency ranking condition
        self.insummary = False #is the player in a summary screen
        self.instruction_2 = False #second instruction screen
        self.information = False #budget option instructions
        self.summary = False #summary choice screen
        self.agency_summary = False #input-based events summary
        self.agency_summary_2 = False #random events summary
        self.show_agencies = False #are the agencies shown
        self.show_effects = False #effects of a given budget choice
        self.show_event_effects = False #effects of a given event
        self.show_main_menu = False #is the main game menu shown
        self.show_feedback = False #is game feedbakc shown
        self.roundover = False #is thed round over
        self.historical = False #show historical performance selection
        self.performance_reports = False #show performance reports
        self.news_reports = False #show news reports selection
        self.history_information = False #show historical performance
        self.news_information = False #show news report
        self.news_choice = False #show news report selection 2
        self.rankings = False #show rankings selection
        self.roundsummary1 = False #round summary screens
        self.roundsummary2 = False
        self.roundsummary3 = False
        self.roundsummary4 = False
        self.roundsummary5 = False
        self.roundsummary6 = False
        self.roundsummary7 = False
        self.show_budget_options = False #show the options players have for budget actions
        self.postgame = False #show the postgame screen
        self.show_rankings = False #show rankings
        self.treatment_information = False #show treatment condition instructions
        self.choice = "null" #main menu choice
        self.roundchoice = "null" #round choice
        self.effects_choice = "null" #event effects choice
        self.button_effects = {} #dictionary of budget option effects
        self.black = (0, 0, 0, 255) #colours used in the game, based on rgb values
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
        self.historical_rankings = [] #list of historical rankings
        self.papers = ["Onafhankelijke Tribune", "Metropolitaans Record", "Levenstijden", "De Explorer Telegram", "De Telegraaf Times", "Zaterdag Tribune", "Eenheid Dagelijks", "Gazette Avond", "Dagelijkse beschermheer", "Dagelijks Thuis", "Ochtendnieuws", "De Primeur Onderzoeker", "De Lokale Krant", "Wereldtijden", "Zenith Nieuws", "Het Eerste Lichtbericht", "Koerier Dagelijks", "Verhalend Weekblad", "Wekelijkse Sentinel", "Dagelijkse Lodestar", "De Prime Kronieken", "De Observer", "Tijd van het Leven", "Vandaag Nieuws", "De Eerste Licht Kroniek" , "De Erfgoedkronieken", "Alliance dagelijks", "Verhalende Avond", "Dagelijks baken", "Wekelijkse Estafette", "De Era Kroniek", "Het Eerste Licht Bulletin", "De Dispatch Kronieken", "Samenleving Nieuws", "De Levenskronieken", "Insider Times", "Observer Avond", "Dagelijks baken", "Ochtend Observer", "Dagelijks Nationaal"] #list of newspapers
        self.authors = ["Tobias Deleu", "Michaël Mostinckx", "Stan Derycke", "Jean-Baptiste Van Den Houte", "Christopher De Neve", "Remco De Pauw", "Max Dermout", "Jasper Viaene", "Manuel Martens", "Ward De Gieter", "Ines Pelleriaux", "Saskia Baert", "Eline De Backer", "Carolien Renson", "Babette Tyberghein", "Kim Van Caemelbeke", "Helena Catteau", "Lise De Smedt", "Selin Van Pruisen", "Marine Dhondt", "Timothy Vermeulen", "Jesse Verhasselt", "Tristan Vercruysse", "Noé Libbrecht", "Davy Van Pruisen", "Maxime Vanderstraeten", "Cyril Van Vaerenbergh", "Baptiste Demuynck", "Bert Nys", "Jef Dermaut", "Isabelle Deleu", "Yasemin Fremaux", "Jill Arijs", "Marjorie Van Tieghem", "Imke Holvoet", "Alizée Deboeck", "Julia Pelleriaux", "Fauve Moerman", "Melisa Vrammout", "Sarah Six"] #list of authors
        self.ranking_schools = ["Trinity", "Adelaarsberg", "Lang Strand", "Koraal Bronnen", "Dennenheuvel", "Zonnige Heuvels", "Regenboog", "Helder Meer", "Esdoorn", "Kleine Rots", "Fortuna", "Eiken Park", "Stonewall", "Bosmeer", "Zonnige Kust", "Appelvallei", "Zegel Hoog", "Rode Landen", "Erfgoed", "Hertenrivier"] #list of schools for comparison
        self.possible_events = ["Talentenjacht", "Sportbeurs", "Wetenschapsbeurs", "Basketbalwedstrijd", "Voetbalwedstrijd", "Cook-off", "Bakselverkoop", "Vragenspel", "Schooluitwisseling", "Workshop schrijven", "Dansvoorstelling", "Muzikale voorstelling", "Vakantiefeest", "Onafhankelijkheidsfeest", "Museumbezoek", "Schattenjacht", "Liefdadigheidsloop", "Schoolfeest"] #names for possible events
        self.report_budget = "null"
        self.budget_question = False
        self.officer_report = False
        self.met_budget = "null"
        self.budget_record = []
        self.year = 2023
        self.semester = 2
        self.gamerankings = []
        self.timer_follow = True
        self.introduction_1 = True
        self.introduction_2 = False
        self.introduction_3 = False
        self.introduction_4 = False
        self.introduction_5 = False
        self.introduction_6 = False
        self.introduction_7 = False
        self.introduction_8 = False
        self.introduction_9 = False
        self.introduction_10 = False

    def check_treatment_condition(self): #assign the treatment condition

        number = random.randrange(1,3)
        if number == 1:
            self.treatment_information = True
            self.introduction_1 = False
        if number == 2:
            self.treatment_information = False
        self.output += f"treatment condition: {str(self.treatment_information)}"
        self.output += "\n"

    def baseconditions(self): #set conditions to return the game to base state
        self.main_menus = self.create_main_menu("base")
        if self.first_time == True:
            self.roundtime = self.time
        self.agency = "null"
        self.roundchoice = "null"
        self.insummary = False
        self.reportchoice = []
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
        self.performance_reports = False
        self.news_reports = False
        self.history_information = False
        self.news_information = False
        self.news_choice = False
        self.roundsummary1 = False
        self.roundsummary2 = False
        self.roundsummary3 = False
        self.roundsummary4 = False
        self.roundsummary5 = False
        self.roundsummary6 = False
        self.roundsummary7 = False
        self.show_budget_options = False
        self.postgame = False
        self.main_menu_action = False
        self.first_time = False
        self.rankings = False
        self.show_rankings = False
        self.budget_question = False
        self.officer_report = False
        self.introduction_1 = False
        self.introduction_2 = False
        self.introduction_3 = False
        self.introduction_4 = False
        self.introduction_5 = False
        self.introduction_6 = False
        self.introduction_7 = False
        self.introduction_8 = False
        self.introduction_9 = False
        self.introduction_10 = False


    def check_url(self): #check the url arguments
        self.arguments = sys.argv
        

    def base_scripts(self): #scripts set to none
        self.scripts[0] = []
        self.scripts[1] = []
    
    def choose_random_scripts(self, amount: int): #chooses random events at the end of the round
        list1 = []
        list2 = []
        while True:
            number = random.randrange(0, 20)
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
                    news_report = self.create_semester_scripts(agency, u)
                    self.reportchoice.append(news_report)
        self.script_events[1] = list1
        self.output += f"random events: {str(list1)}"
        self.output += "\n"

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
                                    news_report = self.create_semester_scripts(agency, u)
                                    self.reportchoice.append(news_report)

        self.script_events[0] = list1
        self.output += f"input events: {str(list1)}"
        self.output += "\n"

        
    def advance_game_round(self): #advances to the next round of the game
        self.increase_click_counter()
        self.semester += 1
        if self.semester == 3:
            self.semester = 1
            self.year += 1
        if self.total_budget < 0:
            self.met_budget = False
            self.report_budget = self.create_semester_scripts("agency", "budget officer not within budget")
            self.budget_record.append(False)
        else:
            self.met_budget = True
            self.report_budget = self.create_semester_scripts("agency", "budget officer within budget") 
            self.budget_record.append(True)
        self.output += "round progression"
        self.output += "\n"
        self.output += f"current round: {str(self.round_number)}"
        self.output += "\n"
        self.output += "game state: "
        self.output += "\n"
        self.output += f"agency scores: {str(self.agency_scores)}"
        self.output += "\n"
        self.output += f"player score: {str(self.score)}"
        self.output += "\n"
        self.output += f"agency stats: {str(self.agency_stats)}"
        self.output += "\n"
        self.output += f"staff stats: {str(self.staff_stats)}"
        self.output += "\n"
        self.output += f"student stats: {str(self.student_stats)}"
        self.output += "\n"
        self.output += f"total budget: {str(self.total_budget)}"
        self.output += "\n"
        self.output += f"current ranking: {str(self.schoolranking)}"
        self.output += "\n"
        self.post_output()
        if self.roundclicked > self.round_number:
            self.reportchoice = []
            self.add_to_score()
            self.run_random_scripts()
            self.run_input_scripts()
            seed = len(self.reportchoice)
            index = random.randrange(0, seed)
            self.report = self.reportchoice[index]
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
            self.total_budget = self.budget_standard
            self.adjust_total_budget(self.budget_standard)
            self.adjust_ranking()
            self.historical_rankings.append(self.schoolranking)
            self.gamerankings.append(self.schoolranking)
        

    def check_score(self): #checks the current player score
        list1 = []
        for i in self.student_stats:
            numbers = []
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

    def add_to_score(self): #adds current score to overall game score
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
        self.add_script([0, "poor learning results (math)", "De leerlingen hadden slechte leerresultaten in wiskunde", ("decrease agency budget", 200), ("decrease staff satisfaction", 0), ("decrease staff performance", 0), ("increase staff stress",0 ), ("decrease staff", 1), ("cancel event", 1), ("increase equipment", 500), ("increase student stress", 0)])
        self.add_script([0, "poor learning results (reading)", "De studenten hadden slechte leerresultaten in lezen", ("decrease agency budget", 200), ("decrease staff satisfaction", 0), ("decrease staff performance", 0), ("increase staff stress", 0), ("decrease staff", 1), ("cancel event", 1), ("increase equipment", 500), ("increase student stress", 0)])
        self.add_script([0, "poor learning results (science)", "De leerlingen hadden slechte leerresultaten in wetenschap", ("decrease agency budget", 200), ("decrease staff satisfaction", 0), ("decrease staff performance", 0), ("increase staff stress", 0), ("decrease staff", 1), ("cancel event", 1), ("increase equipment", 500), ("increase student stress", 0)])
        self.add_script([0, "poor learning results (overall)", "De leerlingen hadden slechte algemene leerresultaten", ("decrease agency budget", 800), ("decrease staff satisfaction", 0), ("decrease staff performance", 0), ("increase staff stress", 0), ("decrease staff", 1), ("cancel event", 1), ("increase equipment", 1500), ("increase student stress", 0)])
        self.add_script([0, "not within budget", "De school bleef niet binnen haar budget", ("increase staff stress", 0), ("increase student stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease staff performance", 0)])
        self.add_script([0, "within budget", "De school bleef binnen haar budget", ("decrease staff stress", 0), ("decrease student stress", 0), ("increase staff satisfaction", 0), ("increase student satisfaction", 0), ("increase staff performance", 0)])
        self.add_script([0, "good learning results (math)", "De leerlingen hadden goede leerresultaten in wiskunde", ("increase agency budget", 200), ("increase staff satisfaction", 0), ("increase staff performance", 0), ("decrease staff stress", 0), ("increase staff", 1), ("plan event", 1), ("decrease equipment", 500), ("decrease student stress", 0)])
        self.add_script([0, "good learning results (reading)", "De studenten hadden goede leerresultaten in lezen", ("increase agency budget", 200), ("increase staff satisfaction", 0), ("increase staff performance", 0), ("decrease staff stress", 0), ("increase staff", 1), ("plan event", 1), ("decrease equipment", 500), ("decrease student stress", 0)])
        self.add_script([0, "good learning results (science)", "De leerlingen hadden goede leerresultaten in wetenschap", ("increase agency budget", 200), ("increase staff satisfaction", 0), ("increase staff performance", 0), ("decrease staff stress", 0), ("increase staff", 1), ("plan event", 1), ("decrease equipment", 500), ("decrease student stress", 0)])
        self.add_script([0, "good learning results (overall)", "De leerlingen hadden goede algemene leerresultaten", ("increase agency budget", 800), ("increase staff satisfaction", 0), ("increase staff performance", 0), ("decrease staff stress", 0), ("increase staff", 1), ("plan event", 1), ("decrease equipment", 1500), ("decrease student stress", 0)])
        self.add_script([0, "high staff stress", "Het personeel had veel stress", ("decrease staff satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([0, "low staff stress", "Het personeel had weinig stress", ("increase staff satisfaction", 0), ("decrease staff stress", 0), ("increase staff performance", 0), ("increase staff", 5), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0)])
        self.add_script([0, "high staff satisfaction", "Het personeel was zeer tevreden", ("increase staff satisfaction", 0), ("decrease staff stress", 0), ("increase staff performance", 0), ("increase staff", 5), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0)])
        self.add_script([0, "low staff performance", "Het personeel presteerde slecht", ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([0, "high staff performance", "Het personeel presteerde goed", ("decrease staff stress", 0), ("increase staff satisfaction", 0), ("increase staff", 5), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0)])
        self.add_script([0, "high student satisfaction", "De studenten waren zeer tevreden", ("decrease student stress", 0), ("increase student satisfaction", 0), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0)])
        self.add_script([0, "low student stress", "De studenten hadden weinig stress", ("decrease student stress", 0), ("increase student satisfaction", 0), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0)])
        self.add_script([0, "high student stress", "De studenten hadden veel stress", ("increase student stress", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([0, "low student satisfaction", "De studenten hadden een lage tevredenheid", ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([0, "low staff satisfaction", "De tevredenheid van het personeel was laag", ("increase student stress", 0), ("decrease student satisfaction", 0), ("decrease staff", 5), ("decrease staff performance", 0)])
        self.add_script([0, "not enough events", "Er werden geen evenementen georganiseerd op de school", ("decrease student satisfaction", 0), ("increase student stress", 0), ("decrease staff stress", 0), ("decrease staff satisfaction", 0)])
        self.add_script([0, "understaffed", "De school was onderbemand", ("decrease student satisfaction", 0), ("increase student stress", 0), ("decrease staff stress", 0), ("decrease staff satisfaction", 0)])
        self.add_script([0, "insufficient equipment", "De school had niet genoeg apparatuur", ("decrease staff satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0), ("decrease student satisfaction", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([1, "misuse of funds", "De schoolleiding heeft misbruik gemaakt van schoolfondsen", ("decrease agency budget", 5000), ("decrease staff satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0), ("decrease student satisfaction", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "improper conduct", "Een werknemer heeft zich ongepast gedragen", ("decrease agency budget", 5000), ("decrease staff satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0), ("decrease student satisfaction", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "theft (outside)", "Een dief brak in de school in en stal waardevolle spullen", ("decrease agency budget", 5000), ("decrease staff satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0), ("decrease student satisfaction", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "theft (inside)", "Een werknemer heeft waardevolle spullen gestolen", ("decrease agency budget", 5000), ("decrease staff satisfaction", 0), ("increase staff stress", 0), ("decrease staff performance", 0), ("decrease student satisfaction", 0), ("decrease staff", 5), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "bullying (students)", "Een student klaagde over pesten", ("increase student stress", 0), ("increase student stress", 0), ("decrease student satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase staff stress", 0)])
        self.add_script([1, "bullying (staff)", "Een personeelslid klaagde over pesten", ("increase staff stress", 0), ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0)])
        self.add_script([1, "alumni grant", "Een oud-leerling heeft een donatie gedaan", ("increase agency budget", 10000), ("increase staff performance", 0), ("increase staff satisfaction", 0), ("decrease staff stress", 0)])
        self.add_script([1, "alumni complaint", "Een alumni klaagde over schoolresultaten", ("decrease staff performance", 0), ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0)])
        self.add_script([1, "flood", "De school kwam onverwacht onder water te staan", ("decrease agency budget", 5000), ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("decrease agency equipment", 2000)])
        self.add_script([1, "mold", "Er is schimmel gevonden in de muren van de school", ("decrease agency budget", 5000), ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0)])
        self.add_script([1, "broken windows", "De ruiten van de school waren gebroken", ("decrease agency budget", 1000), ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("increase student stress", 0), ("decrease agency equipment", 1000)])
        self.add_script([1, "illness (flu)", "Een griepepidemie ging door de school", ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "illness (noro)", "Een norovirus epidemie ging door de school", ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "student injury (limb)", "Een student brak zijn arm", ("increase staff stress", 0), ("increase student stress", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([1, "student injury (concussion)", "Een student liep een hersenschudding op", ("increase staff stress", 0), ("increase student stress", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0)])
        self.add_script([1, "outbreak (lice)", "Er is luizen uitgebroken op de school", ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("cancel event", 1)])
        self.add_script([1, "earthquake", "Een aardbeving beschadigde het schoolgebouw", ("decrease agency budget", 5000), ("increase staff stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("increase student stress", 0), ("decrease agency equipment", 2000)])
        self.add_script([1, "equipment breakage", "Sommige apparatuur ging kapot tijdens een les", ("increase staff stress", 0), ("increase student stress", 0), ("decrease student reading", 0), ("decrease student math", 0), ("decrease student science", 0), ("decrease staff performance", 0)])
        self.add_script([1, "equipment donation", "Een alumni schonk extra apparatuur", ("decrease staff stress", 0), ("decrease student stress", 0), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0), ("increase staff performance", 0)])
        self.add_script([1, "external evaluation", "Er is een externe evaluatie van de school uitgevoerd", ("increase staff stress", 0), ("increase staff performance", 0), ("increase student stress", 0), ("decrease staff satisfaction", 0), ("decrease student satisfaction", 0), ("increase student reading", 0), ("increase student math", 0), ("increase student science", 0)])

    def script_effects(self): #effects of a given script
        rect1 = self.draw_exit("previous")
        x = 100
        y = 50
        text = self.arial.render(f"{self.effects_choice[0]}!", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Dit had de volgende effecten:", True, self.black)
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
                self.finish_game()

    def finish_game(self): #finish the game and redirect the player to exit survey
        self.add_final_output()
        self.post_output()
        if self.redirect != "noredirect":
            url_open = "https://uantwerpen.eu.qualtrics.com/jfe/form/SV_7adyuWjd5qQYEV8" + f"?id1={self.id_participant}&id2={self.id_survey}&id3={self.id_game}"
        webbrowser.open(url_open)
        raise SystemExit

    def execute_script(self, script, agency): #executes a given script
        effects = []
        if script[0] == "decrease agency budget":
            number = script[1]
            self.adjust_agency_budget(agency, -number)
            effects.append(f"Het schoolbudget werd verlaagd met {number}")
        if script[0] == "increase agency budget":
            number = script[1]
            self.adjust_agency_budget(agency, number)
            effects.append(f"Het schoolbudget werd verhoogd met {number}")
        if script[0] == "decrease staff":
            number = script[1]
            self.adjust_agency_staff(agency, -number)
            effects.append(f"Het aantal personeelsleden daalde met {number}")
        if script[0] == "increase staff":
            number = script[1]
            self.adjust_agency_staff(agency, number)
            effects.append(f"Het aantal medewerkers steeg met {number}")
        if script[0] == "plan event":
            number = script[1]
            self.create_agency_event(agency, number, 0)
            effects.append(f"Er werd een nieuw evenement gepland")
        if script[0] == "cancel event":
            number = script[1]
            self.create_agency_event(agency, -number, 0)
            effects.append(f"Een evenement is geannuleerd")
        if script[0] == "increase equipment":
            amount = script[1]
            self.adjust_agency_equipment(agency, amount)
            effects.append(f"De hoeveelheid beschikbare apparatuur is toegenomen met {amount}")
        if script[0] == "decrease equipment":
            amount = script[1]
            self.adjust_agency_equipment(agency, -amount)
            effects.append(f"De hoeveelheid beschikbare apparatuur daalde met {amount}")
        if script[0] == "decrease staff satisfaction":
            self.adjust_soft_stats("staff satisfaction", agency, -1)
            effects.append(f"Tevredenheid personeel afgenomen")
        if script[0] == "increase staff satisfaction":
            self.adjust_soft_stats("staff satisfaction", agency, 1)
            effects.append(f"Tevredenheid personeel toegenomen")
        if script[0] == "decrease student satisfaction":
            self.adjust_soft_stats("student satisfaction", agency, -1)
            effects.append(f"Tevredenheid studenten afgenomen")
        if script[0] == "increase student satisfaction":
            self.adjust_soft_stats("student satisfaction", agency, 1)
            effects.append(f"Tevredenheid studenten toegenomen")
        if script[0] == "decrease staff stress":
            self.adjust_soft_stats("staff stress", agency, -1)
            effects.append(f"Minder stress bij het personeel")
        if script[0] == "increase staff stress":
            self.adjust_soft_stats("staff stress", agency, 1)
            effects.append(f"Stress bij personeel toegenomen")
        if script[0] == "decrease student stress":
            self.adjust_soft_stats("student stress", agency, -1)
            effects.append(f"Minder stress bij studenten")
        if script[0] == "increase student stress":
            self.adjust_soft_stats("student stress", agency, 1)
            effects.append(f"Studentenstress toegenomen")
        if script[0] == "increase student reading":
            self.adjust_soft_stats("student reading", agency, 1)
            effects.append(f"Leesprestaties van studenten verbeterd")
        if script[0] == "increase student math":
            self.adjust_soft_stats("student math", agency, 1)
            effects.append(f"Wiskundeprestaties van leerlingen verbeterd")
        if script[0] == "increase student science":
            self.adjust_soft_stats("student science", agency, 1)
            effects.append(f"Wetenschapsprestaties van leerlingen toegenomen")
        if script[0] == "decrease student reading":
            self.adjust_soft_stats("student reading", agency, -1)
            effects.append(f"Leesprestaties van studenten afgenomen")
        if script[0] == "decrease student math":
            self.adjust_soft_stats("student math", agency, -1)
            effects.append(f"Wiskundeprestaties van leerlingen afgenomen")
        if script[0] == "decrease student science":
            self.adjust_soft_stats("student science", agency, -1)
            effects.append(f"Wetenschapsprestaties van leerlingen afgenomen")
        if script[0] == "decrease staff performance":
            self.adjust_soft_stats("staff performance", agency, -1)
            effects.append(f"Prestaties van personeel afgenomen")
        if script[0] == "increase staff performance":
            self.adjust_soft_stats("staff performance", agency, 1)
            effects.append(f"Prestaties van personeel toegenomen")
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

    def increase_round_counter(self): #increases round counter
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

    def create_output_file(self): #creates the output file, currently as a string
        self.output = ""

    def add_final_output(self): #adds final notes to the output file
        self.output += f"game completed"
        self.output += "\n"
        self.output += f"total number of clicks: {self.click_counter}"
        self.output += "\n"

    def create_identifier(self): #create unique identifier
        try:
            uuid_participant = self.arguments[1]
        except IndexError:
            uuid_participant = "no id found"
        try:
            uuid_survey = self.arguments[0]
        except IndexError:
            uuid_survey = "no id found"
        try:
            uuid_redirect = self.arguments[2]
        except IndexError:
            uuid_redirect = "redirect"
        unique = uuid.uuid4()
        uuid_game = str(unique)
        self.id_participant = str(uuid_participant)
        self.id_survey = str(uuid_survey)
        self.id_game = str(uuid_game)
        self.redirect = str(uuid_redirect)
        self.output += f"participant identifier: {self.id_participant}"
        self.output += "\n"
        self.output += f"survey identifier: {self.id_survey}"
        self.output += "\n"
        self.output += f"game identifier: {self.id_game}"
        self.output += "\n"
        self.output += f"redirect identifier: {self.redirect}"
        self.output += "\n"
        

    def post_output(self): #send post request to API with game results
        ct = datetime.datetime.now()
        time_now = str(ct)
        string1 = ""
        identity = self.id_participant

        self.output += f"timestamp: {time_now}"
        self.output += "\n"
        self.output += f"game time: {self.time}"
        self.output += "\n"


        string1 = self.output

        #do not send request if there is an error (404) from the call

        #condition for 500 error
        #-->fallback retry, redirect if final call is unsuccessful

        #include language condition in parametres

        post_dict = {"identity": identity,
                     "data": string1}
        output = RequestHandler()
        # Define the URL and data for the POST request
        url = "https://httpbin.org/"
        data = post_dict
        # Send the POST request
        try:
            asyncio.run(output.post(url, data))
        except:
            pass
            


    def add_to_output(self, add: str): #records player inputs in the output file
        if self.click_counter > self.output_tracker:
            self.output_tracker += 1
            self.output += add
            self.output += "\n"


    def add_agency(self, agency: str, initial_budget: float, initial_staff: int, initial_equipment: float, initial_events, staff_status, equipment_status, event_status, budget_status): #add different agencies for budgeting; the game currently allows for up to 7 options at a time for graphical reasons. the input includes an initial budget
        self.agencies.append((agency, initial_budget))
        self.agency_stats[agency] = [initial_budget, initial_staff, initial_equipment, initial_events, staff_status, equipment_status, event_status, budget_status, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        lower_bound = 1
        upper_bound = 7
        count = 0
        self.events[agency] = [1, 2, 3, 4]
        for i in range(4):
            if count < initial_events:
                    index = random.randrange(0, 18)
                    self.events[agency][i] = (self.possible_events[index], random.randrange(lower_bound, upper_bound+1))
            else:
                self.events[agency][i] = ("null", random.randrange(lower_bound, upper_bound+1))
            lower_bound += 7
            upper_bound += 7
            count += 1
        self.budget_options[agency] = []
        self.agency_feedback[agency] = []
        self.agency_count += 1
        self.agencynames.append(agency)

    def create_agencies(self): #creates the agencies to be used; the name can be edited to change the labels in the game. With longer names the label code may need to be adjusted. The current form of the code supports up to four different agencies; more can be added if required but this would require more significant changes to the source code
        self.add_agency("Blad Hoog", 1000, 0, 1000, 0, "null", "null", "null", "null")
        self.add_agency("Robin Hoog", -2500, 5, 200, 1, "null", "null", "null", "null")
        self.add_agency("Vallei Primair", -1500, 10, -300, 2, "null", "null", "null", "null")
        self.add_agency("Zee Primair", 3000, -5, 400, 3, "null", "null", "null", "null")
        for i in self.agencies:
            self.agency_events[i[0]] = []
            self.news_archive[i[0]] = []


    def create_historical_rankings(self): #create historical agency rankings

        for u in range (20):
            rangelimit = 0
            ranking_scores = []
            for i in self.ranking_schools:
                score = random.randrange(rangelimit, 101)
                rangelimit += 5
                ranking_scores.append((score, i))
                ranking_scores.sort()
            self.historical_rankings.append(ranking_scores)

    def create_ranking(self): #create agency ranking
        agencies = []
        for i in self.agencies:
            agencies.append(i[0])
        for i in self.ranking_schools:
            if len(agencies) >= 20:
                break
            agencies.append(i)
        self.ranking_schools = agencies
        self.adjust_ranking()
        self.gamerankings.append(self.schoolranking)

    def adjust_ranking(self): #adjust agency ranking
        agencies = []
        ranking_scores = []
        rangelimit = 0
        for i in self.agencies:
            agencies.append(i[0])
        for i in self.ranking_schools:
            if i in agencies:
                ranking_scores.append((self.agency_scores[i], i))
            if i not in agencies:
                score = random.randrange(rangelimit, 101)
                rangelimit += 5
                ranking_scores.append((score, i))
        self.schoolranking = sorted(ranking_scores)

    def adjust_temporary(self):
        agencies = []
        ranking_scores = []
        for i in self.agencies:
            agencies.append(i[0])
        for i in self.schoolranking:
            if i[1] in agencies:
                school = i[1]
                ranking_scores.append((self.agency_scores[school], school))
            if i[1] not in agencies:
                ranking_scores.append(i)
        self.schoolranking = sorted(ranking_scores)
        self.gamerankings.pop()
        self.gamerankings.append(self.schoolranking)

    def create_semester_scripts(self, agency, script): #generate news reports
        authornumber = random.randrange(0, 36)
        papernumber = random.randrange(0, 36)
        x = 20
        y = 40

        if script == "budget officer not within budget":
            schools = ""
            count = 1
            for i in range(len(self.agencies)):
                if count != len(self.agencies):
                    schools += self.agencies[i][0]
                    schools += ", "
                    count += 1
                else:
                    schools += "en "
                    schools += self.agencies[i][0]
                    count += 1
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Begrotingsambtenaar slaagt er niet in rekeningen in evenwicht te brengen", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Het schooldistrict met {schools} bleef het afgelopen semester niet binnen haar budget.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De aankondiging duidt op het onvermogen van de begrotingsambtenaar om de rekeningen van de scholen in evenwicht te brengen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De budgetbeheerder is onlangs gekozen om de financiën van de vier scholen te beheren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Dit volgt op een periode van financiële instabiliteit en wanbeleid op de scholen, waarvan het publiek hoopt dat het zal worden opgelost.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Critici zeggen dat het falen van de begrotingsfunctionaris om de boeken effectief in balans te brengen betekent dat hij de verkeerde persoon voor de baan was.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De huidige begrotingsambtenaar werd gekozen na een zeer competitief selectieproces en geniet een lucratief salaris.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het ministerie van Onderwijs heeft verklaard vertrouwen te hebben in de bekwaamheid van de begrotingsambtenaar.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Nu de kritiek echter toeneemt, staat het ministerie onder druk om de begrotingsambtenaar te vervangen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het valt nog te bezien of de begrotingsambtenaar zijn huidige functie mag behouden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40

        if script == "budget officer within budget":
            schools = ""
            count = 1
            for i in range(len(self.agencies)):
                if count != len(self.agencies):
                    schools += self.agencies[i][0]
                    schools += ", "
                    count += 1
                else:
                    schools += "en "
                    schools += self.agencies[i][0]
                    count += 1
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Begrotingsambtenaar brengt rekeningen in evenwicht", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Het schooldistrict met {schools} bleef binnen haar budget in het afgelopen semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De aankondiging geeft aan dat de begrotingsambtenaar de rekeningen van de scholen in evenwicht kan brengen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De budgetbeheerder is onlangs gekozen om de financiën van de vier scholen te beheren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Dit volgt op een periode van financiële instabiliteit en wanbeleid op de scholen, waarvan het publiek hoopt dat het zal worden opgelost.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het positieve resultaat suggereert dat de begrotingsambtenaar de juiste persoon voor de job lijkt te zijn geweest.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De huidige begrotingsambtenaar werd gekozen na een zeer competitief selectieproces en geniet een lucratief salaris.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het ministerie van Onderwijs heeft verklaard vertrouwen te hebben in de bekwaamheid van de begrotingsambtenaar.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het publiek hoopt dat de begrotingsambtenaar de regio de broodnodige financiële stabiliteit zal geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het valt nog te bezien of de begrotingsambtenaar op de lange termijn succesvol zal zijn.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
        
        if script == "not within budget":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Financiële problemen bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat ze onder hun budget zitten voor het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De aankondiging komt naar aanleiding van de groeiende bezorgdheid over de staat van het financieel beheer op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Veel ouders hebben hun twijfels geuit over de levensduur van de activiteiten bij {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Als de kritiek toeneemt, loopt de school het risico dat ouders ervoor kiezen hun kinderen van de school te halen.{agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het Ministerie van Onderwijs heeft {agency} gewaarschuwd dat aanhoudend financieel wanbeheer kan leiden tot disciplinaire maatregelen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Dit kan leiden tot het ontslag van de school- of wijkleiding of een nader onderzoek naar de activiteiten op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het valt nog te bezien of {agency} in staat zal zijn om de financiële liquiditeit tijdens het komende semester te handhaven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ondanks de financiële problemen meldt de school dat studenten en personeel optimistisch blijven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Sommige ouders twijfelen er echter aan of {agency} in staat zal zijn om de kwaliteit van hun instructie te handhaven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))

        if script == "poor learning results (math)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Wiskundeproblemen bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat ze bijzonder slechte resultaten hebben behaald voor wiskunde in het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De aankondiging geeft aan dat de school moeite heeft om de leerdoelen te halen die van hen verwacht worden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het schooldistrict heeft zijn bezorgdheid geuit over het slechte resultaat en verwacht dat {agency} snel handelt om de kwestie op te lossen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Als de kritiek toeneemt, loopt de school het risico dat ouders ervoor kiezen om hun kinderen van {agency} af te halen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal ouders heeft twijfels geuit over het vermogen van de school om adequaat wiskundeonderwijs te blijven geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Wiskundevaardigheden zijn naar voren gekomen als een van de belangrijkste leermetrics waaraan scholen prioriteit zouden moeten geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De andere kerncijfers zijn de leerresultaten op het gebied van lezen en natuurwetenschappen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Critici van {agency} beweren dat de school faalt in haar fundamentele taak om les te geven en dat er drastische maatregelen moeten worden genomen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De schoolleiding noemt een gebrek aan middelen als reden voor de recente tekortkomingen van de school, maar critici zijn daar niet van overtuigd.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))  

        if script == "poor learning results (reading)":
            x = 40
            y = 40
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Leesproblemen bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat ze bijzonder slechte resultaten hebben geboekt met lezen in het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De aankondiging geeft aan dat de school moeite heeft om de leerdoelen te halen die van hen verwacht worden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het schooldistrict heeft zijn bezorgdheid geuit over het slechte resultaat en verwacht dat {agency} snel handelt om de kwestie op te lossen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Als de kritiek toeneemt, loopt de school het risico dat ouders ervoor kiezen om hun kinderen van {agency} af te halen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal ouders heeft twijfels geuit over de vraag of de school nog wel in staat is om voldoende alfabetiseringsonderwijs te geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Alfabetiseringspercentages zijn aangewezen als een van de belangrijkste leermetrics waaraan scholen prioriteit zouden moeten geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De andere belangrijke maatstaven zijn leerresultaten in wiskunde en natuurwetenschappen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Critici van {agency} beweren dat de school faalt in haar fundamentele taak om les te geven en dat er drastische maatregelen moeten worden genomen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De schoolleiding noemt een gebrek aan middelen als reden voor de recente tekortkomingen van de school, maar critici zijn daar niet van overtuigd.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))

        if script == "poor learning results (science)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Slechte scores voor wetenschap bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat de resultaten voor natuurwetenschappen in het laatste semester bijzonder slecht waren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De aankondiging geeft aan dat de school moeite heeft om de leerdoelen te halen die van hen verwacht worden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het schooldistrict heeft zijn bezorgdheid geuit over het slechte resultaat en verwacht dat {agency} snel handelt om de kwestie op te lossen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Als de kritiek toeneemt, loopt de school het risico dat ouders ervoor kiezen om hun kinderen van {agency} af te halen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal ouders heeft twijfels geuit over het vermogen van de school om adequaat wetenschapsonderwijs te blijven geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Wetenschappelijke vaardigheden zijn aangewezen als een van de belangrijkste leerstofgebieden waaraan scholen prioriteit moeten geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De andere belangrijke maatstaven zijn de leerresultaten op het gebied van lezen en wiskunde.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Critici van {agency} beweren dat de school faalt in haar fundamentele taak om les te geven en dat er drastische maatregelen moeten worden genomen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De schoolleiding noemt een gebrek aan middelen als reden voor de recente tekortkomingen van de school, maar critici zijn daar niet van overtuigd.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))  
        
        if script == "poor learning results (overall)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Leerproblemen bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat ze bijzonder goede leerresultaten hebben behaald in het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De aankondiging geeft aan dat de school moeite heeft om de leerdoelen te halen die van hen verwacht worden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het schooldistrict heeft zijn bezorgdheid geuit over de slechte resultaten en verwacht dat {agency} snel handelt om het probleem op te lossen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Als de kritiek toeneemt, loopt de school het risico dat ouders ervoor kiezen om hun kinderen van {agency} af te halen..", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal ouders heeft twijfels geuit over het vermogen van de school om het onderwijs aan hun kinderen te blijven verzorgen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Wiskunde, natuurwetenschappen en lezen zijn onlangs naar voren gekomen als de belangrijkste meeteenheden om het leren op scholen te volgen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een slecht totaalresultaat betekent dat de school op meerdere gebieden onvoldoende instructie geeft.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Critici van {agency} beweren dat de school faalt in haar fundamentele taak om les te geven en dat er drastische maatregelen moeten worden genomen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De schoolleiding noemt een gebrek aan middelen als reden voor de recente tekortkomingen van de school, maar critici zijn daar niet van overtuigd.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))  
        
        if script == "within budget":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Financiële excellentie bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat ze haar financiële doelstellingen voor het laatste semester heeft gehaald.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De aankondiging heeft ouders gerustgesteld dat de school duurzaam wordt geleid.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders hebben hun vertrouwen uitgesproken in de capaciteiten van {agency} in het licht van deze resultaten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Sommige ouders met kinderen op concurrerende scholen hebben zelfs interesse getoond om hun kinderen naar {agency} te verhuizen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het ministerie van Onderwijs heeft de schoolleiding geprezen voor hun financiële voorzichtigheid.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het personeel hoopt dat de positieve financiële resultaten zullen worden weerspiegeld in extra leermiddelen in het komende semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studenten bij {agency} hebben hun desinteresse geuit, maar hopen dat het management zal investeren in het verbeteren van de schoolmaaltijden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ondanks het financiële succes zeggen critici dat de school nog veel werk moet verzetten om de onderwijsdoelen in het komende semester te halen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Recentelijk is de nadruk gelegd op het belang van leerresultaten als de belangrijkste maatstaf voor het evalueren van schoolsucces.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))  

        if script == "good learning results (math)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Wiskunde succes bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat ze bijzonder goede resultaten hebben behaald in wiskunde in het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De aankondiging geeft aan dat de school succes heeft met de leerdoelen die van hen verwacht worden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het schooldistrict heeft {agency} geprezen voor zijn succes en andere scholen aangemoedigd om hier nota van te nemen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben aangegeven dat ze erg blij zijn met de staat van het wiskundeonderwijs op {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Concurrerende scholen in de omgeving hebben gemeld dat sommige ouders onlangs hebben geprobeerd hun kinderen over te plaatsen naar {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Wiskundevaardigheden zijn aangewezen als een van de belangrijkste leermetrics waaraan scholen prioriteit moeten geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De andere belangrijke maatstaven zijn leerresultaten op het gebied van lezen en natuurwetenschappen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Personeelsleden van {agency} hebben gezegd dat ze blij zijn met de resultaten en dat ze leerlingen uitstekend onderwijs zullen blijven geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De schoolleiding noemt de studentgerichte aanpak van het onderwijs op de school als de sleutel tot het succes.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))   

        if script == "good learning results (reading)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Uitstekende geletterdheid bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat ze bijzonder goede resultaten hebben geboekt op het gebied van lezen in het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De aankondiging geeft aan dat de school succes heeft met de leerdoelen die van hen verwacht worden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het schooldistrict heeft {agency} geprezen voor zijn succes en andere scholen aangemoedigd om hier nota van te nemen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben aangegeven dat ze erg blij zijn met de staat van het alfabetiseringsonderwijs op {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Concurrerende scholen in de omgeving hebben gemeld dat sommige ouders onlangs hebben geprobeerd hun kinderen over te plaatsen naar {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Leesvaardigheid is naar voren gekomen als een van de belangrijkste leermetrics waaraan scholen prioriteit moeten geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De andere belangrijke maatstaven zijn leerresultaten in wiskunde en natuurwetenschappen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Personeelsleden van {agency} hebben gezegd dat ze blij zijn met de resultaten en dat ze leerlingen uitstekend onderwijs zullen blijven geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De schoolleiding noemt de studentgerichte aanpak van het onderwijs op de school als de sleutel tot het succes.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))   

        if script == "good learning results (science)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Wetenschappelijke uitmuntendheid bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat ze in het laatste semester bijzonder goede resultaten hebben behaald in de exacte vakken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De aankondiging geeft aan dat de school succes heeft met de leerdoelen die van hen verwacht worden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het schooldistrict heeft {agency} geprezen voor zijn succes en andere scholen aangemoedigd om hier nota van te nemen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben aangegeven dat ze erg blij zijn met de staat van het wetenschappelijk onderwijs op {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Concurrerende scholen in de omgeving hebben gemeld dat sommige ouders onlangs hebben geprobeerd hun kinderen over te plaatsen naar {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Wetenschappelijke vaardigheden zijn aangewezen als een van de belangrijkste leerstofgebieden waaraan scholen prioriteit moeten geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De andere belangrijke maatstaven zijn de leerresultaten op het gebied van lezen en wiskunde.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Personeelsleden van {agency} hebben gezegd dat ze blij zijn met de resultaten en dat ze leerlingen uitstekend onderwijs zullen blijven geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De schoolleiding noemt de studentgerichte aanpak van het onderwijs op de school als de sleutel tot het succes.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))  

        if script == "good learning results (overall)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Geweldig leren bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat ze bijzonder goede resultaten hebben geboekt in het leren in het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De aankondiging geeft aan dat de school succes heeft met de leerdoelen die van hen verwacht worden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het schooldistrict heeft {agency} geprezen voor zijn succes en andere scholen aangemoedigd om hier nota van te nemen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben aangegeven dat ze erg blij zijn met de staat van het onderwijs op {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Concurrerende scholen in de omgeving hebben gemeld dat sommige ouders onlangs hebben geprobeerd hun kinderen over te plaatsen naar {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Wiskunde, natuurwetenschappen en lezen zijn onlangs naar voren gekomen als de belangrijkste meeteenheden die worden gebruikt om het leren op scholen te volgen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een sterk algemeen resultaat betekent dat de school op meerdere gebieden uitstekend onderwijs geeft.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Personeelsleden van {agency} hebben gezegd dat ze blij zijn met de resultaten en dat ze leerlingen uitstekend onderwijs zullen blijven geven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De schoolleiding noemt de studentgerichte aanpak van het onderwijs op de school als de sleutel tot het succes.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))     

        if script == "high staff stress":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Personeel overweldigd bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Personeel bij {agency} heeft vertegenwoordigers van {self.papers[papernumber]} verteld dat ze collectief onder zeer grote stress staan.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het personeel verklaarde verder dat de eisen die de school aan hen stelt onredelijk en onhoudbaar zijn.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Gedurende het hele laatste semester hebben personeelsleden van {agency} geprobeerd de schoolleiding te benaderen over hun buitensporige werkdruk.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De leerkrachten zeggen echter dat de schoolleiding niet reageert en niet meewerkt met betrekking tot deze kwesties.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De lerarenvakbond zei dat andere scholen soortgelijke problemen hebben gehad en de vakbond overweegt stakingsacties.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De verklaring van hoge stress bij het personeel komt in het kielzog van een verhoogde druk van het management bij {agency} om de leerresultaten te verbeteren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van de school hebben hun bezorgdheid geuit over de langdurige staat van het onderwijs op de school in het licht van de slechte werkomstandigheden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De geïnterviewde studenten hadden begrip voor de werkdruk van de leerkrachten, maar benadrukten dat ook zij zich vaak overwerkt voelden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De schoolleiding weigerde commentaar te geven toen er contact werd opgenomen door {self.papers[papernumber]}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))     

        if script == "low staff stress":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Personeel niet betrokken bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat de arbeidsomstandigheden voor het personeel op de school tot de beste ooit behoren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens interne personeelsinterviews bij {agency} was de stress onder docenten op de school historisch laag tijdens het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Personeelsleden hebben zelf aangegeven tevreden te zijn over hun werkomstandigheden en werkdruk.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens een docent van {agency} geïnterviewd door {self.papers[papernumber]}, laat de school zien hoe waardevol het is om het personeelsbestand niet te overbelasten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond heeft verklaard dat {agency} een lichtend voorbeeld is van duurzame personeelspraktijken in een schoolomgeving.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De verklaring van lage stress bij het personeel komt in het kielzog van een verhoogde druk van het management bij {agency} om de leerresultaten te verbeteren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben gezegd dat ze erg blij zijn voor de leraren, maar hopen dat deze omstandigheden zich zullen vertalen in betere leerresultaten voor de leerlingen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De studenten die hierover werden geïnterviewd waren grotendeels niet geïnteresseerd in de werkdruk van de docent, maar spraken de hoop uit dat lage stress zou leiden tot mildere cijfers.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het schoolmanagement schrijft hun recente succes toe aan een holistische personeelsaanpak die rekening houdt met de individuele behoeften van elke werknemer.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script)) 

        if script == "high staff satisfaction":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Personeel zeer tevreden bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat hun personeel onlangs heeft aangegeven zeer tevreden te zijn over hun werk.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens interne personeelsinterviews bij {agency} was de werktevredenheid onder docenten op de school historisch hoog tijdens het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Personeelsleden hebben zelf aangegeven tevreden te zijn over hun werkomstandigheden en werkgemeenschap.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens een docent van {agency} geïnterviewd door {self.papers[papernumber]}, laat de school zien hoe een school voor haar personeel moet zorgen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond heeft verklaard dat {agency} een voorbeeldige bekwaamheid heeft getoond in het zorgen voor het welzijn van zijn werknemers.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De verklaring van grote tevredenheid van het personeel komt in het kielzog van een verhoogde druk van het management bij {agency} om de leerresultaten te verbeteren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben gezegd dat ze erg blij zijn voor de leraren, maar hopen dat deze resultaten zullen worden vertaald in betere leerresultaten voor de leerlingen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De studenten die hierover werden geïnterviewd, waren blij dat de leerkrachten tevreden waren en spraken de hoop uit dat tevreden leerkrachten hen zouden steunen in hun eigen werk.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} schrijft hun recente succes toe aan een holistische personeelsbenadering die rekening houdt met de individuele behoeften van elke werknemer.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))    

        if script == "low staff performance":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Personeel presteert ondermaats bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat hun personeel de laatste tijd zwaar ondermaats presteert.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens interne personeelsevaluaties bij {agency} waren de werkprestaties van docenten op de school historisch laag tijdens het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Personeelsleden van {agency} hebben zelf toegegeven dat ze de laatste tijd aanzienlijke problemen hebben gehad met het halen van hun prestatiedoelen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens een docent van {agency} zijn de redenen voor de prestatieproblemen een groot personeelsverloop, onhandelbare leerlingen en een slechte inwerkperiode.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond heeft verklaard dat kwesties van deze omvang een falend teammanagement vertegenwoordigen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De verklaring van lage prestaties komt ondanks de toegenomen druk van {agency} om de leerresultaten van studenten te verbeteren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben hun bezorgdheid geuit over de kwaliteit van het onderwijs op de school en sommigen hebben gedreigd hun kind elders onder te brengen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ondervraagde studenten wijten de problemen aan de onwil van docenten om feedback van studenten te krijgen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} heeft verklaard dat ze problemen hebben gehad met het vinden van kwaliteitswerkers en dat ze eraan werken om de problemen op te lossen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))   

        if script == "high staff performance":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Uitstekend personeel bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat hun personeel onlangs uitstekende prestaties heeft geleverd.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens interne personeelsevaluaties bij {agency} waren de werkprestaties van docenten op de school historisch hoog tijdens het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Personeelsleden van {agency} hebben zelf opgemerkt dat ze de laatste tijd geen problemen hebben gehad met het halen van hun prestatiedoelen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens een leraar van {agency} ligt de reden voor de uitmuntendheid van de school in haar vermogen om de beste werknemers aan te trekken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond heeft verklaard dat {agency} deze resultaten alleen kunnen worden bevorderd in een positieve leeromgeving.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De verklaring van hoge prestaties komt na een verhoogde druk van {agency} om de leerresultaten van studenten te verbeteren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben aangegeven dat ze erg blij zijn met de richting waarin het onderwijs op de school gaat.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studenten die over dit onderwerp werden geïnterviewd, stelden dat het voor docenten gemakkelijk is om succes te hebben met zulke uitstekende leerlingen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} heeft verklaard dat ze sterk hebben aangedrongen op verantwoordingsplicht van werknemers, wat tot uiting komt in hun uitstekende prestaties.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))   
                  
        if script == "high student satisfaction":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Hoge tevredenheid bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat hun studenten onlangs zeer tevreden waren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens gestandaardiseerde interviews was de tevredenheid onder studenten van de school historisch hoog tijdens het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Vertegenwoordigers van studenten hebben verklaard dat de school hen een ondersteunende, leuke en veilige leeromgeving biedt.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van {agency} hebben gemeld dat hun kinderen zowel voor als na schooltijd energiek en gemotiveerd zijn en graag willen leren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond heeft het succes op {agency} toegeschreven aan de uitmuntendheid van het onderwijzend personeel op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het management van de school benadrukte desgevraagd hun uitgebreide initiatieven op het gebied van sociale integratie, anti-pesten en interactief leren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Deze initiatieven zijn naar verluidt zeer goed ontvangen door studenten, net als de nadruk op een redelijke werkdruk en sociale evenementen op schoolniveau.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben hun blijdschap geuit namens hun kinderen, maar hopen ook dat de school de focus op de leerresultaten van de leerlingen niet zal verliezen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Andere scholen onderzoeken naar verluidt de methoden die gebruikt worden bij {agency} onder druk om hun eigen tevredenheidscijfers te verhogen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script)) 

        if script == "low student stress":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Weinig stress bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat hun studenten onlangs zeer lage stresspercentages hebben gemeld.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens gestandaardiseerde interviews was de stress onder studenten op de school historisch laag tijdens het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studentenvertegenwoordigers hebben aangegeven dat ze uitstekende ondersteuning hebben gekregen bij het beheren van hun werkdruk en sociale kwesties.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders bij {agency} hebben gerapporteerd dat hun kinderen slechts zelden bedenkingen uiten over hun schoolwerk.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond schreef het succes op {agency} toe aan het hoog opgeleide personeel op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het management van de school benadrukte desgevraagd hun uitgebreide campagnes voor het beheren van de werkdruk en actief leren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Deze initiatieven zijn naar verluidt zeer goed ontvangen door studenten, samen met de steun die ze krijgen van docenten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben hun blijdschap geuit namens hun kinderen, maar hopen ook dat de school de focus op de leerresultaten van de leerlingen niet zal verliezen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Naar verluidt onderzoeken andere scholen de methoden die gebruikt worden bij {agency} onder druk om hun eigen stresscijfers te verlagen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script)) 

        if script == "high student stress":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Veel stress bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat hun studenten onlangs zeer hoge stresscijfers hebben laten zien.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens gestandaardiseerde interviews was de stress onder studenten op de school historisch hoog tijdens het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Vertegenwoordigers van studenten hebben verklaard dat ze een buitensporige werkdruk en beperkte ondersteuning hebben gehad op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders bij {agency} hebben gerapporteerd dat hun kinderen vaak hun bedenkingen uiten over hun schoolwerk en leeromgeving.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond heeft {agency} beschuldigd van overwerken van zowel leraren als studenten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het management van de school benadrukte desgevraagd hun uitgebreide campagnes voor het beheren van de werkdruk en actief leren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Deze initiatieven zijn naar verluidt zeer slecht ontvangen door studenten en bekritiseerd als overgecompliceerd door docenten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben hun bezorgdheid geuit over hun kinderen en maken zich zorgen over het welzijn van de leerlingen op de lange termijn.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Naar verluidt overwegen veel ouders om hun kind over te plaatsen van {agency} naar een gezondere leeromgeving.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))   

        if script == "low student satisfaction":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Lage tevredenheid bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat hun studenten onlangs zeer lage tevredenheidspercentages hebben gemeld.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens gestandaardiseerde interviews was de tevredenheid onder studenten op de school historisch laag tijdens het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Vertegenwoordigers van studenten hebben verklaard dat de schoolomgeving stressvol, hectisch en zelfs onveilig is.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders bij {agency} hebben gemeld dat hun kinderen vaak ongelukkig thuiskomen en niet gemotiveerd zijn voor hun studie.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond heeft {agency} beschuldigd van het creëren van een vijandige werkomgeving.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het management van de school benadrukte desgevraagd hun uitgebreide initiatieven op het gebied van sociale integratie, anti-pesten en interactief leren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Deze initiatieven zijn naar verluidt zeer slecht ontvangen door studenten en als nutteloos bekritiseerd door docenten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben hun bezorgdheid geuit over hun kinderen en maken zich zorgen over de motivatie van de leerlingen op de lange termijn.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Naar verluidt overwegen veel ouders om hun kind over te plaatsen van {agency} naar een meer ondersteunende en motiverende school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))

        if script == "low staff satisfaction":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Personeel ongelukkig bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft aangekondigd dat hun personeel onlangs een zeer lage werktevredenheid heeft aangegeven.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens interne personeelsinterviews bij {agency} was de werktevredenheid onder docenten op de school historisch laag tijdens het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Personeelsleden hebben zelf hun ontevredenheid geuit over hun arbeidsomstandigheden en werkgemeenschap.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens een leraar van {agency} geïnterviewd door {self.papers[papernumber]}, laat de school zien hoe een school faalt in het zorgen voor haar personeel.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond heeft verklaard dat {agency} blijk heeft gegeven van slecht beoordelingsvermogen en slecht management.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De verklaring van lage personeelstevredenheid komt in het kielzog van een verhoogde druk van het management bij {agency} om de leerresultaten te verbeteren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders hebben gezegd dat ze zich zorgen maken over de leraren, maar hopen dat deze resultaten geen invloed zullen hebben op de leerresultaten op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De studenten die hierover werden geïnterviewd waren ontevreden over het feit dat docenten tevreden waren, maar hoopten dat dit niet zou leiden tot bestraffende cijfers.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} schreef de problemen toe aan onvoldoende middelen die ze van de budgethouder hadden gekregen en vroeg de leraren om geduld.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))   
        
        if script == "understaffed":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Personeelsproblemen bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"{agency} heeft meerdere onderwijsvacatures aangekondigd na consistente personeelstekorten tijdens het laatste semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De school is er niet in geslaagd om de vacatures tijdig in te vullen na de massale stakingen van leraren in het midden van het semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Leerkrachten die nog steeds bij {agency} werken, geven de schoolleiding de schuld van het overwerken en onderbetalen van leerkrachten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Volgens een voormalige docent van {agency} heeft de school haar personeel systematisch in de steek gelaten en lijdt ze daar nu onder.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond heeft verklaard dat {agency} blijk heeft gegeven van slecht beoordelingsvermogen en slecht management.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De verklaring van lage personeelstevredenheid komt in het kielzog van een verhoogde druk van het management bij {agency} om de leerresultaten te verbeteren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben gezegd dat ze zich zorgen maken over de levensvatbaarheid van het onderwijs op de lange termijn, gezien het gebrek aan leraren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studenten die hierover werden geïnterviewd, zeiden dat ze zich niet gesteund voelden bij hun studie en vaak zonder leraar of in zeer grote groepen moesten werken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het management van de {agency} schreef de problemen toe aan onvoldoende middelen die ze van de budgethouder hadden gekregen en vroeg om geduld van de ouders.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script)) 

        if script == "not enough events":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Geen evenementen bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Studenten van {agency} hebben geklaagd dat er geen recreatieve evenementen zijn geweest tijdens het afgelopen semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De school heeft de laatste tijd geen evenementen kunnen plannen vanwege beschikbaarheidsproblemen en financieringsproblemen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Leerkrachten verwijten de schoolleiding dat ze leerkrachten overwerkt en onderbetaalt, wat resulteert in een lage motivatie voor het organiseren van evenementen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond heeft verklaard dat {agency} blijk heeft gegeven van slecht beoordelingsvermogen en slecht management.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben gezegd dat ze zich zorgen maken over het welzijn van hun kinderen op de school op de lange termijn.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studenten die hierover werden geïnterviewd, zeiden dat ze zich overweldigd voelden door hun werkdruk, gezien het gebrek aan recreatieve afleiding.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het management van de {agency} schreef de problemen toe aan onvoldoende middelen die ze van de budgethouder hadden gekregen en vroeg om geduld van de ouders.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))         
        
        if script == "insufficient equipment":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Geen apparatuur bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Docenten van {agency} hebben geklaagd dat ze tijdens het vorige semester onvoldoende apparatuur hadden om mee te werken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De school heeft onlangs geen lesmateriaal kunnen kopen vanwege problemen met de aanvoerlijn en financiering.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Leraren bij {agency} verwijten de schoolleiding dat ze het belang van voldoende lesmateriaal voor het succesvol uitvoeren van hun werk onderschat hebben.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond heeft verklaard dat {agency} blijk heeft gegeven van slecht beoordelingsvermogen en slecht management.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders op de school hebben gezegd dat ze zich zorgen maken over de staat van het onderwijs op de school op de lange termijn.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studenten die werden geïnterviewd over deze kwestie zeiden dat ze zich overweldigd voelden door hun werkdruk, gezien het gebrek aan geschikte apparatuur.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het management van de {agency} schreef de problemen toe aan onvoldoende middelen die ze van de budgethouder hadden gekregen en vroeg om geduld van ouders.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))   
                  
        if script == "misuse of funds":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Financieringsschandaal bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Een klokkenluider die bij {agency} werkt, heeft het management van de school ontmaskerd wegens ongepast gebruik van schoolgeld voor persoonlijke doeleinden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Topmanagers worden ervan beschuldigd schoolgeld uit te geven aan zaken als luxeartikelen en autoaccessoires.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De vermeende misdaad is gemeld bij de politie, die een strafrechtelijk onderzoek naar de zaak is begonnen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van de school hebben hun verontwaardiging uitgesproken over deze beschuldigingen en verklaard dat ze het vertrouwen in {agency} hebben verloren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond heeft de vakbondsleden gedistantieerd van het schandaal en legt de schuld volledig bij {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studentenvertegenwoordigers hebben verklaard dat ze vermoedens hadden over mogelijk wangedrag vanwege de verslechterende omstandigheden op school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studenten hebben problemen gemeld zoals lekkende plafonds, verstopte toiletten en afbrokkelende gangen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Toen dit onder de aandacht van de schoolleiding werd gebracht, het personeel beweerde dat de school niet voldoende geld had voor reparaties.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het ministerie van Onderwijs heeft een onderzoek ingesteld naar de vermeende fraude.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))   

        if script == "improper conduct":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Gedragsschandaal bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Een docent van {agency} is beschuldigd van ongepast gedrag ten opzichte van een leerling door een anonieme tip aan {self.papers[papernumber]}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De krant heeft de beschuldigingen doorgegeven aan de politie, die de zaak onderzoekt.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De leraar wordt beschuldigd van zowel ongepast gedrag met een minderjarige als verwaarlozing van zijn lesgevende verantwoordelijkheden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van de school hebben hun verontwaardiging uitgesproken over deze beschuldigingen en verklaard dat ze {agency} niet langer veilig vinden voor leerlingen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Veel ouders dreigen hun kind over te plaatsen naar een andere school als er niet onmiddellijk actie wordt ondernomen om de situatie aan te pakken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Leraren op de school zijn geschokt door de beschuldigingen en verklaarden dat ze op geen enkele manier op de hoogte konden zijn van het vermeende wangedrag.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Vertegenwoordigers van studenten verklaarden dat ze zich niet langer veilig voelden in de school en dat ze al eerder vermoedens hadden geuit bij de schoolleiding.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} beweerde niet op de hoogte te zijn van incidenten, maar verklaarde dat ze volledig zouden meewerken aan elk onderzoek.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Er is een onderzoek ingesteld door het Ministerie van Onderwijs naar het vermeende wangedrag. Een woordvoerder van het ministerie veroordeelde elk wangedrag.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))        

        if script == "theft (outside)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Diefstal bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Volgens vertegenwoordigers van de school is er een waardevolle computer gestolen bij {agency}. De diefstal is gemeld bij de politie.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} zegt niet te weten wie de diefstal heeft gepleegd, maar heeft geen reden om iemand van de school te verdenken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Nadat de diefstal was ontdekt, werd een kapotte schooldeur aangetroffen, vermoedelijk de ingang van de dief.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De directie heeft {self.papers[papernumber]} geïnformeerd dat ze de computer moeten vervangen uit het schoolbudget.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Dit zal extra druk leggen op het budget van de school. Leraren hebben hun bezorgdheid geuit dat dit de beschikbaarheid van andere apparatuur kan beperken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studenten op de school hebben hun bezorgdheid geuit dat hun persoonlijke eigendommen niet veilig zijn op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal ouders van {agency} heeft ook aangegeven dat ze zich zorgen maken over het fysieke en emotionele welzijn van hun kind op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))  

        if script == "theft (inside)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Diefstal bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Volgens vertegenwoordigers van de school is er een waardevolle computer gestolen bij {agency}. De diefstal is gemeld bij de politie.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} verklaart dat ze reden hebben om een leerling of personeelslid van de school te verdenken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Er was een schoolsleutel gebruikt om de school binnen te komen, wat duidt op een persoon die op de een of andere manier toegang heeft tot de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De directie heeft {self.papers[papernumber]} geïnformeerd dat ze de computer moeten vervangen uit het schoolbudget.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Dit zal extra druk leggen op het budget van de school. Leraren hebben hun bezorgdheid geuit dat dit de beschikbaarheid van andere apparatuur kan beperken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studenten op de school hebben hun bezorgdheid geuit dat hun persoonlijke eigendommen niet veilig zijn op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal ouders van {agency} heeft ook aangegeven dat ze zich zorgen maken over het fysieke en emotionele welzijn van hun kind op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))  

        if script == "bullying (students)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Pesten bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Een student van {agency} heeft {self.papers[papernumber]} verteld dat zij het slachtoffer is geworden van systematisch en langdurig pesten door medestudenten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De pesterijen zijn gepleegd door een aantal verschillende leerlingen van de school, van verschillende leeftijden en geslachten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het slachtoffer zegt het doelwit te zijn geweest van zowel fysiek als emotioneel geweld door de andere leerlingen, wat blijvende littekens heeft achtergelaten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het slachtoffer heeft verklaard dat ze bang zijn om zonder hun ouders naar buiten te gaan en dat ze zich geïsoleerd en niet gesteund voelen op school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} heeft verklaard dat ze ervan op de hoogte waren dat het slachtoffer te maken heeft gehad met plagerijen, maar niet van de omvang van de problemen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De school plant een trainingsdag voor alle leerlingen van de school om hen bewust te maken van pesten en hoe ze dit als groep kunnen voorkomen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Leraren op de school hebben verklaard dat ze zich niet in staat voelen om adequaat met de situatie om te gaan vanwege de beperkingen die hen worden opgelegd.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De ouders van het slachtoffer zeggen dat ze liever niet naar een andere school verhuizen, maar dat ze dat wel zullen moeten doen als de situatie niet wordt opgelost.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het incident heeft geleid tot een bredere bezorgdheid in de gemeenschap over de veiligheid van studenten bij {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))          

        if script == "bullying (staff)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Intimidatie van personeel bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Een leraar bij {agency} heeft zijn collega's beschuldigd van pesten en het creëren van een vijandige werkomgeving.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De pesterijen zijn gepleegd door verschillende personeelsleden van de school, van verschillende leeftijden en geslachten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het slachtoffer zegt het doelwit te zijn geweest van zowel sociaal als emotioneel geweld door de andere leerlingen, wat blijvende littekens heeft achtergelaten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het slachtoffer heeft verklaard dat ze nu last hebben van angst als ze naar hun werk gaan en dat ze zich ziek hebben moeten melden vanwege de pesterijen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} heeft verklaard dat ze ervan op de hoogte waren dat het slachtoffer te maken heeft gehad met plagerijen, maar niet van de omvang van de problemen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De school organiseert een verplichte Human Resources-trainingsdag voor alle medewerkers en geeft aan pesten op de werkplek zeer serieus te nemen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van {agency} hebben hun bezorgdheid geuit over het feit dat dit soort slecht gedrag kan worden weerspiegeld in de kwaliteit van de leeromgeving op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Sommige ouders hebben gedreigd hun kind over te plaatsen naar een andere school als de situatie niet snel wordt aangepakt.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het incident heeft geleid tot een bredere bezorgdheid in de gemeenschap over de werkomgeving waarmee leraren op lokale scholen te maken hebben.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))      

        if script == "alumni grant":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Alumnidonatie aan {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Een oud-alumnus van {agency} heeft een gulle donatie gedaan aan het budget van de school voor het komende semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Verwacht wordt dat de subsidie {agency} de broodnodige ademruimte zal geven in het financieel krappe onderwijslandschap in de regio.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De donateur heeft {self.papers[papernumber]} verteld dat ze hun waardering wilden tonen aan de school die hen heeft geholpen hun academische reis te beginnen..", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De donor wil liever anoniem blijven, maar leraren op de school hebben verklaard dat ze zich de donor nog goed herinneren uit hun tijd op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} heeft verklaard dat de gulle donatie het diepgaande effect illustreert dat studeren aan de school zelfs jaren later nog kan hebben.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De school is van plan om de financiering te gebruiken om nieuwe laboratoriumapparatuur voor de school aan te schaffen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van {agency} hebben hun waardering uitgesproken voor de donor en hun hoop dat hun eigen kinderen net zo'n positieve ervaring zullen hebben op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studentenvertegenwoordigers van {agency} zeggen dat ze hopen dat de nieuwe financiering zal leiden tot betere schoolmaaltijden voor studenten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De donatie is al verwerkt en zal worden toegepast op het budget van {agency} voor het komende semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))     

        if script == "alumni complaint":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Alumniklacht bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Een voormalige oud-leerling van {agency} heeft een klacht ingediend over de staat van het onderwijs op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Sommigen maken zich zorgen over een te ideologische focus in het onderwijs op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De alumni hebben {self.papers[papernumber]} verteld dat de pedagogische methoden die op de school gebruikt worden niet meer overeenkomen met hun waarden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De oud-leerling wil liever anoniem blijven, maar leraren op de school hebben verklaard dat ze zich de schenker goed herinneren uit hun tijd op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} heeft verklaard dat het lesgeven op de school in overeenstemming is met de richtlijnen van het Ministerie van Onderwijs.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het ministerie heeft onlangs de focus in hun schoolrichtlijnen en evaluaties verlegd naar leerresultaten op het gebied van natuurwetenschappen, wiskunde en lezen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van {agency} hebben hun bezorgdheid geuit over de klacht, maar hebben zelf geen klacht ingediend over de methoden die op de school worden gebruikt.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studentenvertegenwoordigers van {agency} zeggen dat het onderwijs op de school gewoon geëvolueerd is ten opzichte van toen het alumnilid op de school zat.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het valt nog te bezien of er in het komende semester meer aandacht wordt besteed aan deze kwesties bij {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))   

        if script == "flood":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Overstroming bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Rampspoed heeft toegeslagen bij {agency} in de vorm van een zeer verwoestende overstroming in de afgelopen dag.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Niemand kwam om bij de overstroming, maar verschillende personeelsleden raakten zwaar gewond.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De gewonde personeelsleden zijn naar een bijna-ziekenhuis gebracht en zullen naar verwachting volledig herstellen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Gelukkig waren er geen studenten op school tijdens de overstroming, omdat het semester net de dag ervoor was afgelopen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} heeft verklaard dat de overstroming een bizar ongeluk was en hoopt dat hun medewerkers zo snel mogelijk herstellen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond noemde de reactie van de school op de overstroming ontoereikend en zette vraagtekens bij de protocollen bij {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van {agency} hebben hun bezorgdheid geuit over de overstroming en verklaard dat ze er niet langer op vertrouwen dat hun kinderen veilig zijn op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De schade en medische kosten als gevolg van de overstroming zullen naar verwachting uit het budget van de school betaald moeten worden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Dit is het gevolg van een controversiële recente beslissing dat scholen hun eigen noodkosten moeten dekken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))   

        if script == "mold":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Schimmel bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Er is een gevaarlijke schimmel gevonden bij {agency}, waardoor de gezondheid en veiligheid in gevaar komen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De school werd twee weken voor het einde van het semester gesloten in afwachting van een onderzoek door de regionale gezondheidsdiensten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal studenten en personeelsleden van {agency} verklaart last te hebben gehad van symptomen die overeenkomen met blootstelling aan schimmel.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De ontdekking van schimmel in de school komt in de nasleep van recente problemen met schimmel in verschillende scholen en ziekenhuizen in de regio.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Langdurige blootstelling aan schimmel kan zeer ernstige gevolgen hebben voor de gezondheid, waaronder ademhalingsmoeilijkheden en astma.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het management van de school heeft verklaard dat ze de schimmelsituatie zeer serieus nemen en meewerken met de lokale autoriteiten in hun onderzoek.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het is momenteel onduidelijk of de schimmel te wijten is aan een foutieve constructie of slechte schoonmaakpraktijken bij {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Sommige leraren en leerlingen van {agency} hebben de school ervan beschuldigd eerdere schimmelgerelateerde problemen te negeren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Door de schimmelproblemen in de school is het twijfelachtig of de school volgens plan het volgende semester open kan gaan.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))  

        if script == "broken windows":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Vandalisme bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"De ramen van {agency} zijn vernield door een onbekende vandaal, aldus vertegenwoordigers van de school. Het vandalisme is gemeld bij de politie.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} zegt niet te weten wie het vandalisme heeft gepleegd, maar heeft geen reden om iemand van de school te verdenken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Er werden geen goederen uit de school gestolen, wat erop wijst dat het misdrijf louter vandalisme was.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De directie heeft {self.papers[papernumber]} geïnformeerd dat ze de ramen moeten vervangen uit het schoolbudget.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Dit zal extra druk leggen op het budget van de school. Leraren hebben hun bezorgdheid geuit over het feit dat dit de beschikbaarheid van lesmateriaal kan beperken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studenten op de school hebben hun bezorgdheid geuit dat hun persoonlijke eigendommen niet veilig zijn op de school als de dader niet gevonden kan worden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal ouders van {agency} heeft ook aangegeven dat ze zich zorgen maken over het fysieke en emotionele welzijn van hun kind op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))    
                  
        if script == "illness (flu)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Griepuitbraak bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Er heeft zich een griepuitbraak voorgedaan bij {agency}, met gezondheids- en veiligheidsproblemen als gevolg.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De school werd na het einde van het semester gesloten in afwachting van een onderzoek door de regionale gezondheidsdiensten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal studenten en medewerkers van {agency} geeft aan last te hebben gehad van ernstige griepsymptomen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De griepepidemie op de school komt in de nasleep van recente problemen met virusuitbraken in verschillende scholen en ziekenhuizen in de regio.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Langdurige griepinfecties kunnen zeer ernstige gevolgen hebben voor de gezondheid, waaronder ademhalingsproblemen en astma.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het management van de school heeft verklaard dat ze de situatie zeer serieus nemen en meewerken met de lokale autoriteiten in hun onderzoek.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het is momenteel onduidelijk hoe de uitbraak op de school heeft kunnen plaatsvinden. {agency} heeft gewezen op slechte hygiënepraktijken buiten de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Sommige docenten en studenten van {agency} hebben de school ervan beschuldigd eerdere virusgerelateerde problemen te negeren, waardoor het probleem verergerd is.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van {agency} hebben aangegeven dat ze verwachten dat de situatie naar behoren wordt afgehandeld voordat ze hun kinderen terugsturen naar de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))  

        if script == "illness (noro)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Norovirusuitbraak bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Er is norovirus uitgebroken bij {agency}, waardoor de gezondheid en veiligheid in het geding zijn.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De school werd na het einde van het semester gesloten in afwachting van een onderzoek door de regionale gezondheidsdiensten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal studenten en personeelsleden van {agency} verklaart last te hebben gehad van ernstige voedselvergiftigingsverschijnselen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De uitbraak van het norovirus op de school komt in de nasleep van recente problemen met virusuitbraken in verschillende scholen en ziekenhuizen in de regio.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Langdurige norovirusinfecties kunnen zeer ernstige gevolgen hebben voor de gezondheid, waaronder koorts en spijsverteringsproblemen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het management van de school heeft verklaard dat ze de situatie zeer serieus nemen en meewerken met de lokale autoriteiten in hun onderzoek.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het is momenteel onduidelijk hoe de uitbraak op de school heeft kunnen plaatsvinden. {agency} geeft de schuld aan slechte hygiënepraktijken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Sommige docenten en studenten van {agency} hebben de school ervan beschuldigd eerdere problemen te negeren, waardoor het probleem verergerd is.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van {agency} hebben aangegeven dat ze verwachten dat de situatie naar behoren wordt afgehandeld voordat ze hun kinderen terugsturen naar de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))

        if script == "student injury (limb)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Gebroken arm bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Een leerling van {agency} heeft zijn arm gebroken tijdens een recreatief evenement georganiseerd door de school, aldus schoolfunctionarissen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De student werd naar een ziekenhuis in de buurt gebracht en zal naar verwachting volledig herstellen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal studenten en medewerkers van {agency} hebben {self.papers[papernumber]} verteld dat ze zich zorgen maken over de veiligheidsprotocollen bij {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het ongeluk komt in de nasleep van recente problemen met de veiligheid bij recreatieve evenementen in verschillende scholen en ziekenhuizen in de regio.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Critici zeggen dat het slechts een kwestie van tijd is voordat er ernstigere verwondingen plaatsvinden op de school als de veiligheidsproblemen niet worden aangepakt.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het management van de school heeft verklaard dat ze een externe expert hebben ingehuurd om te helpen bij het bijwerken van hun veiligheidsprotocollen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het is momenteel onduidelijk hoe het ongeluk heeft kunnen gebeuren. Leraren bij {agency} hebben het management de schuld gegeven van te recreatieprogramma's.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Sommige docenten en studenten van {agency} hebben de school er ook van beschuldigd dat ze eerdere veiligheidsgerelateerde problemen hebben genegeerd.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van {agency} hebben aangegeven dat ze verwachten dat de situatie naar behoren wordt afgehandeld voordat ze hun kinderen terugsturen naar de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))   

        if script == "student injury (concussion)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Hersenschudding bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Een leerling van {agency} heeft een hersenschudding opgelopen tijdens een recreatief evenement georganiseerd door de school, aldus de schoolleiding.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De student werd naar een ziekenhuis in de buurt gebracht en zal naar verwachting volledig herstellen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal studenten en medewerkers van {agency} hebben {self.papers[papernumber]} verteld dat ze zich zorgen maken over de veiligheidsprotocollen bij {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het ongeluk komt in de nasleep van recente problemen met de veiligheid bij recreatieve evenementen in verschillende scholen en ziekenhuizen in de regio.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Critici zeggen dat het slechts een kwestie van tijd is voordat er ernstigere verwondingen plaatsvinden op de school als de veiligheidsproblemen niet worden aangepakt.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het management van de school heeft verklaard dat ze een externe expert hebben ingehuurd om te helpen bij het bijwerken van hun veiligheidsprotocollen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het is momenteel onduidelijk hoe het ongeluk heeft kunnen gebeuren. Leraren bij {agency} hebben het management de schuld gegeven van te recreatieprogramma's.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Sommige docenten en studenten van {agency} hebben de school er ook van beschuldigd dat ze eerdere veiligheidsgerelateerde problemen hebben genegeerd.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van {agency} hebben aangegeven dat ze verwachten dat de situatie naar behoren wordt afgehandeld voordat ze hun kinderen terugsturen naar de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))       

        if script == "outbreak (lice)":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Luizenuitbraak bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Er is een luizenuitbraak geweest bij {agency}, met gezondheids- en veiligheidsproblemen tot gevolg.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De school werd twee weken voor het einde van het semester gesloten in afwachting van een onderzoek door de regionale gezondheidsdiensten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal studenten en personeelsleden van {agency} zegt last te hebben gehad van luizenplagen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De luizenuitbraak op de school komt in de nasleep van recente problemen met uitbraken van ongedierte in verschillende scholen en ziekenhuizen in de regio.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een langdurige luizenplaag kan ernstige gevolgen hebben voor de gezondheid, waaronder virale en bacteriële infecties.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het management van de school heeft verklaard dat ze de situatie zeer serieus nemen en meewerken met de lokale autoriteiten in hun onderzoek.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het is momenteel onduidelijk hoe de uitbraak op de school heeft kunnen plaatsvinden. {agency} geeft de schuld aan slechte hygiënepraktijken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Sommige leraren en leerlingen van {agency} hebben de school ervan beschuldigd eerdere problemen met ongedierte te negeren.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van {agency} hebben aangegeven dat ze verwachten dat de situatie naar behoren wordt afgehandeld voordat ze hun kinderen terugsturen naar de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))   

        if script == "earthquake":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Aardbeving bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Een ramp heeft toegeslagen bij {agency} in de vorm van een zeer verwoestende aardbeving in de afgelopen dag.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Niemand kwam om bij de aardbeving, maar verschillende personeelsleden raakten zwaargewond, deels doordat het dak van de school instortte.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De gewonde personeelsleden zijn naar een bijna-ziekenhuis gebracht en zullen naar verwachting volledig herstellen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Gelukkig waren er geen studenten op school tijdens de aardbeving, omdat het semester net de dag ervoor was afgelopen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} heeft verklaard dat de aardbeving een bizar ongeluk was en hoopt dat hun medewerkers zo snel mogelijk herstellen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een vertegenwoordiger van de lerarenvakbond noemde de reactie van de school op de aardbeving inadequaat en trok de veiligheidsprotocollen bij {agency} in twijfel.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"PDe ouders van {agency} hebben hun bezorgdheid geuit over de aardbeving en verklaard dat ze er niet langer op vertrouwen dat hun kinderen veilig zijn op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De schade en medische kosten als gevolg van de aardbeving zullen naar verwachting uit het budget van de school betaald moeten worden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Dit is het gevolg van een controversiële recente beslissing dat scholen hun eigen noodkosten moeten dekken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))   

        if script == "equipment breakage":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Apparatuurbreuk bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Waardevolle apparatuur op {agency} is vernield door een onbekende vandaal, aldus vertegenwoordigers van de school. Het vandalisme is gemeld bij de politie.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} zegt niet te weten wie het vandalisme heeft gepleegd, maar heeft geen reden om iemand van de school te verdenken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Er werden geen goederen uit de school gestolen, wat erop wijst dat het misdrijf louter vandalisme was.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} heeft {self.papers[papernumber]} geïnformeerd dat ze de apparatuur moeten vervangen uit het schoolbudget.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Dit zal extra druk leggen op het budget van de school. Leraren hebben hun bezorgdheid geuit over het feit dat dit de beschikbaarheid van lesmateriaal kan beperken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studenten op de school hebben hun bezorgdheid geuit dat hun persoonlijke eigendommen niet veilig zijn op de school als de dader niet gevonden kan worden.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Een aantal ouders van {agency} heeft ook aangegeven dat ze zich zorgen maken over het fysieke en emotionele welzijn van hun kind op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))  

        if script == "equipment donation":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Apparatuur donatie aan {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Een oud-leerling van {agency} heeft gul een waardevol computersysteem gedoneerd aan de school voor het komende semester.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De donatie zal naar verwachting elders op school geld vrijmaken en leerlingen de beschikking geven over ultramoderne apparatuur om mee te werken.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De donor heeft {self.papers[papernumber]} verteld dat ze hun waardering wilden tonen aan de school die hen heeft geholpen hun academische reis te beginnen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De donor wil liever anoniem blijven, maar leraren op de school hebben verklaard dat ze zich de donor nog goed herinneren uit hun tijd op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} heeft verklaard dat de gulle donatie het diepgaande effect illustreert dat studeren aan de school zelfs jaren later nog kan hebben.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van {agency} hebben de hoop uitgesproken dat hun eigen kinderen net zo'n positieve ervaring zullen hebben op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studentenvertegenwoordigers van {agency} zeggen dat ze hopen dat de nieuwe financiering zal leiden tot betere schoolmaaltijden voor studenten.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De donatie is al verwerkt en zal het komende semester aanwezig zijn bij {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))    

        if script == "external evaluation":
            title = []
            lines = []
            author = []
            paper = []
            name = script
            text = self.arial3.render(f"{self.papers[papernumber]}", True, self.black)
            paper.append((text, (x, y)))
            y += 50
            text = self.arial.render(f"Staatsonderzoek bij {agency}", True, self.black)
            title.append((text, (x, y)))
            y += 50
            text = self.arial2.render(f"Het ministerie van Onderwijs heeft aangekondigd dat het in het volgende semester een ongeplande evaluatie zal uitvoeren van de activiteiten bij {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"De aankondiging komt na publieke bezorgdheid over de staat van het onderwijs op de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het departement heeft {self.papers[papernumber]} verteld dat ze een anonieme klacht over de school hebben ontvangen die de aanleiding was voor hun onderzoek.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het ministerie weigerde verder commentaar te geven op de exacte vorm en aard van de klacht, maar verklaarde dat deze deels betrekking had op de onderwijspraktijk.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{agency} heeft verklaard dat het lesgeven op de school in overeenstemming is met de richtlijnen van het Ministerie van Onderwijs.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het ministerie heeft onlangs de focus in hun schoolrichtlijnen en evaluaties verlegd naar leerresultaten op het gebied van natuurwetenschappen, wiskunde en lezen.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Ouders van {agency} hebben hun bezorgdheid geuit over het onderzoek, maar hebben zelf geen klacht ingediend bij {self.papers[papernumber]} over de school.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Studentenvertegenwoordigers van {agency} zeggen dat er altijd problemen zijn om aan te pakken in het onderwijs.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"Het valt nog te bezien of er in het komende semester meer aandacht wordt besteed aan deze kwesties bij {agency}.", True, self.black)
            lines.append((text, (x, y)))
            y += 40
            text = self.arial2.render(f"{self.authors[authornumber]}", True, self.black)
            author.append((text, (x, y)))
            for i in lines:
                self.window.blit(i[0], (i[1][0], i[1][1]))
            y += 40
            self.news_archive[agency].append(((title, paper, lines, author), self.round_number, script))

        return (title, paper, lines, author)
        


    def create_agency_stats(self): #creates monitors for agency stats
        for i in self.agencies:
            number = random.randrange(0, 101) #staff satisfaction
            number2 = random.randrange(0, 101) #staff performance
            number3 = random.randrange(0, 101) #staff stress
            self.staff_stats[i[0]] = [number, number2, number3, number, number2, number3] #staff satisfaction, staff performance, staff stress levels followed by predicted values
            number = random.randrange(0, 101) #student satisfaction
            number2 = random.randrange(25, 101) #student reading
            number3 = random.randrange(25, 101) #student math
            number4 = random.randrange(25, 101) #student science
            number5 = int((number2 + number3 + number4)/3) #student overall
            number6 = random.randrange(0, 101) #student stress
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
            self.add_budget_option(i[0], "de financiering verhogen", 1000)
            self.add_budget_option(i[0], "vermindering van financiering", -1000)
            self.add_budget_option(i[0], "externe sonde uitvoeren", 300)
            self.add_budget_option(i[0], "personeel inhuren (5 personen)", 2500)
            self.add_budget_option(i[0], "ontslagen initiëren (5 personen)", -2000)
            self.add_budget_option(i[0], "apparatuur aanschaffen", 1000)
            self.add_budget_option(i[0], "evenement plannen", 700)
            self.add_budget_option(i[0], "annulering evenement", -600)
            self.add_budget_option(i[0], "apparatuur recyclen", -500)

    def create_agency_feedback(self): #create feedback for an agency
        for i in self.agencies:
            self.add_agency_feedback(i[0], f"{i[0]} personeel en stress:")
            self.add_agency_feedback(i[0], f"{i[0]} apparatuur en leren:")
            self.add_agency_feedback(i[0], f"{i[0]} evenementen:")


    def adjust_total_budget(self, amount: float): #change the total budget based on player input and game events
        self.total_budget += amount

    def adjust_agency_budget(self, agency, amount: float): #adjusts budget for a given agency
        self.agency_stats[agency][0] += amount
        if self.agency_stats[agency][0] < -8000:
            self.agency_stats[agency][0] = -8000

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
                        index = random.randrange(0, 18)
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
                added = random.randrange(20, 26)
            if number > 20:
                added = random.randrange(15, 21)
            if number > 40:
                added = random.randrange(10, 16)
            if number > 60:
                added = random.randrange(5, 11)
            if number > 80:
                added = random.randrange(1, 6)
        if direction < 0:
            if number > 0:
                added = random.randrange(-5, 2)
            if number > 20:
                added = random.randrange(-10, -4)
            if number > 40:
                added = random.randrange(-15, -9)
            if number > 60:
                added = random.randrange(-20, -14)
            if number > 80:
                added = random.randrange(-25, -19)
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

        if action == "de financiering verhogen" or action == "vermindering van financiering":
            self.adjust_total_budget(-amount)
            self.adjust_agency_budget(agency, amount)
        if action == "personeel inhuren (5 personen)":
            self.adjust_agency_staff(agency, 5)
            self.adjust_agency_budget(agency, -amount)
            self.adjust_soft_stats("student reading", agency, 1)
            self.adjust_soft_stats("student math", agency, 1)
            self.adjust_soft_stats("student science", agency, 1)
            self.adjust_soft_stats("staff performance", agency, 1)
            self.adjust_soft_stats("staff satisfaction", agency, 1)
            self.adjust_soft_stats("staff performance", agency, 1)
            self.adjust_soft_stats("staff stress", agency, -1)
        if action == "externe sonde uitvoeren":
            self.adjust_agency_budget(agency, -amount)
            self.adjust_soft_stats("staff performance", agency, 1)
            self.adjust_soft_stats("staff stress", agency, 1)
            self.adjust_soft_stats("student reading", agency, 1)
            self.adjust_soft_stats("student math", agency, 1)
            self.adjust_soft_stats("student science", agency, 1)
            self.adjust_soft_stats("student stress", agency, 1)
        if action == "ontslagen initiëren (5 personen)":
            self.adjust_agency_budget(agency, -amount)
            self.adjust_agency_staff(agency, -5)
            self.adjust_soft_stats("student reading", agency, -1)
            self.adjust_soft_stats("student math", agency, -1)
            self.adjust_soft_stats("student science", agency, -1)
            self.adjust_soft_stats("staff performance", agency, -1)
            self.adjust_soft_stats("staff satisfaction", agency, -1)
            self.adjust_soft_stats("staff stress", agency, 1)
        if action == "apparatuur aanschaffen":
            self.adjust_agency_budget(agency, -amount)
            self.adjust_agency_equipment(agency, amount - 100)
            self.adjust_soft_stats("student reading", agency, 1)
            self.adjust_soft_stats("student math", agency, 1)
            self.adjust_soft_stats("student science", agency, 1)
            self.adjust_soft_stats("staff satisfaction", agency, 1)
            self.adjust_soft_stats("staff performance", agency, 1)
        if action == "apparatuur recyclen":
            self.adjust_agency_budget(agency, -amount)
            self.adjust_agency_equipment(agency, amount * 1.5)
            self.adjust_soft_stats("student reading", agency, -1)
            self.adjust_soft_stats("student math", agency, -1)
            self.adjust_soft_stats("student science", agency, -1)
            self.adjust_soft_stats("staff satisfaction", agency, -1)
            self.adjust_soft_stats("staff performance", agency, -1)
        if action == "evenement plannen":
            self.create_agency_event(agency, 1, amount)
            self.adjust_soft_stats("student satisfaction", agency, 1)
            self.adjust_soft_stats("student stress", agency, -1)
            self.adjust_soft_stats("staff stress", agency, 1)
        if action == "annulering evenement":
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
                text = self.calibri2.render("Problemen hier", True, self.crimson)
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
                colour = self.forestgreen
                text = self.calibri2.render("Geen problemen!", True, self.black)
                width = text.get_width()
                actions.append((text, (i[0][0]-(width/2), i[0][1]+5)))
            else:
                colour = self.gold
                text = self.calibri2.render("Bevredigend!", True, self.black)
                width = text.get_width()
                actions.append((text, (i[0][0]-(width/2), i[0][1]+5)))
            for u in agencies:
                if self.agency == u[0] and u[1] == count:
                    colour = self.orange
            pygame.draw.circle(self.window, colour, i[0], self.radius)
            count += 1

        for i in self.agency_labels: #writes main menu labels
            text = self.calibri.render(i[0], True, self.black) 
            self.window.blit(text, (i[1], i[2]))
        for i in actions:
            self.window.blit(i[0], (i[1][0], i[1][1]))

        x = 10
        y = 575
        boxwidth = 100
        boxheight = 100
        if self.first_time == False:
            rect1 = (x, y, boxwidth, boxheight)
            pygame.draw.rect(self.window, self.gainsboro, rect1)
            text1 = self.arial.render(f"Klik op een", True, self.black)
            self.window.blit(text1, (x+5, y+10))
            y += 25
            text1 = self.arial.render(f"school om", True, self.black)
            self.window.blit(text1, (x+5, y+10))
            y += 25
            text1 = self.arial.render(f"te selecteren!", True, self.black)
            self.window.blit(text1, (x+5, y+10))


    def menu_option_1(self): #draws the initial instruction screen for the player
        self.window.fill(self.white)
        x = 25
        y = 75
        text = self.arial.render(f"Dit is het budget spel. In dit spel word je gevraagd om op te treden als een beleidsmaker die beslist over schoolbudgetten.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Er zijn {len(self.agencies)} verschillende scholen waarvoor je verantwoordelijk bent over een periode van {self.roundstandard} semesters.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Elke school heeft maatregelen die de prestaties, het geluk en het stressniveau van hun personeel en leerlingen bijhouden.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Het belangrijkste doel van het spel is om de leerresultaten van de leerlingen te maximaliseren terwijl je binnen je totale budget blijft.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Er zijn drie leerresultaten die worden bijgehouden: de scores van de leerlingen voor wiskunde, lezen en natuurwetenschap.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Elke school heeft een index die de status bijhoudt. Er is ook een algemene leerresultatenindex die je een score geeft.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Het secundaire doel van het spel is om voldoende geluk onder het personeel en de studenten te behouden.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Als budgetbeheerder ben je verantwoordelijk voor een aantal maatregelen waarmee je geld kunt besparen of de resultaten kunt verbeteren.", True, self.black)
        self.window.blit(text, (x, y))
        y += 50
        text = self.arial.render(f"Het aannemen van nieuw personeel zal personeel gelukkiger maken en beter laten presteren.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Het ontslaan van personeel zal het tegenovergestelde effect hebben.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"De aankoop van apparatuur zal de prestaties en de tevredenheid van het personeel verbeteren, recycling zal het tegenovergestelde doen.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Het organiseren van evenementen zal het geluk van studenten verhogen en de stress onder studenten verminderen,", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"maar de stress onder het personeel zal toenemen.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Vragen om een externe sonde zal de prestaties verbeteren maar de stress verhogen.", True, self.black)
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
                self.finish_game()

            
    def instruction_screen_2(self): #draws the second instruction screen
        self.window.fill(self.white)
        x = 25
        y = 75
        text = self.arial.render(f"Scholen zijn door het schoolbestuur verplicht om voldoende personeel, apparatuur en evenementen te hebben.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Het geluks-, stress- en prestatieniveau van de studenten zullen elkaar allemaal beïnvloeden:", True, self.black)
        self.window.blit(text, (x, y))
        y += 50
        text = self.arial.render(f"Positieve leerresultaten zorgen ervoor dat personeel en leerlingen gelukkiger en minder gestrest zijn.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Negatieve leerresultaten zullen het tegenovergestelde effect hebben en ertoe leiden dat sommige medewerkers hun baan opzeggen.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Als je niet binnen het budget van de school blijft, raakt het personeel meer gestrest en daalt het prestatieniveau.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Lage gegeneraliseerde prestaties zullen de stress verhogen en de leerresultaten verlagen, hoge prestaties zullen het tegenovergestelde doen.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Als er geen evenementen worden georganiseerd, zullen studenten ongelukkig worden en slechter presteren.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Als de school onderbezet is, zullen zowel leerlingen als personeel slechter presteren en ongelukkig worden; nog meer personeel zal vertrekken.", True, self.black)
        self.window.blit(text, (x, y))
        y += 50
        text = self.arial.render(f"Er zijn ook een aantal willekeurige gebeurtenissen die op elke school kunnen voorkomen. Deze kunnen zowel negatieve als positieve effecten hebben.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"De evenementen variëren van natuurrampen tot alumni-evenementen. Ze worden automatisch gegenereerd aan het einde van elk semester.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Je zult in staat zijn om budgetbeslissingen te nemen voor elke school afzonderlijk. Als je tevreden bent, kun je doorgaan naar het volgende semester.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Je hebt maximaal {int(self.roundtimer/60)} minuten per semester, daarna gaat het spel automatisch door naar het volgende semester.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Tussen de semesters vinden spelevenementen plaats en worden algemene en schoolbudgetten aangepast.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Je kunt op elk moment vanuit het hoofdmenuscherm hiernaar terugkeren om de spelinstructies te lezen.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Je hebt ook de optie om meer in detail te kijken naar de effecten die elke budgetkeuze heeft.", True, self.black)
        self.window.blit(text, (x, y))
        y += 75
        text = self.arial.render(f"Veel plezier met het spel!", True, self.black)
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
                self.finish_game()
            
    def intro_1(self):
        self.window.fill(self.white)
        self.draw_game_board()
        self.draw_agency_menu(self.menu_options)
        x = 150
        y = 200
        text = self.arial.render(f"Dit is het budget spel. In dit spel word je gevraagd om op te treden als een beleidsmaker die beslist over schoolbudgetten.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Er zijn {len(self.agencies)} verschillende scholen waarvoor je verantwoordelijk bent over een periode van {self.roundstandard} semesters.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        rect1 = self.draw_exit("next_intro")

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    self.summary_click_forward(13, rect1)
            if event.type == pygame.QUIT:
                self.finish_game()

    def intro_2(self):
        self.window.fill(self.white)
        menu = self.create_main_menu("video")
        self.draw_main_menu(menu)
        x = 150
        y = 200
        text = self.arial.render(f"Elke school heeft maatregelen die de prestaties, het geluk en het stressniveau van hun personeel en leerlingen bijhouden.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Het belangrijkste doel van het spel is om de leerresultaten van de leerlingen te maximaliseren terwijl je binnen je totale budget blijft.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Het secundaire doel van het spel is om voldoende geluk onder het personeel en de studenten te behouden.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        rect1 = self.draw_exit("next_intro")

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    self.summary_click_forward(14, rect1)
            if event.type == pygame.QUIT:
                self.finish_game()

    def intro_3(self):
        self.window.fill(self.white)
        x = 150
        y = 200
        self.draw_game_board()
        self.draw_agency_menu(self.menu_options)
        for i in self.feedback:
            self.draw_feedback(i, ("cornsilk"))
        text = self.arial.render(f"Er zijn drie leerresultaten die worden bijgehouden: de scores van de leerlingen voor wiskunde, lezen en natuurwetenschap.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Elke school heeft een index die de status bijhoudt. Er is ook een algemene leerresultatenindex die je een score geeft.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        rect1 = self.draw_exit("next_intro")

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    self.summary_click_forward(15, rect1)
            if event.type == pygame.QUIT:
                self.finish_game()

    def intro_4(self):
        self.agency = "Blad Hoog"
        self.window.fill(self.white)
        self.budget_menu = []
        self.budgeting_labels1 = []
        self.budgeting_labels2 = []
        self.budget_buttons = []
        self.budget_menu = self.create_budgeting_menu(self.agency, "video")
        self.draw_budget_options(self.budget_menu)        
        x = 100
        y = 200

        text = self.arial.render(f"Als budgetbeheerder ben je verantwoordelijk voor een aantal maatregelen waarmee je geld kunt besparen of de resultaten kunt verbeteren.", True, self.black)
        self.window.blit(text, (x, y))
        y += 50
        text = self.arial.render(f"Het aannemen van nieuw personeel zal personeel gelukkiger maken en beter laten presteren.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Het ontslaan van personeel zal het tegenovergestelde effect hebben.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"De aankoop van apparatuur zal de prestaties en de tevredenheid van het personeel verbeteren, recycling zal het tegenovergestelde doen.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Het organiseren van evenementen zal het geluk van studenten verhogen en de stress onder studenten verminderen,", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"maar de stress onder het personeel zal toenemen.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Vragen om een externe sonde zal de prestaties verbeteren maar de stress verhogen.", True, self.black)
        self.window.blit(text, (x, y))
        y += 75
        rect1 = self.draw_exit("next_intro")

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    self.summary_click_forward(16, rect1)
            if event.type == pygame.QUIT:
                self.finish_game()

    def intro_5(self):
        self.window.fill(self.white)
        self.agency = "null"
        self.draw_game_board()
        self.draw_agency_menu(self.menu_options)
        for i in self.feedback:
            self.draw_feedback(i, ("cornsilk"))
        x = 150
        y = 200
        text = self.arial.render(f"Scholen zijn door het schoolbestuur verplicht om voldoende personeel, apparatuur en evenementen te hebben.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Het geluks-, stress- en prestatieniveau van de studenten zullen elkaar allemaal beïnvloeden:", True, self.black)
        self.window.blit(text, (x, y))
        y += 50
        text = self.arial.render(f"Positieve leerresultaten zorgen ervoor dat personeel en leerlingen gelukkiger en minder gestrest zijn.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Negatieve leerresultaten zullen het tegenovergestelde effect hebben en ertoe leiden dat sommige medewerkers hun baan opzeggen.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Als je niet binnen het budget van de school blijft, raakt het personeel meer gestrest en daalt het prestatieniveau.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Lage algemeen prestaties zullen de stress verhogen en de leerresultaten verlagen, hoge prestaties zullen het tegenovergestelde doen.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Als er geen evenementen worden georganiseerd, zullen studenten ongelukkig worden en slechter presteren.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Als de school onderbezet is, zullen leerlingen en personeel slechter presteren en ongelukkig zijn; meer personeel zal vertrekken.", True, self.black)
        self.window.blit(text, (x, y))
        y += 50
        rect1 = self.draw_exit("next_intro")

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    self.summary_click_forward(17, rect1)
            if event.type == pygame.QUIT:
                self.finish_game()

    def intro_6(self):
        self.window.fill(self.white)
        x = 50
        y = 200
        text = self.arial.render(f"Er zijn ook een aantal willekeurige gebeurtenissen die op elke school kunnen voorkomen. Deze kunnen zowel negatieve als positieve effecten hebben.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"De evenementen variëren van natuurrampen tot alumni-evenementen. Ze worden automatisch gegenereerd aan het einde van elk semester.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Je zult in staat zijn om budgetbeslissingen te nemen voor elke school afzonderlijk. Als je tevreden bent, kun je doorgaan naar het volgende semester.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Je hebt maximaal {int(self.roundtimer/60)} minuten per semester, daarna gaat het spel automatisch door naar het volgende semester.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        rect1 = self.draw_exit("next_intro")

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    self.summary_click_forward(18, rect1)
            if event.type == pygame.QUIT:
                self.finish_game()

    def intro_7(self):
        self.window.fill(self.white)
        x = 50
        y = 200
        text = self.arial.render(f"Tussen de semesters vinden spelevenementen plaats en worden algemene en schoolbudgetten aangepast.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Je kunt op elk moment vanuit het hoofdmenuscherm hiernaar terugkeren om de spelinstructies te lezen.", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Je hebt ook de optie om meer in detail te kijken naar de effecten die elke budgetkeuze heeft.", True, self.black)
        self.window.blit(text, (x, y))
        y += 75
        text = self.arial.render(f"Veel plezier met het spel!", True, self.black)
        self.window.blit(text, (x, y))
        rect1 = self.draw_exit("next_intro")

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    self.summary_click_forward(19, rect1)
            if event.type == pygame.QUIT:
                self.finish_game()

    def intro_8(self):
        self.window.fill(self.white)
        x = 150
        y = 200
        rect1 = self.draw_exit("next_intro")

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    self.summary_click_forward(20, rect1)
            if event.type == pygame.QUIT:
                self.finish_game()

    def intro_9(self):
        self.window.fill(self.white)
        x = 150
        y = 200
        rect1 = self.draw_exit("next_intro")

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    self.summary_click_forward(21, rect1)
            if event.type == pygame.QUIT:
                self.finish_game()

    def intro_10(self):
        self.window.fill(self.white)
        x = 150
        y = 200
        rect1 = self.draw_exit("next_intro")

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    self.summary_click_forward(22, rect1)
            if event.type == pygame.QUIT:
                self.finish_game()

    def show_budget_warning(self):
        self.show_feedback = False
        self.choice = "null"
        x = 200
        y = 150
        boxheight = 100
        boxwidth = 700
        boxwidth2 = 100
        x2 = 305
        y2 = 100
        self.window.fill(self.white)
        text = self.arial4.render("Je zit onder je maandelijkse budget, weet je zeker dat je door wilt gaan naar de volgende ronde?", True, self.crimson)
        self.window.blit(text, (x-100, y))
        y += 100
        rect2 = (x, y, boxwidth, boxheight)
        pygame.draw.rect(self.window, self.tan, rect2)
        text = self.arial4.render("Klik hier om terug te gaan en je budget in evenwicht te brengen", True, self.black)
        self.window.blit(text, (x+20, y+30))
        y += 150
        rect3 = (x, y, boxwidth, boxheight)
        pygame.draw.rect(self.window, self.tan, rect3)
        text = self.arial4.render("Klik hier om door te gaan naar het volgende semester", True, self.black)
        self.window.blit(text, (x+20, y+30))
        y += 150

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    if self.click_box(x, y, rect2) == True: #checks if a budget option has been clicked
                        self.baseconditions()
                        self.add_to_output(f"budget warning back button clicked")
                    if self.click_box(x, y, rect3) == True: #checks if a budget option has been clicked
                                self.budget_question = False
                                self.choice = "null"
                                self.add_to_output("budget warning advance button clicked")
                                self.main_menu_action = True
                                self.show_agencies = False
                                self.show_main_menu = False
                                self.show_feedback = False
                                self.advance_game_round()
                                self.officer_report = True

        
            if event.type == pygame.QUIT:
                self.finish_game()

    def show_postgame(self): #draws a post-game screen
        x = 200
        y = 100
        boxheight = 50
        boxwidth = 300
        x2 = 305
        y2 = 100
        rounds = []
        if self.redirect == "noredirect":
            self.window.fill(self.white)
            text = self.arial.render("Je hebt het einde van het spel bereikt, bedankt voor het spelen!", True, self.black)
            self.window.blit(text, (x, y))
            y += 30
            text = self.arial.render(f"Je score in het spel was: {self.score_total[0]} uit 100", True, self.black)
            self.window.blit(text, (x, y))
            y += 30
            text = self.arial.render("U kunt dit browservenster sluiten.", True, self.black)
            self.window.blit(text, (x, y))
            y += 30
        else:
            self.window.fill(self.white)
            text = self.arial.render("Je hebt het einde van het spel bereikt, bedankt voor het spelen!", True, self.black)
            self.window.blit(text, (x, y))
            y += 30
            text = self.arial.render(f"Je score in het spel was: {self.score_total[0]} uit 100", True, self.black)
            self.window.blit(text, (x, y))
            y += 30
            text = self.arial.render("Klik op een willekeurige plek om de exit-enquête en debriefing te openen!", True, self.black)
            self.window.blit(text, (x, y))
            y += 30
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.increase_click_counter()
                self.add_to_output(f"finish game button clicked")
                self.finish_game()


            if event.type == pygame.QUIT:
                self.finish_game()



    def draw_summary_prompts(self, condition): #draws a prompt to select needed inputs for summaries
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
            text1 = self.arial.render("Klik op de school waarvan je de", True, self.black)
            self.window.blit(text1, (x+10, y+10))
            text2 = self.arial.render("historische prestatiegegevens wilt zien", True, self.black)
            self.window.blit(text2, (x+10, y+40))
            y += boxheight + 50
            rect3 = (x, y, boxwidth, boxheight)
            pygame.draw.rect(self.window, self.tan, rect3)
            text = self.arial.render("Klik hier om terug te gaan naar het hoofdmenu", True, self.black)
            self.window.blit(text, (x+10, y+10))
            y = 100
            x = 100
            counter = 1
        if condition == "reporting":
            if self.round_number != 1:
                rect1 = (x, y, boxwidth, boxheight)
                if self.agency == "null":
                    pygame.draw.rect(self.window, self.tan, rect1)
                else:
                    pygame.draw.rect(self.window, self.gold, rect1)
                text1 = self.arial.render("Klik op de school waar je", True, self.black)
                self.window.blit(text1, (x+10, y+10))
                text2 = self.arial.render("nieuwsberichten over wilt zien", True, self.black)
                self.window.blit(text2, (x+10, y+40))
                y += boxheight + 50
                rect2 = (x, y, boxwidth, boxheight)
                if self.roundchoice == "null":
                    pygame.draw.rect(self.window, self.tan, rect2)
                else:
                    pygame.draw.rect(self.window, self.gold, rect2)
                text1 = self.arial.render("Klik op het semester waarvoor je rapporten wilt zien", True, self.black)
                self.window.blit(text1, (x+10, y+10))
                y += boxheight + 50
                rect3 = (x, y, boxwidth, boxheight)
                pygame.draw.rect(self.window, self.tan, rect3)
                text = self.arial.render("Klik hier om terug te gaan naar het hoofdmenu", True, self.black)
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
                text1 = self.arial.render("Er is nog geen rapport gemaakt in het spel!", True, self.black)
                self.window.blit(text1, (x+10, y+10))
                y += boxheight*2 + 100
                rect3 = (x, y, boxwidth, boxheight)
                pygame.draw.rect(self.window, self.tan, rect3)
                text = self.arial.render("Klik hier om terug te gaan naar het hoofdmenu", True, self.black)
                self.window.blit(text, (x+10, y+10))
        if condition == "reports":
            rect1 = (x, y, boxwidth, boxheight)
            pygame.draw.rect(self.window, self.tan, rect1)
            text1 = self.arial.render("Klik hier als u informatie", True, self.black)
            self.window.blit(text1, (x+10, y+10))
            text2 = self.arial.render("over historische prestaties wilt zien", True, self.black)
            self.window.blit(text2, (x+10, y+40))
            y += boxheight + 50
            rect2 = (x, y, boxwidth, boxheight)
            pygame.draw.rect(self.window, self.tan, rect2)
            text1 = self.arial.render("Klik hier als u nieuwsberichten", True, self.black)
            self.window.blit(text1, (x+10, y+10))
            text2 = self.arial.render("over scholen wilt bekijken", True, self.black)
            self.window.blit(text2, (x+10, y+40))
            y += boxheight + 50
            rect3 = (x, y, boxwidth, boxheight)
            pygame.draw.rect(self.window, self.tan, rect3)
            text = self.arial.render("Klik hier om terug te gaan naar het hoofdmenu", True, self.black)
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
                text1 = self.arial.render("Klik op de school waarvan", True, self.black)
                self.window.blit(text1, (x+10, y+10))
                text2 = self.arial.render("je een samenvatting wilt ontvangen", True, self.black)
                self.window.blit(text2, (x+10, y+40))
                y += boxheight + 50
                rect2 = (x, y, boxwidth, boxheight)
                if self.roundchoice == "null":
                    pygame.draw.rect(self.window, self.tan, rect2)
                else:
                    pygame.draw.rect(self.window, self.gold, rect2)
                text1 = self.arial.render("Klik op het semester waarvoor je een samenvatting wilt ontvangen", True, self.black)
                self.window.blit(text1, (x+10, y+10))
                y += boxheight + 50
                rect3 = (x, y, boxwidth, boxheight)
                pygame.draw.rect(self.window, self.tan, rect3)
                text = self.arial.render("Klik hier om terug te gaan naar het hoofdmenu", True, self.black)
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
                text1 = self.arial.render("Er zijn nog geen evenementen in het spel!", True, self.black)
                self.window.blit(text1, (x+10, y+10))
                y += boxheight*2 + 100
                rect3 = (x, y, boxwidth, boxheight)
                pygame.draw.rect(self.window, self.tan, rect3)
                text = self.arial.render("Klik hier om terug te gaan naar het hoofdmenu", True, self.black)
                self.window.blit(text, (x+10, y+10))

        if condition == "rankings":
            rect1 = (x, y, boxwidth, boxheight)
            pygame.draw.rect(self.window, self.tan, rect1)
            text1 = self.arial.render("Klik op het gewenste semester", True, self.black)
            self.window.blit(text1, (x+10, y+10))
            text2 = self.arial.render("om de ranglijst van scholen voor", True, self.black)
            self.window.blit(text2, (x+10, y+40))
            y += boxheight + 50
            rect2 = (x, y, boxwidth, boxheight)
            if self.roundchoice == "null":
                pygame.draw.rect(self.window, self.tan, rect2)
            else:
                pygame.draw.rect(self.window, self.gold, rect2)
            rect3 = (x, y, boxwidth, boxheight)
            pygame.draw.rect(self.window, self.tan, rect3)
            text = self.arial.render("Klik hier om terug te gaan naar het hoofdmenu", True, self.black)
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

        if condition == "reports":
            return (rect1, rect2, rect3)
        else:
            return (rect3, rounds)


    def show_information(self, agency, condition): #shows either performance information or a summary
        if condition == "PI":
            text1 = self.arial.render(f"Dit zijn prestatiegegevens over {agency}", True, self.black)
            text2 = self.arial.render(f"Klik ergens om terug te keren naar het hoofdmenu", True, self.black)
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
                        self.finish_game()

                pygame.display.update()
        if condition == "summary":
            while True:
                self.window.fill(self.white)
                x = 50
                y = 50
                text1 = self.arial.render(f"Deze pagina toont een lijst met gebeurtenissen die hebben plaatsgevonden bij {agency}:                    Klik ergens om terug te keren", True, self.black)
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
                            self.finish_game()

                pygame.display.update()
            text1 = self.arial.render(f"Dit is een samenvatting van spelgebeurtenissen voor {agency}", True, self.black)

    def show_budget_effects(self): #show effects of a given budget choice
        self.window.fill(self.white)
        rect1 = self.draw_exit("previous")
        x = 100
        y = 100
        text = self.arial.render(f"De knop die u koos voor meer informatie was: {self.choice}", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        text = self.arial.render(f"Deze keuze resulteert in de volgende effecten:", True, self.black)
        self.window.blit(text, (x, y))
        y += 25
        if self.choice == "de financiering verhogen":
            text = self.arial.render(f"De beschikbare fondsen voor het agentschap worden verhoogd met {self.amount}. Dit bedrag wordt afgetrokken van het totale budget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"Deze actie heeft geen invloed op andere statistieken.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25           
        if self.choice == "vermindering van financiering":
            text = self.arial.render(f"De beschikbare fondsen voor het agentschap worden verlaagd met € {self.amount}. Dit bedrag wordt toegevoegd aan het totale budget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"Deze actie heeft geen invloed op andere statistieken.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25   
        if self.choice == "personeel inhuren (5 personen)":
            text = self.arial.render(f"Er worden 5 extra personeelsleden aangenomen.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"Dit kost de school {self.amount}, wat verwijderd wordt uit het schoolbudget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"De personeelsuitbreiding heeft de volgende effecten op de schoolmetriek:", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"De leerlingen krijgen meer aandacht en hun prestaties voor elk leerresultaat verbeteren.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25       
            text = self.arial.render(f"De medewerkers kunnen zich beter concentreren op hun werk, hun prestaties verbeteren en hun tevredenheid neemt toe.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25   
            text = self.arial.render(f"Het personeel is ook minder overwerkt en hun stressniveau daalt.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
        if self.choice == "externe sonde uitvoeren":
            text = self.arial.render(f"Een externe beoordelaar wordt ingehuurd om de prestaties van de school te onderzoeken en problemen op te lossen.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"Dit kost de school {self.amount}, wat verwijderd wordt uit het schoolbudget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"De verhoogde aandacht van de beoordelaar heeft de volgende effecten op de schoolkenmerken:", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"De studenten raken meer gefocust op hun studie en al hun leerresultaten verbeteren.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25       
            text = self.arial.render(f"Het personeel staat onder druk om problemen op te lossen en hun prestaties nemen ook toe.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25   
            text = self.arial.render(f"Het personeel en de studenten raken echter ook meer gestrest door het onderzoek.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
        if self.choice == "apparatuur aanschaffen":
            text = self.arial.render(f"Er wordt meer apparatuur aangeschaft, die wordt gebruikt voor onderwijsactiviteiten.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"Dit kost de school {self.amount}, wat verwijderd wordt uit het schoolbudget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"De extra apparatuur maakt het makkelijker om de leerlingen les te geven en alle leerresultaten verbeteren.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"Het personeel is vooral blij met meer lesmateriaal en zowel hun tevredenheid als hun prestaties verbeteren.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25       
        if self.choice == "ontslagen initiëren (5 personen)":
            text = self.arial.render(f"5 personeelsleden worden ontslagen om kosten te besparen.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"Dit bespaart de school {self.amount} €, dat wordt toegevoegd aan het schoolbudget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"Als er minder personeel beschikbaar is, hebben leerlingen minder tijd met docenten, waardoor alle leerresultaten afnemen.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"Het personeel staat meer onder druk en hun algemene prestaties nemen af.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25       
            text = self.arial.render(f"De medewerkers raken ook meer gestrest door hun werk en zijn minder tevreden.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25   
        if self.choice == "evenement plannen":
            text = self.arial.render(f"Er wordt een evenement georganiseerd op school.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"Dit kost de school {self.amount}, wat verwijderd wordt uit het schoolbudget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"Het organiseren van het evenement naast ander werk verhoogt de stress bij het personeel.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"De studenten kijken uit naar het evenement en hun tevredenheid neemt toe en stress neemt af.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25       
        if self.choice == "annulering evenement":
            text = self.arial.render(f"Een georganiseerd evenement wordt geannuleerd om geld te besparen.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"Dit bespaart de school {self.amount}, dat wordt toegevoegd aan het schoolbudget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"Minder activiteiten beheren vermindert de stress bij het personeel.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"De studenten zijn teleurgesteld door het afgelaste evenement, hun tevredenheid neemt af en de stress neemt toe.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
        if self.choice == "apparatuur recyclen":
            text = self.arial.render(f"Een deel van de apparatuur op de school wordt gerecycled en een deel van het geld wordt teruggewonnen.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25  
            text = self.arial.render(f"Dit bespaart de school {self.amount} €, dat wordt toegevoegd aan het schoolbudget.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25    
            text = self.arial.render(f"De verminderde uitrusting maakt het moeilijker om de leerlingen les te geven en alle leerresultaten gaan achteruit.", True, self.black)
            self.window.blit(text, (x, y))
            y += 25
            text = self.arial.render(f"Het personeel is vooral ongelukkig met minder lesmateriaal en zowel hun tevredenheid als hun prestaties gaan achteruit.", True, self.black)
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
                            self.choice = 1

            if event.type == pygame.QUIT:
                self.finish_game()


    def menu_option_2(self, menu_options): #prompts the player to select a budget action for which they will be given more information
        self.agency = "Blad Hoog"
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
                self.finish_game()


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
                                self.add_to_output(f"Semester clicked: {round}")
                                self.roundchoice = round
                            
                    if self.agency != "null" and self.roundchoice != "null":
                            self.summary = False
                            self.agency_summary = True
                            self.intervaltime = self.time
                            self.show_agencies = False

                            


            if event.type == pygame.QUIT:
                self.finish_game()

            
    def draw_exit(self, condition): #draw the exit button in a given screen
        x = 340
        y = 5
        boxheight = 30
        boxwidth = 500
        if condition == "treatment":
            text1 = self.arial.render("Klik hier om door te gaan naar het spel", True, self.black)
        if condition == "previous":
            text1 = self.arial.render("Klik hier om terug te gaan naar de menupagina", True, self.black)
        if condition == "next":
            text1 = self.arial.render(f"Klik hier om door te gaan naar de volgende pagina", True, self.black)
        if condition == "next_intro":
            y = 130
            text1 = self.arial.render(f"Klik hier om door te gaan naar de volgende pagina", True, self.black)
        if condition == "roundend":
            text1 = self.arial.render("Klik hier om door te gaan naar de ranglijst van scholen", True, self.black)
        if condition == "rankings":
            text1 = self.arial.render("Klik hier om door te gaan naar het hoofdmenu", True, self.black)
        if condition == "gameend":
            text1 = self.arial.render("Klik hier om door te gaan naar de postwedstrijd", True, self.black)
        if condition == "start":
            text1 = self.arial.render("Klik hier om door te gaan naar het spel!", True, self.black)
        if condition == "treatment_start":
            text1 = self.arial.render(f"Klik hier om door te gaan naar het prestatierankings!", True, self.black)
        if condition == "officer":
            text1 = self.arial.render("Klik hier om door te gaan naar de samenvatting van de ronde", True, self.black)
        rect1 = (x, y, boxwidth, boxheight)
        pygame.draw.rect(self.window, self.tan, rect1)
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
                self.news_information = True
                self.show_rankings = False

        if summary == 6: #historical rankings
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.history_information = False
                self.historical = True
                self.agency = "null"
                self.add_to_output("Historical ranking back button clicked")

        if summary == 7: #news report choice
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.news_reports = True
                self.news_choice = False
                self.agency = "null"
                self.roundchoice = "null"
                self.add_to_output("News display back buttons clicked")


        if summary == 8: #news report display
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("News reports back button clicked")
                self.news_information = False
                self.news_choice = True  

        if summary == 9:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.roundchoice = "null"
                self.add_to_output("news report back button clicked")
                self.roundend()


        if summary == 10:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("start rankings treatment continue button clicked")
                self.show_rankings = False
                self.introduction_1 = True
                self.treatment = False

        if summary == 11:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("start rankings treatment information continue button clicked")
                self.show_rankings = True
                self.treatment = True
                self.treatment_information = False

        if summary == 12:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("Budget report forward button clicked")
                self.officer_report = False
                self.roundsummary1 = True
                self.insummary = True
                self.intervaltime = game.time

        if summary == 13:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("Introduction forward button clicked")
                self.introduction_1 = False
                self.introduction_2 = True

        if summary == 14:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("Introduction forward button clicked")
                self.introduction_2 = False
                self.introduction_3 = True

        if summary == 15:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("Introduction forward button clicked")
                self.introduction_3 = False
                self.introduction_4 = True

        if summary == 16:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("Introduction forward button clicked")
                self.introduction_4 = False
                self.introduction_5 = True

        if summary == 17:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("Introduction forward button clicked")
                self.introduction_5 = False
                self.introduction_6 = True

        if summary == 18:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("Introduction forward button clicked")
                self.introduction_6 = False
                self.introduction_7 = True

        if summary == 19:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("Introduction forward button clicked")
                self.baseconditions()

        if summary == 20:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("Introduction forward button clicked")
                self.introduction_8 = False
                self.introduction_9 = True

        if summary == 21:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("Introduction forward button clicked")
                self.introduction_9 = False
                self.introduction_10 = True

        if summary == 22:
            xy = pygame.mouse.get_pos()
            x = xy[0]
            y = xy[1]
            if self.click_box(x, y, rect1) == True: #checks if a budget option has been clicked
                self.add_to_output("Introduction forward button clicked")
                self.baseconditions()

    def show_agency_summary(self, roundnumber): #show the summary of events at an agency
        rect1 = self.draw_exit("next")
        width = 300
        height = 100
        x = 50
        y = 50
        text = self.arial.render(f"Deze op invoer gebaseerde gebeurtenissen vonden plaats in {self.agency} in semester {roundnumber}:", True, self.black)
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
                    text = self.arial2.render(f"Klik hier om de effecten te zien", True, self.black)
                    self.window.blit(text, (x, y))
                    y += height
                    if y > 720-height:
                        y = 100
                        x += 350

        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
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
                self.finish_game()


    def show_agency_summary_2(self, roundnumber): #show the second event summary
        rect1 = self.draw_exit("previous")
        width = 300
        height = 100
        x = 50
        y = 50
        text = self.arial.render(f"Deze willekeurige gebeurtenissen vonden plaats in {self.agency} in semester {roundnumber}:", True, self.black)
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
                    text = self.arial2.render(f"Klik hier om de effecten te zien", True, self.black)
                    self.window.blit(text, (x, y))
                    y += height
                    if y > 720-height:
                        y = 100
                        x += 350

        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
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
                self.finish_game()

            

    def summary_out(self): #exit any event summary
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
        boxwidth = 450
        x = 150
        x1 = x-20
        x3 = x + boxwidth + 50
        y = 25
        y1 = y
        texts = []
        self.window.fill(self.white)
        text = self.arial.render(f"Deze willekeurige gebeurtenissen vonden dit semester plaats bij {self.agency}:", True, self.crimson)
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

        text = self.arial.render(f"Deze op input gebaseerde gebeurtenissen vonden dit semester plaats bij {self.agency}:", True, self.crimson)
        texts.append((text, (300, y)))

        y += 50
        if self.time > self.intervaltime + self.roundinterval:
            text = self.arial.render("Klik hier om naar het volgende overzichtsscherm te gaan", True, self.black)
            texts.append((text, (x3+10, y+50)))
            progress_button = (x3, y+30, boxwidth3, boxheight1)
            pygame.draw.rect(self.window, self.gold, progress_button)
        else:
            text = self.arial.render(f"Volgende overzichtsscherm beschikbaar in {int(self.roundinterval+1-(self.time-self.intervaltime))} seconden", True, self.black)
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
        pygame.draw.rect(self.window, self.forestgreen, (x1, y, boxwidth, boxheight3))

        text = self.calibri.render(f"Prestatiescore bij {self.agency} dit semester: {score}", True, self.black)
        self.window.blit(text, (x, y+15))
        y += 75

        pygame.draw.rect(self.window, self.orange, (x1, y, boxwidth, boxheight3))

        text = self.calibri.render(f"Je algemene prestatiescore dit semester was: {self.score_last}", True, self.black)
        self.window.blit(text, (x, y+15))


        for i in texts:
            self.window.blit(i[0], i[1])


        pygame.display.update()
        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration


            if event.type == pygame.QUIT:
                self.finish_game()

            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    self.add_to_output(f"round progress button clicked")
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

    def round_summary(self): #show summary of events in a round
        if self.round_number < 11:
            rect1 = self.draw_exit("roundend")
        else:
            rect1 = self.draw_exit("gameend")

        texts = []
        x = 150
        x1 = x-20
        y = 75
        y1 = y-5

        boxheight3 = 30
        boxwidth3 = 100
        boxwidth = 700
        scores = []
        names = []

        if self.met_budget == True:
            text = self.arial.render(f"Je hebt je budget dit semester gehaald!", True, self.black)
            texts.append((text, (x, y)))
            pygame.draw.rect(self.window, self.forestgreen, (x1, y1, boxwidth, boxheight3))

        if self.met_budget == False:
            text = self.arial.render(f"Je hebt je budget dit semester niet gehaald!", True, self.black)
            texts.append((text, (x, y)))
            pygame.draw.rect(self.window, self.crimson, (x1, y1, boxwidth, boxheight3))

        y += 60
        y1 += 60

        text = self.arial.render(f"Je algemene prestatiescore dit semester was: {self.score_last} van de 100", True, self.black)
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
        text = self.arial.render(f"Je laagst presterende school dit semester was {lowest_school} met een prestatiescore van {lowest}", True, self.black)
        texts.append((text, (x, y)))
        pygame.draw.rect(self.window, self.tomato, (x1, y1, boxwidth, boxheight3))
        y += 40
        y1 += 40
        text = self.arial.render(f"Je hoogst presterende school dit semester was {highest_school} met een prestatiescore van {highest}", True, self.black)
        texts.append((text, (x, y)))
        pygame.draw.rect(self.window, self.darkolivegreen3, (x1, y1, boxwidth, boxheight3))
        y += 40
        y1 += 40
        text = self.arial.render(f"Je algemene prestatiescore in elk semester tot nu toe is:", True, self.black)
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
        text = self.arial.render(f"Je gemiddelde prestatiescore in het spel tot nu toe: {int(sum(self.score_total)/len(self.score_total))}", True, self.black)
        texts.append((text, (x, y)))
        pygame.draw.rect(self.window, self.lightsteelblue, (x1, y1, boxwidth, boxheight3))
        y += 60
        y1 += 60

        met_budget = 0
        under_budget = 0
        for i in self.budget_record:
            if i == True:
                met_budget += 1
            if i == False:
                under_budget += 1
        text = self.arial.render(f"Het aantal semesters dat je tot nu toe aan je budget hebt voldaan: {met_budget}", True, self.black)
        texts.append((text, (x, y)))
        pygame.draw.rect(self.window, self.tan, (x1, y1, boxwidth, boxheight3))
        y += 40
        y1 += 40
        text = self.arial.render(f"Het aantal semesters dat je je budget tot nu toe niet hebt gehaald: {under_budget}", True, self.black)
        texts.append((text, (x, y)))
        pygame.draw.rect(self.window, self.tomato, (x1, y1, boxwidth, boxheight3))
        y += 40
        y1 += 40

        for i in texts:
            self.window.blit(i[0], i[1])

        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.QUIT:
                self.finish_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    if self.click_box(x, y, rect1) == True:
                            self.endrankings = True
                            self.roundover = False
                            self.add_to_output("Semester summary forward button clicked")
                            self.roundchoice = self.round_number
                            self.show_rankings = True



    def roundend(self): #end the round
        self.timer_follow = True
        self.roundtime = self.time
        self.increase_round_counter()
        self.baseconditions()
        self.output += "game state: "
        self.output += "\n"
        self.output += f"agency stats: {str(self.agency_stats)}"
        self.output += "\n"
        self.output += f"staff stats: {str(self.staff_stats)}"
        self.output += "\n"
        self.output += f"student stats: {str(self.student_stats)}"
        self.output += "\n"
        self.output += f"total budget: {str(self.total_budget)}"
        self.output += "\n"
        self.output += f"current ranking: {str(self.schoolranking)}"
        self.output += "\n"
        if self.round_number == self.roundstandard + 1:
            self.postgame = True
            self.add_final_output()
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
        summarybuttons = self.draw_summary_prompts("reports")
        rect1 = summarybuttons[0]
        rect2 = summarybuttons[1]
        rect3 = summarybuttons[2]
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    if self.click_box(x, y, rect1) == True:
                        self.historical = True
                        self.performance_reports = False
                        self.add_to_output("summary historical performance clicked")
                    if self.click_box(x, y, rect2) == True:
                        self.news_reports = True
                        self.performance_reports = False
                        self.add_to_output("summary reports button clicked")
                    if self.click_box(x, y, rect3) == True:
                        self.baseconditions()
                        self.add_to_output("summary back button clicked")
                           


            if event.type == pygame.QUIT:
                self.finish_game()

    def reporting_choice(self, menu_options, choice): #show report choice screen
        rect0 = self.draw_exit("previous")
        self.window.fill(self.white)
        self.draw_game_board()
        self.draw_agency_menu(menu_options)
        if choice == "historical":
            summarybuttons = self.draw_summary_prompts("historical")
        if choice == "reporting":
            summarybuttons = self.draw_summary_prompts("reporting")
            rounds = summarybuttons[1]
        rect1 = summarybuttons[0]
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    xy = pygame.mouse.get_pos()
                    x = xy[0]
                    y = xy[1]
                    if self.click_box(x, y, rect1) == True:
                        self.baseconditions()
                        self.add_to_output("summary back button clicked")

                    for i in self.menu_buttons:
                        if self.click_circle(x, y, i[0]) == True: #checks if an agency has been clicked
                            agency = i[1]
                            self.add_to_output(f"agency clicked: {agency}")
                            self.agency = agency
                    
                    if choice == "reporting":
                        for i in rounds:
                            if self.click_circle(x, y, i[0]) == True: #checks if a round has been clicked
                                round = i[1]
                                self.add_to_output(f"Semester clicked: {round}")
                                self.roundchoice = round
                            
                    if self.agency != "null":
                            if choice == "historical":
                                self.historical = False
                                self.history_information = True
                                self.show_agencies = False
                            if choice == "reporting":
                                if self.roundchoice != "null":
                                    self.news_reports = False
                                    self.show_agencies = False  
                                    self.news_choice = True

            if event.type == pygame.QUIT:
                self.finish_game()

    def historical_performance(self, agency): #show historical performance for a school
        count = 0
        results = []
        for i in self.historical_rankings:
            count += 1
        count -= 10
        if count > -2:
            rankings_used = self.historical_rankings[count:]
        count2 = 20
        for i in rankings_used:
            for u in i:
                if u[1] == agency:
                    results.append((u[0], u[1], count2))    
                count2 -= 1
                if count2 == 0:
                    count2 = 20     
        results.reverse()
        if self.endrankings == False:
            rect1 = self.draw_exit("previous")
        texts = []
        x = 50
        x1 = x-20
        y = 50
        y1 = y-5
        boxheight3 = 25
        boxwidth = 700
        boxheight2 = 40
        boxwidth2 = 300
        count = 1
        agencies = []
        text = self.arial2.render(f"Dit zijn de ranglijsten voor {agency} over de afgelopen tien semesters, nieuwste resultaten eerst:", True, self.black)
        texts.append((text, (x, y)))
        pygame.draw.rect(self.window, self.darkolivegreen3, (x1, y1, boxwidth, boxheight3))
        y += 50
        y1 += 50

        semester_tracker = self.semester
        year = self.year
        performances = []
        rankings = []
        for i in results:
            performance = i[0]
            performances.append(performance)
            ranking = i[2]
            rankings.append(ranking)
            colour_box = self.gold
            if ranking < 6:
                colour_box = self.forestgreen
            if ranking > 15:
                colour_box = self.crimson
            text = self.arial2.render(f"Rangschikking semester {semester_tracker}, {year}: {ranking}/20, prestatiescore: {performance}/100", True, self.black)
            texts.append((text, (x, y)))
            pygame.draw.rect(self.window, colour_box, (x1, y1, boxwidth, boxheight3))
            y += 40
            y1 += 40
            semester_tracker -= 1
            if semester_tracker < 1:
                semester_tracker = 2
                year -= 1


        y += 20
        y1 += 20
        average_performance = int((sum(performances))/10)
        average_ranking = int((sum(rankings))/10)
        text = self.arial2.render(f"Gemiddelde ranking in de laatste 10 semesters: {average_ranking}/20", True, self.black)
        texts.append((text, (x, y)))
        colour_box = self.gainsboro
        pygame.draw.rect(self.window, colour_box, (x1, y1, boxwidth, boxheight3))
        y += 40
        y1 += 40
        text = self.arial2.render(f"Gemiddelde prestatiescore in de laatste 10 semesters: {average_performance}/100", True, self.black)
        texts.append((text, (x, y)))
        colour_box = self.gainsboro
        pygame.draw.rect(self.window, colour_box, (x1, y1, boxwidth, boxheight3))

        for i in texts:
            self.window.blit(i[0], i[1])


        y = 100
        x = 750


        text = self.arial2.render(f"Kleurcodes voor rangschikking:", True, self.black)
        self.window.blit(text, (x+5, y+5))
        y += 40

        colour_box = self.forestgreen
        pygame.draw.rect(self.window, colour_box, (x, y, boxwidth2, boxheight2))
        text = self.arial2.render(f"School in de top 5", True, self.black)
        self.window.blit(text, (x+5, y+5))
        y += 75
        colour_box = self.crimson
        pygame.draw.rect(self.window, colour_box, (x, y, boxwidth2, boxheight2))
        text = self.arial2.render(f"School in de onderste 5", True, self.black)
        self.window.blit(text, (x+5, y+5))
        y += 75
        colour_box = self.gold
        pygame.draw.rect(self.window, colour_box, (x, y, boxwidth2, boxheight2))
        text = self.arial2.render(f"School niet bovenaan of onderaan", True, self.black)
        self.window.blit(text, (x+5, y+5))
        y += 75

        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.QUIT:
                self.finish_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    self.summary_click_forward(6, rect1)


    def news_selection(self, agency, roundnumber): #show news reports published about a school
        
        rect1 = self.draw_exit("previous")
        width = 350
        height = 75
        x = 20
        y = 50
        text = self.arial.render(f"Deze nieuwsberichten werden gepubliceerd over {agency} in semester {roundnumber}:", True, self.black)
        self.window.blit(text, (x, y))
        y += 50
        choices = []
        for i in self.news_archive[agency]:
            if roundnumber == i[1]:
                text = i[0][0][0][0]
                title = i[2]
                text_width, text_height = self.arial2.size(title)
                box = pygame.Rect(x-10, y-(text_height), width, height)
                report = i[0]
                choices.append((box, report))
                pygame.draw.rect(self.window, self.tomato, box)
                self.window.blit(text, (x, y))
                y += 25
                text = self.arial2.render(f"Klik hier om het artikel te lezen", True, self.black)
                self.window.blit(text, (x, y))
                y += height
                if y > 720-height:
                    y = 100
                    x += 360

        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    for i in choices:
                        xy = pygame.mouse.get_pos()
                        x = xy[0]
                        y = xy[1]
                        if self.click_box(x, y, i[0]) == True: #checks if a budget option has been clicked
                            self.news_choice = False
                            self.news_information = True
                            self.report = i[1] 
                            self.add_to_output("news report selection button clicked")
                    self.summary_click_forward(7, rect1)


            if event.type == pygame.QUIT:
                self.finish_game()

    def news_summary(self, news): #show selected news report
        self.window.fill(self.white)
        if self.officer_report == True:
            rect1 = self.draw_exit("officer")
        elif self.endrankings == False:
            rect1 = self.draw_exit("previous")
        elif self.endrankings == True:
            rect1 = self.draw_exit("rankings")

        title = news[0]
        paper = news[1]
        lines = news[2]
        author = news[3]

        for i in paper:
            self.window.blit(i[0], (i[1][0], i[1][1]))
        for i in title:
            self.window.blit(i[0], (i[1][0], i[1][1]))
        for i in lines:
            self.window.blit(i[0], (i[1][0], i[1][1]))
        for i in author:
            self.window.blit(i[0], (i[1][0], i[1][1]))

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    if self.officer_report == True:
                        self.summary_click_forward(12, rect1)
                    elif self.endrankings == False:
                        self.summary_click_forward(8, rect1)
                    elif self.endrankings == True:
                        self.summary_click_forward(9, rect1)
            if event.type == pygame.QUIT:
                self.finish_game()

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
                            self.adjust_temporary()
                            self.rankings = False
                            self.show_rankings = True
                            self.show_agencies = False

                            


            if event.type == pygame.QUIT:
                self.finish_game()

    def performance_ranking_instructions(self): #instructions for treatment group
        x = 50
        y = 100
        self.window.fill(self.white)
        rect1 = self.draw_exit("treatment_start")
        text = self.arial.render("Dit is het begin van het budget spel.", True, self.black)
        self.window.blit(text, (x, y))
        y += 30
        text = self.arial.render(f"In het spel ben je budgetbeheerder voor vier scholen in jouw schooldistrict.", True, self.black)
        self.window.blit(text, (x, y))
        y += 30
        text = self.arial.render("Het is uw taak om middelen naar eigen inzicht aan de scholen toe te wijzen.", True, self.black)
        self.window.blit(text, (x, y))
        y += 30      
        text = self.arial.render("De scholen worden geëvalueerd op de prestaties van hun personeel en studenten, met speciale aandacht voor de leerresultaten van studenten.", True, self.black)
        self.window.blit(text, (x, y))
        y += 30   
        text = self.arial.render("In het volgende scherm krijg je een ranglijst te zien van alle scholen in jouw schooldistrict.", True, self.black)
        self.window.blit(text, (x, y))
        y += 30    
        text = self.arial.render("De scholen waar jij de leiding over hebt, worden gemarkeerd in de ranglijst.", True, self.black)
        self.window.blit(text, (x, y))
        y += 30       
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    self.summary_click_forward(11, rect1)



            if event.type == pygame.QUIT:
                self.finish_game()
        

    def show_performance_rankings(self): #show performance ranking
        if self.treatment == True:
            rect1 = self.draw_exit("treatment")
            self.roundchoice = 1
        elif self.endrankings == False:
            rect1 = self.draw_exit("previous")
        elif self.endrankings == True:
            rect1 = self.draw_exit("next")
        ranking = self.gamerankings[self.roundchoice-1]
        texts = []
        x = 50
        x1 = x-20
        y = 50
        y1 = y-5
        boxheight3 = 25
        boxwidth = 700
        boxwidth2 = 300
        boxheight2 = 40
        count = 1
        agencies = []
        text = self.arial2.render(f"Dit is de schoolrangschikking voor semester {self.roundchoice} van alle scholen in de regio. Jouw scholen zijn gemarkeerd.", True, self.black)
        texts.append((text, (x, y)))
        pygame.draw.rect(self.window, self.darkolivegreen3, (x1, y1, boxwidth, boxheight3))
        y += 50
        y1 += 50
        for i in self.agencies:
            agencies.append(i[0])
        for i in ranking[::-1]:
            if i[1] in agencies:
                colour_box = self.gold
                if count > 14:
                    colour_box = self.crimson
                if count < 6:
                    colour_box = self.forestgreen
            else:
                colour_box = self.gainsboro 
            text = self.arial2.render(f"Rangschikking {count}/20: {i[1]}, prestatiescore {i[0]}/100", True, self.black)
            texts.append((text, (x, y)))
            pygame.draw.rect(self.window, colour_box, (x1, y1, boxwidth, boxheight3))
            y += 30
            y1 += 30
            count += 1


        for i in texts:
            self.window.blit(i[0], i[1])


        y = 100
        x = 750


        text = self.arial2.render(f"Kleurcodes voor rangschikking:", True, self.black)
        self.window.blit(text, (x+5, y+5))
        y += 40

        colour_box = self.forestgreen
        pygame.draw.rect(self.window, colour_box, (x, y, boxwidth2, boxheight2))
        text = self.arial2.render(f"Jouw school in de top 5", True, self.black)
        self.window.blit(text, (x+5, y+5))
        y += 75
        colour_box = self.crimson
        pygame.draw.rect(self.window, colour_box, (x, y, boxwidth2, boxheight2))
        text = self.arial2.render(f"Jouw school in de onderste 5", True, self.black)
        self.window.blit(text, (x+5, y+5))
        y += 75
        colour_box = self.gold
        pygame.draw.rect(self.window, colour_box, (x, y, boxwidth2, boxheight2))
        text = self.arial2.render(f"Je school niet bovenaan of onderaan", True, self.black)
        self.window.blit(text, (x+5, y+5))
        y += 75
        colour_box = self.gainsboro
        pygame.draw.rect(self.window, colour_box, (x, y, boxwidth2, boxheight2))
        text = self.arial2.render(f"Niet jouw school", True, self.black)
        self.window.blit(text, (x+5, y+5))
        y += 75

        for event in pygame.event.get(): #checks game events; at the moment only click-based events are taken into consideration
            if event.type == pygame.QUIT:
                self.finish_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.increase_click_counter()
                    if self.treatment == True:
                        self.summary_click_forward(10, rect1)
                    elif self.endrankings == True:
                        self.summary_click_forward(5, rect1)
                    else:
                        self.summary_click_forward(4, rect1)
                    self.add_to_output("Ranking forward button clicked")


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
        y = 75
        x = 60
        for i in self.agencies:
            menu_options.append(((x, y), i))
            self.menu_buttons.append(((x, y, self.radius), i[0]))
            text = i[0]
            text_width, text_height = self.calibri.size(text)
            self.agency_labels.append((text, x-(text_width/2), y-text_height/2))
            y += 75
            y += (7-self.agency_count)*20
        return menu_options

    def update_game_feedback(self): #provides an updating counter which follows the budget available in total and for a given agency
        feedback_monitors = []
        x = 160
        y = 10
        boxheight = 75
        boxwidth = 290
        x2 = 455
        x3 = 750
        if self.total_budget < 0:
            colour = self.crimson
        else:
            colour = self.black
        feedback_monitors.append(((x, y, boxwidth, boxheight), (f"Totaal budget dit semester: {self.total_budget} €"), colour))
        time = int(self.roundtimer+1-(self.time-self.roundtime))
        if time > 10:
            colour = self.black
            feedback_monitors.append(((x3, y, boxwidth, boxheight), (f"Resterende tijd in dit semester: {time}"), colour))
        else:
            colour = self.crimson
            feedback_monitors.append(((x3, y, boxwidth, boxheight), (f"Automatische voortgang in {time} seconden"), colour))

        colour = self.black
        if self.agency != "null":
            if self.agency_stats[self.agency][0] < 0:
                colour = self.crimson
            else:
                colour = self.black
            feedback_monitors.append(((x2, y, boxwidth, boxheight), (f"{self.agency} budget: {self.agency_stats[self.agency][0]} €"), colour))
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
                feedback_monitors.append((f"Problemen bij {self.agency}!", (x, y, boxwidth, boxheight), colour))
            else:
                feedback_monitors.append((f"Alles in orde bij {self.agency}!", (x, y, boxwidth, boxheight), colour))
            feedback_monitors.append((f"{self.agency} prestatiescore: {self.agency_scores[self.agency]}/100", (x2, y, boxwidth, boxheight), colour))
        if self.agency == "null":
            feedback_monitors.append(((x2, y, boxwidth, boxheight), f"Huidig semester: {self.round_number} uit {self.roundstandard}", colour))
            y += 25
            feedback_monitors.append((f"Je gemiddelde prestatiescore: {int(sum(self.score_total)/len(self.score_total))}", (x, y, boxwidth, boxheight), colour))
            feedback_monitors.append((f"Huidige prestatiescore: {self.score}/100", (x2, y, boxwidth, boxheight), colour))
        return feedback_monitors

    def create_main_menu_options(self): #creates the main menu options the player can choose
        self.main_menu_options = []
        self.main_menu_labels = []
        self.main_menu_options.append(("Spelinstructies ontvangen", 0))
        self.main_menu_options.append(("Instructies budgetoptie ontvangen", 1))
        self.main_menu_options.append(("Vooruitgang naar volgende semester", 2))
        self.main_menu_options.append(("Nieuwsberichtgeving bekijken", 3))
        self.main_menu_options.append(("Bekijk historische prestaties", 4))
        self.main_menu_options.append(("Bekijk schoolranglijsten", 5))


    def create_main_menu(self, condition): #creates the main menu based on the selected menu options
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
        if condition == "base":
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
        if condition == "video":
            y += 2*(boxheight + 25)
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
            text = "Je blijft binnen je semesterbudget!"
        elif self.total_budget < 0:
            text = "Je zit onder je semesterbudget!"
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
            text = "Scholen onder budget:"
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
            text = "Alle scholen blijven binnen hun budget!"
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
            text = "Scholen onderbemand:"
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
            text = "Alle scholen zijn volledig bemand!"
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
            text = "Scholen met een tekort aan apparatuur:"
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
            text = "Alle scholen hebben genoeg apparatuur!"
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
            text = "Scholen zonder geplande evenementen:"
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
            text = "Alle scholen hebben evenementen gepland!"
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
            text = f"Scholen met personeelsstress boven {self.stress_standard_low}:"
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
            text = f"Geen enkele school heeft een personeelsstress hoger dan {self.stress_standard_low}!"
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
            text = f"Scholen met personeelstevredenheid onder {self.satisfaction_standard_high}:"
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
            text = f"Geen enkele school heeft personeelstevredenheid onder {self.satisfaction_standard_high}!"
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15
            text = ""
            self.main_menu_feedback.append((text, x+5, y+5))
            y += 15

        text = f"Scholen met personeelsprestaties onder {self.performance_standard_high}:"
        text = ""
        count = 0
        monitor = []
        for i in self.staff_stats:
            if self.staff_stats[i][4] < self.performance_standard_high:
                monitor.append(i)
        if len(monitor) > 0:
            text = f"Scholen met personeelsprestaties onder {self.performance_standard_high}:"
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
            text = f"Geen enkele school heeft personeelsprestaties onder {self.performance_standard_high}!"
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
            text = f"Scholen met leerlingtevredenheid lager dan {self.satisfaction_standard_high}:"
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
            text = f"Geen enkele school heeft een studententevredenheid onder {self.satisfaction_standard_high}!"
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
            text = f"Scholen met een algemene leerachterstand {self.learning_standard_high}:"
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
            text = f"Geen enkele school heeft een totaal leerniveau onder {self.learning_standard_high}!"
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
            text = f"Scholen met leerlingenstress boven {self.stress_standard_low}:"
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
            text = f"Geen enkele school heeft studentenstress boven {self.stress_standard_low}!"
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
                    action_cost_label = f"Kosten: {cost} €"
                else:
                    action_cost_label = f"Geld bespaard: {-cost} €"
                if text == "de financiering verhogen":
                    action_cost_label = f"Kosten: {cost} €"
                if text == "vermindering van financiering":
                    action_cost_label = f"Geld bespaard: {-cost} €"
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
                        text = f"Totaal personeel: {number} (bemand)"
                        self.budgeting_labels2.append((text, x+5, y+30, colour))
                    if float(number) < 0:
                        text = f"Totaal personeel: {number} (onderbezet)"
                        self.budgeting_labels2.append((text, x+5, y+30, colour))
                    text = f"Tevredenheid van het personeel: {self.staff_stats[agency][3]}/100"
                    if self.agency_stats[self.agency][8] == "low staff satisfaction":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][8] == "high staff satisfaction":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+80, colour))
                    text = f"Prestaties van het personeel: {self.staff_stats[agency][4]}/100"
                    if self.agency_stats[self.agency][9] == "low staff performance":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][9] == "high staff performance":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+130, colour))
                    text = f"Stressniveaus van het personeel: {self.staff_stats[agency][5]}/100"
                    if self.agency_stats[self.agency][10] == "high staff stress":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][10] == "low staff stress":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+180, colour))
                    text = f"Stressniveaus bij studenten: {self.student_stats[agency][11]}/100"
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
                        text = f"Totale waarde: {number} € (genoeg)"
                        self.budgeting_labels2.append((text, x+5, y+30, colour))
                    if float(number) < 0:
                        text = f"Totale waarde: {number} € (tekort)"
                        self.budgeting_labels2.append((text, x+5, y+30, colour))
                    
                    text = f"Leerlingprestaties (lezen): {self.student_stats[agency][7]}/100"
                    if self.agency_stats[self.agency][13] == "poor learning results (reading)":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][12] == "good learning results (reading)":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+80, colour))
                    text = f"Leerlingprestaties (wiskunde): {self.student_stats[agency][8]}/100"
                    if self.agency_stats[self.agency][14] == "poor learning results (math)":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][13] == "good learning results (math)":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+130, colour))
                    text = f"Leerlingprestaties (wetenschap): {self.student_stats[agency][9]}/100"
                    if self.agency_stats[self.agency][15] == "poor learning results (science)":
                        colour = self.crimson
                    elif self.agency_stats[self.agency][14] == "good learning results (science)":
                        colour = self.forestgreen
                    else:
                        colour = basecolour
                    self.budgeting_labels2.append((text, x+5, y+180, colour))
                    text = f"Studentenprestaties (algemeen): {self.student_stats[agency][10]}/100"
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
                        text = f"Er zijn geen evenementen gepland!"
                        self.budgeting_labels2.append((text, x+5, y+30, colour))
                    elif self.agency_stats[self.agency][6] == "Events planned":
                        colour = self.forestgreen
                        text = f"Totaal aantal geplande evenementen: {number}"
                        self.budgeting_labels2.append((text, x+5, y+30, colour))
                    text = f"Komende evenementen:"
                    self.budgeting_labels2.append((text, x+5, y+55, basecolour))
                    z = 80
                    for i in self.events[agency]:
                        if i[0] != "null":
                            text = f"{i[0]} gepland voor dag {i[1]}"
                            self.budgeting_labels2.append((text, x+5, y+z, self.royalblue3))

                        if i[0] == "null":
                            text = f"Geen evenement gepland voor dag {i[1]}"
                            self.budgeting_labels2.append((text, x+5, y+z, self.crimson))
                        z += 25
                    text = f"Tevredenheid onder studenten: {self.student_stats[agency][6]}"
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
            text = "Afsluiten naar hoofdmenu"
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
                    action_cost_label = f"Kosten: {cost} €"
                else:
                    action_cost_label = f"Geld bespaard: {-cost} €"
                if text == "de financiering verhogen":
                    action_cost_label = f"Kosten: {cost} €"
                if text == "vermindering van financiering":
                    action_cost_label = f"Geld bespaard: {-cost} €"
                self.budgeting_labels1.append((action_cost_label, x+5, y+30))
                self.budget_buttons.append(((x, y, boxwidth, boxheight), text, cost))
                x += boxwidth + 50
                if x + boxwidth > 1080:
                    x = 100
                    y += boxheight + 25
            menu_options.append(((x2, y2, boxwidth, boxheight), (self.tan)))
            text = "Afsluiten naar hoofdmenu"
            self.budgeting_labels1.append((text, x2+5, y2+5, boxwidth, boxheight))
            self.budget_buttons.append(((x2, y2, boxwidth, boxheight), "exit", "null"))

        if condition == "video":
            menu_options = []
            x = 100
            y = 450
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
                    action_cost_label = f"Kosten: {cost} €"
                else:
                    action_cost_label = f"Geld bespaard: {-cost} €"
                if text == "de financiering verhogen":
                    action_cost_label = f"Kosten: {cost} €"
                if text == "vermindering van financiering":
                    action_cost_label = f"Geld bespaard: {-cost} €"
                self.budgeting_labels1.append((action_cost_label, x+5, y+30))
                self.budget_buttons.append(((x, y, boxwidth, boxheight), text, cost))
                x += boxwidth + 50
                if x + boxwidth > 1080:
                    x = 100
                    y += boxheight + 25
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
    
    def check_caption(self): #check game caption
        pygame.display.set_caption(f"Welkom bij het budgetspel!")



game = BudgetGame()
game.check_url()
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
game.create_identifier()
game.create_ranking()
game.post_output()
game.create_historical_rankings()
game.historical_rankings.append(game.schoolranking)
game.menu_options = game.create_game_menu() #creates the agency selection menu
game.check_treatment_condition()
game.feedback = game.update_game_feedback()
async def main(): #main game loop
    while True:
        game.check_caption()
        game.check_score()
        feedback = game.update_game_feedback()
        game.add_to_output("null input")
        game.window.fill(game.white) #fills the game screen with white
        if game.main_menu_action == False:
            game.draw_game_board()
        if game.start == True and game.intro_style == "text":
            game.menu_option_1()
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
        if game.performance_reports == True:
            game.menu_option_5(game.menu_options)
        if game.rankings == True:
            game.menu_option_6(game.menu_options)
        if game.show_rankings == True:
            game.show_performance_rankings()
        if game.history_information == True:
            game.historical_performance(game.agency)
        if game.news_information == True:
            game.news_summary(game.report)
        if game.officer_report == True:
            game.news_summary(game.report_budget)
        if game.news_choice == True:
            game.news_selection(game.agency, game.roundchoice)
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
        if game.historical == True:
            game.reporting_choice(game.menu_options, "historical")
        if game.news_reports == True:
            game.reporting_choice(game.menu_options, "reporting")
        if game.treatment_information == True:
            game.performance_ranking_instructions()
        if game.budget_question == True:
            game.show_budget_warning()
        if game.introduction_1 == True:
            game.intro_1()
        if game.introduction_2 == True:
            game.intro_2()
        if game.introduction_3 == True:
            game.intro_3()
        if game.introduction_4 == True:
            game.intro_4()
        if game.introduction_5 == True:
            game.intro_5()
        if game.introduction_6 == True:
            game.intro_6()
        if game.introduction_7 == True:
            game.intro_7()
        if game.introduction_8 == True:
            game.intro_8()
        if game.introduction_9 == True:
            game.intro_9()
        if game.introduction_10 == True:
            game.intro_10()

        if game.show_feedback == True:
            for i in feedback:
                game.draw_feedback(i, ("cornsilk"))
        if game.first_time == False and game.insummary == False and abs(game.time-game.roundtime)>game.roundtimer and game.round_number < game.roundstandard + 1 and game.timer_follow == True:
                game.timer_follow = False
                game.baseconditions()                
                game.increase_click_counter()
                game.add_to_output("automatic progression to next round")
                game.main_menu_action = True
                game.show_agencies = False
                game.show_main_menu = False
                game.show_feedback = False
                game.choice = 2
                game.advance_game_round()
                game.officer_report = True
    
                

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
                        if game.choice == 1:
                            game.add_to_output("menu option 2 clicked")
                            game.information = True
                        if game.choice == 3:
                            game.add_to_output("menu option 3 clicked")
                            game.news_reports = True
                        if game.choice == 2:
                            if game.total_budget < 0:
                                game.baseconditions()
                                game.budget_question = True
                                game.add_to_output("menu option 4 clicked")
                            else:
                                game.baseconditions()
                                game.choice = "null"
                                game.add_to_output("menu option 4 clicked")
                                game.main_menu_action = True
                                game.show_agencies = False
                                game.show_main_menu = False
                                game.show_feedback = False
                                game.advance_game_round()
                                game.officer_report = True
                        if game.choice == 4:
                            game.add_to_output("menu option 5 clicked")
                            game.historical = True
                        if game.choice == 5:
                            game.add_to_output("menu option 6 clicked")
                            game.rankings = True
                           

            if event.type == pygame.QUIT:
                game.finish_game()


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