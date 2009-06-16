from random import shuffle
from rank import Ranks, rank

known_pl = {}

class Action:
    Call = 0
    Check = 1
    Bet = 2
    Raise = 3
    Fold = 4

class Round:
    PreFlop = 0
    Flop = 1
    Turn = 2
    River = 3
    Showdown = 4
    Victory = 5   


class Game:
    def __init__(self, ante=2, minbet=5):
        self.plst = []
        self.deck = Deck()
        self.community = []

        self.ante = ante
        self.minbet = minbet

        self.round = Round.PreFlop
        self.current_pl = None
        self.end_pl = None

        self.needs_match = False
        self.match_amt = 0
        self.contributions = {}
        self.potsize = 0

        self.actions = []

        self.winners = ()
        
    def add_pl(self, nm):
        if nm not in known_pl:
            known_pl[nm] = P(nm)
        if nm not in self.plst:
            self.plst.append(known_pl[nm])
            self.contributions[nm] = 0
    
    def deal(self):
        if self.round == Round.Flop:
            self.community = self.deck.flop()
            return self.community
        elif self.round == Round.Turn:
            turn = self.deck.turn()
            self.community.append(turn)
            return self.community
        elif self.round == Round.River:
            river = self.deck.river()
            self.community.append(river)
            return self.community
        else:
            ## pre-flop
            shuffle(self.plst)
            for pl in self.plst:
                pl.amt -= self.ante
            self.potsize = self.ante * len(self.plst)

            for pl in self.plst:
                pl.sidepot = self.potsize
                pl.hnd = self.deck.deal()
            
            self.current_pl = 0
            self.end_pl = len(self.plst) - 1

            return [(pl.name, pl.hnd) for pl in self.plst]

    def maybe_end(self):
        return (self.plst == 0 or
                self.current_pl == self.end_pl and self.no_matches_needed())
    
    def no_matches_needed(self):
        len([p for p in self.plst if p.allin or not p.match_amt]) == len(self.plst)

    def next_pl(self):
        self.current_pl += 1
        if self.current_pl == self.end_pl and self.no_matches_needed():
            self.current_pl = 0
            self.round += 1

        while self.plst[current_pl].allin:
            self.current_pl += 1
            if current_pl == len(self.plst) and not self.needs_match:
                self.current_pl = 0
                self.round += 1

    def avail_actions(self):
        if not self.plst[self.current_pl].match_amt:
            self.actions = (Action.Fold, Action.Check, Action.Bet)
        else:
            self.actions = (Action.Fold, Action.Call, Action.Raise)

            
    def balance_pots(self):
        """This occurs at the end of each round, with the exception of 
        Round.Pre-Flop which is balanced by default.
        For each remaining pl, we consider the contribution of that
        pl with respect to everyone else in order to determine the 
        maximum possible amount he/she will receive should they be 
        successsful.
        Player.contrib refers to contribution _this_ round and is reset
        back to 0 after all is said and done.
        """
        for pl in self.plst:
            if pl.allin:
                pl.sidepot += sum([min(pl.allin_diff, contrib)
                                   for (p, contrib) in self.contributions 
                                   if p is not pl])
            else:
                pl.sidepot += self.potsize
                
                    
        for pl in self.plst:
            self.contributions[pl.name] = 0
            if pl.allin:
                pl.allin_this_cycle = False

            
    def fold_pl(self, nm):
        i = self.plst.index(nm)
        pl = self.plst[i]
        pl.reset()
        self.plst.remove(nm)

        self.next_pl()
        self.avail_actions()
        return self.current_pl, self.actions

    def check_pl(self, nm):
        self.next_pl()
        self.avail_actions()
        return self.current_pl, self.actions

    def call_pl(self, nm):
        i = self.plst.index(nm)
        pl = self.plst[i]
        
        allin = False
        
        if pl.amt < pl.match_amt:
            pl.allin = True
            pl.allin_this_round = True
            pl.allin_diff = pl.amt
            self.contributions[pl.name] = pl.allin_diff

            pl.amt = 0
            pl.match_amt = 0
            allin = True

        else:
            self.contributions[pl.name] += self.match
            pl.amt -= self.match
            pl.match_amt = 0
        
        self.next_pl()
        self.avail_actions()

        return allin, amt, self.current_pl, self.actions

    def allin_pl(self, nm):
        i = self.plst.index(nm)
        pl = self.plst[i]
        pl.allin = True
        pl.allin_this_round = True
        pl.allin_diff = pl.amt
        self.contributions[pl.name] = pl.allin_diff
        self.potsize += pl.allin_diff

    def bet_pl(self, nm, amt):
        i = self.plst.indexOf(nm)
        pl = self.plst[i]

        if amt >= pl.amt:
            amt = pl.amt
            pl.allin = True
            pl.allin_this_round = True

        self.minbet = amt * 2
        self.end_pl = i
        self.potsize += amt
        pl.amt -= amt
        
        for p in self.plst:
            if p.name != nm:
                p.match_amt += amt
                self.needs_match
        
        self.current_pl = self.next_pl()
        avail_actions = self.avail_actions()
        action_value = amt
        return (Action.Bet, action_value, next_pl, avail_actions)

    def raise_pl(self, nm, amt):
        act, val, next_pl, avail_actions = self.bet_pl(nm, amt)
        return (Action.Raise, val, next_pl, avail_actions)

    def rate_hands(self):
        rate_hands(self.plst, self.community)



class P():
    def __init__(self, name, amt=1000, hnd=()):
        self.name = name
        self.amt = amt
        self.hnd = hnd

        self.bet_amt = 0
        self.match_amt = 0

        self.sidepot = 0
        self.contrib = 0

        self.allin = False
        self.allin_this_round = False
        self.allin_diff = 0


    def up_sidepot(self, val):
        if self.allin and self.allin_this_round:
            self.sidepot += min(self.allin_difference, val)
        else:
            pass

    def __repr__(self):
        return self.name + " -- " + str(self.amt)

    def __cmp__(self, other):
        return cmp(self.name, other)

    def reset(self):
        self.hnd = ()
        self.bet_amt = 0
        self.match_amt = 0
        self.sidepot = 0
        self.allin = False


class Deck():
    def __init__(self):
        S = "HDCS"
        F = "23456789TJQKA"
        self.deck = [f+s for f in F for s in S]
        shuffle(self.deck)

    def deal(self):
        a,b = self.deck.pop(), self.deck.pop()
        return a,b

    def flop(self):
        self.deck.pop()
        return [ self.deck.pop(), self.deck.pop(), self.deck.pop()]

    def turn(self):
        self.deck.pop()
        return self.deck.pop()

    def river(self):
        self.deck.pop()
        return self.deck.pop()
        

def register(nm):
    if nm in known_pl:
        return "%s already registered." % nm
    else:
        pl = P(nm)
        known_pl[nm] = pl
        return "%s successfully registered" % nm
    
def status(nm):
    if nm in known_pl:
        return "%s has %s yen remaining" % (nm, known_pl[nm].amt)
    else:
        return "you need to register before you have a status"

