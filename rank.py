# Assigns a numeric value to hand ranks
class Ranks:
	HighCard, Pair, TwoPair, ThreeKind, Straight, \
	Flush, FullHouse, FourKind, StraightFlush = range(9)
	
def rank(players, community):
	"""
	<George>	players is a list of objects
	<George>	players[0].hand is first players hand
	<George>	hards are Card-Card
	<George>	community is 5 community cards
	<George>	(3C,5D,3S,AH,AD) 5-tuple
	<George>	return a tuple
	<George>	(result, winner[s])
	<George>	result is an element of {"Tie", "Win"}
	<George>	winners is a list, always
	<George>	so even if theres a clear member its be ("Win", [player[3]]) or whatever
	"""
	# Structure that holds the player ranking results
	class RankResults():
		def __init__(self):
			self.winner = [] # (WIN, player_name) or (TIE, [player1, player2, ...]) 
			self.bestHands = [] # [(pl_name, bestHand, handRank), ... ]
			self.kicker = [] # If player hands' ranks tie but lose
					# by kicker, this will have one card
			
	
		def __repr__(self):
			if self.winner[0] == "Win":
				winPlayerIndex = [player[0] for player in \
							self.bestHands].index(self.winner[1])
			else:
				winPlayerIndex = [player[0] for player in \
							self.bestHands].index(self.winner[1][0])
			winningRank = self.bestHands[winPlayerIndex][2]
			
			# Returns Win/Tie, player name, and winning rank
	        	return str(self.winner) + " rank = " + str(winningRank) + " kicker = " \
				+ str(self.kicker)

	### Rank function definition starts here

	# Dictionary for converting card strings to numbers
	cardNums = {"A":14, "K":13, "Q":12, "J":11, "10":10, "9":9, "8":8, \
			"7":7, "6":6, "5":5, "4":4, "3":3, "2":2}

	# scan each player's hand and return their best hand
	winHands = []
	result = RankResults()
	for player in players:
		cards = player.hand + community
		(playerHand, handStrength) = best_hand(cards)
		if len(winHands) != 0:
			# compare current player's hand to other
			# players in the best hands list
			if handStrength > winHands[0][2]:
				winHands = [(player.name, playerHand, handStrength)]
			elif handStrength == winHands[0][2]:
				winHands.append( (player.name, playerHand, handStrength) )
		# if first player in list, 
		# create a new list with this player's hand			
		else: 
			winHands = [(player.name, playerHand, handStrength)]
					

		# insert each player's hand into results
		result.bestHands.append( (player.name, playerHand, handStrength) )

	# compare results. 
	# winHands = ((name, handStrength, hand), ...)
	if len(winHands) == 1:
		result.winner = ("Win", winHands[0][0])
	else:
		# tuple the i cards of every player to facilitate
		# comparison
		zippedHands = zip(*[winner[1] for winner in winHands])
		
		# Compare top 5 cards of tied winners
		for i in range(5):
			topCards = zippedHands[i]
			largestCard = max(topCards) # find largest card 
			isPlayerRemoved = False # loser detection flag
			newWinHands = []
			for j in range(len(topCards)):
				if topCards[j] == largestCard:
					newWinHands.append(winHands[j]) 
				else:
					# Remove players with < max
					isPlayerRemoved = True
					#winHands.remove(winHands.index(j))
					
			winHands = newWinHands
			# If only one winner remaining, stop checking
			if len(winHands) == 1:
				result.kicker = largestCard
				result.winner = ("Win", winHands[0][0])		
				print "best hands = " + str(result.bestHands)
				return result	
			# If player was removed, remake zippedHands
			if isPlayerRemoved:
				zippedHands = zip(*[winner[1] for winner in winHands])
					
		
		result.winner = ("Tie", [winner[0] for winner in winHands])
	
	print "best hands = " + str(result.bestHands)

	return result


