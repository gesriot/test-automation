""" Правило #32
Все параметры макроса должны быть заключены в скобки
"""

import sys
import re


reg1 = re.compile(r"#define\s+\D\w*\(([a-zA-Z, 0-9]*)")
reg2 = re.compile(r"#define\s+\D\w*\(([a-zA-Z, 0-9]*)[^\\]*[\\]")
reg3 = re.compile(r"#define\s+\D\w*\s*\(") # должно быть None
reg4 = re.compile(r"#define\s+\D\w*\s+\D") # должно быть None
reg5 = re.compile(r"(#define\s+\D\w*\s+)") # для отслеживания позиции

def main():
    files_c = (f for f in sys.argv[1:] if f.endswith('.c') or f.endswith('.h'))

    for f in files_c:
        list_to_file = [] 
        list_to_file.append(f"******************Файл {f}******************\n")
        list_to_file = scanfile(f, list_to_file)
        with open("out.txt", "w") as out:
            for line in list_to_file:
                out.write(line)


def scanfile(path: str, list_to_file: list) -> list:
    with open(path) as file:
        next_line = False # критерий ищем ли мы аргументы на след.строке
                          # ищем только в том случае, если сработала reg2 - c косой чертой в конце
        for n, line in enumerate(file):
            mo2 = reg2.search(line)
            if mo2 is not None:
                next_line = True
                *args2, = mo2.group(1).split(",")
                args2 = [a.strip() for a in args2 if a.strip()]
                continue
            if next_line:
                # если косой черты нет в конце, на след.строке больше не ищем
                if not line.strip().endswith("\\"): next_line = False
                
                start = -1
                for arg in args2:
                    while True:
                        start = line.find(arg, start+1)
                        if start == -1:
                            break
                        if line[start-1] != "(" and line[start+len(arg)] != ")":
                            list_to_file.append(f"[Cтрока {n}] Параметр макроса должнен быть заключен в скобки:\n")
                            list_to_file.append(line.strip())
                            list_to_file.append(" " * (line.find(arg)-2) + "^"*len(arg))

            mo1 = reg1.search(line)
            if mo1 is not None:
                *args1, = mo1.group(1).split(",")
                args1 = [a.strip() for a in args1 if a.strip()]
                start = line.find(r")") # начинаем искать отсюда
                for arg in args1:
                    while True:
                        start = line.find(arg, start+1)
                        if start == -1:
                            break
                        if line[start-1] != "(" and line[start+len(arg)] != ")":
                            list_to_file.append(f"[Cтрока {n}] Параметр макроса должнен быть заключен в скобки:\n")
                            list_to_file.append(line+ " " * start + "^"*len(arg))
            mo3 = re.match(reg3, line)
            mo4 = re.match(reg4, line)
            if line.find("#define ") != -1 and mo3 is None and mo4 is not None:
                list_to_file.append(f"[Cтрока {n+1}] Параметр макроса должнен быть заключен в скобки:\n")
                match = re.search(reg5, line)
                start = len(match.group())-1
                list_to_file.append(line + " " * start + "^\n")                

    return list_to_file


if __name__ == '__main__':
    main()
