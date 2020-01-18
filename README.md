# 5-in-a-row
This repository holds an implementation of the game 5-in-a-row written in Python, which is played from a command line interface. The `requests` module is required for the client to work. This can be installed using the following command :

`pip install requests`

The clients communicate with a server via HTTP requests. The server contains the business logic of the game as well as the state. Requests are made to the server to alter and retrieve the game state. 

# How to play
To start the server, use the following command:

`$ python server.py`

This will start an instance of the server at `localhost:8000`. After this, two client instances can be started in separate command line interfaces using the following command:

`$ python client.py`

Once two players are connected, they take turns entering a number from 1-9 to put a token into a column. The first player to have 5 tokens in a row horizontally, vertically or diagonally wins. Players are then asked if they would like to play again. 
