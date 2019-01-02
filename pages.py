from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from settings import *
from django.utils.translation import ugettext as _
import math


# --- Instructions -----------------------------------------------------------------------------------------------------

class Instructions(Page):

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):

        GTpayoffs = list(zip(*[self.player.participant.vars['GTpayoff1']] + self.player.participant.vars['GTpayoffs'])) + [list(zip(*self.player.participant.vars['GameTree']))[-1]]
        GTpayoffs = [tuple(GTpayoffs[j][k] for j in range(0, len(GTpayoffs))) for k in range(0, len(self.player.participant.vars['GameTree']))]

        GTpayoffs_str = list(zip(*GTpayoffs))
        strings = [str(tuple(GTpayoffs_str[j][k] for j in range(0, len(GTpayoffs_str)-1))) for k in range(0, len(self.player.participant.vars['GameTree']))]
        xpoints = self.player.participant.vars['GTxpoints']
        GTpayoffs_str = [(strings[j], xpoints[j]) for j in range(0, len(strings))]

        if Constants.graph_instructions == 'horizontal':
            add_to_last_price = 600/Constants.num_players
            place_of_buy = 300 / Constants.num_players
            font_size_buy = 10 + 4 * (3/Constants.num_players)
            font_size_price = 14+4*(3/Constants.num_players)
            font_size_payoff = 20*(3/Constants.num_players)
        else:
            add_to_last_price = 40+480/Constants.num_players+40
            place_of_buy = 300/Constants.num_players+40
            font_size_buy = 12
            font_size_price = 16
            font_size_payoff = 16
        height = add_to_last_price * Constants.num_players

        return {
            'GameTree': self.player.participant.vars['GameTree'],
            'GTpayoff1': self.player.participant.vars['GTpayoff1'],
            'GTpayoffN': self.player.participant.vars['GTpayoffN'],
            'GTpayoffs': GTpayoffs,
            'GTpayoffs_str': GTpayoffs_str,
            'add_to_last_price': add_to_last_price,
            'place_of_buy': place_of_buy,
            'font_size_buy': font_size_buy,
            'font_size_price': font_size_price,
            'font_size_payoff': font_size_payoff,
            'graph': Constants.graph_instructions,
            'height': height,
            'add_to_last_payoff': add_to_last_price+15,
            'num_players': Constants.num_players,
            'tooltip_price': Constants.tooltip_price,
            'tooltip_payoff': Constants.tooltip_payoff,
            'TAB': self.player.participant.vars['TAB'],
            'exp_currency': Constants.exp_currency
        }


# --- ControlQuestions -------------------------------------------------------------------------------------------------

class ControlQuestions(Page):

    # form model
    # ----------------------------------------------------------------------------------------------------------------
    form_model = 'player'

    # form fields
    # ----------------------------------------------------------------------------------------------------------------
    def get_form_fields(self):
        form_fields = self.player.participant.vars['cq_form_fields']
        return form_fields

    if Constants.controlquestions_correct:
        def error_message(self, values):
            for item, id, question, answer0, answer1, correct in self.player.participant.vars['cq']:
                if values['cq_' + str(id)] != str(correct):
                    return _('You answered Q') + str(id) + _(' incorrectly.')
            for item, id, question, answer0, answer1, answer2, answer3, correct in self.player.participant.vars['cq1']:
                if values['cq_' + str(id)] != str(correct):
                    return _('You answered Q') + str(id) + _(' incorrectly.')

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return {
            'cq': self.player.participant.vars['cq'],
            'cq1': self.player.participant.vars['cq1'],
            'controlquestions_correct': Constants.controlquestions_correct
        }



# --- Decision ---------------------------------------------------------------------------------------------------------

