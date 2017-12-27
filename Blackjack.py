import random
import time

# TO DO:
# Counter AI makes choice to hit/stand/etc. involving count
# Random ints changing each call
# Split functions: compare totals, deal new card, play blackjack, lucky lucky


# Cards have suits, names, and values. Values and names are equal in all cases, except for face cards and aces.
class Card:
    def __init__(self, suit, name):
        self.suit = suit
        self.name = name
        if self.name in ["Jack", "Queen", "King"]:
            self.value = 10
        elif self.name == "Ace":
            self.value = 11
        else:
            self.value = name

    # Get the full name of the card. For example, 'Ace of Diamonds'
    def getFullName(self):
        return "{} of {}".format(self.name, self.suit)

    # Print a string to correspond to the card being dealt.
    # The article changes from 'a' to 'an' if the card is an Ace or an 8 since they start with vowels
    def printCardDealt(self, target):
        if self.name == "Ace" or self.name == 8:
            print("The dealer deals {} an {}.".format(target, self.getFullName()))
        else:
            print("The dealer deals {} a {}.".format(target, self.getFullName()))


# Each player has a name, list of hands (initially empty), and amount of money held.
# The Player class keeps track of the card count, though this is currently only used by the Counter, Copycat, and
# Enigma subclasses
class Player:
    cardCount = 0

    def __init__(self, name):
        self.name = name
        self.hands = []
        self.money = 100

    # Adds a new instance of the Hand class to the player's list of hands, and reduces their total money held by the
    # amount they're betting on the hand
    def createNewHand(self, bet):
        self.money -= bet
        self.hands.append(Hand(self, bet))

    # Resets the player's list of hands to its initial empty state
    def resetHand(self):
        self.hands = []

    def playerTurn(self, hand, deck, dealerTotal, previousPlayer):
        while True:
            choice = hand.getPlayerChoice()
            if choice.lower() == "x" and len(hand.cards) == 2 and hand.cards[0][0] == hand.cards[1][0]:
                hand.split()
            elif choice.lower() == "h" or (choice.lower() == "d" and
                                           ((len(hand.cards) == 2 and len(self.hands) == 1) or
                                            len(hand.cards) == 1) and self.money >= hand.bet):
                if choice.lower() == "d":
                    hand.player.money -= hand.bet
                    print("You add {} to your bet.".format(hand.bet))
                    hand.bet *= 2
                    hand.hit(deck)
                    return False
                else:
                    hand.hit(deck)
                    if hand.totalValue > 21:
                        return False
            elif choice.lower() == "s":
                return False
            else:
                print("I'm sorry, I didn't understand that.")
                time.sleep(1)


class AI(Player):
    def __init__(self, name):
        super().__init__(name)
        self.money = 5000

    def makeBet(self, previousBet):
        print("\n{} bets the $2 minimum.".format(self.name))
        return 2


class Dealer(AI):
    dealerSoft17 = False

    def __init__(self, name, isDealer=False):
        super().__init__(name)
        self.isDealer = isDealer

    def makeBet(self, previousBet):
        print("\n{} bets the $2 minimum.".format(self.name))
        return 2

    def playerTurn(self, hand, deck, dealerTotal, previousPlayer):
        while hand.totalValue < 17 or (hand.totalValue == 17 and hand.totalHighAces and Dealer.dealerSoft17):
            hand.hit(deck)

        if hand.totalValue <= 21:
            if self.isDealer:
                print("The dealer stands at {}.".format(hand.totalValue))
            else:
                print("{} stands at {}.".format(self.name, hand.totalValue))
            time.sleep(2)


class Mathematician(AI):
    def __init__(self, name):
        super().__init__(name)

    def makeBet(self, previousBet):
        if self.money >= 5:
            print("\n{} bets $5 for this hand.".format(self.name))
            return 5
        else:
            print("\n{} bets ${} for this hand.".format(self.name, self.money))
            return self.money

    def playerTurn(self, hand, deck, dealerTotal, previousPlayer):
        while True:
            if (len(hand.cards) == 2 and len(self.hands) == 1) or len(hand.cards) == 1:
                canDouble = True
            else:
                canDouble = False

            # If the AI has the opportunity to split
            if len(hand.cards) == 2 and hand.cards[0][0] == hand.cards[1][0]:
                if hand.totalValue == 18 and dealerTotal in [7, 10, 11]:
                    break
                elif (hand.totalValue == 8 and dealerTotal not in [5, 6]) or (hand.totalValue <= 14 and
                                                                              8 <= dealerTotal <= 11):
                    hand.hit(deck)
                else:
                    hand.split(deck)
            # If the AI has a soft total
            elif hand.totalHighAces > 0:
                if canDouble and ((hand.totalValue <= 18 and dealerTotal in [5, 6]) or
                                  (15 <= hand.totalValue <= 18 and dealerTotal == 4) or
                                  (hand.totalValue in [17, 18] and dealerTotal == 3)):
                    self.money -= hand.bet
                    print("{} adds another {} to their bet.".format(self.name, hand.bet))
                    hand.bet *= 2
                    hand.hit(deck)
                    return
                if hand.totalValue >= 19 or (hand.totalValue == 18 and dealerTotal <= 8):
                    break
                else:
                    hand.hit(deck)
            elif (13 <= hand.totalValue <= 16 and dealerTotal <= 6) or (hand.totalValue == 12 and
                                                                        4 <= dealerTotal <= 6) or hand.totalValue >= 17:
                break
            elif canDouble and ((hand.totalValue == 9 and 3 <= dealerTotal <= 6) or
                                (hand.totalValue == 10 and dealerTotal <= 9) or
                                (hand.totalValue == 11 and dealerTotal <= 10)):
                    self.money -= hand.bet
                    print("{} adds another {} to their bet.".format(self.name, hand.bet))
                    hand.bet *= 2
                    hand.hit(deck)
                    return
            else:
                hand.hit(deck)

        if hand.totalValue <= 21:
            print("{} stands at {}.".format(self.name, hand.totalValue))
            time.sleep(2)


