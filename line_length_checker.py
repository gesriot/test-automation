import sys
import os


def main():
    files_c = (f for f in sys.argv[1:] if f.endswith('.c') or f.endswith('.h'))

    if os.path.exists("out.txt"):
        with open("out.txt", "w") as out:
            out.write(f"")

    for f in files_c:
        ls = [] 
        ls = scanfile(f, ls)
        with open("out.txt", "a") as out:
            for line in ls:
                out.write(line+"\n")

        
def scanfile(path: str, ls: list) -> list:
    count_all = 0
    count_comment = 0
    count_multicomment = 0
    multicomment_track = False
    count_empty = 0
    long_lines = []
    with open(path) as file:
        for n, line in enumerate(file):
            count_all += 1
            if len(line)>100:
                long_lines.append(n+1)
            if line.strip().startswith(r"//") and multicomment_track is False:
                count_comment += 1
            if not line.strip():
                count_empty += 1
            if line.strip().startswith(r"/*"):
                count_multicomment += 1
                multicomment_track = True
                continue
            if multicomment_track:
                count_multicomment += 1
            if line.strip().endswith(r"*/"):
                multicomment_track = False

    k_comment = (count_comment+count_multicomment)/count_all * 100.0
    k_empty = count_empty/count_all * 100.0
    k_comment_empty = (count_comment+count_multicomment+count_empty)/count_all * 100.0
    k_code = (count_all-count_comment-count_multicomment-count_empty)/count_all * 100.0
    ls.append(f"Файл {path}:")
    if len(long_lines) == 1:
        ls.append(f"Строка {long_lines[0]} слишком длинная, разбейте на две")
    elif len(long_lines) > 1:
        long_lines = ", ".join(str(i) for i in long_lines)
        ls.append(f"Строки {long_lines} слишком длинные, разбейте на две")
    ls.append(f"Комментариев: {round(k_comment, 2)}%")
    ls.append(f"Комментариев и пустых строк: {round(k_comment_empty, 2)}%")
    ls.append(f"Кода: {round(k_code, 2)}%")
    ls.append(f"Пустых строк: {round(k_empty, 2)}%\n")
    return ls

if __name__ == "__main__":
    main()
