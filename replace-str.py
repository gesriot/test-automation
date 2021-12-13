import sys
import re

def main():
    filenames = [f for f in sys.argv[1:] if f.endswith(".def")]

    if len(filenames) == 0: return
    elif len(filenames) == 1:
        ls = modify_strings(filenames[0])
        save_data("dst.def", ls)
    else:
        for i, filename in enumerate(filenames):
            ls = modify_strings(filename)
            save_data("dst" + str(i+1) + ".def", ls)


def read_data(filename: str) -> list:
    ls = []
    with open(filename) as file:
        for line in file:
            ls.append(line)
    return ls


def save_data(output: str, ls: list) -> None:
    with open(output, "w") as out:
        for line in ls:
            out.write(line)


def modify_strings(filename: str) -> list:
    reg = re.compile(r"([0-9A-F]x[0-9A-F]{2})") # шестнадцетиричное значение
                      
    lines = read_data(filename)

    first_str = True # Чтобы удалить только 1ю строку Write SFR_CMC0..., а следующие нет
    block_a = []
    block_a.append('// Initial "Config A" SFR configuration values\n')

    block_b = []
    block_b.append('// Initial "Config B" SFR configuration values\n')

    block_c = []
    block_c.append('// Initial "Config Common" SFR configuration values (not read-, but write-only SFRs)\n')

    block_d = []

    for line in lines:
        if line.startswith("//"): continue # 1е требование (удалить шапку)
        
        if not line.strip(): continue
        
        if line.startswith("Write SFR_CMC0") and first_str: # 2е требование
            first_str = False
            continue

        if line.find("Write SFR_SFRPAGE     	0x00	 //Special Function Register Page Register") >= 0: # 3е требование
            continue

        if line.find("_MID") >= 0: # 9е требование
            line = line.replace("_MID","_MID_")    

        mo = reg.search(line) # 15е требование
        if mo is not None:
            line = line.replace(mo.group(), "(" + mo.group() + "U)")
            
        # Блок А
        if line.find("_A_") >= 0:            
            if line.find("Write SFR_A") >= 0:  # 10е требование                
                line = line.replace("Write SFR_A", "#define RF_CFG_A_SFR_VALUE")       

        # Блок B
        if line.find("_B_") >= 0:            
            if line.find("Write SFR_B") >= 0:  # 11е требование                
                line = line.replace("Write SFR_B", "#define RF_CFG_B_SFR_VALUE")            

        # Блок D
        if line.find("SFR_CMC") >= 0:                       
            if line.find("Write SFR_CMC") >= 0:  # 13е требование           
                line = line.replace("Write SFR_", "#define RF_CFG_C_SFR_VALUE_")
                block_d.append(line)
                continue

        # Блок C - все остальные строки (кот. не вошли в блоки A,B или D)
        if line.find("Write SFR_") >= 0:            
            line = line.replace("Write SFR_", "#define RF_CFG_C_SFR_VALUE_")       
        


        # Теперь добавляем эти измененные строки в списки A,B,C и D
        # Блок А
        if line.find("_A_") >= 0:            
            block_a.append(line)
            continue

        # Блок B
        if line.find("_B_") >= 0:            
            block_b.append(line)
            continue        

        # Блок C - все остальные строки (кот. не вошли в блоки A,B или D)
        block_c.append(line) 

    # 14е требование    
    for i, a in enumerate(block_a):
        if a.find("#define RF_CFG_A_SFR_VALUE_IF1 ") >= 0:
            block_a[i] = a.replace("#define RF_CFG_A_SFR_VALUE_IF1 ", "//#define RF_CFG_A_SFR_VALUE_IF1 ")  
        if a.find("#define RF_CFG_A_SFR_VALUE_EOMDLEN ") >= 0:
            block_a[i] = a.replace("#define RF_CFG_A_SFR_VALUE_EOMDLEN ", "//#define RF_CFG_A_SFR_VALUE_EOMDLEN ")  
        if a.find("#define RF_CFG_A_SFR_VALUE_PLLINTC1 ") >= 0:
            block_a[i] = a.replace("#define RF_CFG_A_SFR_VALUE_PLLINTC1 ", "#define RF_CFG_A_SFR_VALUE_PLLINTC ") 
    
    for i, b in enumerate(block_b):
        if b.find("#define RF_CFG_B_SFR_VALUE_IF1 ") >= 0:
            block_b[i] = b.replace("#define RF_CFG_B_SFR_VALUE_IF1 ", "//#define RF_CFG_B_SFR_VALUE_IF1 ")  
        if b.find("RF_CFG_B_SFR_VALUE_EOMDLEN ") >= 0:
            block_b[i] = b.replace("#define RF_CFG_B_SFR_VALUE_EOMDLEN ", "//#define RF_CFG_B_SFR_VALUE_EOMDLEN ") 
        if b.find("#define RF_CFG_B_SFR_VALUE_PLLINTC1 ") >= 0:
            block_b[i] = b.replace("#define RF_CFG_B_SFR_VALUE_PLLINTC1 ", "#define RF_CFG_B_SFR_VALUE_PLLINTC ") 

    for i, c in enumerate(block_c):
        if c.find("#define RF_CFG_C_SFR_VALUE_RSSISLOPE ") >= 0:
            block_c[i] = c.replace("#define RF_CFG_C_SFR_VALUE_RSSISLOPE ", "#define RF_CFG_C_SFR_VALUE_RSSILOPE ") 
    
    block_a.append("\n")   
    block_a.extend(block_b)
    block_a.append("\n")
    block_a.extend(block_c)
    block_a.append("\n")
    block_a.extend(block_d)
    return block_a

                    
if __name__ == "__main__":
    main()
