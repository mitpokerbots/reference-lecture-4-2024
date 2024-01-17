'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, BidAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import random
import eval7
import pickle
import time


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        self.opp_holes = []
        self.opp_bids = []  

        prev_time = time.time()
        with open("hand_strengths", "rb") as file:
            self.starting_strengths = pickle.load(file)
        print("pickle load:", time.time() - prev_time)
        
        rank_to_numeric = dict()

        for i in range(2,10):
            rank_to_numeric[str(i)] = i

        for num, rank in enumerate("TJQKA"): #[(0,T), (1,J), (2,Q) ...]
            rank_to_numeric[rank] = num + 10

        self.rank_to_numeric = rank_to_numeric

        self.num_showdowns = 0
        self.opp_avg_strength = 0.5


    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        
        self.early_game = (round_num < NUM_ROUNDS // 4)

        if round_num < 5:
            print("game clock:", game_clock)


        self.strong_hole = False

        if not self.early_game:

            card_strength = self.hand_to_strength(my_cards)
            card_strength = (card_strength[0] + card_strength[1])/2

            if card_strength > self.opp_avg_strength:
                self.strong_hole = True
        
        if round_num == NUM_ROUNDS:
            print("game clock:", game_clock)


    def hand_to_strength(self, my_cards): #AcKs, Jc9s

        card_1 = my_cards[0]
        card_2 = my_cards[1]

        rank_1, suit_1 = card_1
        rank_2, suit_2 = card_2

        num_1 = self.rank_to_numeric[rank_1]
        num_2 = self.rank_to_numeric[rank_2]

        suited = 'o'
        if suit_1 == suit_2:
            suited = "s"

        if num_1 >= num_2:
            key = rank_1 + rank_2 + suited
        else:
            key = rank_2 + rank_1 + suited

        return self.starting_strengths[key]


        #KA, AK

        

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed

        opp_bid = previous_state.bids[1-active]

        
        if len(opp_cards) >= 2:
            opp_cur_strength = self.hand_to_strength(opp_cards[:2])
            opp_cur_strength = (opp_cur_strength[0] + opp_cur_strength[1])/2
            self.opp_avg_strength = (self.opp_avg_strength *self.num_showdowns + opp_cur_strength) /(self.num_showdowns + 1)
            self.num_showdowns += 1
            # self.opp_holes.append(opp_cards[:2])
            self.opp_bids.append(opp_bid)


    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        # May be useful, but you may choose to not use.
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        my_bid = round_state.bids[active]  # How much you bid previously (available only after auction)
        opp_bid = round_state.bids[1-active]  # How much opponent bid previously (available only after auction)
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        if RaiseAction in legal_actions:
           min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
           min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
           max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        
        if self.early_game: # loose passive
            if RaiseAction in legal_actions and street == 0:
                if 2 * BIG_BLIND == min_raise:
                    return RaiseAction(min_raise)    
            if BidAction in legal_actions:
                return BidAction(int(random.random()*my_stack))
            if CheckAction in legal_actions:
                return CheckAction()
            return CallAction()
        
        else: # tight aggressive

            if self.strong_hole: # tight range
                if BidAction in legal_actions:
                    idx = random.randint(1, len(self.opp_bids))
                    bid = self.opp_bids[idx] + 1
                    bid = min(bid, my_stack)
                    return BidAction(bid)
                if RaiseAction in legal_actions:
                    raise_frac = 0.2 + random.random() * 0.2
                    raise_amount = int(min_raise + (max_raise - min_raise) * raise_frac)
                    return RaiseAction(raise_amount)
                if CallAction in legal_actions:
                    return CallAction()

            if CheckAction in legal_actions:
                return CheckAction()
            if BidAction in legal_actions:
                return BidAction(0)
            return FoldAction()



        


if __name__ == '__main__':
    run_bot(Player(), parse_args())