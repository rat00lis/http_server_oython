import socket
import os
import mimetypes

code_errors = {
    "200": "HTTP/1.1 200 OK\r\n",
    "404": "HTTP/1.1 404 Not Found\r\n",
    "405": "HTTP/1.1 405 Method Not Allowed\r\n",
    "301": "HTTP/1.1 301 Moved Permanently\r\n",
    "500": "HTTP/1.1 500 Internal Server Error\r\n",
    "505": "HTTP/1.1 505 HTTP Version Not Supported\r\n",
    "418": "HTTP/1.1 418 I'm a teapot\r\n"
}


def header(code=None,size=None,type=None,location=None):
    response = code_errors[code]
    if(code=="301"):
        response += f"Location: http://localhost:8000/{location}\r\n"
        response += "\r\n"
        return response.encode()
    if(type):
        response += f"Content-Type: {type}\r\n"
    if(size):
        response += f"Content-Length: {size}\r\n"
    response += "\r\n"
    return response.encode()



def handle_request(request):
    try:
        # Extract the filename from the request
        method, path, version = request.split(' ')[:3]
        filename = path[1:]  # Remove the leading '/' from the path
        version = version[0:8]
        # Check if the file exists
        print(filename)
        
        if(filename==""):
            filename+="index.html"
            
        if version != 'HTTP/1.1':
            response = header('505')
            return response
        
        if(method !="GET"):
            if(method == "BREW"):
                filename = "teapot.html"
                with open(filename, 'rb') as file:
                    file_contents = file.read()
                content_type, _ = mimetypes.guess_type(filename)
                content_length = len(file_contents)
                response = header("418",content_length,content_type) + file_contents
                return response
            else:
                response = header("405")
                return response
            
        if os.path.isfile(filename):
            # File exists, read its contents
            with open(filename, 'rb') as file:
                file_contents = file.read()

            # Determine the content type
            content_type, _ = mimetypes.guess_type(filename)
            if content_type is None:
                content_type = 'application/octet-stream'

            # Get the content length
            content_length = len(file_contents)
            response = header("200",content_length,content_type) + file_contents
        else:
            filer = filename
            filename+="index.html"
            if os.path.isfile(filename):
                with open(filename, 'rb') as file:
                    file_contents = file.read()

                # Determine the content type
                content_type, _ = mimetypes.guess_type(filename)
                if content_type is None:
                    content_type = 'application/octet-stream'

                # Get the content length
                content_length = len(file_contents)
                response = header("200",content_length,content_type) + file_contents
                return response
            filename= filer + "/index.html"
            if os.path.isfile(filename):
                content_length=None
                content_type=None
                response = header("301",content_length,content_type,filename)
                return response
            else:
                response = header("404")

        return response
    except:
        response = header("500")
        return response



def run_server():
    # Set the host and port
    host = 'localhost'
    port = 8000

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_socket.bind((host, port))

    # Listen for incoming connections
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    while True:
        # Accept a connection
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr[0]}:{addr[1]}")

        # Receive data from the client
        request = client_socket.recv(1024).decode()

        # Handle the request and get the response
        response = handle_request(request)

        # Send the response back to the client
        client_socket.sendall(response)

        # Close the client socket
        client_socket.close()

    # Close the server socket
    server_socket.close()

# Run the server
run_server()
