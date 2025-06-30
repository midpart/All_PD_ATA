from otree.api import *
import os
import json
import time
from datetime import datetime
from configFile import *

# Construct the absolute path to the config file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Gets the directory of models.py
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')  # Moves up one level to project folder

doc = """
Basic PD ATA game
"""
    
class C(BaseConstants):
    NAME_IN_URL = 'Basic_PD_ATA'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = get_rounds_from_config(CONFIG_PATH)
    payoff_matrix = get_payoff_matrix(CONFIG_PATH)
    default_value = ""

class Subsession(BaseSubsession):
    pass

def creating_session(subsession):
    for p in subsession.session.get_participants():
        p.is_dropout = False  # Default value

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
    prolific_id = models.StringField(label="Please indicate your prolific ID", initial="")
    is_dropout = models.BooleanField(initial=False)

# PAGES
class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1  # Only show for the first round
    
    @staticmethod
    def vars_for_template(player: Player):
        your_choice_order, other_choice_order, expectation_of_rounds = get_selection_order(CONFIG_PATH)
        first_row_percentage = get_first_row_percentage(CONFIG_PATH)
        round_list = list(range(0, C.NUM_ROUNDS))
        show_other_participant_info = get_show_other_participant_info(CONFIG_PATH)
        return dict(
            order_list = list(range(0, 3)),
            round_list = round_list,
            courrent_round = 0,
            your_choice_order = your_choice_order,
            other_choice_order = other_choice_order,
            expectation_of_rounds = expectation_of_rounds,
            first_row_percentage = first_row_percentage,
            show_other_participant_info = show_other_participant_info,
            prolific_id = get_prolific_id(player),
        )

    # @staticmethod
    # def get_timeout_seconds(player):
    #     if player.participant.is_dropout:
    #         return 1  # instant timeout, 1 second
    #     else:
    #         return get_instruction_page_time_out_in_sec(CONFIG_PATH)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant

        # if timeout_happened:
        #     participant.is_dropout = True

class WaitForGamePage(WaitPage):
    body_text = "Waiting for other players to join the game..."
    @staticmethod
    def after_all_players_arrive(group: Group):
        return True  

class ChoicePage(Page):
    form_model = 'player'
    form_fields = ['your_choice', 'your_think_other_choice', 'choice_AC_me', 'choice_AC_other', 'choice_AD_me', 'choice_AD_other', 'choice_BC_me', 'choice_BC_other', 'choice_BD_me', 'choice_BD_other']

    @staticmethod
    def get_timeout_seconds(player):

        # group = player.group
        # current_page = player.participant._current_page_name

        # all_here = all(
        #     p.participant._current_page_name == current_page
        #     for p in player.group.get_players()
        # )

        # if not all_here:
        #     return None  # No timeout yet

        if player.participant.is_dropout:
            return get_bot_time_delay(CONFIG_PATH)
        else:
            return get_game_page_time_out_in_sec(CONFIG_PATH)

    @staticmethod
    def vars_for_template(player: Player):
        if 'start_time' not in player.participant.vars:
            player.participant.vars['start_time'] = time.time()
        round_list = list(range(0, C.NUM_ROUNDS))
        player_id = player.id_in_group
        opponent = other_player(player)
        current_round = player.round_number
        your_choice_order, other_choice_order, expectation_of_rounds = get_selection_order(CONFIG_PATH)
        first_row_percentage = get_first_row_percentage(CONFIG_PATH)
        show_other_participant_info = get_show_other_participant_info(CONFIG_PATH)

        return dict(
            order_list = list(range(0, 3)),
            round_list = round_list,
            player_id = player_id,
            opponent_id = opponent.id_in_group,
            current_round = current_round,
            your_choice_order = your_choice_order,
            other_choice_order = other_choice_order,
            expectation_of_rounds = expectation_of_rounds,
            first_row_percentage = first_row_percentage,
            show_other_participant_info = show_other_participant_info,
        )
    
    @staticmethod
    def js_vars(player):
        previous_rounds = player.in_previous_rounds()

        previous_rounds_data = [
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
            previous_rounds_data = previous_rounds_data,
        )
    
    @staticmethod
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
        if timeout_happened:
            player.participant.is_dropout = True
        set_end_time(player)

class ChoiceWaitPage(WaitPage):
    # @staticmethod
    # def is_displayed(player: Player):
    #     return choice_wait_page_is_display(player, C, get_game_page_time_out_in_sec(CONFIG_PATH), get_instruction_page_time_out_in_sec(CONFIG_PATH))

    @staticmethod
    def after_all_players_arrive(group: Group):
        set_payoffs(group, C)

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
        
        show_other_participant_info = get_show_other_participant_info(CONFIG_PATH)

        return dict(
            current_round=self.subsession.round_number,
            max_round=C.NUM_ROUNDS,
            rounds_data=rounds_data,  # Pass the list to the template
            total_me_payoff = total_me_payoff,
            total_other_payoff = total_other_payoff,
            show_other_participant_info = show_other_participant_info,
            prolific_url = self.session.config['prolific_completion_url'],
            prolific_id = Player.prolific_id
        )

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        print('upcoming_apps is', upcoming_apps)
        return None
        # if player.whatever:
        #     return upcoming_apps[-1]

page_sequence = [Instructions, WaitForGamePage, ChoicePage, ChoiceWaitPage, ResultsWaitPage, Results]
