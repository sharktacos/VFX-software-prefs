import os
import nuke
import platform
import re


def write_directory_maker():
    selected_write = nuke.thisNode()
    selected_write_full_path = selected_write['file'].value()
    selected_write_path = selected_write_full_path.rsplit('/',1)[0]
    isdir = os.path.isdir(selected_write_path)

    if isdir == 1:
        print ''
    elif isdir == 0:
        mkdir = os.makedirs(selected_write_path)