from otree.api import *
import os
import json
import time
from datetime import datetime

# Construct the absolute path to the config file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Gets the directory of models.py
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')  # Moves up one level to project folder

doc = """
Basic PD ATA game
"""

def get_config():
    try:
      with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f"Error reading config.json: {e}")

def get_rounds_from_config():
    try:
        config = get_config()
        return int(config.get("round_number", 1))
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return 1 

def get_payoff_matrix():
    try:
        config = get_config()
        matrix = config.get("payoff_matrix", {})
        return {(k.split('_')[0], k.split('_')[1]): tuple(v) for k, v in matrix.items()}
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return {}

def get_selection_order():
    try:
        config = get_config()
        return [int(config.get("your_choice_order", 1)), int(config.get("other_choice_order", 2)), int(config.get("expectation_of_rounds", 3))]
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return {}

def get_first_row_percentage():
    try:
        config = get_config()
        return int(config.get("first_row_width_percentage", 30))
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return {}
    
def get_show_other_participant_info():
    try:
        config = get_config()
        return bool(config.get("show_other_participant_info", False))
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return {}
    
class C(BaseConstants):
    NAME_IN_URL = 'Basic_PD_ATA'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = get_rounds_from_config()
    payoff_matrix = get_payoff_matrix()
    default_value = ""


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    your_choice = models.StringField(initial="")
    your_think_other_choice = models.StringField(initial="")
    me_payoff = models.IntegerField(initial=0)
    other_payoff = models.IntegerField(initial=0)
    choice_AC_me = models.IntegerField(initial=0)
    choice_AC_other = models.IntegerField(initial=0)
    choice_AD_me = models.IntegerField(initial=0)
    choice_AD_other = models.IntegerField(initial=0)
    choice_BC_me = models.IntegerField(initial=0)
    choice_BC_other = models.IntegerField(initial=0)
    choice_BD_me = models.IntegerField(initial=0)
    choice_BD_other = models.IntegerField(initial=0)
    me_total_payoff = models.IntegerField(initial=0)
    other_total_payoff = models.IntegerField(initial=0)
    start_time = models.FloatField(initial=0)
    start_time_formatted = models.StringField()
    end_time = models.FloatField(initial=0)
    end_time_formatted = models.StringField()
    duration = models.FloatField(initial=0)


def other_player(player: Player):
    return player.get_others_in_group()[0]

# PAGES
class Instructions(Page):
    @staticmethod
    def vars_for_template(player: Player):
        your_choice_order, other_choice_order, expectation_of_rounds = get_selection_order()
        first_row_percentage = get_first_row_percentage()
        round_list = list(range(0, C.NUM_ROUNDS))
        show_other_participant_info = get_show_other_participant_info()
        return dict(
            order_list = list(range(0, 3)),
            round_list = round_list,
            courrent_round = 0,
            your_choice_order = your_choice_order,
            other_choice_order = other_choice_order,
            expectation_of_rounds = expectation_of_rounds,
            first_row_percentage = first_row_percentage,
            show_other_participant_info = show_other_participant_info,
        )
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1  # Only show for the first round



class ChoicePage(Page):
    form_model = 'player'
    form_fields = ['your_choice', 'your_think_other_choice', 'choice_AC_me', 'choice_AC_other', 'choice_AD_me', 'choice_AD_other', 'choice_BC_me', 'choice_BC_other', 'choice_BD_me', 'choice_BD_other']

    @staticmethod
    def vars_for_template(player: Player):
        if 'start_time' not in player.participant.vars:
            player.participant.vars['start_time'] = time.time()
        round_list = list(range(0, C.NUM_ROUNDS))
        player_id = player.id_in_group
        opponent = other_player(player)
        courrent_round = player.round_number
        your_choice_order, other_choice_order, expectation_of_rounds = get_selection_order()
        first_row_percentage = get_first_row_percentage()
        show_other_participant_info = get_show_other_participant_info()

        return dict(
            order_list = list(range(0, 3)),
            round_list = round_list,
            player_id = player_id,
            opponent_id = opponent.id_in_group,
            courrent_round = courrent_round,
            your_choice_order = your_choice_order,
            other_choice_order = other_choice_order,
            expectation_of_rounds = expectation_of_rounds,
            first_row_percentage = first_row_percentage,
            show_other_participant_info = show_other_participant_info,
        )
    @staticmethod
    def js_vars(player):
        previous_rounds = player.in_previous_rounds()

        previoud_rounds_data = [
            dict(round_number=p.round_number, choice1=p.your_choice, choice2=p.your_think_other_choice,  payoff=p.payoff
                 , me_payoff= p.me_payoff, other_payoff = p.other_payoff
                  , choice_AC_me = p.choice_AC_me, choice_AC_other=p.choice_AC_other
                  , choice_AD_me = p.choice_AD_me, choice_AD_other=p.choice_AD_other
                  , choice_BC_me = p.choice_BC_me, choice_BC_other=p.choice_BC_other
                  , choice_BD_me = p.choice_BD_me, choice_BD_other=p.choice_BD_other
                  , me_total_payoff = p.me_total_payoff, other_total_payoff = p.other_total_payoff
                    )
            for p in previous_rounds
         ]
        return dict(
            current_round=player.round_number,
            default_value = C.default_value,
            previoud_rounds_data = previoud_rounds_data,
        )
    def error_message(player, values): 
        if values['your_choice'] not in ["A", "B"]:
            return "Please select value between A or B"
        if values['your_think_other_choice'] not in ["C", "D"]:
            return "Please select value between A or B"
        if values['choice_AC_me'] < 0 or values['choice_AC_other'] < 0 or values['choice_AD_me'] < 0 or values['choice_AD_other'] < 0:
            return "Please select value between 0 to 100"
        if values['choice_BC_me'] < 0 or values['choice_BC_other'] < 0 or values['choice_BD_me'] < 0 or values['choice_BD_other'] < 0:
            return "Please select value between 0 to 100"

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_end_time(player)

