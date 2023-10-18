import re
import shutil
import sys
from glob import glob

checklist = []
regex = re.compile(r"[\d_\\\-\.]+\d+_BHT_\d+_(?P<phone_number>\d+)_.*")
path_template = "\\\\rumow1-fp01\\Work\\Field\\Projects\\Tele2\\2023_CATI\\21-095526-28-01_Трекинг здоровья бренда_Октябрь_2023\\SIIS\\DEX_audio\\{file_name}"
report = []

with open("checklist.txt", "r", encoding="utf-8") as input_file:
    checklist = [row.strip() for row in input_file]

folder_name = sys.argv[1]
for file_name in glob(f"{folder_name}/*"):
    match = regex.match(file_name)

    if match:
        phone_number = match.group("phone_number")
        if phone_number in checklist:
            dest_dir = "."
            shutil.copy(file_name, dest_dir)
            new_file_name = file_name[len(folder_name) :]
            report.append(f"{phone_number},{path_template.format(file_name=new_file_name)}")

with open("result.csv", "w", encoding="cp1251") as output_file:
    output_file.write("phone_number,path\n")
    for row in report:
        output_file.write(f"{row}\n")
