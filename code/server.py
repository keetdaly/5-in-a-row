from http.server import HTTPServer, BaseHTTPRequestHandler
from ctypes import c_int64
from socketserver import ThreadingMixIn
import cgi
import json
import pickle
import numpy as np

class ThreadingServer(ThreadingMixIn, HTTPServer):
    pass

class ServerHandler(BaseHTTPRequestHandler):
    
    # Counter for checking who's turn it is
    counter = c_int64(0)
    gameState = {'board': np.zeros((6,9)).tolist(), 'win': False, 'players': [], 'counter': counter.value}
    
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    def do_GET(self):
        '''
        Handles GET requests
        '''
        self._set_headers()
        if self.path == '/state':
            self.get_state()
        elif self.path == '/turn':
            self.get_turn()
        elif self.path == '/reset':
            self.reset()
    
    def get_state(self):
        '''
        Returns game state
        '''
        self.wfile.write(pickle.dumps(json.dumps(self.gameState)))
    
    def get_turn(self):
        '''
        Returns the player who's turn it is
        '''
        player = self.gameState['players'][self.counter.value]
        data = {'name': player}
        self.wfile.write(pickle.dumps(json.dumps(data)))
        
    def do_POST(self):
        '''
        Handles POST requests
        '''
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        
        # Refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # Read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        message = json.loads(pickle.loads(self.rfile.read(length)))
        
        self._set_headers()
        if self.path == '/player':
            self.add_player(message)
        elif self.path == '/move':
            self.make_move(message)
        elif self.path == '/remove':
            self.remove_player(message)
        
    def add_player(self, message):
        '''
        Input: message containing name of player
        Output: confirmation message for connection
        '''
        player_name = message['name']
        self.gameState['players'].append(player_name)
        response = {'response':'You are now connected!'}
        self.wfile.write(pickle.dumps(json.dumps(response)))
        
    def make_move(self, message):
        '''
        Input: message containing column to put chip in
        Output: returns new game state after move is made
        '''
        col = int(message['col']) - 1
        board = np.array(self.gameState['board'])
        # Negative row indexing to start at bottom
        for row in range(-1, -7, -1):
            if(board[row, col] == 0):
                if((self.counter.value) == 0):
                    board[row, col] = 1
                    break
                else:
                    board[row, col] = 2
                    break

        self.gameState['win'] = self.check_for_winner(board, self.counter.value + 1)
        self.gameState['counter'] = self.increment_counter()
        self.gameState['board'] = board.tolist()
        self.wfile.write(pickle.dumps(json.dumps(self.gameState)))
        
    def remove_player(self, message):
        '''
        Input: message containing user to remove
        Output: message confirming disconnection
        Method also resets the game state upon disconnection of a player
        '''
        name = message['name']
        self.gameState['players'].remove(name)
        response = {'response': 'You have been removed from the server successfully'}
        print(self.gameState['players'])
        self.reset_game()
        self.wfile.write(pickle.dumps(json.dumps(response)))
        
    def reset(self):
        '''
        Method to reset the game state
        Output: game state after reset
        '''
        self.reset_game()
        self.wfile.write(pickle.dumps(json.dumps(self.gameState)))
            
    def reset_game(self):
        '''
        Reset game without HTTP response
        '''
        self.counter.value = 0
        self.gameState['board'] = np.zeros((6,9)).tolist()
        self.gameState['win'] = False

    def increment_counter(self):
        self.counter.value = (self.counter.value + 1) % 2
        return self.counter.value
        
    def check_for_winner(self, board, numCheck):
        '''
        Input: game board and player number to check
        Output: boolean for whether there is a winner or not
        '''
        
        # horizontal
        for x in range(0, 6):
            for y in range(0, 5):
                if(board[x, y] == numCheck and board[x, y+1] == numCheck and board[x, y+2] == numCheck and board[x, y+3] == numCheck and board[x, y+4] == numCheck):
                    return True            
        # vertical 
        for x in range(0, 2):
            for y in range(0, 9):
                if(board[x, y] == numCheck and board[x+1, y] == numCheck and board[x+2, y] == numCheck and board[x+3, y] == numCheck and board[x+4, y] == numCheck):
                    return True
    
        # positive diagonal /
        for x in range(0, 2):
            for y in range(4, 9):
                if(board[x, y] == numCheck and board[x+1, y-1] == numCheck and board[x+2, y-2] == numCheck and board[x+3, y-3] == numCheck and board[x+4, y-4] == numCheck):
                    return True
            
        # negative diagonal \
        for x in range(0, 2):
            for y in range(0, 5):
                if(board[x, y] == numCheck and board[x+1, y+1] == numCheck and board[x+2, y+2] == numCheck and board[x+3, y+3] == numCheck and board[x+4, y+4] == numCheck):
                    return True
        
        return False

def run(server_class=ThreadingServer, handler_class=ServerHandler, addr='localhost', port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f'Starting http server on {addr}:{port}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Ctrl + C pressed, shutting down')


if __name__ == '__main__':
    run()