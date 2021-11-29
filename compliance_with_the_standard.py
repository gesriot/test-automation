from os import getcwd, listdir
import re


def must_be_comment(path: str) -> None:
    """Все объявления и определения идентификаторов должны быть прокомментированы"""
    with open(path) as file:
        for n, line in enumerate(file):
            pass

def only_ads(path: str) -> None:
    """В заголовочном h-файле должны быть только объявления идентификаторов, все объявления в с-файле(исключение - inline-функции)"""
    if path.endswith(".h"):
        pass
    elif path.endswith(".c"):
        pass

def main():
    path = getcwd()
    files = listdir(path)
    files_c = [f for f in files if f.endswith('.c') or f.endswith('.h')]

    for f in files_c:
        only_ads(f)


if __name__ == '__main__':
    main()
