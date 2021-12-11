""" Правило #13
Базовые типы данных не должны использоваться в исходном коде,
вместо этого следует использовать переопределения
"""

import sys


c_types = (
    "char", "signed char", "unsigned char",
    "short", "short int", "signed short", "signed short int",
    "unsigned short", "unsigned short int",
    "int", "signed", "signed int",
    "unsigned", "unsigned int",
    "long", "long int", "signed long", "signed long int",
    "unsigned long", "unsigned long int",
    "long long", "long long int", "signed long long", "signed long long int",
    "unsigned long long", "unsigned long long int",
    "float", "double", "long double",    
    )


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
        for n, line in enumerate(file):
            if line.strip().startswith("typedef"):
                continue
            index = line.find(r"//")
            for word in c_types:
                if 0 <= line.find(word) < index:
                    list_to_file.append()
                    list_to_file.append(f"[Cтрока {n}] Используется базовый тип данных:")
                    list_to_file.append(line, " " * (line.find(word)-1) + "^"*len(word))
    return list_to_file


if __name__ == '__main__':
    main()