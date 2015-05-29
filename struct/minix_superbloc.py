# -*- coding: utf-8 -*-
from constantes import *

class minix_superbloc(object):
    def __init__(self, bloc_device):
        # Charge le bloc 1 dans la variable superBloc
        superBloc = bloc_device.read_bloc(1)

        # Charge la structure avec le contenu du bloc
        self.s_ninodes = struct.unpack("<H", superBloc[0:2])[0]
        self.s_nzones = struct.unpack("<H", superBloc[2:4])[0]
        self.s_imap_blocks = struct.unpack("<H", superBloc[4:6])[0]
        self.s_zmap_blocks = struct.unpack("<H", superBloc[6:8])[0]
        self.s_firstdatazone = struct.unpack("<H", superBloc[8:10])[0]
        self.s_log_zone_size = struct.unpack("<H", superBloc[10:12])[0]
        self.s_max_size = struct.unpack("<I", superBloc[12:16])[0]
        self.s_magic = struct.unpack("<H",superBloc[16:18])[0]
        self.s_state = struct.unpack("<H",superBloc[18:20])[0]
        return
