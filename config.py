from otree.api import Currency as c
from otree.constants import BaseConstants
from django.utils.translation import ugettext as _


# --- Class CONSTANTS --------------------------------------------------------------------------------------------------

class Constants(BaseConstants):

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Game-specific Settings --- #
    # ---------------------------------------------------------------------------------------------------------------- #

    # number of players per group
    # this is also the number of relevant decisions for subjects' payoffs
    num_players = 3

    # number of different prices displayed
    # (Warning: <num_prices> must be at least as large as <num_players>!)
    num_prices = 3

    # number of repetitions of the game
    num_repetitions = 1

    # group subjects randomly (if <num_players > 1>)
    # if <random_grouping = False>, then subjects will be assigned to groups according to the time
    # they enter the experiment
    random_grouping = False

    # prices will be a multiple of <multiple>
    multiple = 10

    # distribution for initial prices
    # set the distribution from which to draw x for the initial price of <multiple> to the power of x:
    # 'geometric', 'Poisson', 'binomial', or 'uniform'
    dist_initprices = 'geometric'

    # parameter p for geometric distribution and binomial distribution, and lambda for Poisson distribution,
    # respectively;
    p = 0.5

    # parameter n for binomial distribution and uniform distribution, respectively
    n = 4

    # cap on the initial price
    # if <cap = 0>, then there is no cap on the initial price
    # if <cap > 0>, then the cap is set at <cap>
    cap = 10000

    # earnings if no action is realised, i.e. the player does not buy the asset
    earnings_noaction = 1

    # earnings if a player succeeds in reselling the asset; by default this variable is set to <multiple>
    earnings_success = multiple

    # Set <strategy_method = True> to use the strategy method, i.e. to elicit subjects' choices for each
    # possible price; if <strategy_method = False>, only one price is offered to each player - note that this
    # requires <one_choice_per_page = True> (below)!
    strategy_method = True

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Overall Settings and Appearance --- #
    # ---------------------------------------------------------------------------------------------------------------- #

    # order of choices
    # if <order = 'ascending'>, then the choices will appear in ascending order
    # if <order = 'descending'>, then the choices will appear in descending order
    # if <order = 'random'>, then the choices will appear in random order
    order = 'ascending'

    # show each lottery pair on a separate page
    # if <one_choice_per_page = True>, each single binary choice between lottery "A" and "B" is shown on a separate page
    # if <one_choice_per_page = False>, all <num_choices> choices are displayed in a table on one page
    one_choice_per_page = False

    if strategy_method == False:
        one_choice_per_page = True

    # show choices as buttons instead of radio inputs if <one_choice_per_page = True>
    buttons = True

    # enforce consistency, i.e. only allow for a single switching point
    # if <enforce_consistency = True>, all "false" announcements above a selected "false" announcement
    # are automatically selected; similarly, all "true" announcements below a selected "true announcement
    # are automatically checked, implying consistent choices;
    # note that <enforce_consistency> is only implemented if <one_choice_per_page = False> and <random_order = False>
    enforce_consistency = False

    # show instructions page
    # if <instructions = True>, a separate template "Instructions.html" is rendered prior to the task
    # if <instructions = False>, the task starts immediately (e.g. in case of printed instructions)
    instructions = True

    # number of possible initial prices shown in price/probability-table in the instructions if <cap = 0>;
    # e.g. if <num_instrprices = 2>, then probabilities for possible initial prices 1, 10, and 100 are
    # shown in the instructions (if <multiple = 10>), i.e. <multiple> to the power of 0, 1, and 2
    num_instrprices = 6

    # show graphical decision tree in the instructions
    # <graph = 'none'> for no graph
    # <graph = 'horizontal'> for price sequence in horizontal order (only recommended for <num_prices> <= 4)
    # <graph = 'vertical'> for price sequence in vertical order
    graph_instructions = 'horizontal'

    # show control questions page
    # if <controlquestions = True>, a separate template "ControlQuestions.html" is rendered
    # after the Instructions (if <instructions = True>) and prior to the task
    controlquestions = False

    # select control questions
    # each control question has a number (1 to 16); write which ones you want to include;
    # e.g. <controlquestions_binary = [1, 2, 3]> includes only the first 3 binary control questions and no
    # control questions with four answers, while <controlquestions_binary = []> and
    # <controlquestions_fouranswers = [10, 11, 12] includes no binary control questions but control questions 10,
    # 11, and 12 with four answers;
    # questions 1 to 9 are binary control questions from Moinas and Pouget (2016),
    # questions 10 to 16 are control questions with four answers, adapted from Janssen, Füllbrunn, and Weitzel (2018)
    controlquestions_set1 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    controlquestions_set2 = [10, 11, 12, 13, 14, 15, 16]

    # require correct answers in control questions
    controlquestions_correct = False

    # show results page summarizing the game's outcome including payoff information
    # if <results = True>, a separate page containing all relevant information is displayed after finishing the task
    # if <results = False>, the template "Results.html" will not be rendered
    results = True

    # show graphical decision tree in the results
    # <graph = 'none'> for no graph
    # <graph = 'horizontal'> for price sequence in horizontal order (only recommended for <num_prices> <= 4)
    # <graph = 'vertical'> for price sequence in vertical order
    graph_results = 'horizontal'

    # set the experimental currency
    exp_currency = 'ECU'

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- oTree Settings etc. (Don't Modify) --- #
    # ---------------------------------------------------------------------------------------------------------------- #

    name_in_url = 'bg'
    players_per_group = None if num_players == 1 else num_players
    num_rounds = num_prices * num_repetitions if one_choice_per_page and strategy_method else num_repetitions

    tooltip_price = _("For each price you have to decide whether to buy the asset.")
    tooltip_payoff = _("Payoffs if this point is reached (depending on players' 'buy'- and 'dont't-buy'-decisions). "
                       "The first number refers to Player 1's payoff, the second "
                       "number refers to Player 2's payoff, and so forth.")

