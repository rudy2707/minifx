# -*- coding: utf-8 -*-
# emulate a simple bloc device using a file
# reading it only by bloc units
from client.constantes import *

class bloc_device(object):
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
