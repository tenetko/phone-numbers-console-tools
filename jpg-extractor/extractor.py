import pytesseract
import os
import re

import PIL
from glob import glob
import wand.image
from typing import Dict, List
from datetime import datetime


class ImageExtractor:
    PHONE_NUMBER_REGEX = re.compile(
        r".*(?P<phone_number>\+7 (\(|\[)\d{3}(\)|\]) [\d\-]+).*"
    )
    DATE_REGEX_1 = re.compile(r".*(?P<date>2023\.\d{2}\.\d{2}).*")
    DATE_REGEX_2 = re.compile(r".*(?P<date>2023\.\d{4}).*")
    DATE_REGEX_3 = re.compile(r".* (?P<date>2023\d{4} ).*")

    TIME_REGEX_1 = re.compile(r".*(?P<time>\d{2}:\d{2}:\d{2}).*")
    TIME_REGEX_2 = re.compile(r".*(?P<time>\d{2}:\d{4}).*")
    TIME_REGEX_3 = re.compile(r".*(?P<time>\d{4}:\d{2}).*")
    TIME_REGEX_4 = re.compile(r".*\s(?P<time>[0-2][0-9]\d{4})\s.*")
    TIME_REGEX_5 = re.compile(r".*\s(?P<time>[0-2][0-9]\d{2}\.\d{2})\s.*")
    TIME_REGEX_6 = re.compile(r".*\s(?P<time>[0-2][0-9][0-5][0-9][0-5][0-9])$")

    def recognize_images(self) -> None:
        results = []

        for file_name in glob("*.jpg"):
            text = self.recognize_image(file_name)
            text = text.split("\n")
            result = self.parse_text(text)
            result["file_name"] = file_name
            result["datetime"] = self.get_date_time(result)
            results.append(result)

            self.dump_result(results)

    def recognize_image(self, file_name: str) -> str:
        self.create_contrasted_image(file_name)
        image = PIL.Image.open(f"./temp/{file_name}")
        text = pytesseract.image_to_string(image, lang="rus")

        return text

    def create_contrasted_image(self, file_name: str) -> None:
        if not os.path.exists("./temp"):
            os.makedirs("./temp")

        with wand.image.Image(filename=file_name) as image:
            with image.clone() as brightness_contrast:
                brightness_contrast.brightness_contrast(int(-40), int(+60))
                brightness_contrast.save(filename=f"./temp/{file_name}")

    def parse_text(self, text: List) -> Dict:
        result = {}
        for row in text:
            if match := self.PHONE_NUMBER_REGEX.match(row):
                phone_number = re.sub(r"[\[\]()+\s\-]", "", match.group("phone_number"))
                result["phone_number"] = phone_number

            if "руб" in row:
                result["amount"] = row.replace(" руб.", "").replace("Сумма", "").strip()

            if match := self.DATE_REGEX_1.match(row):
                result["date"] = match.group("date")

            if match := self.DATE_REGEX_2.match(row):
                date = match.group("date")
                date = f"{date[:4]}.{date[5:7]}.{date[7:9]}"
                result["date"] = date

            if match := self.DATE_REGEX_3.match(row):
                date = match.group("date")
                date = f"{date[:4]}.{date[4:6]}.{date[6:8]}"
                result["date"] = date

            if match := self.TIME_REGEX_1.match(row):
                if "time" in result:
                    continue
                result["time"] = match.group("time")

            elif match := self.TIME_REGEX_2.match(row):
                if "time" in result:
                    continue
                time = match.group("time")
                time = f"{time[:2]}:{time[3:5]}:{time[5:7]}"
                result["time"] = time

            elif match := self.TIME_REGEX_3.match(row):
                if "time" in result:
                    continue
                time = match.group("time")
                time = f"{time[:2]}:{time[2:4]}:{time[5:7]}"
                result["time"] = time

            elif match := self.TIME_REGEX_4.match(row):
                if "time" in result:
                    continue
                time = match.group("time")
                time = f"{time[:2]}:{time[2:4]}:{time[4:6]}"
                result["time"] = time

            elif match := self.TIME_REGEX_5.match(row):
                if "time" in result:
                    continue
                time = match.group("time")
                time = f"{time[:2]}:{time[2:4]}:{time[5:7]}"
                result["time"] = time

            elif match := self.TIME_REGEX_6.match(row):
                if "time" in result:
                    continue
                time = match.group("time")
                time = f"{time[:2]}:{time[2:4]}:{time[4:6]}"
                result["time"] = time

        return result

    def get_date_time(self, result: Dict) -> str:
        date_time = ""

        if "time" in result:
            try:
                date_time = f"{result['date']} {result['time']}"
                date_time = datetime.strptime(date_time, "%Y.%m.%d %H:%M:%S")
                date_time = datetime.strftime(date_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                date_time = datetime.strptime(result["date"], "%Y.%m.%d")
                date_time = datetime.strftime(date_time, "%Y-%m-%d")

        else:
            date_time = datetime.strptime(result["date"], "%Y.%m.%d")
            date_time = datetime.strftime(date_time, "%Y-%m-%d")

        return date_time

    def dump_result(self, results: List) -> None:
        with open("report.csv", "w") as output_file:
            output_file.write("phone_number,amount,date,file_name\n")
            for record in results:
                output_file.write(f"{record.get('phone_number', '')},")
                output_file.write(f"{record['amount']},")
                output_file.write(f"{record['datetime']},")
                output_file.write(f"{record['file_name']}\n")


if __name__ == "__main__":
    extractor = ImageExtractor()
    extractor.recognize_images()