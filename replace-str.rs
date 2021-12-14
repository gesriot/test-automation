use std::{env, fs, io::Write};
use regex::Regex;

fn main() {
    let filenames: Vec<String> = env::args().filter(|s| s.ends_with(".def")).collect();

    if filenames.len() == 0 { return; }
    else if filenames.len() == 1 {
        let ls = modify_strings(&filenames[0]);
        save_data("dst.def".to_string(), ls);
    } else {
        for (i, filename) in filenames.iter().enumerate() {
            let ls = modify_strings(filename);
            save_data("dst".to_owned() + &(i+1).to_string() + ".def", ls)
        }
    }
}

fn read_data(filename: &String) -> Vec<String> {
    let mut ls: Vec<String> = vec![];

    let content = fs::read_to_string(filename)
        .expect("При чтении файла что-то пошло не так");

    let lines: std::str::Lines = content.lines();

    for line in lines {
        ls.push(line.to_string());
    }
    ls
}

fn save_data(output: String, ls: Vec<String>) {
    let mut file = std::fs::File::create(output).expect("ошибка создания файла");

    for item in ls {
        file.write_all((item).as_bytes()).expect("ошибка записи в файл");
    }
}

fn modify_strings(filename: &String) -> Vec<String> {
    let re = Regex::new(r"([0-9A-F]x[0-9A-F]{2})").unwrap(); // шестнадцетиричное значение

    let lines = read_data(filename);

    let mut first_str = true; // Чтобы удалить только 1ю строку Write SFR_CMC0..., а следующие нет

    let mut block_a: Vec<String> = Vec::with_capacity(90); // строки с последовательностью символов _A_
    block_a.push("// Initial \"Config A\" SFR configuration values\n".to_string());

    let mut block_b: Vec<String> = Vec::with_capacity(90); // строки с последовательностью символов _B_
    block_b.push("// Initial \"Config B\" SFR configuration values\n".to_string());

    let mut block_c: Vec<String> = Vec::with_capacity(55); // остальные строки, за исключеним строк SFR_CMC0 и SFR_CMC1
    block_c.push("// Initial \"Config Common\" SFR configuration values (not read-, but write-only SFRs)\n".to_string());

    let mut block_d: Vec<String> = Vec::with_capacity(4); // строки SFR_CMC0 и SFR_CMC1

    for mut line in lines {
        if line.starts_with(r"//") { // 1е требование (удалить шапку)
            continue;
        }
        if line.trim().is_empty() { continue; }

        if line.starts_with("Write SFR_CMC0") && first_str { // 2е требование
            first_str = false;
            continue;
        }
        if line.contains("Write SFR_SFRPAGE     	0x00	 //Special Function Register Page Register") { // 3е требование
            continue
        }

        // 9е требование
        if line.contains("_MID") {
            line = line.replace("_MID","_MID_");
        }

        for cap in re.captures_iter(&line) {
            line = line.replace(&cap[1], &("(".to_string() + &cap[1] + "U)"));
            break;
        }

        // Блок А
        if line.contains("_A_") {
            if line.contains("Write SFR_A") { // 10е требование
                line = line.replace("Write SFR_A", "#define RF_CFG_A_SFR_VALUE");
            }
        }

        // Блок B
        if line.contains("_B_") {
            if line.contains("Write SFR_B") { // 11е требование
                line = line.replace("Write SFR_B", "#define RF_CFG_B_SFR_VALUE");
            }
        }

        // Блок D
        if line.contains("SFR_CMC") {
            if line.contains("Write SFR_CMC") { // 13е требование
                line = line.replace("Write SFR_", "#define RF_CFG_C_SFR_VALUE_") + "\n";
                block_d.push(line);
                continue;
            }
        }

        // Блок C – все остальные строки (кот. не вошли в блоки A,B или D)
        if line.contains("Write SFR_") {
            line = line.replace("Write SFR_", "#define RF_CFG_C_SFR_VALUE_");
        }

        // Теперь добавляем эти измененные строки в списки A,B,C и D
        // Блок А
        if line.contains("_A_") {
            block_a.push(line + "\n");
            continue;
        }

        // Блок B
        if line.contains("_B_") {
            block_b.push(line + "\n");
            continue;
        }

        // Блок C – все остальные строки (кот. не вошли в блоки A,B или D)
        block_c.push(line + "\n");
    }

    // 14е требование
    for (i, a) in block_a.clone().iter().enumerate() {
        if a.contains("#define RF_CFG_A_SFR_VALUE_IF1 ") {
            block_a[i] = a.replace("#define RF_CFG_A_SFR_VALUE_IF1 ", "//#define RF_CFG_A_SFR_VALUE_IF1 ");
        }
        if a.contains("#define RF_CFG_A_SFR_VALUE_EOMDLEN ") {
            block_a[i] = a.replace("#define RF_CFG_A_SFR_VALUE_EOMDLEN ", "//#define RF_CFG_A_SFR_VALUE_EOMDLEN ");
        }
        if a.contains("#define RF_CFG_A_SFR_VALUE_PLLINTC1 ") {
            block_a[i] = a.replace("#define RF_CFG_A_SFR_VALUE_PLLINTC1 ", "#define RF_CFG_A_SFR_VALUE_PLLINTC ");
        }
    }

    for (i, b) in block_b.clone().iter().enumerate() {
        if b.contains("#define RF_CFG_B_SFR_VALUE_IF1 ") {
            block_b[i] = b.replace("#define RF_CFG_B_SFR_VALUE_IF1 ", "//#define RF_CFG_B_SFR_VALUE_IF1 ");
        }
        if b.contains("RF_CFG_B_SFR_VALUE_EOMDLEN ") {
            block_b[i] = b.replace("#define RF_CFG_B_SFR_VALUE_EOMDLEN ", "//#define RF_CFG_B_SFR_VALUE_EOMDLEN ");
        }
        if b.contains("#define RF_CFG_B_SFR_VALUE_PLLINTC1 ") {
            block_b[i] = b.replace("#define RF_CFG_B_SFR_VALUE_PLLINTC1 ", "#define RF_CFG_B_SFR_VALUE_PLLINTC ");
        }
    }

    for (i, c) in block_c.clone().iter().enumerate() {
        if c.contains("#define RF_CFG_C_SFR_VALUE_RSSISLOPE ") {
            block_c[i] = c.replace("#define RF_CFG_C_SFR_VALUE_RSSISLOPE ", "#define RF_CFG_C_SFR_VALUE_RSSILOPE ");
        }
    }

    block_a.push("\n".to_string());
    block_a.extend(block_b);
    block_a.push("\n".to_string());
    block_a.extend(block_c);
    block_a.push("\n".to_string());
    block_a.extend(block_d);

    block_a
}