class Counter(AI):
    def __init__(self, name):
        super().__init__(name)

    def makeBet(self, previousBet):
        if self.cardCount == 0:
            if self.money >= 5:
                print("\n{} bets $5 this hand.".format(self.name))
                return 5
            else:
                print("\n{} bets ${} for this hand.".format(self.name, self.money))
                return self.money
        elif self.cardCount > 0:
            tempBet = max(200, 5 + self.cardCount * 10)
            if self.money >= tempBet:
                print("\n{} bets ${} this hand.".format(self.name, tempBet))
                return tempBet
            else:
                print("\n{} bets ${} for this hand.".format(self.name, self.money))
                return self.money
        else:
            print("\n{} bets the $2 minimum.".format(self.name))
            return 2

    def playerTurn(self, hand, deck, dealerTotal, previousPlayer):
        while True:
            if (len(hand.cards) == 2 and len(self.hands) == 1) or len(hand.cards) == 1:
                canDouble = True
            else:
                canDouble = False

            # If the AI has the opportunity to split
            if len(hand.cards) == 2 and hand.cards[0][0] == hand.cards[1][0]:
                if hand.totalValue == 18 and dealerTotal in [7, 10, 11]:
                    break
                elif (hand.totalValue == 8 and dealerTotal not in [5, 6]) or (hand.totalValue <= 14 and
                                                                              8 <= dealerTotal <= 11):
                    hand.hit(deck)
                else:
                    hand.split(deck)
            # If the AI has a soft total
            elif hand.totalHighAces > 0:
                if canDouble and ((hand.totalValue <= 18 and dealerTotal in [5, 6]) or
                                  (15 <= hand.totalValue <= 18 and dealerTotal == 4) or
                                  (hand.totalValue in [17, 18] and dealerTotal == 3)):
                    self.money -= hand.bet
                    print("{} adds another {} to their bet.".format(self.name, hand.bet))
                    hand.bet *= 2
                    hand.hit(deck)
                    return
                if hand.totalValue >= 19 or (hand.totalValue == 18 and dealerTotal <= 8):
                    break
                else:
                    hand.hit(deck)
            elif (13 <= hand.totalValue <= 16 and dealerTotal <= 6) or (hand.totalValue == 12 and
                                                                        4 <= dealerTotal <= 6) or hand.totalValue >= 17:
                break
            elif canDouble and ((hand.totalValue == 9 and 3 <= dealerTotal <= 6) or
                                (hand.totalValue == 10 and dealerTotal <= 9) or
                                (hand.totalValue == 11 and dealerTotal <= 10)):
                    self.money -= hand.bet
                    print("{} adds another {} to their bet.".format(self.name, hand.bet))
                    hand.bet *= 2
                    hand.hit(deck)
                    return
            else:
                hand.hit(deck)

        if hand.totalValue <= 21:
            print("{} stands at {}.".format(self.name, hand.totalValue))
            time.sleep(2)


class Gambler(AI):
    def __init__(self, name):
        super().__init__(name)

    def makeBet(self, previousBet):
        randomBet = random.randint(2, 50)
        if randomBet > self.money:
            randomBet = self.money
        print("\n{} bets ${} this hand.".format(self.name, randomBet))
        return randomBet

    def playerTurn(self, hand, deck, dealerTotal, previousPlayer):
        while True:
            if len(hand.cards) == 2 and hand.cards[0][0] == hand.cards[1][0]:
                hand.split(deck)
            elif hand.totalValue < 12 and ((len(hand.cards) == 2 and len(self.hands) == 1) or len(hand.cards) == 1):
                self.money -= hand.bet
                print("{} adds another {} to their bet.".format(self.name, hand.bet))
                hand.bet *= 2
                hand.hit(deck)
                return
            elif hand.totalValue > 17:
                break
            else:
                hand.hit(deck)

        if hand.totalValue <= 21:
            print("{} stands at {}.".format(self.name, hand.totalValue))
            time.sleep(2)


