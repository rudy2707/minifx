# -*- coding: utf-8 -*-
# Note : minix-fs types are little endian

from bitarray import *
from client.bloc_device import *
from client.minix_superbloc import *
from client.minix_inode import *
from array import *

class minix_file_system(object):
    def __init__(self,filename):
        self.disk = bloc_device(BLOCK_SIZE, filename)
        self.superBlock = minix_superbloc(self.disk)

        # bitmap inode
        self.inode_map = bitarray(endian='little')
        self.inode_map.frombytes(self.disk.read_bloc(2, self.superBlock.s_imap_blocks))

        # bitmap blocs
        self.zone_map = bitarray(endian='little')
        self.zone_map.frombytes(self.disk.read_bloc(2+self.superBlock.s_imap_blocks,self.superBlock.s_zmap_blocks))

        # inodes list
        inodes_from_img = self.disk.read_bloc(self.superBlock.s_imap_blocks + self.superBlock.s_zmap_blocks + MINIX_SUPER_BLOCK_NUM + 1, self.superBlock.s_firstdatazone)
        self.inodes_list = []
        self.inodes_list.append(minix_inode(None))
        for i in range(0, self.superBlock.s_ninodes):
            # take one inode by one and put it in inodes_list being a minix_inode object
            # i + 1 represents the number of inode
            self.inodes_list.append(minix_inode(inodes_from_img[i*INODE_SIZE:(i+1)*INODE_SIZE], i+1))
        return
    
    # return the first free inode number available
    # starting at 0 and upto s.n_inodes-1.
    # The bitmap ranges from index 0 to inod_num-1
    # Inode 0 is never and is always set.
    # according to the inodes bitmap
    def ialloc(self):
        i = 0
        while self.inode_map[i]:
            i += 1
        self.inode_map[i] = 1
        self.inodes_list[i] = minix_inode(num=i)
        return i

    # toggle an inode as available for the next ialloc()
    def ifree(self,inodnum):
        self.inode_map[inodnum] = 0
        return

    # return the first free bloc index in the volume. The bitmap
    # indicate the index from the bloc zone, add first_datazone then
    # to the bloc index
    def balloc(self):
        i = 0
        while self.zone_map[i]:
            i += 1
        self.zone_map[i] = 1
        blk_null = '\0' * BLOCK_SIZE
        self.disk.write_bloc(i+self.superBlock.s_firstdatazone, blk_null)
        return i+self.superBlock.s_firstdatazone
    
    # toggle a bloc as available for the next balloc()
    # blocnum is an index in the zone_map
    def bfree(self,blocnum):
        self.zone_map[blocnum] = 0
        return
    
    def bmap(self,inode,blk):
        if blk < 7:
            return inode.i_zone[blk]
        blk -= 7
        if blk < 512:
            indirect_bloc = self.disk.read_bloc(inode.i_indir_zone)
            return struct.unpack_from("<H", indirect_bloc, blk*(BLOCK_SIZE/512))[0]
        blk -= 512
        if blk < 512*512:
            indirect_bloc = self.disk.read_bloc(inode.i_dbl_indr_zone)
            indirect_bloc2 = self.disk.read_bloc(struct.unpack_from("<H", indirect_bloc, blk*(BLOCK_SIZE/(512*512)))[0])
            return struct.unpack_from("<H", indirect_bloc2, (blk % 512) * (BLOCK_SIZE/(512)))[0]

        return
    
    # lookup for a name in a directory, and return its inode number, given inode directory dinode
    def lookup_entry(self,dinode,name):
        for i in range(0,dinode.i_size):
            blk = self.disk.read_bloc(self.bmap(dinode, i))
            for j in range(0, BLOCK_SIZE/INODE_SIZE):
                inode = blk[INODE_SIZE*j:INODE_SIZE*(j+1)]
                if name in inode[2:16]:
                    return struct.unpack("<H", inode[0:2])[0]
        return
    
    # find an inode number according to its path
    # ex : '/usr/bin/cat'
    # only works with absolute paths
    def namei(self,path):
        inode = MINIX_ROOT_INO
        if path == '/':
            return inode
        for i in path[1:len(path)].split('/'):
            inode = self.lookup_entry(self.inodes_list[inode], i)
        return inode
    
    def ialloc_bloc(self,inode,blk):

        # Cas 0
        if (blk < len(inode.i_zone)):
            if (inode.i_zone[blk] == 0):
                inode.i_zone[blk] = self.balloc()

                inode.i_size += BLOCK_SIZE
            return inode.i_zone[blk]

        blk -= len(inode.i_zone)

        # Cas 1
        if (blk < 512):
            if (inode.i_indir_zone == 0):
                inode.i_indir_zone = self.balloc()

            indirect_bloc = self.disk.read_bloc(inode.i_indir_zone)
            if (indirect_bloc[blk] == 0):
                indirect_bloc[blk] = self.balloc()
                self.disk.write_bloc(inode.i_indir_zone, indirect_bloc)

                inode.i_size +=BLOCK_SIZE
            return indirect_bloc[blk]
        return
    
    # create a new entry in the node
    # name is an unicode string
    # parameters : directory inode, name, inode number
    def add_entry(self,dinode,name,new_node_num):

        # navigate in the inode
        for i in range(0, int(round(dinode.i_size / BLOCK_SIZE, 0)) + 1):

            # load the block
            block = self.disk.read_bloc(self.bmap(dinode, i))

            # navigate in the block
            for j in range(0, BLOCK_SIZE / DIRSIZE):

                # looking for an empty entry
                if (struct.unpack_from("<H", block, j * DIRSIZE)[0] == 0):
                    new_block = array('c', block)
                    struct.pack_into("<H", new_block, j*DIRSIZE, new_node_num)
                    struct.pack_into("<14s", new_block, 2 + j*DIRSIZE, name)

                    # write the new directory on the disk
                    self.disk.write_bloc(self.bmap(dinode, i), new_block)
                    return

        # if we don't find an empty block, we alloc a new block in the inode
        new_block = array('c', '\0' * BLOCK_SIZE)
        struct.pack_into("<H", new_block, 0, new_node_num)
        struct.pack_into("<14s", new_block, 2, name)
        self.disk.write_bloc(self.ialloc_bloc(dinode, i+1), new_block)
        return

    # delete an entry named "name"
    def del_entry(self,inode,name):

        # fill the name with \0
        name = name.ljust(14, "\0")

        # navigate in the inode
        for i in range(0, int(round(inode.i_size / BLOCK_SIZE, 0)) + 1):

            # load the block
            block = self.disk.read_bloc(self.bmap(inode, i))

            # navigate in the block
            for j in range(0, BLOCK_SIZE / DIRSIZE):

                # looking for the dir name in the block
                if struct.unpack_from("<14s", block, 2 + j *DIRSIZE)[0] == name:

                    # to delete the directory, we place a new block to replace the old one
                    new_block = array('c', self.disk.read_bloc(self.bmap(inode, i)))
                    struct.pack_into("<H", new_block, j*DIRSIZE, 0)
                    self.disk.write_bloc(self.bmap(inode, i), new_block)
                    return
        return -1


