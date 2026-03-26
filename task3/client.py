import socket
import threading

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5689
BUFFER_SIZE = 1024

question_received = threading.Event()


def listen_for_messages(client_socket):
    """
    Listens for incoming messages from the server and prints them.
    If a question is received, it sets the event to enable answering.
    """
    while True:
        try:
            message, _ = client_socket.recvfrom(BUFFER_SIZE)
            decoded_message = message.decode()
            print(decoded_message)

            # If the server sends a question, allow user input
            if decoded_message.startswith("Question"):
                question_received.set()

        except:
            break


# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

username = input("Enter your username: ")
client_socket.sendto(username.encode(), (SERVER_IP, SERVER_PORT))

# Start a thread to listen for server messages
thread = threading.Thread(target=listen_for_messages, args=(client_socket,))
thread.daemon = True
thread.start()

try:
    while True:
        # Wait for the server to send a question
        question_received.wait()
        answer = input("Enter your answer: ")
        client_socket.sendto(answer.encode(), (SERVER_IP, SERVER_PORT))
        question_received.clear()  # Reset the event after the answer is sent
except KeyboardInterrupt:
    print("Exiting game...")
finally:
    client_socket.close()