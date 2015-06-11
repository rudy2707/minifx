# -*- coding: utf-8 -*-
# emulate a simple bloc device using a file
# reading it only by bloc units
from client.constantes import *

import socket
import random
from struct import *

class bloc_device(object):
    def __init__(self,blksize,pathname):
        self.blocfile = open(pathname, 'rb+')

        self.connexion_serveur = 0
        self.request = 0
        self.response = 0

        random.seed()
        return

    def read_bloc(self,bloc_num,numofblk=1):
        self.connect_socket('172.20.10.3', 2412)
        #self.blocfile.seek(bloc_num*BLOCK_SIZE)
        self.create_request(0, bloc_num*BLOCK_SIZE, BLOCK_SIZE)
        self.send_socket()
        self.listen_socket()
        self.analyze_response()
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

    def connect_socket(self, adresse, port):
        self.connexion_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connexion_serveur.connect((adresse, port))

        return

    def listen_socket(self):
        self.response = self.connexion_serveur.recv(2412)
        return

    def send_socket(self):
        self.connexion_serveur.send(self.request)
        return

    def close_socket(self):
        self.connexion_serveur.close()
        return

    def create_request(self, mode, offset, length, payload=0):
        magic = '0x76767676'

        # TODO : random seed following the date and time of the system
        handle = '0x12345678'

        if (mode == 0):
            # read request
            type = '0x0'
            self.request = struct.pack("!BBBBB", magic, type, handle, offset, length)
        else:
            # write request
            type = '0x1'
            self.request = struct.pack("!5B"+str(len(payload))+"I", magic, type, handle, offset, length, payload)

        return

    def analyze_response(self):

        return
"""
pour tester.py :

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