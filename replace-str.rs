use std::{env, fs, io::Write};
use regex::Regex;

fn main() {
    let re = Regex::new(r"([0-9A-F]x[0-9A-F]{2})").unwrap(); // шестнадцетиричное значение

    let mut first_str: bool = true; //Чтобы удалить только 1ю строку Write SFR_CMC0..., а следующие нет

    let mut block_a = Vec::<String>::new(); // строки с последовательностью символов _A_
    block_a.push(r#"// Initial "Config A" SFR configuration values"#.to_string());

    let mut block_b = Vec::<String>::new(); // строки с последовательностью символов _B_
    block_b.push(r#"// Initial "Config B" SFR configuration values"#.to_string());

    let mut block_c = Vec::<String>::new(); // остальные строки, за исключеним строк SFR_CMC0 и SFR_CMC1
    block_c.push(r#"// Initial "Config Common" SFR configuration values (not read-, but write-only SFRs)"#.to_string());

    let mut block_d = Vec::<String>::new(); // строки SFR_CMC0 и SFR_CMC1

    let args: Vec<String> = env::args().collect();

    let filename = &args[1];

    let content = fs::read_to_string(filename)
        .expect("При чтении файла что-то пошло не так");

    let lines: std::str::Lines = content.lines();

    for mut line in lines {
        if line.starts_with(r"//") { // 1е правило (удалить шапку)
            continue;
        }

        if line.trim().is_empty() { continue; }

        if line.starts_with("Write SFR_CMC0") && first_str { // 2е правило
            first_str = false;
            continue;
        }
        if line.starts_with("Write SFR_SFRPAGE") { // 3е правило
            continue;
        }

        // 9е правило
        let mut line_ = String::new();
        if line.contains("_MID") {
            line_ = line.replace("_MID","_MID_");
            line = &line_;
        }

        let mut line_ = String::new();
        // 15е правило
        for cap in re.captures_iter(line) {
            line_ = line.replace(&cap[1], &("(".to_string() + &cap[1] + "U)"));
            line = &line_;
            break;
        }

        if line.contains("Write SFR_RSSISLOPE") {
            line_ = line.replace("Write SFR_RSSISLOPE","Write SFR_RSSILOPE");
            line = &line_;
        }

        let mut line_ = String::new();
        if line.contains("_A_") {
            if line.contains("Write SFR_A") { // 10е правило
                line_ = line.replace("Write SFR_A","#define RF_CFG_A_SFR_VALUE");
                line = &line_;
            }
            if line.contains("#define RF_CFG_A_SFR_VALUE_EOMDLEN ") {
                line_ = line.replace("#define RF_CFG_A_SFR_VALUE_EOMDLEN",
                                     "//#define RF_CFG_A_SFR_VALUE_EOMDLEN");
                line = &line_;
            }
            if line.contains("#define RF_CFG_A_SFR_VALUE_PLLINTC1") {
                line_ = line.replace("#define RF_CFG_A_SFR_VALUE_PLLINTC1",
                                     "#define RF_CFG_A_SFR_VALUE_PLLINTC");
                line = &line_;
            }
            block_a.push(line.to_string());
            continue;
        }

        if line.contains("_B_") {
            if line.contains("Write SFR_B") { // 11е правило
                line_ = line.replace("Write SFR_B","#define RF_CFG_B_SFR_VALUE");
                line = &line_;
            }
            if line.contains(r#"#define RF_CFG_B_SFR_VALUE_IF1"#) {
                line_ = line.replace("#define RF_CFG_B_SFR_VALUE_IF1",
                                     "//#define RF_CFG_B_SFR_VALUE_IF1");
                line = &line_;
            }

            if line.contains(r#"RF_CFG_B_SFR_VALUE_EOMDLEN"#) {
                line_ = line.replace("#define RF_CFG_B_SFR_VALUE_EOMDLEN ",
                                     "//#define RF_CFG_B_SFR_VALUE_EOMDLEN ");
                line = &line_;
            }

            if line.contains("#define RF_CFG_B_SFR_VALUE_PLLINTC1") {
                line_ = line.replace("#define RF_CFG_B_SFR_VALUE_PLLINTC1",
                                     "#define RF_CFG_B_SFR_VALUE_PLLINTC");
                line = &line_;
            }
            block_b.push(line.to_string());
            continue;
        }

        if line.contains("SFR_CMC") {
            if line.trim_start().starts_with("Write SFR_CMC") { // 13е правило
                line_ = line.replace("Write SFR_","#define RF_CFG_C_SFR_VALUE_");
                line = &line_;
            }
            block_d.push(line.to_string());
            continue;
        }
        line_ = line.replace("Write SFR_","#define RF_CFG_C_SFR_VALUE_");
        line = &line_;

        block_c.push(line.to_string());
    }

    let mut file = std::fs::File::create("dst.def").expect("ошибка создания файла");

    for item in block_a {
        if item.trim().is_empty() {
            file.write_all((item).as_bytes()).expect("ошибка записи в файл");
        } else {
            file.write_all((item+"\n").as_bytes()).expect("ошибка записи в файл");
        }
    }
    file.write_all("\n".as_bytes()).expect("ошибка записи в файл");
    for item in block_b {
        if item.trim().is_empty() {
            file.write_all((item).as_bytes()).expect("ошибка записи в файл");
        } else {
            file.write_all((item+"\n").as_bytes()).expect("ошибка записи в файл");
        }
    }
    file.write_all("\n".as_bytes()).expect("ошибка записи в файл");
    for item in block_c {
        if item.trim().is_empty() {
            file.write_all((item).as_bytes()).expect("ошибка записи в файл");
        } else {
            file.write_all((item+"\n").as_bytes()).expect("ошибка записи в файл");
        }
    }

    file.write_all("\n".as_bytes()).expect("ошибка записи в файл");
    for item in block_d {
        if item.trim().is_empty() {
            file.write_all((item).as_bytes()).expect("ошибка записи в файл");
        } else {
            file.write_all((item+"\n").as_bytes()).expect("ошибка записи в файл");
        }
    }
}