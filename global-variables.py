""" Правило #8
Глобальные переменные, которые должны быть инициализированы нулем,
просто объявляются без присвоения
"""

import sys


def main():
    files_c = (f for f in sys.argv[1:] if f.endswith('.c') or f.endswith('.h'))

    for f in files_c:
        list_to_file = [] 
        list_to_file.append(f"******************Файл {f}******************")
        list_to_file = scanfile(f, list_to_file)
        with open("out.txt", "w") as out:
            for line in list_to_file:
                out.write(line)


def scanfile(path: str, list_to_file: list) -> list:
    with open(path) as file:       
        count_br = 0 # если 0 - то не в функции (т.е. глобальная)
        for n, line in enumerate(file):
            if line.find(r"//") != -1:
                line, _ = line.split(r"//")
            # ищем {
            start = -1
            while True:
                start = line.find("{", start+1)
                if start == -1:
                    break
                count_br += 1
            # ищем }
            start = -1
            while True:
                start = line.find("}", start+1)
                if start == -1:
                    break
                count_br -= 1
                    
            if line.strip().endswith("= 0;") and count_br == 0:                
                list_to_file.append(f"[Строка {n}] Глобальная переменная должна объявляться без присвоения:")
                list_to_file.append(line.strip())
                list_to_file.append(" " * (line.find("= 0;")-2) + "^")
    return list_to_file

            
if __name__ == '__main__':
    main()