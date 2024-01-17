import pickle
import eval7
import itertools

def calculate_strength( my_cards, iters):
    deck = eval7.Deck()
    my_cards = [eval7.Card(card) for card in my_cards]
    for card in my_cards:
        deck.cards.remove(card)
    wins_w_auction = 0
    wins_wo_auction = 0

    for i in range(iters):
        deck.shuffle()
        opp = 3
        community = 5
        draw = deck.peek(opp+community)
        opp_cards = draw[:opp]
        community_cards = draw[opp:]

        our_hand = my_cards + community_cards
        opp_hand = opp_cards + community_cards

        our_hand_val = eval7.evaluate(our_hand)
        opp_hand_val = eval7.evaluate(opp_hand)

        if our_hand_val > opp_hand_val:
            # We won the round
            wins_wo_auction += 2
        if our_hand_val == opp_hand_val:
            # We tied the round
            wins_wo_auction += 1
        else:
            # We lost the round
            wins_wo_auction

    for i in range(iters):
        deck.shuffle()
        opp = 2
        community = 5
        auction = 1
        draw = deck.peek(opp+community+auction)
        opp_cards = draw[:opp]
        community_cards = draw[opp: opp + community]
        auction_card = draw[opp+community:]
        our_hand = my_cards + auction_card + community_cards
        opp_hand = opp_cards + community_cards

        our_hand_val = eval7.evaluate(our_hand)
        opp_hand_val = eval7.evaluate(opp_hand)

        if our_hand_val > opp_hand_val:
            # We won the round
            wins_w_auction += 2
        elif our_hand_val == opp_hand_val:
            # we tied the round
            wins_w_auction += 1
        else:
            #We tied the round
            wins_w_auction += 0
        
        strength_w_auction = wins_w_auction / (2* iters)
        strength_wo_auction = wins_wo_auction/ (2* iters)

    return strength_w_auction, strength_wo_auction

if __name__ == "__main__":

    ranks = "AKQJT98765432"
    iters = 1000

    offrank_holes = list(itertools.combinations(ranks, 2))
   # [0,1,2] [a,b,c] ---> [(0,a), (1,b), (2,c)]
    paired_holes = list(zip(ranks,ranks))

    suited_off_rank_str = [hole_card[0] + hole_card[1] + 'o' for hole_card in offrank_holes] #AKo, AKs, KAs
    off_suit_off_rank_str = [hole_card[0] + hole_card[1] + 's' for hole_card in offrank_holes]
    paired_cards_str = [hole_card[0] +  hole_card[1] + 'o' for hole_card in paired_holes]

    suited_off_rank = [[hole_card[0] + 'c', hole_card[1] + 'c'] for hole_card in offrank_holes]
    off_suit_off_rank = [[hole_card[0] + 'c', hole_card[1] + 's'] for hole_card in offrank_holes]
    paired_cards = [[hole_card[0] + 'c', hole_card[1] + 's'] for hole_card in paired_holes]

    suited_off_rank_strength = [calculate_strength(hole_cards, iters) for hole_cards in suited_off_rank]
    off_suit_off_rank_strength = [calculate_strength(hole_cards, iters) for hole_cards in off_suit_off_rank]
    paired_cards_strength = [calculate_strength(hole_cards, iters) for hole_cards in paired_cards]

    all_holes = suited_off_rank_str + off_suit_off_rank_str + paired_cards_str
    all_strengths = suited_off_rank_strength + off_suit_off_rank_strength + paired_cards_strength

    hand_to_strength = dict()

    for cards, strength in zip(all_holes, all_strengths):

        #print("strength:", strength)
        hand_to_strength[cards] = strength
    
    with open("hand_strengths", "wb") as file:
        pickle.dump(hand_to_strength, file)





