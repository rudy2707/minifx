# -*- coding: utf-8 -*-
from client.constantes import *

class minix_superbloc(object):
    def __init__(self, bloc_device):
        # Charge le bloc 1 dans la variable superBloc
        self.superBloc = bloc_device.read_bloc(1)

        # Charge la structure avec le contenu du bloc
        self.s_ninodes = struct.unpack("<H", self.superBloc[0:2])[0]
        self.s_nzones = struct.unpack("<H", self.superBloc[2:4])[0]
        self.s_imap_blocks = struct.unpack("<H", self.superBloc[4:6])[0]
        self.s_zmap_blocks = struct.unpack("<H", self.superBloc[6:8])[0]
        self.s_firstdatazone = struct.unpack("<H", self.superBloc[8:10])[0]
        self.s_log_zone_size = struct.unpack("<H", self.superBloc[10:12])[0]
        self.s_max_size = struct.unpack("<I", self.superBloc[12:16])[0]
        self.s_magic = struct.unpack("<H",self.superBloc[16:18])[0]
        self.s_state = struct.unpack("<H",self.superBloc[18:20])[0]
        return
