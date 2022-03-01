"""
Глобальные переменные, которые должны быть инициализированы нулем,
просто объявляются без присвоения
"""

import sys
import re
import os


path_results = "../test/out.txt"


def main():
    if os.path.exists(path_results):
        with open(path_results, "w") as out:
            out.write("")
    
    files_c = (f for f in sys.argv[1:] if f.endswith('.c'))

    for f in files_c:
        list_to_file = [] 
        f_ = f.lstrip("../test/")  
        list_to_file.append(f"******************Файл {f_}******************")
        list_to_file = scanfile(f, list_to_file)
        with open(path_results, "a") as out:
            for line in list_to_file:
                out.write(line)
                
    print("\nThe result of the analysis in the file out.txt")


def scanfile(path: str, list_to_file: list) -> list:
    reg1 = re.compile(r"\s*0U?\.?0*\s*;")
    reg2 = re.compile(r"\s*\{(0?U?\.?0?,\s*)*0?U?\.?0?\s*\}\s*;")
    is_multicomment = False
    with open(path) as file:       
        count_br = 0 # если 0 - то не в функции (т.е. глобальная)
        for n, line in enumerate(file):
            if line.strip().startswith(r"/*"):
                is_multicomment = True
                continue
            if line.find(r"//") != -1:
                line, *l = line.split(r"//")
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
            mo1 = reg1.search(line)
            mo2 = reg2.search(line)
            if (mo1 is not None or mo2 is not None) and count_br == 0 and is_multicomment is False:                
                list_to_file.append(f"\n[Строка {n+1}] Глобальная переменная должна объявляться без присвоения:\n")
                list_to_file.append(line.strip())
                list_to_file.append("\n" + " " * (line.find("=")) + "^")
            if line.strip().endswith(r"*/"):
                is_multicomment = False
    return list_to_file

            
if __name__ == '__main__':
    main()
