from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from pathlib import Path
import mimetypes 
import socket
from threading import Thread
import logging
import json
from datetime import datetime
import os
BASE_DIR = Path()
BUFFER_SIZE = 1024
HTTP_PORT = 3000
HTTP_HOST = '0.0.0.0'
SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 5000

class HomeworkFramework(BaseHTTPRequestHandler):

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case '/':
                self.send_html('index.html')
            case '/message':
                self.send_html('message.html')
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html(filename='error.html', status_code= 404)


    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data,(SOCKET_HOST,SOCKET_PORT))
        client_socket.close()
        self.send_response(302)
        self.send_header('Location', '/message')
        self.end_headers()


    def send_html(self, filename,status_code = 200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())
            
    def send_static(self, filename,status_code = 200):
        self.send_response(status_code)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header('Content-Type', mime_type)
        else:
            self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        with open(filename,'rb') as file:
            self.wfile.write(file.read())

    def check_storage_directory():
        storage_dir = 'storage'
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        return storage_dir



    @staticmethod
    def save_data_from_form(data):
        data_parse = urllib.parse.unquote_plus(data.decode())
        try:
            parse_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            data_dict = {}
          
            data_json_file = os.path.join('storage/data.json')
            if not os.path.exists(data_json_file):
                with open('storage/data.json', 'w') as f:
                    json.dump({},f)                
            data_dict[timestamp] = parse_dict
            
            with open('storage/data.json', 'a',encoding='UTF-8')as file:
                json.dump(data_dict,file, ensure_ascii=False,indent=4)
        except ValueError as err:
            logging.error(err)
        except OSError as err:
            logging.error(err)
        


    @staticmethod
    def run_socket_server(host,port):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((host,port))
        # server_socket.listen()
        logging.info("Starting socket server")
        try:
            while True:
                msg, address = server_socket.recvfrom(BUFFER_SIZE)
                logging.info(f'{address}:{msg}')
                HomeworkFramework.save_data_from_form(msg)
        except KeyboardInterrupt:
            pass
        finally:
            server_socket.close()


    @staticmethod
    def run_http_server(host,port):
        address = (host,port) 
        http_server = HTTPServer(address,HomeworkFramework)
        logging.info("Starting http server")
        try:
            http_server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            http_server.server_close()


if __name__ == '__main__':


    logging.basicConfig(level=logging.DEBUG,format='%(threadName)s %(message)s')

    server = Thread(target=HomeworkFramework.run_http_server, args=(HTTP_HOST, HTTP_PORT))
    server.start()
    client = Thread(target=HomeworkFramework.run_socket_server, args=(SOCKET_HOST, SOCKET_PORT))
    client.start()
    