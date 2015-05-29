# -*- coding: utf-8 -*-
# emulate a simple bloc device using a file
# reading it only by bloc units
from client.constantes import *

class bloc_device(object):
    def __init__(self,blksize,pathname):
        self.blksize = blksize
        self.pathname = pathname
        self.blocfile = os.open(self.pathname, os.O_RDWR)
        return
    def read_bloc(self,bloc_num,numofblk=1):
        #os.SEEK_SET permet de parcourir le bloc depuis le debut
        os.lseek(self.pathname, bloc_num*BLOCK_SIZE, os.SEEK_SET)
        return os.read(self.blocfile, bloc_num)
    def write_bloc(self,bloc_num,bloc):
        #os.SEEK_SET permet de parcourir le bloc depuis le debut
        os.lseek(self.pathname, bloc_num*BLOCK_SIZE, os.SEEK_SET)
        return os.write(self.blocfile, bloc_num)