#function
def set_payoffs(group):
        players = group.get_players()
        player1 = players[0]
        player2 = players[1]

        player1.payoff, player2.payoff = C.payoff_matrix.get((player1.your_choice, player2.your_choice))
        player1.me_payoff = int(player1.payoff)
        player2.me_payoff = int(player2.payoff)

        player1.other_payoff = player2.me_payoff
        player2.other_payoff = player1.me_payoff

        player1_previous_rounds = player1.in_previous_rounds()
        player2_previous_rounds = player2.in_previous_rounds()

        
        player1.me_total_payoff = sum(p.me_payoff for p in player1_previous_rounds) + player1.me_payoff
        player2.me_total_payoff = sum(p.me_payoff for p in player2_previous_rounds) + player2.me_payoff

        player1.other_total_payoff = player2.me_total_payoff
        player2.other_total_payoff = player1.me_total_payoff

def set_end_time(player: Player):
    start_time = player.participant.vars['start_time']
    player.start_time = start_time
    player.start_time_formatted = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    player.end_time = time.time()
    player.end_time_formatted = datetime.fromtimestamp(player.end_time).strftime('%Y-%m-%d %H:%M:%S')
    player.duration = (player.end_time - player.start_time)
    del player.participant.vars['start_time']

#function end
class ChoiceWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

class ResultsWaitPage(WaitPage):
    def is_displayed(Group):
        return Group.round_number > C.NUM_ROUNDS  # Only in last round


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Show this page only in the last round
        return player.round_number == C.NUM_ROUNDS
     
    def vars_for_template(self):
        all_rounds = Player.in_all_rounds(self) 
        total_me_payoff = sum(p.me_payoff for p in Player.in_all_rounds(self))
        total_other_payoff = sum(p.other_payoff for p in Player.in_all_rounds(self))
        rounds_data = [
            dict(round_number=p.round_number, choice1=p.your_choice, choice2=p.your_think_other_choice,  payoff=p.payoff
                 , me_payoff= p.me_payoff, other_payoff = p.other_payoff
                  , choice_AC_me = p.choice_AC_me, choice_AC_other=p.choice_AC_other
                  , choice_AD_me = p.choice_AD_me, choice_AD_other=p.choice_AD_other
                  , choice_BC_me = p.choice_BC_me, choice_BC_other=p.choice_BC_other
                  , choice_BD_me = p.choice_BD_me, choice_BD_other=p.choice_BD_other
                  , me_total_payoff = p.me_total_payoff, other_total_payoff = p.other_total_payoff
                 , start_time = p.start_time_formatted, end_time = p.end_time_formatted, duration=p.duration
                    )
            for p in all_rounds
        ]
        
        show_other_participant_info = get_show_other_participant_info()

        return dict(
            current_round=self.subsession.round_number,
            max_round=C.NUM_ROUNDS,
            rounds_data=rounds_data,  # Pass the list to the template
            total_me_payoff = total_me_payoff,
            total_other_payoff = total_other_payoff,
            show_other_participant_info = show_other_participant_info,
        )



page_sequence = [Instructions, ChoicePage, ChoiceWaitPage, ResultsWaitPage, Results]
