#!/usr/bin/env python
# -*- coding: utf-8 -*-

from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn # <--- Ajoute cet import

# Crée un serveur qui accepte plusieurs connexions simultanées
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
#~ from http.server import HTTPServer, SimpleHTTPRequestHandler
#~ class MyHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        # 1. Récupérer la taille du message
        content_length = int(self.headers['Content-Length'])
        # 2. Lire le message
        post_data = self.rfile.read(content_length)
        
        print(f"Message reçu : {post_data.decode('utf-8')}")
        
        # 3. Répondre à la page web pour dire que c'est reçu
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Message bien recu par le serveur !")

if __name__ == '__main__':

    print("Serveur lancé sur le port 8000...")
    #~ HTTPServer(('0.0.0.0', 8000), MyHandler).serve_forever()
    
    server = ThreadedHTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()

    
    