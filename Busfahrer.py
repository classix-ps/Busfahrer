import numpy as np

def getRandomDeck(jokers=False):
    deck = np.array(list(np.arange(2, 15)) * 4)
    if jokers:
        deck = np.append(deck, [1, 1, 1])
    
    np.random.shuffle(deck)
    return deck

def simulateCards(runs=10000, threshold=5):
    results = np.zeros(3) # Right, Wrong, Fail
    
    for run in range(runs):
        deck = getRandomDeck()
        
        firstCard = deck[0]
        
        seenCards = deck[1:40]
        lowSeenCards = len(seenCards[seenCards < 8])
        highSeenCards = len(seenCards[seenCards > 8])
        
        if abs(lowSeenCards - highSeenCards) < threshold or firstCard == 8:
            results[2] += 1
        else:
            guess = False if highSeenCards > lowSeenCards else True
            if (firstCard > 8) == guess:
                results[0] += 1
            else:
                results[1] += 1
            
    return results

def simulateMonty(runs=10000):
    results = np.zeros(3) # Right, Wrong, Fail
    
    doors = [True, False, False]
    for run in range(runs):
        doorChoice = np.random.randint(3)
        openDir = 2 * np.random.randint(2) - 1
        doorOpen = (doorChoice + openDir) % len(doors)
        doorLast = (doorChoice - openDir) % len(doors)
        
        if doors[doorOpen] == True:
            results[2] += 1
        else:
            if doors[doorLast] == True:
                results[0] += 1
            else:
                results[1] += 1
                
    return results

#print("Chance to guess card correctly after randomly seeing cards: ", simulateCards(100000))
#print("Chance to guess door correctly after randomly opening door: ", simulateMonty())

class Card:
    def __init__(self, suit, val):
        self.suit = suit
        self.val = val
        
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.val == other.val
        return False
        
    def getVal(self):
        return self.val
        
    def getColor(self):
        return 1 if self.suit in ["Spades", "Clubs"] else -1
        
    def show(self):
        print(f"{self.val} of {self.suit}")

class Deck:
    def __init__(self, jokers=False):
        if jokers:
            self.cards = np.empty(shape=(55,), dtype=object)
        else:
            self.cards = np.empty(shape=(52,), dtype=object)
        self.build(jokers)
        self.shuffle()
        
    def build(self, jokers=False):
        pos = 0
        for suit in ["Spades", "Clubs", "Diamonds", "Hearts"]:
            for val in range(2, 15):
                self.cards[pos] = Card(suit, val)
                pos += 1
        
        if jokers:
            while pos < len(self.cards):
                self.cards[pos] = Card("Spades", 1)
                pos += 1
                
    def shuffle(self):
        np.random.shuffle(self.cards)
        
    def length(self):
        return len(self.cards)
        
    def draw(self, count = 1):
        drawn = self.cards[0:count]
        self.cards = np.delete(self.cards, np.arange(count))
        return drawn
        
    def removeCards(self, toRemove):
        toRemoveIndices = []
        for i, card in enumerate(self.cards):
            if card in toRemove:
                toRemoveIndices.append(i)
                
        self.cards = np.delete(self.cards, toRemoveIndices)
        
    def getAverageVal(self):
        sum = 0
        for card in self.cards:
            sum += card.getVal()
        return sum / self.length()
        
    def getCompareVal(self, compare, remainingBoard):
        sum = 0
        for card in np.concatenate([self.cards, remainingBoard]):
            sum += 1 if card.getVal() > compare else -1
        return compare + sum / self.length()        
        
    def getAverageColor(self, remainingBoard=np.empty(0)):
        sum = 0
        for card in np.concatenate([self.cards, remainingBoard]):
            sum += card.getColor()
        return sum / self.length()
        
    def show(self):
        for card in self.cards:
            card.show()

