import socket
import threading
import random
import time

# Server configuration
HOST = "0.0.0.0"
PORT = 5689
BUFFER_SIZE = 1024
MIN_PLAYERS = 2
WAIT_FOR_PLAYERS = 20
QUESTION_DELAY = 10
ANSWER_TIMEOUT = 10

# Question database
questions_db = {
    "What is the capital of France?": "Paris",
    "Who wrote 'Hamlet'?": "Shakespeare",
    "What is 5 + 7?": "12",
    "What is the boiling point of water (Celsius)?": "100",
    "Which planet is known as the Red Planet?": "Mars",
}

# Global storage for clients and scores
clients = {}  # Stores (address: username)
scores = {}  # Stores (address: score)
answers_per_client = {}  # Stores (address: [answers])


def broadcast(message, exclude=None):
    """
    Sends a message to all connected clients, except the specified one.
    """
    for client in clients:
        if exclude and client == exclude:
            continue
        server_socket.sendto(message.encode(), client)


def game_round():
    """
    Orchestrates multiple rounds of the trivia game.
    """
    if len(clients) < MIN_PLAYERS:
        print("Not enough players to start a round.")
        return

    broadcast(f"Game will start in {WAIT_FOR_PLAYERS} seconds. Get ready!")
    print(f"Waiting {WAIT_FOR_PLAYERS} seconds before starting the game...")
    time.sleep(WAIT_FOR_PLAYERS)

    while True:
        # Ensure enough questions exist to start a round
        if len(questions_db) < 3:
            print("Not enough questions in the database to start a round.")
            broadcast("Game cannot start due to insufficient questions. Please try later.")
            return

        # Select random questions from the database
        round_questions = random.sample(list(questions_db.items()), 3)
        broadcast("The game is starting now!")

        # Initialize answers for clients
        for client in clients:
            if client not in answers_per_client:
                answers_per_client[client] = []

        for i, (question, answer) in enumerate(round_questions, start=1):
            time.sleep(QUESTION_DELAY)
            broadcast(f"Question {i}: {question}")
            print(f"Broadcasting Question {i}: {question}")
            start_time = time.time()
            client_answers = {}

            while time.time() - start_time < ANSWER_TIMEOUT:
                try:
                    data, addr = server_socket.recvfrom(BUFFER_SIZE)
                    if addr in clients and addr not in client_answers:
                        client_answers[addr] = data.decode().strip()
                        print(f"{clients[addr]} answered: {data.decode().strip()}")
                except socket.timeout:
                    continue

            broadcast(f"Time's up! The correct answer was: {answer}")
            print(f"Correct answer: {answer}")

            # Evaluate answers
            for client, response in client_answers.items():
                if response.lower() == answer.lower():
                    scores[client] = scores.get(client, 0) + 1  # Increment score by 1 for correct answer
                    answers_per_client[client].append("1")
                    broadcast(f"{clients[client]} answered correctly!")
                else:
                    answers_per_client[client].append("0")
                    broadcast(f"{clients[client]} answered incorrectly!")

        # After all questions in the round, print the scores
        broadcast("End of the round! Current leaderboard:")
        for client in clients:
            total_score = sum(int(answer) for answer in answers_per_client[client])
            print(f"{clients[client]} ({'+'.join(answers_per_client[client])}) = {total_score} points")
            broadcast(f"{clients[client]} ({'+'.join(answers_per_client[client])}) = {total_score} points")

        # Ask players if they want to play another round
        broadcast("Do you want to play another round? (yes/no)")
        print("Waiting for players' responses...")
#here u can delete this or replace by 2 and continue the example
        ready_players = 2
        for _ in range(len(clients)):
            try:
                data, addr = server_socket.recvfrom(BUFFER_SIZE)
                if data.decode().strip().lower() == "yes":
                    ready_players += 1
            except socket.timeout:
                continue
        
    
        if ready_players < MIN_PLAYERS:
            broadcast("Not enough players want to continue. The game has ended.")
            print("Game has ended.")
            break
        else:
            broadcast("Starting a new round!")
        

def handle_client(addr, username):
    """
    Handles a new client joining the game.
    """
    clients[addr] = username
    scores[addr] = 0
    print(f"New client joined: {username} ({addr})")
    broadcast(f"{username} has joined the game!")

    # Start the game if minimum players are reached
    if len(clients) >= MIN_PLAYERS:
        threading.Thread(target=game_round).start()


# Start the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))
server_socket.settimeout(1)

print(f"Server started at {HOST}:{PORT}")

try:
    while True:
        try:
            data, addr = server_socket.recvfrom(BUFFER_SIZE)
            if addr not in clients:
                username = data.decode().strip()
                threading.Thread(target=handle_client, args=(addr, username)).start()
        except socket.timeout:
            continue
except KeyboardInterrupt:
    print("Server shutting down...")
finally:
    server_socket.close()