class Decision(Page):

    # form model
    # ----------------------------------------------------------------------------------------------------------------
    form_model = 'player'

    # form fields
    # ----------------------------------------------------------------------------------------------------------------
    def get_form_fields(self):
        # unzip list of form_fields from <cem_choices> list
        form_fields = self.player.participant.vars['form_fields']

        if Constants.order == 'descending':
            form_fields = sorted(form_fields, reverse=True)

        # provide form field associated with pagination <one_choice_per_page>
        if Constants.one_choice_per_page:
            page_repetition = [int(Constants.num_prices * math.ceil(float(j)/Constants.num_prices) / Constants.num_prices) - 1 for j in range(1, Constants.num_rounds + 1)]
            page = self.subsession.round_number - page_repetition[self.subsession.round_number - 1] * Constants.num_prices
            if Constants.strategy_method:
                if Constants.order == 'random':
                    return [form_fields[[self.group.get_player_by_id(1).participant.vars['prices_displayed'][page - 1]][0][0]-1]]
                else:
                    return [form_fields[page - 1]]
            else:
                if Constants.order == 'random':
                    return [form_fields[[self.group.get_player_by_id(1).participant.vars['prices_displayed'][page - 1]][0][0]-1]]
                else:
                    return [form_fields[self.player.id_in_group-1]]

        # provide list of form_fields in case of no pagination
        return form_fields

    # variables for template
    # ----------------------------------------------------------------------------------------------------------------
    def vars_for_template(self):

        page_repetition = [
            int(Constants.num_prices * math.ceil(float(j) / Constants.num_prices) / Constants.num_prices) - 1 for j in
            range(1, Constants.num_rounds + 1)]
        page = self.subsession.round_number - page_repetition[self.subsession.round_number - 1] * Constants.num_prices

        choices = self.group.get_player_by_id(1).participant.vars['choices']
        prices = self.group.get_player_by_id(1).participant.vars['prices_displayed']

        w, x, y, z = zip(*choices)
        choices_unzipped = sorted(list(y))

        a, b = zip(*prices)
        prices_unzipped = sorted(list(b))

        price_choice_match = sorted([prices_unzipped.index(choices_unzipped[k]) + 1 for k in range(0, Constants.num_players)])

        if Constants.one_choice_per_page:
            if Constants.strategy_method:
                return {
                    'page': page,
                    'choices': self.group.get_player_by_id(1).participant.vars['choices'],
                    'prices': [self.group.get_player_by_id(1).participant.vars['prices_displayed'][page - 1]],
                    'price': [self.group.get_player_by_id(1).participant.vars['prices_displayed'][page - 1]][0][1],
                    'one_choice_per_page': Constants.one_choice_per_page,
                    'real_currency': REAL_WORLD_CURRENCY_CODE,
                    'exp_currency': Constants.exp_currency,
                    'price_choice_match': price_choice_match,
                    'choices_unzip': choices_unzipped,
                    'prices_unzip': prices_unzipped,
                    'buttons': Constants.buttons,
                    'buys': self.player.participant.vars['buys'],
                    'breaks': self.player.participant.vars['breaks'],
                    'prices_displayed': [self.group.get_player_by_id(1).participant.vars['prices_displayed'][0]]
                }
            else:
                return {
                    'choices': self.group.get_player_by_id(1).participant.vars['choices'],
                    'prices': [self.group.get_player_by_id(1).participant.vars['prices_displayed'][self.player.id_in_group - 1]],
                    'price': [self.group.get_player_by_id(1).participant.vars['prices_displayed'][self.player.id_in_group - 1]][0][1],
                    'one_choice_per_page': Constants.one_choice_per_page,
                    'real_currency': REAL_WORLD_CURRENCY_CODE,
                    'exp_currency': Constants.exp_currency,
                    'price_choice_match': price_choice_match,
                    'choices_unzip': choices_unzipped,
                    'prices_unzip': prices_unzipped,
                    'buttons': Constants.buttons,
                    'buys': self.player.participant.vars['buys'],
                    'form_fields': [self.player.participant.vars['form_fields'][[self.group.get_player_by_id(1).participant.vars['prices_displayed'][page - 1]][0][0]-1]]
                }
        else:
            return {
                'choices': self.group.get_player_by_id(1).participant.vars['choices'],
                'prices': self.group.get_player_by_id(1).participant.vars['prices_displayed'],
                'one_choice_per_page': Constants.one_choice_per_page,
                'real_currency': REAL_WORLD_CURRENCY_CODE,
                'exp_currency': Constants.exp_currency,
                'price_choice_match': price_choice_match,
                'choices_unzip': choices_unzipped,
                'prices_unzip': prices_unzipped,
                'buttons': Constants.buttons
            }

    def before_next_page(self):
        self.player.set_decision()
        self.player.set_buy_price()
        if self.subsession.round_number == Constants.num_rounds:
            self.player.set_max_buy()
        self.player.set_repetition()


# --- ResultsWaitPage --------------------------------------------------------------------------------------------------

class ResultsWaitPage(WaitPage):

    # skip results calculation until last page
    # ----------------------------------------------------------------------------------------------------------------
    def is_displayed(self):
        if Constants.one_choice_per_page and Constants.strategy_method:
            return self.subsession.round_number in self.participant.vars['breaks']
        return True

    def after_all_players_arrive(self):
        self.group.set_results()