def drive(boardSize=8, jokers=False, memory=False, reshuffle=False, verbose=False):
    deck = Deck(jokers)
    results = np.zeros(2) # Total boards, total cards

    origAvgColor = deck.getAverageColor()
    origAvgVal = deck.getAverageVal()

    cleared = boardSize
    board = np.empty(shape=(boardSize,), dtype=object)
    while True:
        while deck.length() > cleared:
            drawn = deck.draw(cleared)
            board[0:len(drawn)] = drawn
            
            cleared = 0
            while cleared < boardSize:
                if cleared == 0: # Guess color
                    avgColor = deck.getAverageColor(board[cleared:]) if memory else origAvgColor
                    if avgColor > 0:
                        guess = 1
                    elif avgColor < 0:
                        guess = -1
                    else:
                        guess = 2 * np.random.randint(2) - 1
                        
                    if verbose:
                        print(avgColor, guess, board[cleared].getColor())
                    
                    if board[cleared].getColor() == guess:
                        cleared += 1
                    else:
                        cleared += 1
                        results[0] += cleared
                        results[1] += 1
                        break
                else: # Guess higher or lower
                    avgVal = deck.getCompareVal(board[cleared-1].getVal(), board[cleared:]) if memory else origAvgVal
                    if avgVal > board[cleared-1].getVal():
                        guess = True
                    elif avgVal < board[cleared-1].getVal():
                        guess = False
                    else:
                        guess = True if np.random.randint(2) else False
                    
                    if verbose:
                        print(avgVal, board[cleared-1].getVal(), guess, board[cleared].getVal())
                    
                    if (board[cleared].getVal() > board[cleared-1].getVal() and guess) or (board[cleared].getVal() < board[cleared-1].getVal() and not guess):
                        cleared += 1
                    else:
                        cleared += 1
                        results[0] += cleared
                        results[1] += 1
                        break
            else:
                results[0] += cleared
                results[1] += 1
                return results
                
        if reshuffle == False:
            break
            
        remainingCards = np.copy(board[cleared:])
        deck = Deck(jokers)
        deck.removeCards(remainingCards)
    
    results[0] = 0
    return results

def runDrives(runs=1000):
    boardSizes = [10]
    jokersUsed = [True]
    memoryUsed = [True, False]
    reshuffleUsed = [True, False]
    
    for boardSize in boardSizes:
        for jokers in jokersUsed:
            print(f"{boardSize}-Card Busfahrer with jokers")
            for reshuffle in reshuffleUsed:
                for memory in memoryUsed:
                    results = np.zeros((runs, 2))
                    for run in range(runs):
                        results[run, :] = drive(boardSize, jokers, memory, reshuffle)
                        
                    print("With{mem} memorizing encountered cards and with{re} reshuffling after deck is depleted".format(mem="" if memory else "out", re="" if reshuffle else "out"))
                    if reshuffle:
                        avgCards = sum(results[:, 0]) / runs
                        avgBoards = sum(results[:, 1]) / runs
                        print("\tAverage cards encountered: {:.2f}".format(avgCards))
                        print("\tAverage boards refilled (\u2263 Schlücke): {:.2f}".format(avgBoards))
                    else:
                        winChance = np.count_nonzero(results[:, 0]) / runs
                        avgBoards = sum(results[:, 1]) / runs
                        print("\tChance of winning before deck is depleted: {:.2f}%".format(winChance * 100))
                        print("\tAverage boards refilled (\u2263 Schlücke): {:.2f}".format(avgBoards))

import matplotlib.pyplot as plt
def plotDrives(runs=1000, maxBoard=21):
    fig, axs = plt.subplots(1, 2)
    fig.suptitle(f"Busfahrer comparison for board sizes in interval [1, {maxBoard-1}]")

    boardSizeRange = range(1, maxBoard)
    jokersUsed = [True]
    memoryUsed = [True, False]
    reshuffleUsed = [True, False]
    
    for jokers in jokersUsed:
        for i, reshuffle in enumerate(reshuffleUsed):
            for memory in memoryUsed:
                ys = np.zeros(len(boardSizeRange))
                for boardSize in boardSizeRange:
                    results = np.zeros((runs, 2))
                    for run in range(runs):
                        results[run, :] = drive(boardSize, jokers, memory, reshuffle)
                        
                    ys[boardSize-1] = sum(results[:, 0]) / runs if reshuffle else (np.count_nonzero(results[:, 0]) / runs) * 100
                    
                axs[i].plot(boardSizeRange, ys, label = "{mem}".format(mem="Memory" if memory else "No memory"))
                axs[i].set_title("{re}".format(re="Reshuffle" if reshuffle else "No reshuffle"))
                axs[i].legend()
                if reshuffle:
                    axs[i].set(xlabel = "Board size", ylabel = "Number of cards encountered until win")
                else:
                    axs[i].set(xlabel = "Board size", ylabel = "Win chance (in %)")
    
    plt.show()

#print(drive(8, True, True, True, True))
#print(drive(8, True, False, True, True))
#runDrives(1000000)
plotDrives(10000, 16)