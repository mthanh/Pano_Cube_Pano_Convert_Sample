'''
Created on Jun 29, 2021

@author: Duong_Thanh
'''

#file process
# import os
from os import listdir
from os.path import isfile, join

import os.path
from os import path

class support_func():   
    
    def listfile(self, path_in):
        list_out = [f for f in listdir(path_in) if isfile(join(path_in, f))]
        return list_out
    
    def check_file_exist(self, file_check):
        return path.exists(file_check)
     
    def check_dir_OK(self, dir_check):
        if os.path.exists(dir_check) and os.path.isdir(dir_check):
            if not os.listdir(dir_check):
                # print("Directory is empty")
                return True
            else:    
                # print("Directory is not empty")
                return True
        else:
            # print("Given directory doesn't exist")
            return False
    