def best_hand(cards):
	"""Checks cards for a straight flush, four of a kind, full house, etc.

	Input: A list with the player's hand concatenated with the
	community cards.

	Returns: A tuple containing a number (enum Class) denoting the rank, and
	a sorted list of strings representing the cards in the best
	hand.

	Example output: (['QC', 'JS', '9D', '8D', '7H'], 0)
	"""

	values = [card[0:-1] for card in cards]
	suits = [card[-1] for card in cards]

	# Dictionary for converting card strings to numbers
	cardNums = {"A":14, "K":13, "Q":12, "J":11, "10":10, "9":9, "8":8, \
			"7":7, "6":6, "5":5, "4":4, "3":3, "2":2}

	# Convert card values to real numbers
	unsortedValues = [cardNums[value] for value in values]
	# unsorted values is necessary for retrieving card + suit
	# later
	values = unsortedValues [:] # make a copy of list
	values.sort() 		# sort values 
	values.reverse()	# largest # first 

	### Check for possible hands


	# prepare variables for holding potential hands
	fourkind = []
	flush = [] 	# stores the suit of the flush
	straight = [] 	# stores the highest number of straight 
	threekind = []  # stores the best possible 3-of-a-kind 
	pairs = [] 	# stores one number for each pair

	# prepare counters for tracking possible hands
	straightCounter = 1 # always have a straight of 1
	
	# Check for flush
	for suit in suits:
		if suits.count(suit) >= 5:
			flush = suit	
			break

	# check for straight, 4-kind, 3-kind, pairs
	for i in range(6): # Don't process the last card

		# Check for straight if still possible
		if len(straight) == 0:
			print "values = " + str(values)
			straightSeq = [values.count(values[i]-j) >= 1 for j in range(1,5)]	
			print "straightSeq = " + str(straightSeq)
			if straightSeq.count(True) == 4:
				straight.append(values[i])	

			# check for 5-4-3-2-A straight
			if values[i] == 5:
				# check for 4-2-3 first
				straightSeq = [values.count(values[i]-j) >= 1 for j in range(1,4)]	
				# check for Ace
				if straightSeq.count(True) == 3 and \
					values.count(cardNums["A"]) >= 1:
					straight.append(values[i])	

		# Check for 4-kind
		if len(fourkind) == 0 and values.count(values[i]) == 4:
			fourkind = [values[i]]
		# Check for 3-kind but don't add same one twice 
		elif values.count(values[i]) == 3 and \
			threekind.count(values[i]) == 0:	
			if len(threekind) == 0:
				threekind.append(values[i])
			else: # add to pairs
				pairs.append(values[i])
		# Check for pairs, don't add same pair twice
		elif values.count(values[i]) == 2 and \
			pairs.count(values[i]) == 0: 
			pairs.append(values[i])

	

	### Determine hand strength based on found hands
	# Since values are separated from suits, have to iterate
	# through unsorted values to find correct index of each card

	besthand = []

	# Straight flush
	if len(straight) != 0 and len(flush) != 0:
		for i in range(5): 
			# check for 5-4-3-2-A straight
			if i == 4 and straight[0] == cardNums["5"]:
				cardIndex = unsortedValues.index(cardNums["A"])
			else:
				cardIndex = unsortedValues.index(straight[0] - i)

			card = cards[cardIndex] 
			if card[-1] == flush:
				besthand.append(card)
			else:
				break
		if len(besthand) == 5:
			return (besthand, Ranks.StraightFlush)
		else: # not a straight flush, so re-init besthand
			besthand = []

	# Four of a kind
	if len(fourkind) != 0:
		cardValue = convNumToCard(fourkind[0])
		# insert the 4 out of 5 cards b/c suit is known
		besthand = [cardValue + "S", cardValue + "H", cardValue + "C", cardValue + "D"]
		# add the highest value card that isn't 4-of-a-kind
		for i in range(7):
			# search sorted list for high card
			if values[i] != fourkind[0]:
				# find card in original unsorted list
				cardIndex = unsortedValues.index(values[i])
				card = cards[cardIndex] 
				besthand.append(card)
				break
		return (besthand, Ranks.FourKind)
	# Full House	
	elif len(threekind) != 0 and len(pairs) != 0:
		for i in range(7): # add 3-kind to besthand
			if unsortedValues[i] == threekind[0]:
				besthand.append(cards[i])
				if len(besthand) == 3:
					break
		
		for i in range(7): # add pair to besthand
			if unsortedValues[i] == pairs[0]:
				besthand.append(cards[i])
				if len(besthand) == 5:
					break
		return (besthand, Ranks.FullHouse)
	# Flush
	elif len(flush) != 0:
		# iterate through sorted cards, add that card if its
		# suit matches the flush suit
		for i in range(7):
			# find card in original unsorted list
			cardIndex = unsortedValues.index(values[i])
			card = cards[cardIndex] 
			if card[-1] == flush[0]:
				besthand.append(card)
				if len(besthand) == 5:
					break
		return (besthand, Ranks.Flush)
	# Straight
	elif len(straight) != 0:

		for i in range(5): 
			# check for 5-4-3-2-A straight
			if i == 4 and straight[0] == cardNums["5"]:
				cardIndex = unsortedValues.index(cardNums["A"])
			else:
				cardIndex = unsortedValues.index(straight[0] - i)
			card = cards[cardIndex] 
			besthand.append(card)
		return (besthand, Ranks.Straight)
	# Three of a kind
	elif len(threekind) != 0:
		for i in range(7): # add 3-kind to besthand
			if unsortedValues[i] == threekind[0]:
				besthand.append(cards[i])
				if len(besthand) == 3:
					break
		for i in range(7): # add two high cards to best hand
			# search sorted list for high card
			if values[i] != threekind[0]:
				# find card in original unsorted list
				cardIndex = unsortedValues.index(values[i])
				card = cards[cardIndex] 
				besthand.append(card)
				if len(besthand) == 5:
					break
		return (besthand, Ranks.ThreeKind)
	# Two pair
	elif len(pairs) == 2:
		for i in range(7): # add 1st pair to besthand
			if unsortedValues[i] == pairs[0]:
				besthand.append(cards[i])
				if len(besthand) == 2:
					break
		for i in range(7): # add 2nd pair to besthand
			if unsortedValues[i] == pairs[1]:
				besthand.append(cards[i])
				if len(besthand) == 4:
					break
		for i in range(7): # add high card to best hand
			# search sorted list for high card
			if values[i] != pairs[0] and values[i] != pairs[1]:
				# find card in original unsorted list
				cardIndex = unsortedValues.index(values[i])
				card = cards[cardIndex] 
				besthand.append(card)
				if len(besthand) == 5:
					break
		return (besthand, Ranks.TwoPair)
	# Pair
	elif len(pairs) == 1:
		for i in range(7): # add pair to besthand
			if unsortedValues[i] == pairs[0]:
				besthand.append(cards[i])
				if len(besthand) == 2:
					break
		for i in range(7): # add high card to best hand
			# search sorted list for high card
			if values[i] != pairs[0]:
				# find card in original unsorted list
				cardIndex = unsortedValues.index(values[i])
				card = cards[cardIndex] 
				besthand.append(card)
				if len(besthand) == 5:
					break
		return (besthand, Ranks.Pair)
	# High card
	else:
		for i in range(7):
			cardIndex = unsortedValues.index(values[i])
			card = cards[cardIndex] 
			besthand.append(card)
			if len(besthand) == 5:
				return (besthand, Ranks.HighCard)

	

