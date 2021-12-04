""" Правило #8
Глобальные переменные, которые должны быть инициализированы нулем,
просто объявляются без присвоения
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
                print(f"[Строка {n}] Глобальная переменная должна объявляться без присвоения:")
                print(line.strip())
                print(" " * (line.find("= 0;")-2) + "^")

            
if __name__ == '__main__':
    main()
