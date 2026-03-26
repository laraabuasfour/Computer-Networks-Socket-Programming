import socket

# Function to create the HTTP request message
def create_request(resource):
    request = f"GET {resource} HTTP/1.1\r\n"
    request += "Host: 192.168.1.29:5689\r\n"  # Replace with your server's IP address
    request += "Connection: keep-alive\r\n"
    request += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8\r\n"
    request += "Accept-Encoding: gzip, deflate\r\n"
    request += "Accept-Language: en-US,en;q=0.9\r\n"
    request += "\r\n"
    return request

# Function to handle the server response
def handle_response(response):
    print("Response:")
    print(response)

# Create the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Server address (replace with your server's IP address and port)
server_ip = "192.168.1.29"
server_port = 5689

# Connect to the server
client_socket.connect((server_ip, server_port))
print(f"Connected to {server_ip}:{server_port}")

# Resource to request
resource = "/h.png"  # The resource you're requesting

# Create the HTTP GET request for the resource
request = create_request(resource)

# Send the request to the server
client_socket.send(request.encode())
print(f"Request sent: {request}")

# Receive the server's response
response = client_socket.recv(1024).decode()

# Handle and print the response
handle_response(response)

# Close the client socket after receiving the response
client_socket.close()
print("Connection closed.")
