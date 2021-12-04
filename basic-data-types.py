""" Правило #13
Базовые типы данных не должны использоваться в исходном коде,
вместо этого следует использовать переопределения
"""

import os


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
    path = os.getcwd()
    files = os.listdir(path)
    files_c = (f for f in files if f.endswith('.c') or f.endswith('.h'))

    for f in files_c:
        print(f"******************Файл {f}******************")
        scanfile(f)


def scanfile(path: str) -> None:
    with open(path) as file:
        for n, line in enumerate(file):
            if line.strip().startswith("typedef"):
                continue
            index = line.find(r"//")
            for word in c_types:
                if 0 <= line.find(word) < index:
                    print(f"[Cтрока {n}] Используется базовый тип данных:")
                    print(line, " " * (line.find(word)-1) + "^"*len(word))


if __name__ == '__main__':
    main()
