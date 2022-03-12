""" Корректность комментариев к функциям

- Если функция возвращает не void, в комментарии
@ReturnValue не должно быть написано None.
В противном случае - должно.

- Проверить количество и имена параметров в функциях
и в шапке @Parameters. Если совпадают - писать TEST PASS,
в противном случае - FAIL.
"""

import sys
import os
import re


path_results = "../test/out.txt"


def main():
    files_c = (f for f in sys.argv[1:] if f.endswith('.c'))

    for f in files_c:
        scanfile(f)
    print("\nThe result of the analysis in the file out.txt")


def add_to_file(line):
    if type(line) is not str:
        line = str(line)
        
    with open(path_results, "a") as out:
        out.write(line + "\n")


def read_data(filename: str) -> list:
    ls = []
    with open(filename, "r") as file:
        for line in file:
            ls.append(line)
    return ls


def read_fn_declaration(file_ls, number_str):
    ls = []
    number_str -= 1
    n = number_str

    if file_ls[number_str].find(")") >= 0:
        ls.append(file_ls[number_str].rstrip())
        return ls
    else:
        while(file_ls[n].find(")") == -1):
            ls.append(file_ls[n].rstrip())
            n += 1
        ls.append(file_ls[n].rstrip())
    return ls


def scanfile(path):
    reg = re.compile(r"^[\w*]+(\s[\w*]*)*\(")
    ls = []

    # затираем файл с результатами
    if os.path.exists(path_results):
        with open(path_results, "w") as out:
            f_ = path.lstrip("../test/")
            out.write(f"******************Файл {f_}******************\n")    

    with open(path) as file:
        next_line_param = False  # критерий ищем ли мы параметры на след.строке шапки @Parameters
        next_line_func = False  # критерий ищем ли мы параметры на след.строке функции
        is_fail = True # флаг, чтобы вывести FAIL всего лишь один раз
        fail_counts = 0 # количество функций с некорректной шапкой
        param_com = []
        param = []
        return_value_com = ""
        return_value = ""
        func_pos_n = 0
        is_add1 = False
        is_add2 = False

        add_ls = [] # Сюда добавляем то, что будем писать в файл, если fail_counts != 0
                    # иначе (если fail_counts == 0) мы просто напишем "PASS"

        data = read_data(path)

        for n, line in enumerate(file):
            if line.find(";") >= 0:
                continue

            if line.find("@ReturnValue") >= 0:
                return_value_com = line.split("@ReturnValue")[1].strip()

            if line.find("@Parameters") >= 0:
                is_add1 = True
                param1 = line.split("@Parameters")[1].strip()
                if param1 != "None":
                    param1 = param1.split()[0]
                    next_line_param = True

                param_com.append(param1)
                continue

            if next_line_param and line.find("**") >= 0:
                next_line_param = False  # перечисление параметров закончено

            if next_line_param:
                if (line.find("-") or line.find("–") or line.find("—")) == -1:
                    continue
                else:
                    ls_ = (line.find("-"), line.find("–"), line.find("—"))
                    n_ = [x for x in ls_ if x != -1][0]  # позиция разделителя
                    delimiter = line[n_]
                    param2 = line.split(delimiter)[0].strip().split()[1]
                    param_com.append(param2)
                    continue

            mo = reg.search(line)
            if mo is not None:
                if not line.strip().endswith(";"):
                    is_add2 = True
                    func_pos_n = n + 1
                if line.find("void ") >= 0 and (line.find("void ") < line.find("(")):
                    return_value = "None"
                else:
                    param_with_name = line.split("(")[0].strip()
                    param_name = param_with_name.split()[-1]
                    name_pos = param_with_name.find(param_name)
                    return_value = param_with_name[:name_pos].strip()  # здесь могут быть static и extern
                    if return_value.find("static ") >= 0:
                        return_value = return_value.replace("static ", "")
                    if return_value.find("extern ") >= 0:
                        return_value = return_value.replace("extern ", "")

                if line.find("void)") >= 0 and line.find(";") == -1:
                    param.append("None")
                    next_line_func = False
                    continue
                elif line.find(")") >= 0:
                    param_with_name = line.split("(")[1].split(")")[0]
                    param_name = param_with_name.split()[-1]
                    param.append(param_name)
                    next_line_func = False
                    continue
                else:  # несколько параметров
                    param_with_name = line.split("(")[1].strip()[:-1]
                    param_name = param_with_name.split()[-1]
                    param.append(param_name)
                    next_line_func = True
                    continue
            if next_line_func and line.find(")") == -1:  # не 1й и не посл. параметр
                param_with_name = line.strip()[:-1]
                
                if len(param_with_name) != 0:
                    param_name = param_with_name.split()[-1]
                    param.append(param_name)
                continue
            elif next_line_func and line.find(")") >= 0:  # посл. параметр
                param_with_name = line.strip()[:-1]
                if len(param_with_name) != 0:
                    param_name = param_with_name.split()[-1]
                    param.append(param_name)
                next_line_func = False
            if next_line_func and line.find("**") >= 0:
                next_line_func = False

            if is_add1 and is_add2:
                if is_fail:                    
                    add_ls.append("FAIL")
                    is_fail = False

                ret_val = return_value_com.strip(".")                
                
                if return_value != "None" and ret_val == "None":
                    fail_counts += 1
                    add_ls.append(f"\n[Строка {func_pos_n}]")
                    add_ls.append("В комментарии к фунции, возвращающей НЕ void в @ReturnValue НЕ должно быть написано None")
                if param_com != param:
                    fail_counts += 1
                    add_ls.append(f"\n[Строка {func_pos_n}]")
                    add_ls.append(f"@Parameters: {param_com}")

                    ls = read_fn_declaration(data, func_pos_n)
                    for l in ls:
                        add_ls.append(l)

                is_add1 = False
                is_add2 = False

                param_com = []
                param = []
        
        if fail_counts == 0:
            add_to_file("PASS")
        else:
            for l in add_ls:
                add_to_file(l)


if __name__ == '__main__':
    main()
