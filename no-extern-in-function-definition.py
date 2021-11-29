""" Правило #24
При объявлении и определении функции не следует использовать "extern"
"""

import os


def main():
    path = os.getcwd()
    files = os.listdir(path)
    files_c = (f for f in files if f.endswith('.c') or f.endswith('.h'))

    for f in files_c:
        print(f"******************Файл {f}******************")
        scanfile(f)


def scanfile(path: str) -> None:
    with open(path) as file:
        for n, line in enumerate(file):
            index_com = line.find(r"//")
            index_br = line.find(r"(")
            is_extern = line.strip().startswith("extern")
            if not is_extern:
                continue
            if index_br >= 0 and index_com >= 0 and index_br < index_com:
                print(f'[Cтрока {n}] При объявлении/определении функции не следует использовать "extern":')
                print(line + " " * (line.find("extern")) + "^"*len("extern"))
                continue
            if index_br >= 0 and index_com == -1:
                print(f'[Cтрока {n}] При объявлении/определении функции не следует использовать "extern":')
                print(line + " " * (line.find("extern")) + "^"*len("extern"))            
                continue
            if index_br == -1:
                continue


if __name__ == '__main__':
    main()
