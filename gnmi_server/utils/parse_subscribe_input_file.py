import json

def read_txt_file(file):
    with open(file,'r') as f:
        lines = []
        for line in f:
            line = line.strip()
            lines.append(line)
    return lines