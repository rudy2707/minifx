# -*- coding: utf-8 -*-
# emulate a simple bloc device using a file
# reading it only by bloc units
from client.constantes import *

import socket
import random
from struct import *


ADR='172.20.10.3'
PORT=2411
HEADER_SIZE=12
READ_MODE=0x0
WRITE_MODE=0x1
HANDLE=0x12345678
RESPONSE_MAGIC=0x87878787
REQUEST_MAGIC=0x76767676

class bloc_device(object):
    def __init__(self,blksize,pathname):
        self.blocfile = open(pathname, 'rb+')

        # initialisation des variables sockets
        self.connexion_serveur = 0
        self.request = 0
        self.response = 0
        self.mode = 0
        self.handle = 0

        # initialisation du random
        random.seed()
        return

    def read_bloc(self,bloc_num,numofblk=1):
        # Recuperation du nombre de bloc a recevoir en reponse du serveur
        self.numofblk = numofblk

        # creation du socket
        self.connect_socket(ADR, PORT)

        # mode lecture
        self.mode = READ_MODE

        # creation de la requete suivant les parametres de la fonction
        self.create_request(bloc_num*BLOCK_SIZE, numofblk*BLOCK_SIZE)

        # envoi de la requete
        self.send_socket()

        # attente de la reponse
        self.listen_socket()

        # analyse de la reponse
        if (self.analyze_response() == 0):
            # rendu du payload
            bloc_response = self.response[HEADER_SIZE:len(self.response)]
        else:
            bloc_response = -1

        # fermeture du socket
        self.close_socket()

        return bloc_response

    def write_bloc(self,bloc_num,bloc):
        # creation du socket
        self.connect_socket(ADR, PORT)

        # mode ecriture
        self.mode = WRITE_MODE

        # creation de la requete suivant les parametres de la fonction
        self.create_request(bloc_num*BLOCK_SIZE, BLOCK_SIZE, bloc)

        # envoi de la requete
        self.send_socket()

        # attente de la reponse
        self.listen_socket()

        # analyse de la reponse
        if (self.analyze_response() == 0):
            print("Write success")
        else:
            print("Write failed")

        # fermeture du socket
        self.close_socket()
        return

    # Creation du socket et connexion au serveur
    def connect_socket(self, adresse, port):
        self.connexion_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connexion_serveur.connect((adresse, port))
        return

    # Ecoute du port pour la reponse
    def listen_socket(self):
        if (self.mode == READ_MODE):
            self.response = self.connexion_serveur.recv(self.numofblk*BLOCK_SIZE + HEADER_SIZE)
        else:
            self.response = self.connexion_serveur.recv(HEADER_SIZE)
        return

    # Envoie de la requete dans le socket
    def send_socket(self):
        self.connexion_serveur.send(self.request)
        return

    # Ferme le socket
    def close_socket(self):
        self.connexion_serveur.close()
        return

    # Cree une requete suivant le mode de transmission
    def create_request(self, offset, length, payload=0):

        if self.mode == READ_MODE:
            # read request
            self.request = struct.pack("!IIIII", REQUEST_MAGIC, self.mode, HANDLE, offset, length)
        else:
            # write request
            self.request = struct.pack("!IIIII"+str(len(payload))+"s", REQUEST_MAGIC, self.mode, HANDLE, offset, length, payload)

        return

    # Test la conformite des reponses du serveur
    def analyze_response(self):
        magic = struct.unpack(">I", self.response[0:4])[0]
        err = struct.unpack(">I", self.response[4:8])[0]
        handle = struct.unpack(">I", self.response[8:12])[0]

        if self.mode == READ_MODE:
            print("Read mode")
        else:
            print("Write mode")

        if err < 0:
            print("Error from server")
            return -1
        if magic == int(RESPONSE_MAGIC) and handle == int(HANDLE):
            print("Good response")
            return 0
        else:
            print("Bad response")
            return -1
        return
"""
pour tester.py en non-socket :

    def __init__(self,blksize,pathname):
        self.blocfile = open(pathname, 'rb+')
        return


    def read_bloc(self,bloc_num,numofblk=1):

        self.blocfile.seek(bloc_num*BLOCK_SIZE)

        return self.blocfile.read(numofblk*BLOCK_SIZE)

    def write_bloc(self,bloc_num,bloc):
        # curseur du fichier à la bonne position
        self.blocfile.seek(BLOCK_SIZE*bloc_num)
        # buffer avec les données à écrire
        buff = buffer(bloc,0,BLOCK_SIZE)
        # ecriture des block
        for i in range(BLOCK_SIZE):
            self.blocfile.write(buff[i])
        return
"""