class Conservative(AI):
    def __init__(self, name):
        super().__init__(name)

    def makeBet(self, previousBet):
        print("\n{} bets the $2 minimum.".format(self.name))
        return 2

    def playerTurn(self, hand, deck, dealerTotal, previousPlayer):
        while True:
            if hand.totalValue > 15 or (hand.totalValue > 13 and dealerTotal < 7):
                break
            else:
                hand.hit(deck)

        if hand.totalValue <= 21:
            print("{} stands at {}.".format(self.name, hand.totalValue))
            time.sleep(2)


class Copycat(AI):
    def __init__(self, name):
        super().__init__(name)

    def makeBet(self, previousBet):
        if previousBet > self.money:
            previousBet = self.money
        print("\n{} bets ${} this hand.".format(self.name, previousBet))
        return previousBet

    def playerTurn(self, hand, deck, dealerTotal, previousPlayer):
        while True:
            if (len(hand.cards) == 2 and len(self.hands) == 1) or len(hand.cards) == 1:
                canDouble = True
            else:
                canDouble = False

            if (len(hand.cards) == 2 and hand.cards[0][0] == hand.cards[1][0]) and len(previousPlayer.hands) > 1:
                hand.split(deck)
            if hand.totalValue > 18 or len(hand.cards) >= len(previousPlayer.hands[-1]):
                break
            elif canDouble and len(previousPlayer.hands[-1]) == len(hand.cards) + 1:
                self.money -= hand.bet
                print("{} adds another {} to their bet.".format(self.name, hand.bet))
                hand.bet *= 2
                hand.hit(deck)
                return
            else:
                hand.hit(deck)

        if hand.totalValue <= 21:
            print("{} stands at {}.".format(self.name, hand.totalValue))
            time.sleep(2)


class Enigma(AI):
    def __init__(self, name):
        super().__init__(name)

    def makeBet(self, previousBet):
        possibleActionsDict = {0: Dealer.makeBet, 1: Mathematician.makeBet, 2: Counter.makeBet,
                               3: Conservative.makeBet, 4: Gambler.makeBet, 5: Copycat.makeBet}
        randomAct = random.randint(0, 5)
        return possibleActionsDict[randomAct](self, previousBet)

    def playerTurn(self, hand, deck, dealerTotal, previousPlayer):
        possibleActionsDict = {0: Dealer.playerTurn, 1: Mathematician.playerTurn, 2: Counter.playerTurn,
                               3: Conservative.playerTurn, 4: Gambler.playerTurn, 5: Copycat.playerTurn}
        randomAct = random.randint(0, 5)
        possibleActionsDict[randomAct](self, hand, deck, dealerTotal, previousPlayer)


