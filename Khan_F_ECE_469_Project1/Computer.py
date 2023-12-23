from copy import deepcopy
import signal
import time
import random


#####NODE CLASS#####

#This class bundles the current game state, the move that was made, and the score for the game state
class Node:

    def __init__(self, game, move, value):
        self.game =game
        self.move= move
        self.value = value

#To limit the program's search to a certain amount of time
#we can use the SIGALRM signal
class TimeoutException(Exception):
    pass

#we create a handler function so that when the program receives the signal
#it raises a TimeoutException
def timeout_handler(signal, frame):
    raise TimeoutException


#we set our signal handler
signal.signal(signal.SIGALRM, timeout_handler)

    
MAX_DEPTH = 30


#This function is a wrapper for our heuristic
def evaluate(game, maximizer, depth):

    #The evaluation function has two parts to it, one for evaluating the endgame
    #and for the opening and midgame. 
    over, pieces = game.is_over()

    #If there are less than 5 pieces on the board then we consider that when the endgame
    #begins.
    if pieces == "Black" or pieces == "Red" or (pieces[0] + pieces[1]) < 5:
        return endgame(game, maximizer, depth)
    
    return earlygame(game,maximizer)

#This function implements our heuristic for the early gamew
def earlygame(game, maximizer):
    
    def valid(x,y):
        return ((0 <= x < 8) and (0 <= y < 8))

    #We initalize all of the components in our evaluation function
    soldiers = 0
    kings= 0
    bRow = 0
    mBox = 0
    mRow = 0
    threatened = 0
    defended = 0
    diff = 0

    delx = [1, 1, -1, -1]
    dely = [1, -1, 1, -1]

    #we go through each square in the board
    for row in range(8):
        for col in range(8):
            #if the square is empty, we skip it
            if game.Board[row][col] == 0:
                continue
            #else if the current piece we're on belongs to the maximizer
            #all of the metrics that we calculate will be subtracted from the total heuristic score
            #since they're advantagous for the minimizer
            sign = -1
            if game.Board[row][col] %2  == maximizer:
                sign = 1

            #if the piece is a soldier
            if game.Board[row][col] <= 2:
                #then we add it to our soldier score
                soldiers += sign
            #else the piece is a king and we add it to the corresponding score
            else:
                kings += sign

            #we then check to see how many pieces are in the back row. In the mid game, it's generally a
            #good idea to not move the pieces in the back row since we want to stop the opponent's pieces from being promoted
            if sign == 1 and ((row == 0 and maximizer == 1) or (row == 7 and maximizer == 0)):

                bRow += 1

            #we then check to see which side controls the middle box in the board
            #This is a really important region because the pieces here have the most freedom to move.
            
            if row == 3 or row == 4:

                if col >= 2 and col < 6:
                    mBox += sign
                #we then also check to see which side controls the center rows outside of the box
                #since the player that controls these rows can stop the other player from promoting their pieces
                else:
                    mRow += sign

            #finally we check to see how many pieces oon the board are vulnerable (can be captured) and how many are protected
            #have an opposing piece but have a piece backing it from behind or are against an edge
            
            myDirection = -1
            if maximizer == 1:
                myDirection = 1
            vul = False

            #we check every possible move that the piece can make
            for idx in range(4):
                x = row + delx[idx]
                
                y = col + dely[idx]

                n = row - delx[idx]

                m = col - dely[idx]
                
                opDirection = abs(x-n)/(x-n)

                #if an opposing piece is able to attack us
                #we set vul to true
                if valid(x,y) and game.Board[x][y] != 0 and game.Board[x][y] % 2 !=  maximizer and valid(n, m) and game.Board[n][m] == 0 and (game.Board[x][y] > 2 or myDirection != opDirection):
                    vul = True
                    break
            #else we're defended. It's good to incentivize the computer to be in these kinds of positions
            #because it encourages it to find ways to get to the opponent's side of the board and hopefully get promoted
            if vul:
                threatened += sign
            else:
                defended += sign

    #we also check to see how restricted each player is by looking at how many moves each side can be made
    #This is a pretty expensive operation but in my opinion I think it was worth it
    moves1 = len(game.get_legal_moves())
    game.turn = (game.turn + 1) % 2
    moves2 = len(game.get_legal_moves())
    game.turn = (game.turn + 1) % 2

    
    if game.turn == maximizer:
        diff = moves1 - moves2
    else:
        diff = moves2 - moves1

    #we take all of the metrics that we have made and create a weighted sum as our evaluation
    return soldiers*1500 + kings*3000 + bRow*400 + mBox*250 + mRow*50  + 300*defended + 300*diff -300*threatened


