from copy import deepcopy

############GAME CLASS############

#This class holds the current game state such as:
#the board, the current turn, and the amount of time
#that the program has to choose its move
class Game:

    #We initalize the game either from the beginning
    #or from a file that contains the current state of the board
    #as well as whose turn it is and the time limit
    def __init__(self, fname = None, turn = None, time = None):

        #if no filename is given
        if fname == None:

            #we start the game from the beginning
            self.Board = [ [0 for i in range(8)] for j in range(8)]
            
            self.Board[0] = [0, 1, 0, 1, 0, 1, 0, 1]
            self.Board[1] = [1, 0, 1, 0, 1, 0, 1, 0]
            self.Board[2] = [0, 1, 0, 1, 0, 1, 0, 1]

            self.Board[5] = [2, 0, 2, 0, 2, 0, 2, 0]
            self.Board[6] = [0, 2, 0, 2, 0, 2, 0, 2]
            self.Board[7] = [2, 0, 2, 0, 2, 0, 2, 0]

            self.turn = turn
            self.time = time

    
        else:
            #else we load up the game state from the given file
            f = open(fname)

            board_text = f.read().replace(" ", "").replace("\n", "")

            self.Board = [ [0 for i in range(8)] for j in range(8)]

            index = 0
            for row in range(8):
                for col in range(8):

                    if row % 2 != col % 2:
                        self.Board[row][col] = int(board_text[index])

                        index += 1

            f.close()
            self.turn = int(board_text[index]) % 2

            self.time = int(board_text[index + 1:])
                        

    #This function displays our board in an easy to read format
    def __str__(self):
        disp = ""

        #we go through each square
        for row in range(8):
            for col in range(8):

                #white king on red square
                #white pawn on red square
                #black pawn on red square
                #black pawn on black square
                #no piece on red square
                disp += "\x1b["

                #if the row and col # have the same parity then we're on a black square
                if row % 2 == col %2:
                    disp += "0;30;40m       "

                else:
                    #else we have 5 different cases where the displays are slightly different
                    match self.Board[row][col]:

                        #we either have a blank red square
                        case 0:
                            disp += "2;31;41m       "
                        ##a red piece on a red square (which we color as white)
                        case 1:
                            disp += "2;37;41m   O   "

                        #black piece on a red square
                        case 2:
                            disp += "2;30;41m   O   "

                        #red king on a red square
                        case 3:
                            disp += "2;37;41m   \u03A6   "

                        #and a black king on a red square
                        case 4:
                            disp += "4;30;41m   \u03A6   "
                
                disp += "\x1b[0m"
            #at the end of each row, we display the row #
            disp += " " + str(row) + "\n"
            
        #and then on the bottom, we print out the column #
        return disp + "   0      1      2      3      4      5      6      7"

    #This function gets all of the legal  moves that the player whose turn it is can make (player A)
    def get_legal_moves(self):

        legal_moves = []

        #We go through every position in the board and check to see if there are any legal moves
        #that start at that position which is what the helper function does

        #move stores the chain of actions performed, board is the current state of the board, jump is if in the chain we had performed a jump,
        #and terminate is if we have reached the end of the chain
        def helper(self, move,  board, jump = False, terminate = False):

            #if we've reached the end of the move
            if terminate:
                #we append the move to our list of legal moves
                legal_moves.append(tuple(move))
                return None
            
            
            row, col =move[-1][0], move[-1][1]

            #if player A doesn't have a piece on the start square, there aren't any legal moves
            #so we terminate
            if board[row][col] == 0 or board[row][col] % 2 != self.turn:
                return None

            #we set the list of actions possible depending on what piece is on the current square
            match board[row][col]:

                case 1:
                    directions = [(1, -1), (1, 1)]
                case 2:
                    directions = [(-1, 1), (-1, -1)]
                case _:
                    directions = [(1, 1), (1, -1), (-1, -1), (-1, 1)]

            #if we aren't doing a jump
            if not jump:
                #then we try out every possible non-capture move from the current position
                for dr, dc in directions:
                
                    new_row, new_col = row + dr, col + dc
                    
                    if 0 <= new_row < 8 and 0 <= new_col < 8:

                        #if the move is within the bounds of the board and we're not moving into an empty square
                        if board[new_row][new_col] == 0:
                            #we set the terminate flag and append the move to our list
                            helper(self, move +  [(new_row, new_col)], board, terminate = True)

            #once we have found every non capture move, we then look at all of the moves involving jumps
            #we try out every possible jump
            for dr, dc in directions:

                #and check to see if any of them are legal
                mid_row, mid_col = row + dr, col + dc
                new_row, new_col = row + dr*2, col + dc*2


                #we check to see if the space we're jumping into is empty and if the square that we're jumping over has an opposing piece
                if (0 <= new_row < 8) and (0 <= new_col < 8) and (board[new_row][new_col] == 0 and board[mid_row][mid_col] != 0 and board[mid_row][mid_col] % 2 != self.turn):
                    
                    #if we were moving a soldier and it reached the back row, then our move finishes and we terminate and add the move to the list
                    if (board[row][col] == 1 and row == 7) or (board[row][col] == 2 and row == 0):

                        
                        helper(self, move + [(new_row, new_col)], board, jump = True, terminate = True)

                    #else we mark the jump on the board
                    new_board = deepcopy(board)
                    
                    new_board[new_row][new_col], new_board[row][col] = new_board[row][col], new_board[new_row][new_col]
                    new_board[mid_row][mid_col] = 0
                    
                    
                    
                
                    #and then call on our helper function to see if there are any further jumps that can be made
                    helper(self, move + [(new_row, new_col)], new_board, jump = True)

            #we check to see if there are any jumps that can be made
            term = True  
            for dr, dc in directions:
                mid_row, mid_col = row + dr, col + dc
                new_row, new_col = row + dr*2, col + dc*2

                
                if (0 <= new_row < 8) and (0 <= new_col < 8) and (board[new_row][new_col] == 0 and board[mid_row][mid_col] != 0 and board[mid_row][mid_col] % 2 != self.turn):
                    term = False
            #if there are then the move is incomplete and we don't count it
            if jump and term:
                #but if it is then we add it to the list
                legal_moves.append(tuple(move))

        #we call on our helper function on each of the squares in our board
        for row in range(8):
            for col in range(8):
                helper(self, [(row, col)], self.Board)
        
        #legal_moves = sorted(list(set(legal_moves)), key = lambda x: abs(x[0][0] - x[1][0]))


        #if a jump is possible then it has to be made so we remove any non-capture moves
        #from our list
                
        legal = []
        for index in range(len(legal_moves)):

            if abs(legal_moves[index][0][0] - legal_moves[index][1][0]) > 1:
                legal.append(legal_moves[index])
            
        
        if legal == []:
            return legal_moves
        return legal

    #This function executes the given move on our board
    def execute(self, move):

        #if the piece isn't a king and the move ends with the piece reaching the backrow then we promote it to king
        if (self.Board[move[0][0]][move[0][1]]  == 1 and move[-1][0] == 7) or (self.Board[move[0][0]][move[0][1]] == 2 and move[-1][0] == 0):
            self.Board[move[0][0]][move[0][1]] += 2

        #if we have a non-capture move
        if abs(move[0][0] - move[1][0]) == 1:

            #we move our piece and increment the turn count
            self.Board[move[0][0]][move[0][1]], self.Board[move[1][0]][move[1][1]] = self.Board[move[1][0]][move[1][1]], self.Board[move[0][0]][move[0][1]]
            self.turn = (self.turn + 1) %2
            return None

        
        #else we go through the sequence of jumps
        for index in range(len(move) - 1):

            #move up the piece
            self.Board[move[index][0]][move[index][1]], self.Board[move[index + 1][0]][move[index+1][1]] = self.Board[move[index + 1][0]][move[index+1][1]], self.Board[move[index][0]][move[index][1]]

            #and then remove the piece that was captured from the board
            self.Board[(move[index][0] + move[index + 1][0]) //2][ (move[index][1] + move[index+ 1][1])//2] = 0

        self.turn = (self.turn + 1) %2

    #This function checks to see if someone has won the game
    def is_over(self):
        
        rPieces = 0
        bPieces = 0

        #we go through the board and check to see how many red and black pieces there 
        for row in range(8):
            for col in range(8):

                if self.Board[row][col] == 0:
                    continue
                if self.Board[row][col] %2 == 0:
                    bPieces += 1
                else:
                    rPieces += 1
        #if there are no red pieces, black wins
        if rPieces == 0:
            return True, "Black"
        #and if there are no black pieces, red wins
        if bPieces == 0:
            return True, "Red"
        #else we return False and a tuple containing the count of the # of pieces for each side
        return False, (rPieces, bPieces)
