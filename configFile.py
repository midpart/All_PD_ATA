import json
import time
from datetime import datetime
import random

def get_config(path):
    try:
        with open(path, 'r') as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f"Error reading config.json: {e}")


def get_rounds_from_config(path):
    try:
        config = get_config(path)
        return int(config.get("round_number", 1))
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return 1


def get_payoff_matrix(path):
    try:
        config = get_config(path)
        matrix = config.get("payoff_matrix", {})
        return {(k.split('_')[0], k.split('_')[1]): tuple(v) for k, v in matrix.items()}
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return {}


def get_selection_order(path):
    try:
        config = get_config(path)
        return [int(config.get("your_choice_order", 1)), int(config.get("other_choice_order", 2)),
                int(config.get("expectation_of_rounds", 3))]
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return {}


def get_first_row_percentage(path):
    try:
        config = get_config(path)
        return int(config.get("first_row_width_percentage", 30))
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return {}


def get_show_other_participant_info(path):
    try:
        config = get_config(path)
        return bool(config.get("show_other_participant_info", False))
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return {}

def get_instruction_page_time_out_in_sec(path):
    try:
        config = get_config(path)
        return int(config.get("instruction_page_time_out_in_sec", 60*5))
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return {}

def get_game_page_time_out_in_sec(path):
    try:
        config = get_config(path)
        return int(config.get("game_page_time_out_in_sec", 60*10))
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return {}    

def other_player(player):
    return player.get_others_in_group()[0]

def choice_wait_page_is_display(player, constant, game_page_time_out, instruction_page_time_out):
    others = player.get_others_in_group()
    wait_duration = time.time() - player.participant.vars['going_to_wait_page']
    if others:
        other = others[0]
        # if wait_duration > (game_page_time_out + instruction_page_time_out) + 1:
        #     other.participant.is_dropout = True
        
        if other.participant.is_dropout == True:
            set_payoffs(player.group, constant)
        return not other.participant.is_dropout
    return True

def set_end_time(player):
    start_time = player.participant.vars['start_time']
    player.start_time = start_time
    player.start_time_formatted = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    player.end_time = time.time()
    player.end_time_formatted = datetime.fromtimestamp(player.end_time).strftime('%Y-%m-%d %H:%M:%S')
    player.duration = (player.end_time - player.start_time)
    del player.participant.vars['start_time']

    ## for calculating timeout in the wait page
    player.participant.vars['going_to_wait_page'] = time.time()

def get_prolific_id(player):
    player.participant.vars.setdefault('prolific_id', 'unknown')
    return player.participant.vars['prolific_id']

def get_random_choice():
    return random.choice(['A', 'B'])

def set_payoffs(group, constant):
    players = group.get_players()
    player1 = players[0]
    player2 = players[1]

    player1.prolific_id = get_prolific_id(player1)
    player2.prolific_id = get_prolific_id(player2)

    if player1.participant.is_dropout:
        player1.is_dropout = True
    
    if player2.participant.is_dropout:
        player2.is_dropout = True

    if player1.your_choice not in ("A", "B") or player1.is_dropout == True:
        player1.your_choice = get_random_choice()
    if player2.your_choice not in ("A", "B") or player2.is_dropout == True:
        player2.your_choice = get_random_choice()

    player1.payoff, player2.payoff = constant.payoff_matrix.get((player1.your_choice, player2.your_choice))
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

def validate_prolific_id(prolific_id):
    if prolific_id is None or len(prolific_id) != 24:
        return f"Prolific ID must be 24 characters long"