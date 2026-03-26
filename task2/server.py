import socket
import threading
import os

def get_path(content_type = "text/html"):
    if content_type == "text/html":
        return "html/"
    elif content_type == "text/css":
        return "css/"
    elif "image/" in content_type:
        return "imgs/"
    elif "video/" in content_type:
        return "vids/"
    else:
        return ""

# Function to get the local machine IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'  # Default to localhost if no external network is available
    finally:
        s.close()
    return local_ip

# Function to serve static files (like images or HTML files) from the same directory as the script
def serve_static_file(file_name, client_socket, content_type="image/png"):
    try:
        # Check if the requested file exists
        file_name = get_path(content_type) + file_name
        if os.path.exists(file_name):
            with open(file_name, 'rb') as file:
                file_content = file.read()
            
            # Prepare the response for the file
            response = "HTTP/1.1 200 OK\r\n"
            response += f"Content-Type: {content_type}\r\n\r\n"
            client_socket.sendall(response.encode())
            client_socket.sendall(file_content)
        else:
            # File not found, send a 404 response
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Type: text/html\r\n\r\n"
            response += "<html><body><h1>File Not Found</h1></body></html>"
            client_socket.sendall(response.encode())
    except Exception as e:
        print(f"Error serving file: {e}")
        response = "HTTP/1.1 500 Internal Server Error\r\n"
        response += "Content-Type: text/html\r\n\r\n"
        response += "<html><body><h1>Internal Server Error</h1></body></html>"
        client_socket.sendall(response.encode())

# Function to handle client requests
def handle_request(client_socket, client_address):
    print(f"Connection from {client_address} has been established.")
    
    try:
        # Receive the request from the client (max 1024 bytes)
        request = client_socket.recv(1024).decode()
        print(f"Request received: {request}")
        
        # Check if the request is fora a specific HTML page (main_en.html)
        if 'GET / ' in request or 'GET /en' in request or 'GET /index.html' in request or 'GET /main.html' in request:
            # Serve the main_en.html file
            serve_static_file('main.html', client_socket, content_type="text/html")
        elif 'GET /supporting_material_en' in request:
            serve_static_file('supporting_material_en.html', client_socket, content_type="text/html")
        elif 'GET /supporting_material_ar' in request:
            serve_static_file('supporting_material_ar.html', client_socket, content_type="text/html")        
        # Check if the request is for a specific HTML page (main_ar.html)
        elif 'GET /ar' in request or 'GET /main_ar.html' in request:
            # Serve the main_ar.html file
            serve_static_file('main_ar.html', client_socket, content_type="text/html")
        elif '.css ' in request:
            css_file = request.split(' ')[1].strip('/')
            serve_static_file(css_file, client_socket, content_type="text/css")
        elif 'GET /get_material' in request:
            requestPath = request.split(' ')[1]
            query = requestPath.split("?")[1]
            params = query.split("&")
            found = False
            file_in_query = ""
            for param in params:
                if "file-request=" in param:
                    parts = param.split("=")
                    file_in_query = parts[1]
                    if os.path.exists(get_path("image/") + parts[1]):
                        found = True
                        if file_in_query.endswith('.mp4'):
                            serve_static_file(parts[1], client_socket, content_type="video/mp4")
                        else:
                            serve_static_file(parts[1], client_socket)
            if not found:
                if file_in_query.endswith((".png", ".jpg", ".jpeg")):
                    search_term = file_in_query.rsplit('.', 1)[0].replace(" ", "+")
                    response = f"HTTP/1.1 302 Found\r\nLocation: https://www.google.com/search?q={search_term}\r\n\r\n"
                    client_socket.sendall(response.encode())
                elif file_in_query.endswith((".mp4")):
                    search_term = file_in_query.rsplit('.', 1)[0].replace(" ", "+")
                    youtube_url = f"https://www.youtube.com/results?search_query={search_term}"
                    response = f"HTTP/1.1 302 Found\r\nLocation: {youtube_url}\r\n\r\n"
                    client_socket.sendall(response.encode())
                else:
                    response = "HTTP/1.1 404 Not Found\r\n"
                    response += "Content-Type: text/html\r\n\r\n"
                    response += "<html><body><h1>File Not Found</h1></body></html>"
                    client_socket.sendall(response.encode())
        
        # Check if the request is for an image file
        elif '.png ' in request:
            # Serve the h.png file
            file_name = request.split(' ')[1].strip('/')
            serve_static_file(file_name, client_socket)
        elif 'GET /TCP.jpg' in request:
            serve_static_file('TCP.jpg', client_socket)
        elif 'GET /UDP.jpg' in request:
            serve_static_file('UDP.jpg', client_socket)
        elif 'GET /youtube' in request:
            # Extract search term for YouTube from the request (e.g., /youtube cat videos)
            search_term = request.split(' ')[1].strip('/youtube').strip()
            youtube_url = f"https://www.youtube.com/results?search_query={search_term}"
            # Redirect to YouTube search
            response = f"HTTP/1.1 302 Found\r\nLocation: {youtube_url}\r\n\r\n"
            client_socket.sendall(response.encode())
        else:
            # If not an image or YouTube, search on Google for the term requested
            search_term = request.split(' ')[1].strip('/')
            response = f"HTTP/1.1 302 Found\r\nLocation: https://www.google.com/search?q={search_term}\r\n\r\n"
            client_socket.sendall(response.encode())
    
    except Exception as e:
        print(f"Error while handling request: {e}")
    
    finally:
        # Close the connection after serving the client
        client_socket.close()
        print(f"Connection with {client_address} closed.")

# Create the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get the current local IP address of the machine
local_ip = get_local_ip()

# Set the server to reuse the address and port
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the server socket to the local IP address and a port number (e.g., 5689)
server_socket.bind((local_ip, 5689
                    
                    ))

server_socket.listen(5)
print(f"Server listening on {local_ip}:5689...")

def start_server():
    while True:
        #new connection
        client_socket, client_address = server_socket.accept()
        
      
        client_thread = threading.Thread(target=handle_request, args=(client_socket, client_address))
        client_thread.start()


start_server()
