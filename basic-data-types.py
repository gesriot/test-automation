""" Правило #13
Базовые типы данных не должны использоваться в исходном коде,
вместо этого следует использовать переопределения
"""

import sys
import os


c_types = (
    "const char ", "const signed char ", "const unsigned char ", "unsigned char ",
    "signed char ", "char ", "short ", "short int ", "signed short ",
    "signed short int ", "unsigned short ", "unsigned short int ",
    "signed ", "signed int ", "unsigned ", "unsigned int ", "long ", "long int ",
    "signed long ", "signed long int ", "unsigned long ", "unsigned long int ",
    "long long ", "long long int ", "signed long long ", "signed long long int ",
    "unsigned long long ", "unsigned long long int ", "int ", 
    "float ", "double ", "long double ",    
    )


def main():
    files_c = (f for f in sys.argv[1:] if f.endswith('.c'))

    # Затираем файл с результатами
    if os.path.exists("out.txt"):
        with open("out.txt", "w") as out:
            out.write("")

    for f in files_c:
        list_to_file = []  
        list_to_file.append(f"******************Файл {f}******************\n")
        list_to_file = scanfile(f, list_to_file)
        with open("out.txt", "a") as out:
            for line in list_to_file:
                out.write(line)
count = 0

def scanfile(path: str, list_to_file: list) -> list:
    with open(path) as file:
        for n, line in enumerate(file):
            if line.strip().startswith("typedef"):
                continue
            index = line.find(r"//")
            for word in c_types:
                if index == -1:
                    if line.find(word) != -1:                        
                        list_to_file.append(f"[Строка {n+1}] Используется базовый тип данных:\n")
                        list_to_file.append(line)
                        list_to_file.append(" " * (line.find(word)) + "^" + "\n")
                        break
                else:
                    if -1 < line.find(word) < index:                        
                        list_to_file.append(f"[Строка {n+1}] Используется базовый тип данных:\n")
                        list_to_file.append(line)
                        list_to_file.append(" " * (line.find(word)) + "^" + "\n")
                        break
    return list_to_file


if __name__ == '__main__':
    main()
