
import Computer
from Board import Game

#This function gets the player's move
def get_player_move(game):

    #we get all of the legal moves possible
    legal_moves = game.get_legal_moves()

    for index in range(len(legal_moves)):
        #and display them for the user
        print(str(index + 1) + ". ", end = "")
        print(legal_moves[index])

    while True:
        #and then prompt the user to choose a move
        move = input("Please enter a number from 1 to " + str(len(legal_moves)) + " to indicate which move you would like to make: ")

        if not(move.isdigit()) or int(move) not in list(range(1, len(legal_moves) + 1)):
            print("Invalid input, please try again\n")
            continue
        break


    return legal_moves[int(move) - 1]

#This function gets the settings from the user (time limit for program's search, game state, etc.)
def grab_settings():
    
    fname = None

    #we ask the user if they want to load a game state from a  file
    while(True):

        fname = input("Would you like to load in a game state from a file? (y/n) ")

        if fname != "y" and fname != "n":
            print("Invalid input, please try again")
            continue
        break

    #if they do then we prompt them for a filename
    if fname == "y":
        fname = input("Please enter in the filename where the game state is located: ")

            
    
    #we then ask them if they want the computer to play against itself
    while(True):

        comp = input("Would you like the computer to play against itself? (y/n) ")

        if comp != "y" and comp != "n":

            print("Invalid input, please try again")
            continue
        break

    #if no then we ask the user if they would like to play as black or white
    if comp == "n":
        while(True):
            player = input("Would you like to play as black (0) or white (1)? ")

            if player != "0" and player != "1":
                print("Invalid input, please try again")
                continue
            break
    #and if the user didn't give a filename then we load the default board and ask them how much time they would like to give
    #the computer
    if fname == "n":
        while(True):
        
            time = input("How much time would you like to give the computer? ")
            
        
        
            if(not time.isdigit()):
                print("Invalid input, please try again")
                continue
            break
    

    
    if fname != "n":
        game = Game(fname = fname)
    else:
        game = Game(fname = None, time = int(time), turn = 1)

    return game, comp, int(player)



def main():

    #we gret the settings from the user
    game, comp, player = grab_settings()

    print("\n")
    trn = 0
    old_rPieces = 0
    old_bPieces = 0
    while(True):

        #we check if the game is over
        over, winner = game.is_over()

        #if a player has won
        if over:
            #we let the user know and then terminate the program
            print("Congrats to " + winner + " for winning!")
            break

        #else we check to see if it's a draw. I decided to make it so that a draw would happen
        #when no pieces have been captured for 20 turns
        else:
            if winner[0] == old_rPieces and winner[1] == old_bPieces:
                trn += 1
            else:
                old_rPieces = winner[0]
                old_bPieces = winner[1]
                trn = 0
        

        if trn == 20:
            print("It's a draw!")
            break

        #A draw also occurs if none of the players have any legal moves
        legal_moves = game.get_legal_moves()
        game.turn = (game.turn + 1) % 2
        legal_moves += game.get_legal_moves()
        game.turn = (game.turn + 1) % 2

        if len(legal_moves) == 0:
            print("It's a draw!")
            break

        #if the computer is playing against itself
        if comp == "y":
            print("\n")
            print(game)
            print("\n")
            move = Computer.get_computer_move(game)

            if move == None:
                continue
            game.execute(move)
            print("\n")
            print(game)
            print("\n")
            move = Computer.get_computer_move(game)

            if move == None:
                continue
            game.execute(move)

            
        
        #if the player didn't want to go first
        if (player != game.turn):
            print("\n")
            print(game)
            print("\n")
            move  =Computer.get_computer_move(game)

            if move == None:
                continue
            game.execute(move)

            print("\n")
            print(game)
            print("\n")
            game.execute(get_player_move(game))


        
        else:
            print(game)
            print("\n")
            game.execute(get_player_move(game))

            print(game)
            print("\n")
            move = Computer.get_computer_move(game)
            if move == None:
                continue
            game.execute(move)


        
            
            
main()
    
        

                    
