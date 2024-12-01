import json
import re
from dummy import *

def OpenFile(path):
    """
    Convert JSON string to a Python dictionary
    """
    with open(path, 'r', encoding="utf8") as file:
        data = json.load(file)
    
    return data


def unQuote(key: str) -> str:
    return key.replace("\"", "")


def clean_str(key):
    new = re.sub(r' |-', '_', str(key))
    new = re.sub(r'\W', '', str(new))

    return new[:-1] if new[-1] == "_" else new


def get_all_keys(d):
    """
    Print all keys on the first level
    """
    unique = set()
    for dct in d:
        for key in dct:
            new = clean_str(key)
            unique.add(new)
    
    return unique

def get_all_info_keys(d):
    """
    Print all keys on the second level 'info' keys
    """
    unique = dict()
    for data in d:
        info_dct = data["info"]
        for info in info_dct:
            new = clean_str(info)
            unique[info] = new.lower()
    
    return unique


def get_all_actual_char(d):
    """
    Print all characters
    """
    unique = set()
    for char in d:
        info_dct = char["info"]
        if "Portrayer" in info_dct:
            unique.add(char["name"])
    
    return unique


def process_string(item):
    name: str = item.split(' (')[0].strip()
    return name.replace("\"", "")


def write_all_chars(data):
    with open("./result/clean_chars.txt", "w", encoding="utf-8") as file:
        file.write("{\n")
        for dat in data:
            clean_dat = clean_str(process_string(dat["name"]))
            file.write(f"\t\"{clean_dat}\",\n")
        file.write("}")
    

def get_all_chars(data):
    unique = set()
    for dat in data:
        clean_dat = clean_str(process_string(dat["name"]))
        unique.add(clean_dat)
    return unique
        

def get_relatives(data):
    unique = set()
    for char in data:
        for key, val in char["info"].items():
            if key in CHAR_INFO_CHAR:
                if type(val) == list:
                    for lst_value in val:
                        clean_value = clean_str(process_string(lst_value))
                else:
                    clean_value = clean_str(process_string(val))
                unique.add(clean_value)
    return unique


def get_anomaly(data):
    rels = get_relatives(data)
    chars = get_all_chars(data)
    with open("./result/problem_chars.txt", "w", encoding="utf-8") as file:
        file.write("{\n")
        for rel in rels:
            if (rel not in chars) and ("unnamed" not in rel.lower()) and ("onknown" not in rel.lower()) and ("at_least" not in rel.lower()):
                file.write(f"\t\"{rel}\",\n")
        file.write("}")
            
    
def main():
    path = "./data/spongebob_characters.json"
    data = OpenFile(path)

    write_all_chars(data)

if __name__ == "__main__":
    main()