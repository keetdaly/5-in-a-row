import requests
import pickle
import json
import numpy as np
import atexit

def print_board(board):
    board = np.array(board)
    for i in range(0,6):
        for j in range(0, 9):
            if(board[i, j] == 0):
                print('[ ]', end=' ')
            elif(board[i, j] == 1):
                print('[X]', end=' ')
            else:
                print('[O]', end=' ')
        # Go to next line
        print()
        
def remove_name(session, url, headers, name):
    '''
    Input: session object, url as string, headers as dict, name as dict
    Output: response for successful removal
    Makes API call to server to remove player name when user disconnects
    '''
    remove_req = session.post(url, headers=headers, data=pickle.dumps(json.dumps(name)))
    response = json.loads(pickle.loads(remove_req.content))
    print(response['response'])
    print('Disconnecting...')
        
def reset_game(session, url):
    '''
    Input: session object, url as string
    Output: game state after reset
    Makes API call to server to reset game state for other player upon disconnection
    '''
    print('Resetting game state')
    reset_req = session.get(url)
    state = json.loads(pickle.loads(reset_req.content))
    return state

if __name__ == '__main__':
    
    # Strings to hold server URL and header info + API paths
    url = 'http://localhost:8000'
    header = {'content-type': 'application/json'}
    get_state = '/state'
    get_turn = '/turn'
    get_reset = '/reset'
    post_player = '/player'
    post_move = '/move'
    post_remove = '/remove'
    
    
    s = requests.Session()
    
    name = input('Enter your name: ')
    data = {'name': name}
    add_player_req = s.post(url + post_player, headers=header, data=pickle.dumps(json.dumps(data)))
    add_player_resp = json.loads(pickle.loads(add_player_req.content))
    print(add_player_resp['response'])
    
    # Register functions to run when process ends
    atexit.register(remove_name, s, url + post_remove, header, data)
    atexit.register(reset_game, s, url + get_reset)
    
    # Request board for start of game 
    print('Requesting board')
    state_req = s.get(url + get_state)
    board = json.loads(pickle.loads(state_req.content))['board']
    print_board(board)
     
    # Main game loop
    while(True):
        
        # Get list of players
        players_req = s.get(url + get_state)
        players_list = json.loads(pickle.loads(players_req.content))['players']
        
        # Wait until 2 players are connected
        if(len(players_list) < 2):
            print('Waiting for another player to connect...')
            while(True):
                state_req = s.get(url + get_state)
                players_list = json.loads(pickle.loads(state_req.content))['players']
                if(len(players_list) == 2):
                    # Break out of waiting loop
                    break
            print("Two players connected, the game will now begin!")
        
        # Get player turn  
        turn_req = s.get(url + get_turn)
        turn = json.loads(pickle.loads(turn_req.content))
        turn_name = turn['name']
        # Wait for other player to take their turn
        if(turn_name != name):
            print('Waiting for ' + turn_name + ' to make a move')
            while(True):
                turn_req = s.get(url + get_turn)
                turn_name = json.loads(pickle.loads(turn_req.content))['name']
                if(turn_name == name):
                    # Break out of waiting loop
                    break
            
            # Get state of game after other player makes move
            state_req = s.get(url + get_state)
            state = json.loads(pickle.loads(state_req.content))
            board = state['board']
            players = state['players']
            counter = state['counter']
            
            # Check for winner
            if(state['win']):
                print_board(board)
                print('You have lost, ' + players[(counter + 1) % 2] + ' is the winner!')
                play_again = input('Would you like to play again? (y/n): ')
                if(play_again == 'y'):
                    state = reset_game(s, url + get_reset)
                    print_board(state['board'])
                    # Restart game loop
                    continue
                else:
                    break
                
            print_board(board)
                
        # Input move
        col = input('Please enter a column ' + name + ' (1-9): ')
        data = {'col':col}
        move_req = s.post(url + post_move, headers=header, data=pickle.dumps(json.dumps(data)))
        new_state = json.loads(pickle.loads(move_req.content))
        
        # Check for winner
        if(new_state['win']):
            print_board(new_state['board'])
            print('You have won!')
            play_again = input('Would you like to play again? (y/n): ')
            if(play_again == 'y'):
                state = reset_game(s, url + get_reset)
                print_board(state['board'])
                continue
            else:
                break

        print_board(new_state['board'])