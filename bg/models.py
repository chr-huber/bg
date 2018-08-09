from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from bg.config import *
from django.utils.translation import ugettext as _
import math
import random
import numpy as np
from scipy.stats import geom, poisson, binom, randint


author = """
Christoph Huber
Email: christoph.huber@uibk.ac.at
"""

doc = """
Bubble Game by Moinas and Pouget (2013), Econometrica 81(4): 1507-1539
"""


#--- Class SUBSESSION --------------------------------------------------------------------------------------------------

class Subsession(BaseSubsession):

    def creating_session(self):
        if self.round_number == 1:
            self.start_session()

    def start_session(self):

        # group subjects randomly (if <random_grouping = True>)
        # ----------------------------------------------------------------------------------------------------------------
        if Constants.random_grouping:
            self.group_randomly()

        breaks = [j * Constants.num_prices for j in range(1, Constants.num_repetitions + 1)]

        n = Constants.num_players
        nprices = Constants.num_prices

        for p in self.get_players():

            p.participant.vars['breaks'] = breaks

            indices = [i for i in range(1, nprices + 1)]
            form_fields = ['buy_' + str(k) for k in indices]

            p.participant.vars['form_fields'] = form_fields

            p.participant.vars['buy'] = []
            p.participant.vars['buys'] = []

        for group in self.get_groups():

            indices = [i for i in range(1, n + 1)]
            positions = [i for i in range(1, n + 1)]

            # determine initial price depending on cap
            # ----------------------------------------------------------------------------------------------------
            price = 1
            possibleinitprices = [1]
            while price < Constants.cap:
                price = price * Constants.multiple
                possibleinitprices += [price]

            price1 = -1
            if Constants.cap == 0:
                if Constants.dist_initprices == 'geometric':
                    n1 = np.random.geometric(Constants.p)
                elif Constants.dist_initprices == 'poisson':
                    n1 = np.random.poisson(Constants.p)
                elif Constants.dist_initprices == 'binomial':
                    n1 = np.random.binomial(Constants.N, Constants.p)
                elif Constants.dist_initprices == 'uniform':
                    n1 = np.random.randint(0, Constants.N + 1)
                price1 = Constants.multiple ** (n1 - 1)
            else:
                while price1 not in possibleinitprices:
                    if Constants.dist_initprices == 'geometric':
                        n1 = np.random.geometric(Constants.p)
                    elif Constants.dist_initprices == 'poisson':
                        n1 = np.random.poisson(Constants.p)
                    elif Constants.dist_initprices == 'binomial':
                        n1 = np.random.binomial(Constants.N, Constants.p)
                    elif Constants.dist_initprices == 'uniform':
                        n1 = np.random.randint(0, Constants.N + 1)
                    price1 = Constants.multiple ** (n1 - 1)

            prices = [price1 * (Constants.multiple ** (i - 1)) for i in positions]

            # random player matching
            # ----------------------------------------------------------------------------------------------------
            players = [group.get_player_by_id(k).id_in_group for k in range(1, n + 1)]
            if Constants.random_grouping:
                random.shuffle(players)

            choices = list(zip(indices, positions, prices, players))

            # determine possible choices
            # ----------------------------------------------------------------------------------------------------
            if Constants.num_prices == Constants.num_players:
                prices_displayed = prices
            else:
                prices_displayed = []
                p1 = price1
                while p1 > 1 and len(prices_displayed) < Constants.num_prices - Constants.num_players:
                    p1 = p1/Constants.multiple
                    prices_displayed = [int(p1)] + prices_displayed
                prices_displayed = prices_displayed + prices
                while len(prices_displayed) < Constants.num_prices:
                    pn = prices_displayed[-1] * Constants.multiple
                    prices_displayed = prices_displayed + [pn]

            prices_displayed_zip = list(zip(range(1, len(prices_displayed) + 1), prices_displayed))

            # store <choices> and <prices_displayed> on each player of each group
            # ----------------------------------------------------------------------------------------------------
            for j in range(1, Constants.num_players + 1):
                p = group.get_player_by_id(j)
                p.participant.vars['choices'] = choices
                p.participant.vars['prices_displayed'] = prices_displayed_zip

                # determine order of prices from <order>
                # ------------------------------------------------------------------------------------------------
                if Constants.order == 'random':
                    random.shuffle(p.participant.vars['prices_displayed'])
                elif Constants.order == 'ascending':
                    p.participant.vars['prices_displayed'] = sorted(p.participant.vars['prices_displayed'],
                                                                    key=lambda x: x[0])
                    p.participant.vars['choices'] = sorted(p.participant.vars['choices'],
                                                           key=lambda x: x[0])
                elif Constants.order == 'descending':
                    p.participant.vars['prices_displayed'] = sorted(p.participant.vars['prices_displayed'],
                                                                    key=lambda x: x[0], reverse=True)
                    p.participant.vars['choices'] = sorted(p.participant.vars['choices'],
                                                           key=lambda x: x[0], reverse=True)

                # generate data for game tree
                #  -----------------------------------------------------------------------------------------------
                GTindices = [a for a, b, c, d in choices]
                GTprices = [c for a, b, c, d in choices]
                GTxpoints = [(40+480/Constants.num_players) * j for j in range(0, len(GTprices))]

                GT = list(zip(GTindices, GTprices, GTxpoints))
                p.participant.vars['GameTree'] = GT

                combinations = [(a, b) for a in range(0, Constants.num_players) for b in range(0, Constants.num_players) if a + b == Constants.num_players - 1]
                GTpayoff1 = tuple([Constants.earnings_noaction] * Constants.num_players + [0])
                GTpayoffN = [tuple([Constants.earnings_success] * x + [0] + [Constants.earnings_noaction] * y ) for x, y in combinations][-1]
                GTpayoffN = [(str(GTpayoffN), GTxpoints[Constants.num_players-1])]
                GTpayoffs = [tuple([Constants.earnings_success] * x + [0] + [Constants.earnings_noaction] * y) for x, y in combinations][0:(len(combinations)-1)]

                p.participant.vars['GTpayoff1'] = GTpayoff1
                p.participant.vars['GTpayoffN'] = GTpayoffN
                p.participant.vars['GTpayoffs'] = GTpayoffs
                p.participant.vars['GTxpoints'] = GTxpoints

                # generate table for instructions
                #  -----------------------------------------------------------------------------------------------
                if Constants.cap == 0:
                    TABprices = [Constants.multiple ** i for i in range(0, Constants.num_instrprices)]
                    if Constants.dist_initprices == 'geometric':
                        TABprobabilities = [geom.pmf(j, Constants.p) * 100 for j in range(1, len(TABprices) + 1)]
                    elif Constants.dist_initprices == 'poisson':
                        TABprobabilities = [poisson.pmf(j, Constants.p) * 100 for j in range(0, len(TABprices))]
                    elif Constants.dist_initprices == 'binomial':
                        TABprobabilities = [binom.pmf(j, Constants.N, Constants.p) * 100 for j in range(0, len(TABprices))]
                    elif Constants.dist_initprices == 'uniform':
                        TABprobabilities = [randint.pmf(j, 0, len(TABprices)) * 100 for j in range(1, len(TABprices))] + [100 - sum([randint.pmf(j, 0, len(TABprices)) * 100 for j in range(1, len(TABprices))])]

                else:
                    TABprices = possibleinitprices
                    if Constants.dist_initprices == 'geometric':
                        TABprobabilities = [geom.pmf(j, Constants.p) * 100 for j in range(1, len(TABprices))] + [100 - sum([geom.pmf(j, Constants.p)*100 for j in range(1, len(TABprices))])]
                    elif Constants.dist_initprices == 'poisson':
                        TABprobabilities = [poisson.pmf(j, Constants.p) * 100 for j in range(0, len(TABprices)-1)] + [100 - sum([poisson.pmf(j, Constants.p) * 100 for j in range(0, len(TABprices)-1)])]
                    elif Constants.dist_initprices == 'binomial':
                        TABprobabilities = [binom.pmf(j, Constants.N, Constants.p) * 100 for j in range(0, len(TABprices))] + [100 - sum([binom.pmf(j, Constants.N, Constants.p) * 100 for j in range(0, len(TABprices))])]
                    elif Constants.dist_initprices == 'uniform':
                        TABprobabilities = [randint.pmf(j, 0, len(TABprices)) * 100 for j in range(1, len(TABprices))] + [100 - sum([randint.pmf(j, 0, len(TABprices)) * 100 for j in range(1, len(TABprices))])]

                p.participant.vars['TAB'] = list(zip(TABprices, TABprobabilities))

                # determine control questions
                # ------------------------------------------------------------------------------------------------
                cq_items_binary = [
                    'CQ1',
                    'CQ2',
                    'CQ3',
                    'CQ4',
                    'CQ5',
                    'CQ6',
                    'CQ7',
                    'CQ8',
                    'CQ9'
                ]

                cq_items_fouranswers = [
                    'CQ10',
                    'CQ11',
                    'CQ12',
                    'CQ13',
                    'CQ14',
                    'CQ15',
                    'CQ16'
                ]

                cq_questions_binary = [
                    # --- Questions from Moinas and Pouget (2016) ---
                    _('Is it possible to be first and be proposed to buy at a price of 100,000?'),
                    _('If you are proposed to buy at a price of 1, are you sure to be first?'),
                    _('If you are proposed to buy at a price of 100,000, are you sure to be second?'),
                    _('If you are proposed to buy at a price of 100, are you sure to be third?'),
                    _('If you are proposed to buy at a price of 1,000,000, are you sure to be third ?'),
                    _('If you accept to buy at 100, you will propose to resell at'),
                    _('If you are first, buy at 100, and resell at 1,000, your payoff in the game is'),
                    _('If you are first, buy at 100, and find nobody to resell to at 1,000, your payoff in the game is'),
                    _('If you refuse to buy, your payoff is'),
                ]

                cq_questions_fouranswers = [
                    # --- Questions from Janssen, Füllbrunn, and Weitzel (2018) ---
                    _('What is the probability of being third in line when you have not been offered a price yet?'),
                    _('What is the probability of the first price (P1) being 1,000?'),
                    _('What is the probability of the first price (P1) being 100,000?'),
                    _('If you are offered a price of 1,000, what is the probability of not being last in line?'),
                    _('What is your profit when you are first in line and buy but the person next in line does not buy?'),
                    _('What is your profit if you are second in line and the person before and after you in line buy, but you do not buy?'),
                    _('What is your profit when you are first in line, you decide to buy and the trader next in line also buys?')
                ]

                cq_answers0_binary = [
                                  _('Yes')
                              ] * 5 + [
                                  '1000',
                                  '10 ' + str(Constants.exp_currency),
                                  '0 ' + str(Constants.exp_currency),
                                  '1 ' + str(Constants.exp_currency)
                              ]
                cq_answers1_binary = [
                                  _('No')
                              ] * 5 + [
                                  '1100',
                                  '900 ' + str(Constants.exp_currency),
                                  '10 ' + str(Constants.exp_currency),
                                  '0 ' + str(Constants.exp_currency)
                              ]

                cq_answers0_fouranswers = [
                    '100%',
                    '0%',
                    '0%',
                    '70%',
                    '0 ' + str(Constants.exp_currency),
                    '0 ' + str(Constants.exp_currency),
                    '0 ' + str(Constants.exp_currency)
                ]
                cq_answers1_fouranswers = [
                    '75%',
                    '15%',
                    '15%',
                    '40%',
                    '1 ' + str(Constants.exp_currency),
                    '1 ' + str(Constants.exp_currency),
                    '1 ' + str(Constants.exp_currency)
                ]
                cq_answers2_fouranswers = [
                    '10%',
                    '20%',
                    '20%',
                    '10%',
                    '3 ' + str(Constants.exp_currency),
                    '3 ' + str(Constants.exp_currency),
                    '3 ' + str(Constants.exp_currency)
                ]
                cq_answers3_fouranswers = [
                    '33.33%',
                    '30%',
                    '30%',
                    '30%',
                    '10 ' + str(Constants.exp_currency),
                    '10 ' + str(Constants.exp_currency),
                    '10 ' + str(Constants.exp_currency)
                ]

                cq_correct_binary = [
                    1,
                    0,
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0
                ]

                cq_correct_fouranswers = [
                    3,
                    2,
                    0,
                    0,
                    0,
                    2,
                    3
                ]

                controlquestions_set1 = [k-1 for k in Constants.controlquestions_set1]
                cq_ids_binary = [k for k in range(1, len(controlquestions_set1)+1)]
                cq_items_binary = [cq_ids_binary[k] for k in controlquestions_set1]
                cq_questions_binary = [cq_questions_binary[k] for k in controlquestions_set1]
                cq_answers0_binary = [cq_answers0_binary[k] for k in controlquestions_set1]
                cq_answers1_binary = [cq_answers1_binary[k] for k in controlquestions_set1]
                cq_correct_binary = [cq_correct_binary[k] for k in controlquestions_set1]
                cq = list(zip(cq_items_binary, cq_ids_binary, cq_questions_binary, cq_answers0_binary, cq_answers1_binary, cq_correct_binary))

                controlquestions_set2 = [k-10 for k in Constants.controlquestions_set2]
                cq_ids_fouranswers = [k for k in range(len(controlquestions_set1) + 1, len(controlquestions_set1) + 1 + len(controlquestions_set2))]
                cq_questions_fouranswers = [cq_questions_fouranswers[k] for k in controlquestions_set2]
                cq_answers0_fouranswers = [cq_answers0_fouranswers[k] for k in controlquestions_set2]
                cq_answers1_fouranswers = [cq_answers1_fouranswers[k] for k in controlquestions_set2]
                cq_answers2_fouranswers = [cq_answers2_fouranswers[k] for k in controlquestions_set2]
                cq_answers3_fouranswers = [cq_answers3_fouranswers[k] for k in controlquestions_set2]
                cq_correct_fouranswers = [cq_correct_fouranswers[k] for k in controlquestions_set2]
                cq1 = list(zip(cq_items_fouranswers, cq_ids_fouranswers, cq_questions_fouranswers, cq_answers0_fouranswers, cq_answers1_fouranswers, cq_answers2_fouranswers, cq_answers3_fouranswers, cq_correct_fouranswers))

                p.participant.vars['cq'] = cq
                p.participant.vars['cq1'] = cq1

                cq_form_fields = ['cq_' + str(k) for k in range(1, len(cq)+1)] + ['cq_' + str(k) for k in range(len(cq) + 1, len(cq) + 1 + len(cq1))]
                p.participant.vars['cq_form_fields'] = cq_form_fields


