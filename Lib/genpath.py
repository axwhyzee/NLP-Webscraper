import random
import os

def gen_path(ext=''):
    path = str(random.random())[2:] + ext
    
    while path in os.listdir():
        path = str(random.random())[2:] + ext
        
    return path
