import os

def base_dir_path():
    return os.path.dirname(os.path.dirname(__file__))

def read_file(file):
    f = open(file, 'r')
    data = f.read()
    f.close()

    return data

def read_file_lines(file):
    f = open(file, 'r')
    lines = f.readlines()
    f.close()

    return lines