#--- Class GROUP -------------------------------------------------------------------------------------------------------

class Group(BaseGroup):

    # determine results
    # ----------------------------------------------------------------------------------------------------
    def set_results(self):

        # unzip <choices> and <prices> and determine points of intersections
        # ----------------------------------------------------------------------------------------------------
        choices = self.get_player_by_id(1).participant.vars['choices']
        prices = self.get_player_by_id(1).participant.vars['prices_displayed']

        w, x, y, z = zip(*choices)
        choices_unzipped = sorted(list(y))

        a, b = zip(*prices)
        prices_unzipped = sorted(list(b))

        price_choice_match = [prices_unzipped.index(choices_unzipped[k]) + 1 for k in range(0, Constants.num_players)]

        for p in self.get_players():

            p.participant.vars['price_choice_match'] = sorted(price_choice_match)
            price_choice_match = sorted(price_choice_match)

            # determine relevant realisations
            # ----------------------------------------------------------------------------------------------------
            if Constants.one_choice_per_page and Constants.strategy_method:

                p.others = [(getattr(j, 'id_in_group'), k, j.participant.vars['buys'][k - 1]) for k in
                            range(1, Constants.num_prices + 1) for j in p.in_round(k).get_others_in_group()]
                p.others1 = [(a, b, c) for a, b, c in p.others if b in price_choice_match]
                p.participant.vars['others'] = p.others
                p.participant.vars['others1'] = p.others1

                if Constants.order == 'descending':
                    p.participant.vars['buys'] = p.participant.vars['buys'][::-1]

                if Constants.strategy_method:
                    if p.id_in_group == 1:
                        if Constants.order == 'ascending':
                            p.relevant_realisations = [p.participant.vars['buys'][price_choice_match[0]-1]] + [c for a, b, c in p.others1 if a == 2 and b == price_choice_match[1]]
                        elif Constants.order == 'descending':
                            p.relevant_realisations = [p.participant.vars['buys'][price_choice_match[0]-1]] + [c for a, b, c in p.others1 if a == Constants.num_players-1 and b == price_choice_match[0]]
                    elif p.id_in_group == Constants.num_players:
                        p.relevant_realisations = [c for a, b, c in p.others1 if a == b - price_choice_match[0] + 1] + [p.participant.vars['buys'][price_choice_match[Constants.num_players-1]-1]]
                    else:
                        p.relevant_realisations_below = [c for a, b, c in p.others1 if a == b - price_choice_match[0] + 1 and a < getattr(p, 'id_in_group')]
                        p.relevant_realisations_above = [c for a, b, c in p.others1 if a == b - price_choice_match[0] + 1 and a > getattr(p, 'id_in_group')]
                        p.relevant_realisations = p.relevant_realisations_below + [p.participant.vars['buys'][price_choice_match[getattr(p, 'id_in_group')-1]-1]] + p.relevant_realisations_above

                else:
                    if p.id_in_group == 1:
                        p.relevant_realisations = [int(getattr(p, 'buy_' + str(p.id_in_group)))] + [int(getattr(j, 'buy_' + str(j.id_in_group))) for j in p.get_others_in_group() if getattr(j, 'id_in_group') == 2]
                    elif p.id_in_group == Constants.num_players:
                        p.relevant_realisations = [int(getattr(j, 'buy_' + str(j.id_in_group))) for j in p.get_others_in_group()] + [int(getattr(p, 'buy_' + str(p.id_in_group)))]
                    else:
                        p.relevant_realisations = [int(getattr(j, 'buy_' + str(j.id_in_group))) for j in p.get_others_in_group() if getattr(j, 'id_in_group') < p.id_in_group] + [int(getattr(p, 'buy_' + str(p.id_in_group)))] + [int(getattr(j, 'buy_' + str(j.id_in_group))) for j in p.get_others_in_group() if getattr(j, 'id_in_group') > p.id_in_group]

            else:
                if p.id_in_group == 1:
                    p.relevant_realisations = [int(getattr(j, 'buy_' + str(price_choice_match[0]+getattr(j, 'id_in_group')-1))) for j in p.get_others_in_group() if getattr(j, 'id_in_group') == 2]
                    p.relevant_realisations = [int(getattr(p, 'buy_' + str(price_choice_match[0]+p.id_in_group-1)))] + p.relevant_realisations
                elif p.id_in_group == Constants.num_players:
                    p.relevant_realisations = [int(getattr(j, 'buy_' + str(price_choice_match[0]+getattr(j, 'id_in_group')-1))) for j in p.get_others_in_group()]
                    p.relevant_realisations = p.relevant_realisations + [int(getattr(p, 'buy_' + str(price_choice_match[0] + p.id_in_group - 1)))]
                else:
                    p.relevant_realisations_below = [
                        int(getattr(j, 'buy_' + str(price_choice_match[0] + getattr(j, 'id_in_group') - 1))) for j in
                        p.get_others_in_group() if getattr(j, 'id_in_group') < p.id_in_group]
                    p.relevant_realisations_above = [
                        int(getattr(j, 'buy_' + str(price_choice_match[0] + getattr(j, 'id_in_group') - 1))) for j in
                        p.get_others_in_group() if getattr(j, 'id_in_group') > p.id_in_group]
                    p.relevant_realisations = p.relevant_realisations_below + [int(getattr(p, 'buy_' + str(price_choice_match[0] + p.id_in_group - 1)))] + p.relevant_realisations_above

            p.participant.vars['relevant_realisations'] = p.relevant_realisations

            # determine earnings
            # ----------------------------------------------------------------------------------------------------
            p.earnings = 0

            if p.id_in_group == 1:
                if p.relevant_realisations[0] == 0:
                    p.earnings = Constants.earnings_noaction
                else:
                    p.earnings = Constants.earnings_noaction - Constants.earnings_noaction * p.relevant_realisations[0] + Constants.earnings_success * p.relevant_realisations[1]
            elif p.id_in_group == Constants.num_players:
                if 0 in p.relevant_realisations[0:p.id_in_group]:
                    p.earnings = Constants.earnings_noaction
                else:
                    p.earnings = Constants.earnings_noaction - Constants.earnings_noaction * p.relevant_realisations[Constants.num_players-1]
            else:
                if 0 in p.relevant_realisations[0:p.id_in_group]:
                    p.earnings = Constants.earnings_noaction
                else:
                    p.earnings = Constants.earnings_noaction - Constants.earnings_noaction * p.relevant_realisations[p.id_in_group - 1] + Constants.earnings_success * p.relevant_realisations[p.id_in_group]

            # set payoffs
            # ----------------------------------------------------------------------------------------------------
            p.payoff = p.earnings