#This function implements our evaluation function for the endgame
def endgame(game, maximizer, depth):

    #we initialize our scores
    soldiers = 0
    kings = 0
    victory = 0
    distance = 0
    corner = 0

    #because there are fewer pieces in the end game, there aren't as many opportunities for capturing
    #which means with the early game evaulation function, our program would think that a lot of the moves would seem
    #equally valid even though they aren't


    #one metric that we can use to give the program more direction in the endgame is the total distance between the red and black pieces
    #If a player has more pieces then they should attack the opponent else they should run away
    max_pieces = []
    min_pieces = []

    #for each square
    for row in range(8):
        for col in range(8):
            
            if game.Board[row][col] == 0:
                continue
            sign = -1

            #we get the positions of the red and black pieces
            if game.Board[row][col] %2 == maximizer:
                sign = 1
                max_pieces.append((row, col))
            else:
                min_pieces.append((row, col))

            #and then also look at the number of soldiers and kings
            if game.Board[row][col] == 1:
                #additionally if there are any remaining soldiers then we want to incentivize the program to get them promoted
                soldiers += sign*(1 + row/8)
            if game.Board[row][col] == 2:
                soldiers += sign*(1 + (7 - row/8))
            if game.Board[row][col] > 2:
                kings += sign

    #we calculate the distance between the minimizer's and maximizer's pieces
    for max_piece in max_pieces:
        for min_piece in min_pieces:
            
            distance += abs(max_piece[0] - min_piece[0]) + abs(max_piece[1] - min_piece[1])


    if len(max_pieces) >= len(min_pieces):
        distance *= -1

        #We create a score that incentivizes the program to use the top left and bottom right corners if they have fewer pieces
        #and if the computer has more pieces, to drive out enemy pieces in the corner
        for min_piece in min_pieces:

            #In order to get an opposing piece out of the corner, we want one of the computer's pieces to occupy the other corner square so that the opposing piece is forced to move out
            #This is very important for resolving 2 King, 1 King endgames
            if (min_piece == (0, 1) and game.Board[1][0] == 0) or (min_piece == (1, 0) and game.Board[0][1] == 0) or (min_piece == (6,7) and game.Board[7][6] == 0) or (min_piece == (7,6) and game.Board[6][7] == 0):
                corner -= 1

    else:
        for max_piece in max_pieces:
            if (max_piece == (0, 1) and game.Board[1][0] == 0) or (max_piece == (1, 0) and game.Board[0][1] == 0) or (max_piece == (6,7) and game.Board[7][6] == 0) or (max_piece == (7,6) and game.Board[6][7] == 0):
                corner += 1


    #finally we incentivize the computer to go for a quick victory if it's winning
    #and to delay a loss for as long as possible if it's losing
    if (game.is_over()[1] == "Black" and maximizer == 1) or (game.is_over()[1] == "White" and maximizer == 0):
        victory -= 1200 - depth*100
    elif (game.is_over()[1] == "White" and maximizer == 1) or (game.is_over()[1] == "Black" and maximizer == 0):
        victory += 1200 - depth*100

    
    return corner*300 + soldiers*2000 + kings*4000  + distance*100  + victory
    


#In this function, the program uses the minimax algorithm to find the best move to make
def get_computer_move(game):

    #we get the list of our legal moves
    legal_moves = game.get_legal_moves()

    #if the list is empty we terminate and return None
    if len(legal_moves) == 0:
        return None

    #and if we only have one move we can make we don't perform a search and just return that move
    if len(legal_moves) == 1:
        print("Searched to a depth of 0")
        print("Time taken: 0 seconds")
        return legal_moves[0]

    #we store the nodes correpsonding to each possible game state after we make a move in a list
    nodes = []

    for move in legal_moves:

        new_game = deepcopy(game)

        

        new_game.execute(move)
        nodes.append(Node(new_game, move, evaluate(new_game, game.turn, 0)))
        


    #we start our alarm for however many seconds the user gave us
    start = time.time()
    signal.alarm(game.time)

    try:
        #then we perform iterative deepening
        for depth in range(MAX_DEPTH):
            
            nodes.sort(key = lambda x: x.value, reverse = True)
            for node in nodes:
                #and perform the minimax algorithm with each possible game state after we make a move being the root of the tree that we search
                node.value = minimax(deepcopy(node.game), float("-inf"), float("inf"), depth, game.turn)

    #if while searching we run out of time
    except TimeoutException:
        signal.alarm(0)
    
    signal.alarm(0)
    #we notify the user how far into the game tree we were able to get and the amount of time it took
    elapsed = time.time() - start
    print("Searched to a depth of " + str(depth + 1))
    print("Total time taken: " + str(round(elapsed, ndigits = 5))  +" seconds")

    #and then we get the best move from our search and break ties randomly
    best_moves = [node for node in nodes if nodes[0].move == node.move]

    
    return random.choice(best_moves).move


#Here we implement the minimax algorithm with alpha beta pruning
def minimax(game, alpha, beta, depth, maximizer, isMax = True):
    
    #if we've reached the maximum depth or we reached a terminal node
    if depth == 0 or game.is_over()[0]:
        #we evaluate the game state and return it
        return evaluate(game, maximizer, depth)
        
    
    #else we get the children of the node
    legal_moves = game.get_legal_moves()

    children = []

    for move in legal_moves:

        new_game = deepcopy(game)

        new_game.execute(move)
        children.append(new_game)

    
    if isMax:
        #and then recursively apply the algorithm to the children
        value = float("-inf")

        for child in children:

            value=  max(value, minimax(child, alpha, beta, depth - 1, maximizer, isMax = False))

            #and if we find a value greater than beta, we stop searching since the minimizer will never go down here
            if value >= beta:
                return value
            
            alpha = max(alpha, value)

        return value


    else:
        value = float("inf")

        for child in children:

            value = min(value, minimax(child, alpha, beta, depth - 1, maximizer, isMax = True))

            if value <= alpha:
                return value

            beta = min(beta, value)
            
        return value
    
    
    
                
        

        
        