# --- Results ----------------------------------------------------------------------------------------------------------

class Results(Page):

    # skip results until last page
    # ----------------------------------------------------------------------------------------------------------------
    def is_displayed(self):
        if Constants.one_choice_per_page and Constants.strategy_method:
            return self.subsession.round_number in self.participant.vars['breaks']
        return True

    # variables for template
    # ----------------------------------------------------------------------------------------------------------------
    def vars_for_template(self):

        page = self.subsession.round_number

        choices = self.group.get_player_by_id(1).participant.vars['choices']
        if Constants.order == 'descending':
            choices = choices[::-1]
        w, x, y, z = zip(*choices)
        realisations = self.group.get_player_by_id(Constants.num_players).participant.vars['relevant_realisations']
        payoffs = [getattr(j, 'earnings') for j in self.group.get_players()]

        results = list(zip(w, x, y, z, realisations, payoffs))

        GTpayoffs = list(zip(*[self.player.participant.vars['GTpayoff1']] + self.player.participant.vars['GTpayoffs'])) + [list(zip(*self.player.participant.vars['GameTree']))[-1]]
        GTpayoffs = [tuple(GTpayoffs[j][k] for j in range(0, len(GTpayoffs))) for k in range(0, len(self.player.participant.vars['GameTree']))]

        GTpayoffs_str = list(zip(*GTpayoffs))
        strings = [str(tuple(GTpayoffs_str[j][k] for j in range(0, len(GTpayoffs_str)-1))) for k in range(0, len(self.player.participant.vars['GameTree']))]
        xpoints = self.player.participant.vars['GTxpoints']
        GTpayoffs_str = [(strings[j], xpoints[j]) for j in range(0, len(strings))]

        if Constants.graph_results == 'horizontal':
            add_to_last_price = 600/Constants.num_players
            place_of_buy = 300 / Constants.num_players
            font_size_buy = 10 + 4 * (3/Constants.num_players)
            font_size_price = 14+4*(3/Constants.num_players)
            font_size_payoff = 20*(3/Constants.num_players)
        else:
            add_to_last_price = 40+480/Constants.num_players+40
            place_of_buy = 300/Constants.num_players+40
            font_size_buy = 12
            font_size_price = 16
            font_size_payoff = 16
        height = add_to_last_price * Constants.num_players

        return {
            'one_choice_per_page': Constants.one_choice_per_page,
            'real_currency': REAL_WORLD_CURRENCY_CODE,
            'exp_currency': Constants.exp_currency,
            'position': self.player.id_in_group,
            'earnings': self.player.earnings,
            'results': results,
            'realisations': self.player.participant.vars['relevant_realisations'],
            'pcm': self.player.participant.vars['price_choice_match'],
            'GameTree': self.player.participant.vars['GameTree'],
            'GTpayoff1': self.player.participant.vars['GTpayoff1'],
            'GTpayoffN': self.player.participant.vars['GTpayoffN'],
            'GTpayoffs': GTpayoffs,
            'GTpayoffs_str': GTpayoffs_str,
            'add_to_last_price': add_to_last_price,
            'place_of_buy': place_of_buy,
            'font_size_buy': font_size_buy,
            'font_size_price': font_size_price,
            'font_size_payoff': font_size_payoff,
            'graph': Constants.graph_results,
            'height': height,
            'add_to_last_payoff': add_to_last_price + 15,
            'num_players': Constants.num_players,
            'tooltip_price': Constants.tooltip_price,
            'tooltip_payoff': Constants.tooltip_payoff,
            'TAB': self.player.participant.vars['TAB'],
            'buys': self.player.participant.vars['buys'],
            'buy': self.player.participant.vars['buy']
        }


# --- DecisionWaitPage -------------------------------------------------------------------------------------------------

class DecisionWaitPage(WaitPage):

    def is_displayed(self):
        if Constants.one_choice_per_page and Constants.strategy_method:
            return self.subsession.round_number - 1 in self.participant.vars['breaks']
        return self.subsession.round_number != 1

    def after_all_players_arrive(self):
        self.subsession.start_session()


# --- Page Sequence ----------------------------------------------------------------------------------------------------

page_sequence = [Decision]

if Constants.controlquestions:
    page_sequence.insert(0, ControlQuestions)

if Constants.instructions:
    page_sequence.insert(0, Instructions)

if Constants.results and Constants.num_players > 1:
    page_sequence.append(ResultsWaitPage)
    page_sequence.append(Results)

if Constants.num_repetitions > 1:
    page_sequence.insert(0, DecisionWaitPage)