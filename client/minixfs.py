# -*- coding: utf-8 -*-
#Note : minix-fs types are little endian

from bitarray import *
from client.bloc_device import *
from client.minix_superbloc import *
from client.minix_inode import *

class minix_file_system(object):
    def __init__(self,filename):
        self.imgMinixFs = bloc_device(BLOCK_SIZE, filename)
        self.superBlock = minix_superbloc(self.imgMinixFs)

        # bitmap inode
        self.inode_map = bitarray(endian='little')
        self.inode_map.frombytes(self.imgMinixFs.read_bloc(2, self.superBlock.s_imap_blocks))

        # bitmap blocs
        self.zone_map = bitarray(endian='little')
        self.zone_map.frombytes(self.imgMinixFs.read_bloc(2+self.superBlock.s_imap_blocks,self.superBlock.s_zmap_blocks))

        # inodes list
        inodes_from_img = self.imgMinixFs.read_bloc(2+self.superBlock.s_imap_blocks+self.superBlock.s_zmap_blocks, self.superBlock.s_firstdatazone)
        self.inodes_list = []
        self.inodes_list.append(minix_inode(None))
        for i in range(0, self.superBlock.s_ninodes):
            # take one inode by one and put it in inodes_list being a minix_inode object
            # i + 1 represents the number of inode
            self.inodes_list.append(minix_inode(inodes_from_img[i*INODE_SIZE:i*INODE_SIZE+INODE_SIZE], i+1))


        return
    
    #return the first free inode number available
    #starting at 0 and upto s.n_inodes-1. 
    #The bitmap ranges from index 0 to inod_num-1
    #Inode 0 is never and is always set.
    #according to the inodes bitmap
    def ialloc(self):
        return

    #toggle an inode as available for the next ialloc() 
    def ifree(self,inodnum):
        return 
    #return the first free bloc index in the volume. The bitmap
    #indicate the index from the bloc zone, add first_datazone then
    #to the bloc index
    def balloc(self):
        return
    
    #toggle a bloc as available for the next balloc() 
    #blocnum is an index in the zone_map
    def bfree(self,blocnum):
        return
    
    def bmap(self,inode,blk):
        #if (blk < inode[14:15])

        return
    
    #lookup for a name in a directory, and return its inode number, given inode directory dinode
    def lookup_entry(self,dinode,name):
        return
    
    #find an inode number according to its path
    #ex : '/usr/bin/cat'
    #only works with absolute paths
                   
    def namei(self,path):
        return
    
    def ialloc_bloc(self,inode,blk):
        return
    
    #create a new entry in the node
    #name is an unicode string
    #parameters : directory inode, name, inode number
    def add_entry(self,dinode,name,new_node_num):
        return

    #delete an entry named "name" 
    def del_entry(self,inode,name):
        return


