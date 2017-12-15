import random
import time


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
# Players may also be flagged to be AI controlled, or to be the dealer
class Player:
    def __init__(self, name, isAI=False, isDealer=False):
        self.name = name
        self.isAI = isAI
        self.isDealer = isDealer
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
        self.cards.append(newCard.name)

        if self.player.isDealer:
            newCard.printCardDealt("himself")
        else:
            newCard.printCardDealt(self.player.name)
        time.sleep(1)
        self.changeAceValueIfBusted()

        # Print the hand's total value only if the hand has more than one card in it, or the player is the dealer
        # The opening deal gives 2 cards to all players except the dealer, so this prevents the message from appearing
        # in the middle of a player's opening hand being dealt
        if len(self.cards) > 1 or self.player.isDealer:
            self.printTotalValue()
            time.sleep(1.5)

    # Check the total value of the hand. If the hand busts, but there are high aces remaining, remove one of the high
    # aces and decrease the hand's value by 10 (i.e., Treat the ace as a 1 instead of as an 11)
    def changeAceValueIfBusted(self):
        if self.totalValue > 21 and self.totalHighAces > 0:
            self.totalValue -= 10
            self.totalHighAces -= 1

    def playerTurn(self, deckOfCards):
        if self.player.isAI:
            while self.totalValue < 17 or (self.totalValue == 17 and self.totalHighAces > 0):
                self.hit(deckOfCards)
            if self.totalValue <= 21:
                if self.player.isDealer:
                    print("The dealer stands at {}.".format(self.totalValue))
                else:
                    print("{} stands at {}.".format(self.player.name, self.totalValue))
                time.sleep(2)

        else:
            choice = self.getPlayerChoice()
            if choice.lower() == "x" and len(self.cards) == 2 and self.cards[0] == self.cards[1]:
                self.split()
            elif choice.lower() == "h" or (choice.lower() == "d" and
                                           ((len(self.cards) == 2 and len(self.player.hands) == 1) or
                                           len(self.cards) == 1) and self.player.money >= self.bet):
                self.hit(deckOfCards)
                if choice.lower() == "d":
                    self.player.money -= self.bet
                    print("You add {} to your bet.".format(self.bet))
                    self.bet *= 2
                    return False
                if self.totalValue > 21:
                    return False
            elif choice.lower() == "s":
                return False
            else:
                print("I'm sorry, I didn't understand that.")
                time.sleep(1)
            return True

    def getPlayerChoice(self):
        inputTextList = ["Press H to hit", "S to stand"]
        if len(self.cards) == 2 and self.cards[0] == self.cards[1]:
            inputTextList.append("X to split")
        if self.player.money >= self.bet and (len(self.cards) == 1 or (len(self.cards) == 2 and
                                                                       len(self.player.hands) == 1)):
            inputTextList.append("D to double down")
        inputTextList[-1] = "or " + inputTextList[-1]
        inputText = ", ".join(inputTextList)
        inputText += ":  "
        playerChoice = input(inputText)
        return playerChoice

    def hit(self, deckOfCards):
        self.dealNewCard(deckOfCards)
        self.checkAndPrintBustMessage()

    def split(self):
        self.totalValue = self.totalValue // 2
        self.totalHighAces = self.totalHighAces // 2
        splitCard = self.cards.pop()
        if splitCard in ["Ace", "Jack", "Queen", "King"]:
            print("Splitting {}s! Your total is now {}.".format(splitCard, self.totalValue))
        else:
            print("Splitting {}'s! Your total is now {}.".format(splitCard, self.totalValue))

        self.player.createNewHand(self.bet)
        self.player.hands[-1].totalValue = self.totalValue
        self.player.hands[-1].totalHighAces = self.totalHighAces
        self.player.hands[-1].cards = self.cards[:]
        time.sleep(1)

    def printTotalValue(self):
        if self.player.isDealer:
            print("The dealer's total is now {}.".format(self.totalValue))
        elif self.player.isAI:
            print("{}'s total is now {}.".format(self.player.name, self.totalValue))
        else:
            print("{}, your total is now {}.".format(self.player.name, self.totalValue))

    def printMessageOnBlackjack(self):
        if self.totalValue == 21:
            if self.player.isAI:
                print("\n\t\t{} draws a Blackjack!".format(self.player.name))
            else:
                print("\n\t\tYou see a Blackjack, {}!".format(self.player.name))
            time.sleep(2)

    def checkAndPrintBustMessage(self):
        if self.totalValue > 21:
            if self.player.isDealer:
                print("The dealer has busted.")
            elif self.player.isAI:
                print("Oh no, looks like {} has busted.".format(self.player.name))
            else:
                print("I'm sorry {}, but you have busted.".format(self.player.name))
            time.sleep(2)

    def printPlayerTurnMessage(self):
        if self.player.isDealer:
            print("\nIt is now the dealer's turn. The dealer's total is {}.".format(self.totalValue))
        elif self.player.isAI:
            print("\nIt is now {0}'s turn. {0}'s total is {1}.".format(self.player.name, self.totalValue))
        else:
            print("\n{}, it is your turn. Your total is now {}.".format(self.player.name, self.totalValue))
        time.sleep(0.5)

    def compareTotals(self, dealerValue):
        if 22 > self.totalValue > dealerValue or dealerValue >= 22 > self.totalValue:
            if self.player.isAI:
                print("\n{} beats the dealer, {} to {}!".format(self.player.name, self.totalValue, dealerValue))
            else:
                print("\nCongratulations {}! With {} to {}, you have won!".format(self.player.name, self.totalValue,
                                                                                  dealerValue))
            time.sleep(0.5)
            if self.totalValue == 21 and len(self.cards) == 2:
                print("Blackjack pays 3 to 2! {} earns ${}!".format(self.player.name, self.bet * 3 // 2))
                self.player.money += self.bet * 5 // 2
            else:
                print("{} earns ${}!".format(self.player.name, self.bet))
                self.player.money += self.bet * 2
        elif self.totalValue == dealerValue:
            print("\n\t\tPUSH!")
            time.sleep(1)
            if self.player.isAI:
                print("{0} pushes the dealer. {0}'s bet is returned.".format(self.player.name))
            else:
                print("You push the dealer. Your bet of ${} is returned to you, {}.".format(self.bet, self.player.name))
            self.player.money += self.bet
        elif self.totalValue > 21:
            if self.player.isAI:
                print("\n{} has busted with a hand of {}.".format(self.player.name, self.totalValue))
            else:
                print("\nSorry {}, but your {} has busted. Your bet of ${} is lost.".format(self.player.name,
                                                                                            self.totalValue, self.bet))
        elif self.player.isAI:
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
def buildBlackjackDeck(totalSuits, totalValues, numberOfDecks):
    deck = []
    for _ in range(numberOfDecks):
        deck.extend(buildDeck(totalSuits, totalValues))
    return deck


# Shuffle the deck in place in a random order
def shuffleDeck(deckOfCards):
    random.shuffle(deckOfCards)


def openingDeal(deckOfCards, listOfPlayers, dealer, bets):
    dealer.createNewHand(0)
    dealer.hands[0].dealNewCard(deckOfCards)

    for player in listOfPlayers:
        if len(deckOfCards) < 12:
            deckOfCards = buildBlackjackDeck(suits, values, 6)
            shuffleDeck(deckOfCards)
            print("The dealer reshuffles the deck.")

        player.createNewHand(bets[playerList.index(player)])
        for hand in player.hands:
            print()
            hand.dealNewCard(deckOfCards)
            hand.dealNewCard(deckOfCards)
            time.sleep(1.5)


def playBlackjack(deckOfCards, playersList, dealer):
    fullDeckSize = len(deckOfCards)
    while True:
        allPlayersKickedOut = checkIfAllPlayersKickedOut(playersList)
        playersList = [player for player in playersList if 2 <= player.money <= 999999]
        if allPlayersKickedOut:
            return

        if len(deckOfCards) < fullDeckSize * 0.3:
            deckOfCards = buildBlackjackDeck(suits, values, 6)
            shuffleDeck(deckOfCards)
            print("The dealer reshuffles the deck.")
        newPlayerList = []
        bets = []
        for player in playersList:
            amountBet = acceptBet(player)
            if amountBet != 0:
                bets.append(amountBet)
                newPlayerList.append(player)
            time.sleep(1)
        playersList = newPlayerList
        if not playersList:
            checkIfAllPlayersKickedOut(playersList)
            return
        for player in playersList:  # del
            print(player.name, "AA")  # del
        print(bets) # del
        openingDeal(deckOfCards, playersList, dealer, bets)
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
                            deckOfCards = buildBlackjackDeck(suits, values, 6)
                            shuffleDeck(deckOfCards)
                            print("The dealer reshuffles the deck.")
                        continueDealing = hand.playerTurn(deckOfCards)
                    time.sleep(1)

        if any([hand.totalValue <= 21 for hand in player.hands] for player in playersList):
            print()
            dealer.hands[0].playerTurn(deckOfCards)
            time.sleep(1)

        for player in playersList:
            for hand in player.hands:
                hand.compareTotals(dealer.hands[0].totalValue)
        for player in playerList:
            checkMoney(player)
            player.resetHand()
        dealer.resetHand()


def getPlayers(listOfPlayers):
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
    for player in range(numberOfHumanPlayers):
        ordinalDict = {0: "first", 1: "second", 2: "third", 3: "fourth", 4: "fifth", 5: "sixth"}
        playerName = input("Please type in the name of the {} human player.  ".format(ordinalDict[player]))
        listOfPlayers.append(Player(playerName))
        time.sleep(0.5)

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
        for player in range(numberOfAIPlayers):
            ordinalDict = {0: "first", 1: "second", 2: "third", 3: "fourth", 4: "fifth", 5: "sixth"}
            playerName = input("Please type in the name of the {} AI player.  ".format(ordinalDict[player]))
            listOfPlayers.append(Player(playerName, isAI=True))
            time.sleep(0.5)
    return listOfPlayers


def checkMoney(player):
    if player.money < 2:
        print("I'm sorry {}, but you can no longer afford the minimum bet.".format(player.name))
        time.sleep(2)
    elif player.money > 999999:
        print("Congratulations on your winnings, {}! You're now a millionaire!".format(player.name))
        print("Unfortunately, you're going to bankrupt us at this rate, so we have to ban you from our tables.")
        time.sleep(2)


def checkIfAllPlayersKickedOut(playersList):
    if all(player.isAI for player in playersList):
        print("\n\nThank you so much for playing at our casino. Please, come again next payday.")
        return True
    return False


def acceptBet(player):
    while True:
        if player.isAI:
            print("\n{} bets the $2 minimum.".format(player.name))
            return 2
        else:
            amountBet = input("\n{}, place your bet! You have ${} to spend.\n"
                              "$2 minimum, $500 maximum. Input 'Q' to leave the "
                              "casino.  ".format(player.name, player.money))
            if amountBet.lower() == "q":
                return 0
            try:
                amountBet = int(amountBet)
                if 2 <= amountBet <= 500 and amountBet <= player.money:
                    return amountBet
                elif amountBet > player.money:
                    print("I'm sorry {}, but you cannot afford that bet.".format(player.name))
                else:
                    print("Please input a number between 2 and 500, or else 'q' to leave the casino.")
            except ValueError:
                print("Please input a number between 2 and 500, or else 'q' to leave the casino.")
            time.sleep(1)


suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
values = ["Ace", 2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King"]
tempValues = [3, 5, 6]
playerList = []

newDeck = buildBlackjackDeck(suits, values, 6)
shuffleDeck(newDeck)
playerList = getPlayers(playerList)
dealerAI = Player("Dealer", isAI=True, isDealer=True)
playBlackjack(newDeck, playerList, dealerAI)
