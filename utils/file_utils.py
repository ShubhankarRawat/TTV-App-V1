import os
import shutil

def create_folder(folder_name):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.mkdir(folder_name)
    print("Folder created with name = ", folder_name)