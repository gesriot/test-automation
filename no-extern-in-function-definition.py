""" Правило #24
При объявлении и определении функции не следует использовать "extern"
"""

import sys


def main():
    files_c = (f for f in sys.argv[1:] if f.endswith('.c'))

    for f in files_c:
        list_to_file = [] 
        list_to_file.append(f"******************Файл {f}******************")
        list_to_file = scanfile(f, list_to_file)
        with open("out.txt", "w") as out:
            for line in list_to_file:
                out.write(line)


def scanfile(path: str, list_to_file: list) -> list:
    with open(path) as file:
        for n, line in enumerate(file):
            index_com = line.find(r"//")
            index_br = line.find(r"(")
            is_extern = line.strip().startswith("extern")
            if not is_extern:
                continue
            if index_br >= 0 and index_com >= 0 and index_br < index_com:
                list_to_file.append(f'[Cтрока {n}] При объявлении/определении функции не следует использовать "extern":')
                list_to_file.append(line + " " * (line.find("extern")) + "^"*len("extern"))
                continue
            if index_br >= 0 and index_com == -1:
                list_to_file.append(f'[Cтрока {n}] При объявлении/определении функции не следует использовать "extern":')
                list_to_file.append(line + " " * (line.find("extern")) + "^"*len("extern"))            
                continue
            if index_br == -1:
                continue
    return list_to_file


if __name__ == '__main__':
    main()