def convNumToCard(cardNum):
	""" A helper function for converting card number to string.
	Input: A number representing a card.
	Returns a string representing a card.
	"""

	cardDict = {14:"A", 13:"K", 12:"Q", 11:"J"}

	if cardNum > 10:
		return cardDict[cardNum]
	else: return str(cardNum)	

# george's player class

class P():
    index = 0
    def __init__(self, name, amt=1000, hand=()):
        self.name = name
        self.hand = hand
        self.state = None

        self.amt = amt

        self.bet_amt = 0
        self.invested_amt = 0

        self.match_amt = 0

        self.sidepot = 0

        self.allin = False

        P.index += 1
        self.index = P.index
    
    def __repr__(self):
        return self.name + " -- " + str(self.amt)

    def __cmp__(self, other):
        return cmp(self.name, other)


if __name__ == "__main__":

	# Test cases
	communities = (#("3C","5D","9S","AH","AD") ,)  # test1 
			#("KD","QD","JD","9C","10C"), # test2
			("4C", "5C", "3C", "9D", "JS"), ) # test3: 
	hands = (("AC","AS"), # test1: four of a kind
		("AC","5S"),  # test1: full house
		("AS","2H"),  # test1: three of a kind
		("2D", "3D"),  # test1: 2 pair, test2: flush
		("AD", "10D"), # test2: royal/straight flush 
		("7H", "8D"),  # test1: pair, test2: straight, # test3: high card 
		("4D", "2D"),  # test1: A-5 straight
		("AC", "2C"),  # test3: A-5 str8 flush
		("6C", "2C") ) # test3: 2-6 str8.
				

	# Test players
	players = ( 	P(name="haabaa", hand=hands[0]),
			P(name="george", hand=hands[0]),	
			P(name="matto", hand=hands[0]),
			P(name="nitto", hand=hands[8]),
			P(name="dardar", hand=hands[6]),
			P(name="barry", hand=hands[7]) )
	for community in communities:
		print "Start of new test community\n"
		#for hand in hands:
		#	print best_hand(hand + community)
		for i in range(6):
			print "community:" + str(community)
			print "".join(str((player.name, player.hand)) for player in players[i:])
			print rank(players[i:], community)
			print "\n"