#--- Class PLAYER ------------------------------------------------------------------------------------------------------
class Player(BasePlayer):

    earnings = models.FloatField()
    max_buy = models.IntegerField()
    repetition = models.IntegerField()

    # write <buy_n> decisions in list <buy>
    # ----------------------------------------------------------------------------------------------------
    def set_decision(self):

        if Constants.one_choice_per_page:
            page_repetition = [
                int(Constants.num_prices * math.ceil(float(j) / Constants.num_prices) / Constants.num_prices) - 1 for j
                in
                range(1, Constants.num_rounds + 1)]
            page = self.group.subsession.round_number - page_repetition[self.group.subsession.round_number - 1] * Constants.num_prices

            repetition = int(Constants.num_prices * math.ceil(float(self.round_number)/Constants.num_prices)) / Constants.num_prices

            if Constants.strategy_method:
                form_fields = [self.participant.vars['form_fields'][page - 1]]

                if Constants.order == 'ascending':
                    # buys = [int(getattr(j, 'buy_' + str(j.group.subsession.round_number))) for j in self.in_all_rounds() if getattr(j, 'round_number') <= Constants.num_players]
                    buys = [int(getattr(j, 'buy_' + str(j.group.subsession.round_number - page_repetition[j.group.subsession.round_number - 1] * Constants.num_prices))) for j in self.in_all_rounds() if getattr(j, 'round_number') in range(int(Constants.num_prices * (repetition - 1) + 1), int(Constants.num_prices * repetition + 1))]
                elif Constants.order == 'descending':
                    buys = [int(getattr(j, 'buy_' + str(self.participant.vars['prices_displayed'][getattr(j, 'round_number')-1][0]))) for j in self.in_all_rounds()]

            else:
                form_fields = [self.participant.vars['form_fields'][self.id_in_group - 1]]
                buys = [0]*(self.id_in_group-1) + [int(getattr(j, 'buy_' + str(j.id_in_group))) for j in self.in_all_rounds()] + [0]*(Constants.num_players - self.id_in_group)

            self.participant.vars['buys'] = buys

        else:
            form_fields = self.participant.vars['form_fields']

        buy = [getattr(self, field) for field in form_fields]
        self.participant.vars['buy'] = buy

    def set_max_buy(self):
        if Constants.one_choice_per_page:
            if Constants.order == 'ascending':
                buys = [str(j) for j in self.participant.vars['buys']]
            else:
                buys = list(reversed([str(j) for j in self.participant.vars['buys']]))
        else:
            buys = self.participant.vars['buy']
        if '1' in buys:
            self.max_buy = max([j for j in range(1, len(buys)+1) if buys[j-1] == '1'])
        else:
            self.max_buy = 0

    def set_buy_price(self):
        page_repetition = [
            int(Constants.num_prices * math.ceil(float(j) / Constants.num_prices) / Constants.num_prices) - 1 for j
            in
            range(1, Constants.num_rounds + 1)]
        page = self.group.subsession.round_number - page_repetition[self.group.subsession.round_number - 1] * Constants.num_prices
        if Constants.one_choice_per_page:
            setattr(self, 'buy_' + str(self.participant.vars['prices_displayed'][page-1][0]) + '_price', self.participant.vars['prices_displayed'][page-1][1])
        else:
            if Constants.order == 'ascending':
                [setattr(self, 'buy_' + str(j) + '_price', self.participant.vars['prices_displayed'][j-1][1]) for j in list(zip(*self.participant.vars['prices_displayed']))[0]]
            else:
                [setattr(self, 'buy_' + str(j) + '_price', list(reversed(self.participant.vars['prices_displayed']))[j-1][1]) for j in list(zip(*self.participant.vars['prices_displayed']))[0]]

    def set_repetition(self):
        page_repetition = [
            int(Constants.num_prices * math.ceil(float(j) / Constants.num_prices) / Constants.num_prices) - 1 for j
            in
            range(1, Constants.num_rounds + 1)]
        self.repetition = page_repetition[self.round_number - 1] + 1


# ::: set model fields for each choice dynamically (added to class player)
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: #
for i in range(1, Constants.num_prices + 1):
    Player.add_to_class(
        'buy_%i' % i,
            models.CharField()
    )
    Player.add_to_class(
        'buy_%i_price' % i,
            models.CharField()
    )
for i in range(1, len(Constants.controlquestions_set1) + 1):
    Player.add_to_class(
        'cq_%i' % i,
            models.CharField()
    )
for i in range(len(Constants.controlquestions_set1) + 1, len(Constants.controlquestions_set1) + 1 + len(Constants.controlquestions_set2)):
    Player.add_to_class(
        'cq_%i' % i,
            models.CharField()
    )
