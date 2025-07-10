from otree.api import *
import time
from configFile import validate_prolific_id

doc = """
Route participant to either Basic or normal ATA PD experiment
"""
class C(BaseConstants):
    NAME_IN_URL = 'Basic_PD_ATA_Router'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    TIMEOUT_IN_SECONDS = 300


def creating_session(subsession):
    session = subsession.session
    session.vars['basic_pd_ata_simple'] = 0
    session.vars['basic_pd_ata'] = 0
    session.vars['basic_sh'] = 0
    session.vars['basic_sh_simple'] = 0
    session.vars['total'] = 0

class Subsession(BaseSubsession):

    def group_by_arrival_time_method(subsession, waiting_players):
        if len(waiting_players) >= 2:
            return waiting_players[:2]

        for player in waiting_players:
            if waiting_too_long(player):
                player.timed_out = True  # mark player as timed out
                return [player]


def waiting_too_long(player):
    arrival = player.participant.vars['start_time']
    if arrival is None:
        return False
    return time.time() - arrival > C.TIMEOUT_IN_SECONDS

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    prolific_id = models.StringField(label="Please indicate your prolific ID", initial="")
    assigned_game = models.StringField(initial="")
    start_time = models.FloatField(initial=0)
    end_time = models.FloatField(initial=0)
    duration = models.FloatField(initial=0)
    name = models.StringField(initial="")
    timed_out = models.BooleanField(initial=False)

# PAGES
class RedirectWaitPage(WaitPage):
    group_by_arrival_time = True
    wait_for_all_groups = False
    body_text = "Waiting for other players to join..."

    @staticmethod
    def is_displayed(player):
        if 'start_time' not in player.participant.vars:
            player.participant.vars['start_time'] = time.time()
        return True

class Redirect(Page):
    form_model = 'player'
    form_fields = ['prolific_id']

    @staticmethod
    def is_displayed(player):
        # return not player.timed_out
        return True

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
        )

    @staticmethod
    def error_message(player, values):
        prolific_id = (values['prolific_id']).strip()
        message = validate_prolific_id(prolific_id)
        if message is not None:
            return message

        others = player.subsession.get_players()
        for other in others:
            if other.prolific_id.strip() == prolific_id:
                return "Someone already has a same prolific ID"

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        start_time = player.participant.vars['start_time']
        player.start_time = start_time
        player.end_time = time.time()
        player.duration = (player.end_time - player.start_time)
        del player.participant.vars['start_time']

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        if player.timed_out:
            return False
        session = player.session
        ata_simple  = session.vars.get('basic_pd_ata_simple', 0)
        ata_regular  = session.vars.get('basic_pd_ata', 0)
        sh_simple  = session.vars.get('basic_sh_simple', 0)
        sh_regular  = session.vars.get('basic_sh', 0)
        total  = session.vars.get('total', 0)
        player.participant.vars['prolific_id'] = player.prolific_id
        
        if(total == 0 or ata_simple %2 != 0 or (ata_simple == ata_regular and ata_simple == sh_simple and ata_simple == sh_regular)):
            assigned_app = 'Basic_PD_ATA_Simple'
            session.vars['basic_pd_ata_simple'] = ata_simple + 1
            session.vars['total'] = total + 1
        elif(ata_regular == 0 or ata_regular%2 != 0 or (ata_regular == sh_simple and ata_regular == sh_regular)):
            assigned_app = 'Basic_PD_ATA'
            session.vars['basic_pd_ata'] = ata_regular + 1
            session.vars['total'] = total + 1
        elif(sh_simple == 0 or sh_simple%2 != 0 or sh_simple == sh_regular):
            assigned_app = 'Basic_SH_Simple'
            session.vars['basic_sh_simple'] = sh_simple + 1
            session.vars['total'] = total + 1
        else:
            assigned_app = 'Basic_SH'
            session.vars['basic_sh'] = sh_regular + 1
            session.vars['total'] = total + 1

        player.participant.vars['which_app'] = assigned_app
        player.assigned_game = assigned_app
        return assigned_app

class Timeout(Page):
    @staticmethod
    def is_displayed(player):
        return player.timed_out

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            prolific_url = player.session.config['prolific_completion_url']
        )

page_sequence = [RedirectWaitPage, Redirect, Timeout]