# Hands track their total value, total number of high aces (aces treated as 11 instead of 1), the amount bet on them,
# and a list of all card names in the hand
class Hand:
    def __init__(self, player, bet):
        self.player = player
        self.totalValue = 0
        self.totalHighAces = 0
        self.bet = bet
        self.cards = []

    # Deal a new card. Increase the hand's total value and list of cards accordingly, then print a message for the card
    # dealt and check
    def dealNewCard(self, deckOfCards):
        newCard = deckOfCards.pop()
        self.totalValue += newCard.value
        if newCard.name == "Ace":
            self.totalHighAces += 1
        self.cards.append((newCard.name, newCard.suit))

        if isinstance(self.player, Dealer) and self.player.isDealer:
            newCard.printCardDealt("himself")
        else:
            newCard.printCardDealt(self.player.name)
        time.sleep(1)
        self.changeAceValueIfBusted()

        if newCard.value <= 6:
            Player.cardCount -= 1
        elif newCard.value >= 10:
            Player.cardCount += 1

        # Print the hand's total value only if the hand has more than one card in it, or the player is the dealer
        # The opening deal gives 2 cards to all players except the dealer, so this prevents the message from appearing
        # in the middle of a player's opening hand being dealt
        if len(self.cards) > 1 or (isinstance(self.player, Dealer) and self.player.isDealer):
            self.printTotalValue()
            time.sleep(1.5)

    # Check the total value of the hand. If the hand busts, but there are high aces remaining, remove one of the high
    # aces and decrease the hand's value by 10 (i.e., Treat the ace as a 1 instead of as an 11)
    def changeAceValueIfBusted(self):
        if self.totalValue > 21 and self.totalHighAces > 0:
            self.totalValue -= 10
            self.totalHighAces -= 1

    def getPlayerChoice(self):
        inputTextList = ["Press H to hit", "S to stand"]
        if self.player.money >= self.bet and len(self.cards) == 2 and self.cards[0][0] == self.cards[1][0]:
            inputTextList.append("X to split")
        if self.player.money >= self.bet and (len(self.cards) == 1 or (len(self.cards) == 2 and
                                                                       len(self.player.hands) == 1)):
            inputTextList.append("D to double down")
        inputTextList[-1] = "or " + inputTextList[-1]
        inputText = ", ".join(inputTextList)
        inputText += ":  "
        playerChoiceInput = input(inputText)
        return playerChoiceInput

    def hit(self, deckOfCards):
        self.dealNewCard(deckOfCards)
        self.checkAndPrintBustMessage()

    def split(self):
        self.totalValue = self.totalValue // 2
        self.totalHighAces = self.totalHighAces // 2
        splitCard = self.cards.pop()
        if splitCard[0] in ["Ace", "Jack", "Queen", "King"]:
            print("Splitting {}s! Your total is now {}.".format(splitCard, self.totalValue))
        else:
            print("Splitting {}'s! Your total is now {}.".format(splitCard, self.totalValue))

        self.player.createNewHand(self.bet)
        self.player.hands[-1].totalValue = self.totalValue
        self.player.hands[-1].totalHighAces = self.totalHighAces
        self.player.hands[-1].cards.append(splitCard)
        time.sleep(1)

    def printTotalValue(self):
        if isinstance(self.player, Dealer) and self.player.isDealer:
            print("The dealer's total is now {}.".format(self.totalValue))
        elif isinstance(self.player, AI):
            print("{}'s total is now {}.".format(self.player.name, self.totalValue))
        else:
            print("{}, your total is now {}.".format(self.player.name, self.totalValue))

    def printMessageOnBlackjack(self):
        if self.totalValue == 21:
            if isinstance(self.player, AI):
                print("\n\t\t{} draws a Blackjack!".format(self.player.name))
            else:
                print("\n\t\tYou see a Blackjack, {}!".format(self.player.name))
            time.sleep(2)

    def checkAndPrintBustMessage(self):
        if self.totalValue > 21:
            if isinstance(self.player, Dealer) and self.player.isDealer:
                print("The dealer has busted.")
            elif isinstance(self.player, AI):
                print("Oh no, looks like {} has busted.".format(self.player.name))
            else:
                print("I'm sorry {}, but you have busted.".format(self.player.name))
            time.sleep(2)

    def printPlayerTurnMessage(self):
        if isinstance(self.player, Dealer) and self.player.isDealer:
            print("\nIt is now the dealer's turn. The dealer's total is {}.".format(self.totalValue))
        elif isinstance(self.player, AI):
            print("\nIt is now {0}'s turn. {0}'s total is {1}.".format(self.player.name, self.totalValue))
        else:
            print("\n{}, it is your turn. Your total is now {}.".format(self.player.name, self.totalValue))
        time.sleep(0.5)

    def compareTotals(self, dealerValue, charlie):
        if 22 > self.totalValue > dealerValue or dealerValue >= 22 > self.totalValue:
            if isinstance(self.player, AI):
                print("\n{} beats the dealer, {} to {}!".format(self.player.name, self.totalValue, dealerValue))
            else:
                print("\nCongratulations {}! With {} to {}, you have won!".format(self.player.name, self.totalValue,
                                                                                  dealerValue))
            time.sleep(0.5)
            if (charlie == 7 or charlie == 57) and len(self.cards) >= 7:
                print("Amazing! A Seven-Card-Charlie! {} wins four times their bet, "
                      "getting ${}!".format(self.player.name, self.bet * 4))
                self.player.money += self.bet * 5

            elif (charlie == 5 or charlie == 57) and len(self.cards) >= 5:
                print("Five-Card-Charlie! {} earns a bonus 3 to 2 payment of ${}!".format(self.player.name,
                                                                                          self.bet * 3 // 2))
                self.player.money += self.bet * 5 // 2
            elif self.totalValue == 21 and len(self.cards) == 2:
                print("Blackjack pays 3 to 2! {} earns ${}!".format(self.player.name, self.bet * 3 // 2))
                self.player.money += self.bet * 5 // 2
            else:
                print("{} earns ${}!".format(self.player.name, self.bet))
                self.player.money += self.bet * 2
        elif self.totalValue == dealerValue:
            print("\n\t\tPUSH!")
            time.sleep(1)
            if isinstance(self.player, AI):
                print("{0} pushes the dealer. {0}'s bet is returned.".format(self.player.name))
            else:
                print("You push the dealer. Your bet of ${} is returned to you, {}.".format(self.bet, self.player.name))
            self.player.money += self.bet
        elif self.totalValue > 21:
            if isinstance(self.player, AI):
                print("\n{} has busted with a hand of {}.".format(self.player.name, self.totalValue))
            else:
                print("\nSorry {}, but your {} has busted. Your bet of ${} is lost.".format(self.player.name,
                                                                                            self.totalValue, self.bet))
        elif isinstance(self.player, AI):
            print("\n{} to {}: {} fails to beat the dealer.".format(self.totalValue, dealerValue, self.player.name))
        else:
            print("\n{} to {}: I'm sorry {}, but this hand has lost you ${}.".format(self.totalValue, dealerValue,
                                                                                     self.player.name, self.bet))
        time.sleep(3)


# Build a list of Cards of all values in the totalValues list, for each suit in the totalSuits list
def buildDeck(totalSuits, totalValues):
    deck = []
    for value in totalValues:
        for suit in totalSuits:
            deck.append(Card(suit, value))
    return deck


# Build a list of n decks of cards
def buildBlackjackDeck(totalSuits, totalValues, amountOfDecks):
    deck = []
    for _ in range(amountOfDecks):
        deck.extend(buildDeck(totalSuits, totalValues))
    return deck


# Shuffle the deck in place in a random order
def shuffleDeck(deckOfCards):
    random.shuffle(deckOfCards)


def luckyLuckyGame(playerFirstCard, playerSecondCard, dealerCard, player, luckyBet):
    cardValues = [playerFirstCard[0], playerSecondCard[0], dealerCard[0]]
    cardSuits = True if len({playerFirstCard[1], playerSecondCard[1], dealerCard[1]}) == 1 else False
    newCardValues = []
    for cardVal in cardValues:
        if cardVal in ["Jack", "Queen", "King"]:
            newCardValues.append(10)
        elif cardVal == "Ace":
            newCardValues.append(11)
        else:
            newCardValues.append(cardVal)
    if playerFirstCard[0] == playerSecondCard[0] == 11:
        playerSecondCard = 1
    cardTotalSum = sum(newCardValues)

    if cardValues == [7, 7, 7]:
        if cardSuits:
            print("Lucky Lucky jackpot!!! This is amazing! We pay 200 to 1 for suited 7's! "
                  "{} wins an incredible {}!".format(player.name, luckyBet * 200))
            player.money += luckyBet * 201
        else:
            print("Lucky Lucky! We have a winner: 50 to 1 for triple 7's! "
                  "{} wins an amazing {}!".format(player.name, luckyBet * 50))
            player.money += luckyBet * 51
    elif len(set(newCardValues)) == 3 and all(newCardValues) in [6, 7, 8]:
        if cardSuits:
            print("Lucky Lucky jackpot!!! Unbelievable! We pay 100 to 1 for suited 6-7-8! "
                  "{} wins an incredible {}!".format(player.name, luckyBet * 100))
            player.money += luckyBet * 101
        else:
            print("Lucky Lucky! We have a nice 30 to 1 payoff for 6-7-8! "
                  "{} wins a great {}!".format(player.name, luckyBet * 30))
            player.money += luckyBet * 31
    elif cardTotalSum == 21:
        if cardSuits:
            print("Lucky Lucky! We pay a nice 15 to 1 for a suited 21! "
                  "{} wins {} today.".format(player.name, luckyBet * 15))
            player.money += luckyBet * 16
        else:
            print("Lucky Lucky! {0} wins 3 to 1 for their lucky total of 21! "
                  "{1} is given to {0}.".format(player.name, luckyBet * 3))
            player.money += luckyBet * 4
    elif cardTotalSum == 19 or cardTotalSum == 20:
        print("Lucky Lucky! {0} wins 2 to 1 for their lucky total of {2}! "
              "{1} is given to {0}.".format(player.name, luckyBet, cardTotalSum))
        player.money += luckyBet * 2
    else:
        print("Unlucky! There's no Lucky Lucky bonus for {} this time.".format(player.name))
    time.sleep(1)


def openingDeal(deckOfCards, listOfPlayers, dealer, bets):
    dealer.createNewHand(0)
    dealer.hands[0].dealNewCard(deckOfCards)

    for player in listOfPlayers:
        if len(deckOfCards) < 12:
            deckOfCards = buildBlackjackDeck(suits, values, numberOfDecks)
            shuffleDeck(deckOfCards)
            print("The dealer reshuffles the deck.")
            Player.cardCount = 0
        player.createNewHand(bets[listOfPlayers.index(player)][0])
        for hand in player.hands:
            print()
            hand.dealNewCard(deckOfCards)
            hand.dealNewCard(deckOfCards)
            time.sleep(1.5)


def playBlackjack(deckOfCards, playersList, dealer, charlieChoice, luckyLuckyChoice):
    fullDeckSize = len(deckOfCards)
    while True:
        allPlayersKickedOut = checkIfAllPlayersKickedOut(playersList)
        playersList = [player for player in playersList if 2 <= player.money <= 999999]
        if allPlayersKickedOut:
            return

        if len(deckOfCards) < fullDeckSize * 0.3:
            deckOfCards = buildBlackjackDeck(suits, values, numberOfDecks)
            shuffleDeck(deckOfCards)
            print("The dealer reshuffles the deck.")
            Player.cardCount = 0
        bets = [acceptBet(playersList[0], luckyLuckyChoice, (0, 0))]
        newPlayerList = []
        if bets[0][0] != 0:
            newPlayerList = [playersList[0]]
        for player in playersList[1:]:
            if isinstance(player, AI) and not newPlayerList:
                break
            else:
                amountBet = acceptBet(player, luckyLuckyChoice, bets[-1] or (0, 0))
                if amountBet[0] != 0:
                    bets.append(amountBet)
                    newPlayerList.append(player)
            time.sleep(1)
        playersList = newPlayerList[:]
        if not playersList:
            checkIfAllPlayersKickedOut(playersList)
            return
        openingDeal(deckOfCards, playersList, dealer, bets)
        if luckyLuckyChoice:
            for player in playersList:
                if bets[playersList.index(player)][1] > 0:
                    luckyLuckyGame(player.hands[0].cards[0], player.hands[0].cards[1], dealer.hands[0].cards[0], player,
                                   bets[playersList.index(player)][1])
        for player in playersList:
            for hand in player.hands:
                hand.printMessageOnBlackjack()
        for player in playersList:
            for hand in player.hands:
                if hand.totalValue != 21:
                    hand.printPlayerTurnMessage()
                    continueDealing = True
                    while continueDealing:
                        if len(deckOfCards) < fullDeckSize * 0.3:
                            deckOfCards = buildBlackjackDeck(suits, values, numberOfDecks)
                            shuffleDeck(deckOfCards)
                            print("The dealer reshuffles the deck.")
                            Player.cardCount = 0
                        continueDealing = player.playerTurn(hand, deckOfCards, dealer.hands[0].totalValue,
                                                            playersList[playersList.index(player) - 1])
                    time.sleep(1)

        dealerTurn = False
        for player in playersList:
            for hand in player.hands:
                if hand.totalValue <= 21:
                    dealerTurn = True

        if dealerTurn:
            print()
            dealer.playerTurn(dealer.hands[0], deckOfCards, dealer.hands[0].totalValue, playersList[-1])
            time.sleep(1)

        for player in playersList:
            for hand in player.hands:
                hand.compareTotals(dealer.hands[0].totalValue, charlieChoice)
        for player in playersList:
            checkMoney(player)
            player.resetHand()
        dealer.resetHand()


def getPlayers(listOfPlayers, setAIBehaviour):
    while True:
        numberOfHumanPlayers = input("How many human players would you like sitting at your table?  ")
        try:
            numberOfHumanPlayers = int(numberOfHumanPlayers)
            if 1 <= numberOfHumanPlayers <= 6:
                break
            else:
                print("Please input a number between 1 and 6.")
        except ValueError:
            print("Please input a number between 1 and 6.")
        time.sleep(1)
    for playerIndex in range(numberOfHumanPlayers):
        playerName = getPlayerName(playerIndex,  "human")
        listOfPlayers.append(Player(playerName))

    if numberOfHumanPlayers < 6:
        while True:
            numberOfAIPlayers = input("How many AI players would you like sitting at your table?  ")
            try:
                numberOfAIPlayers = int(numberOfAIPlayers)
                if 0 <= numberOfAIPlayers <= 6 - numberOfHumanPlayers:
                    break
                else:
                    print("Please input a number between 0 and {}.".format(6 - numberOfHumanPlayers))
            except ValueError:
                print("Please input a number between 0 and {}.".format(6 - numberOfHumanPlayers))
            time.sleep(1)
        for playerIndex in range(numberOfAIPlayers):
            playerNameAI = getPlayerName(playerIndex, "AI")
            if setAIBehaviour:
                setAI(listOfPlayers, playerNameAI)
            else:
                listOfPlayers.append(Dealer(playerNameAI, isDealer=False))
            time.sleep(0.5)
    return listOfPlayers


def getPlayerName(playerOrdinal, humanOrAI):
    ordinalDict = {0: "first", 1: "second", 2: "third", 3: "fourth", 4: "fifth", 5: "sixth"}
    playerName = input("Please type in the name of the {} {} player.  ".format(ordinalDict[playerOrdinal], humanOrAI))
    time.sleep(0.5)
    return playerName


def setAI(listOfCurrentPlayers, playerName):
    while True:
        print("What kind of player would you like {} to be?".format(playerName))
        time.sleep(1)
        optionChoice = input("\t1. The pseudo-dealer (Plays like a dealer)\n"
                             "\t2. The mathematician (Always plays the odds)\n"
                             "\t3. The card counter (Alters play based on the cards remaining in the deck)\n"
                             "\t4. The gambler (Takes risks and bets high)\n"
                             "\t5. The conservative (Frequently stands and bets low)\n"
                             "\t6. The copycat (Follows the lead of the player to their left)\n"
                             "\t7. The enigma (Nobody can really pin down how they'll play)\n")
        if optionChoice == "1":
            listOfCurrentPlayers.append(Dealer(playerName, isDealer=False))
            print("{} will act under the same rules as the dealer. They will stand on 17 or higher, hit on 16 or lower, "
                  "bet the minimum, and never double or split.".format(playerName))
            break
        elif optionChoice == "2":
            listOfCurrentPlayers.append(Mathematician(playerName))
            print("{} will always try to play to the odds. Their decision will depend on the dealer's opening card and "
                  "their current total.".format(playerName))
            break
        elif optionChoice == "3":
            listOfCurrentPlayers.append(Counter(playerName))
            print("{} will act more aggressively when there are many high cards left in the deck, and keep a low profile "
                  "when the deck is full of low cards.".format(playerName))
            break
        elif optionChoice == "4":
            listOfCurrentPlayers.append(Gambler(playerName))
            print("{} will bet high and play aggressively, and will more bust more often than they lose to the dealer. "
                  "They love Lucky Lucky bets.".format(playerName))
            break
        elif optionChoice == "5":
            listOfCurrentPlayers.append(Conservative(playerName))
            print("{} will bet low and play conservatively. They will almost never bust, but will frequently have too "
                  "weak of a hand to face the dealer.".format(playerName))
            break
        elif optionChoice == "6":
            listOfCurrentPlayers.append(Copycat(playerName))
            print("{} will try to mimic the decisions of the player to their left whenever possible.".format(playerName))
            break
        elif optionChoice == "7":
            listOfCurrentPlayers.append(Enigma(playerName))
            print("{} will randomly act each round.".format(playerName))
            break
        else:
            print("I'm sorry, I didn't understand that.")
    time.sleep(1)


def checkMoney(player):
    if player.money < 2:
        print("I'm sorry {}, but you can no longer afford the minimum bet.".format(player.name))
        time.sleep(2)
    elif player.money > 999999:
        print("Congratulations on your winnings, {}! You're now a millionaire!".format(player.name))
        print("Unfortunately, you're going to bankrupt us at this rate, so we have to ban you from our tables.")
        time.sleep(2)


def checkIfAllPlayersKickedOut(playersList):
    if all(isinstance(player, AI) for player in playersList):
        print("\n\nThank you so much for playing at our casino. Please, come again next payday.")
        return True
    return False


def acceptBet(player, playLuckyLucky, previousBet):
    luckyBet = 0
    while True:
        if isinstance(player, AI):
            amountBet = player.makeBet(previousBet[0])
            if playLuckyLucky:
                time.sleep(1)
            break
        else:
            amountBet = input("\n{}, place your bet! You have ${} to spend.\n"
                              "$2 minimum, $500 maximum. Input 'Q' to leave the "
                              "casino.  ".format(player.name, player.money))
            if amountBet.lower() == "q":
                amountBet = 0
                break
            try:
                amountBet = int(amountBet)
                if 2 <= amountBet <= 500 and amountBet <= player.money:
                    break
                elif amountBet > player.money:
                    print("I'm sorry {}, but you cannot afford that bet.".format(player.name))
                else:
                    print("Please input a number between 2 and 500, or else 'q' to leave the casino.")
            except ValueError:
                print("Please input a number between 2 and 500, or else 'q' to leave the casino.")
            time.sleep(1)
    if playLuckyLucky and player.money > 0 and amountBet != 0:
        while True:
            if isinstance(player, Gambler):
                print("{} puts $2 in for Lucky Lucky.".format(player.name))
                luckyBet = 2
                break
            elif isinstance(player, Copycat) and previousBet[1] != 0:
                print("{} puts ${} in for Lucky Lucky.".format(player.name, previousBet[1]))
                luckyBet = previousBet[1]
                break
            elif isinstance(player, Enigma):
                randomBet = random.randint(0, 5)
                if randomBet == 0:
                    print("{} puts $2 in for Lucky Lucky.".format(player.name))
                    luckyBet = 2
                    break
                elif previousBet[1] != 0 and randomBet == 1:
                    print("{} puts ${} in for Lucky Lucky.".format(player.name, previousBet[1]))
                    luckyBet = previousBet[1]
                    break
            elif isinstance(player, AI):
                break
            else:
                luckyBet = input("\n{}, care to play Lucky Lucky? You have ${} left to spend still.\n"
                                 "$1 minimum, $50 maximum. Input '0' to not play Lucky "
                                 "Lucky.  ".format(player.name, player.money))
                if luckyBet == "0":
                    luckyBet = 0
                    break
                try:
                    luckyBet = int(luckyBet)
                    if 1 <= luckyBet <= 50 and luckyBet <= player.money:
                        break
                    elif luckyBet > player.money:
                        print("I'm sorry {}, but you cannot afford that bet.".format(player.name))
                    else:
                        print("Please input a number between 1 and 50, or else '0' to not play Lucky Lucky.")
                except ValueError:
                    print("Please input a number between 1 and 50, or else '0' to not play Lucky Lucky.")
                time.sleep(1)
    return amountBet, luckyBet


def setOptions():
    deckAmountUsed, charlieChoice, luckyChoice, setPlayerAIChoice = 6, 0, False, False
    while True:
        print("Which of the following options would you like to change?")
        time.sleep(1)
        optionChoice = input("\t1. Change the number of decks used\n"
                             "\t2. Change if the dealer stands on soft 17's\n"
                             "\t3. Five-Card-Charlies and Seven-Card-Charlies\n"
                             "\t4. Lucky Lucky\n"
                             "\t5. Manually set the AI players' behavior\n"
                             "\t6. Start the game\n")
        if optionChoice == "1":
            deckAmountUsed = setDecks()
        elif optionChoice == "2":
            setSoft17()
        elif optionChoice == "3":
            charlieChoice = setCharlie()
        elif optionChoice == "4":
            luckyChoice = setLuckyLucky()
        elif optionChoice == "5":
            setPlayerAIChoice = setAIBehavior()
        elif optionChoice == "6":
            return deckAmountUsed, charlieChoice, luckyChoice, setPlayerAIChoice
        else:
            print("I'm sorry, that's not a valid selection.")
        time.sleep(1)


def setDecks():
    while True:
        deckTotalInput = input("Please input the number of decks you'd like to use in this game.  ")
        try:
            deckTotalInput = int(deckTotalInput)
            if deckTotalInput == 1:
                print("The game will be played with just 1 deck.")
                break
            elif 2 <= deckTotalInput <= 10:
                print("The game will be played with {} decks.".format(deckTotalInput))
                break
            else:
                print("Please input a number between 1 and 10.")
        except ValueError:
            print("Please input a number between 1 and 10.")
        time.sleep(1)
    return deckTotalInput


def setSoft17():
    while True:
        soft17Input = input("Would you like the dealer to stand on soft 17's? Type 'y' for yes, or 'n' for no.  ")
        if soft17Input.lower() == "y":
            print("Okay, the dealer will stand on soft 17's.")
            Dealer.dealerSoft17 = False
            break
        elif soft17Input.lower() == "n":
            print("Okay, the dealer will now hit on soft 17's.")
            Dealer.dealerSoft17 = True
            break
        else:
            print("I didn't understand that. Please only type 'y' or 'n'.")
        time.sleep(1)


def setCharlie():
    print("Five-Card-Charlies and Seven-Card-Charlies provide additional payment to players who manage to "
          "beat the dealer with at least five (or seven) cards.")
    time.sleep(1)
    while True:
        charlieInput = input("\t1. Do not play with Charlies\n"
                             "\t2. Play with Five-Card-Charlies\n"
                             "\t3. Play with Seven-Card-Charlies\n"
                             "\t4. Play with both Five-Card-Charlies and Seven-Card-Charlies\n")
        if charlieInput == "1":
            print("Okay, we will not be playing with Charlies.")
            charlieChoice = 0
            break
        elif charlieInput == "2":
            print("Okay, we will play with Five-Card-Charlies.")
            charlieChoice = 5
            break
        elif charlieInput == "3":
            print("Okay, we will play with Seven-Card-Charlies.")
            charlieChoice = 7
            break
        elif charlieInput == "4":
            print("Okay, we will play with both Charlies.")
            charlieChoice = 57
            break
        else:
            print("I didn't understand. Please select one of the options.")
        time.sleep(1)
    return charlieChoice


def setLuckyLucky():
    print("Lucky Lucky is an additional bet you can place that pays you if your opening deal and the dealer's "
          "first card match a pattern.")
    time.sleep(1)
    while True:
        luckyInput = input("Would you like to play with Lucky Lucky? Type 'y' for yes, or 'n' for no.  ")
        if luckyInput.lower() == "y":
            print("Okay, we will play with Lucky Lucky.")
            luckyChoice = True
            break
        elif luckyInput.lower() == "n":
            print("Okay, we will not be playing with Lucky Lucky today.")
            luckyChoice = False
            break
        else:
            print("I didn't understand that. Please only type 'y' or 'n'.")
        time.sleep(1)
    return luckyChoice


def setAIBehavior():
    print("AI players normally play under the same rules as the dealer. If you'd like, you can customize "
          "their behavior.")
    time.sleep(1)
    while True:
        setPlayerAIInput = input("Would you like to manually set the AI players' behaviors? "
                                 "Type 'y' for yes, or 'n' for no.  ")
        if setPlayerAIInput.lower() == "y":
            print("Okay, you will be given the options for their behaviors when you choose your players.")
            setPlayerAIChoice = True
            break
        elif setPlayerAIInput.lower() == "n":
            print("Okay, all AI players will follow the same rules as the dealer.")
            setPlayerAIChoice = False
            break
        else:
            print("I didn't understand that. Please only type 'y' or 'n'.")
        time.sleep(1)
    return setPlayerAIChoice


suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
values = ["Ace", 2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King"]
tempValues = ["Ace", 2, 3]
playerList = []
numberOfDecks, charlieBoolean, luckyLuckyBoolean, setPlayerAIManually = 6, 0, False, False

print("Welcome to the blackjack tables.")
time.sleep(1)
while True:
    playerChoice = input("Please press '1' to start the game, or '2' to change the option settings.  ")
    if playerChoice == "1":
        break
    elif playerChoice == "2":
        numberOfDecks, charlieBoolean, luckyLuckyBoolean, setPlayerAIManually = setOptions()
        break
    else:
        print("I'm sorry, I didn't catch that.")
        time.sleep(1)

newDeck = buildBlackjackDeck(suits, values, numberOfDecks)
shuffleDeck(newDeck)
dealerAI = Dealer("Dealer", isDealer=True)

playerList = getPlayers(playerList, setPlayerAIManually)
playBlackjack(newDeck, playerList, dealerAI, charlieBoolean, luckyLuckyBoolean)
