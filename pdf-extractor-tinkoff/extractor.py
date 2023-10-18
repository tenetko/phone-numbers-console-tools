import re
from datetime import datetime
from glob import glob
from typing import List

from pdfquery import PDFQuery
from pyquery.pyquery import PyQuery


class PhoneNumbersExtractor:
    MONTH_CONVERTER = {
        "января": "January",
        "февраля": "February",
        "марта": "March",
        "апреля": "April",
        "мая": "May",
        "июня": "June",
        "июля": "July",
        "августа": "August",
        "сентября": "September",
        "октября": "October",
        "ноября": "November",
        "декабря": "December",
    }

    DATE_REGEX = re.compile(r"\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2}")

    def parse_files(self) -> List:
        phone_numbers = []
        files = glob("*.pdf")
        counter = 0
        for file_name in files:
            phone_numbers.append(self.parse_file(file_name))
            counter += 1
            print(f"{counter} / {len(files)}")

        return phone_numbers

    def parse_file(self, file_name: str) -> str:
        pdf = PDFQuery(file_name)
        pdf.load()

        text_elements = pdf.pq("LTTextBoxHorizontal")
        phone_number = self.extract_phone_number_from_file(text_elements)
        sum = self.extract_sum_from_file(text_elements)

        text_elements = pdf.pq("LTTextLineHorizontal")
        operation_datetime = self.extract_date_from_file(text_elements)

        result = f"{phone_number},{sum},{operation_datetime}"

        return result

    def extract_phone_number_from_file(self, text_elements: PyQuery) -> str:
        for e in text_elements:
            text = e.text
            if len(text) > 0 and text[0] == "+":
                phone_number = self.format_phone_number(text)

                return phone_number

    def format_phone_number(self, phone_number: str) -> str:
        return re.sub(r"[()\s\+\-]+", "", phone_number)

    def extract_sum_from_file(self, text_elements: PyQuery) -> str:
        get_next_row = False

        for e in text_elements:
            text = e.text
            if len(text) > 0 and "Сумма" in text:
                get_next_row = True

            if get_next_row is True and len(text) > 0 and "i" in text:
                payment_sum = self.format_payment_sum(text).replace(" i", "").strip()

                return payment_sum

    def format_payment_sum(self, sum: str) -> str:
        return sum.replace("₽", "").replace(",", ".")

    def extract_date_from_file(self, text_elements: PyQuery):
        for e in text_elements:
            text = e.text
            match = self.DATE_REGEX.match(text)
            if match:
                operation_datetime = self.format_operation_datetime(text.strip())

                return operation_datetime

    def format_operation_datetime(self, dt: str) -> str:
        dt_parsed = datetime.strptime(dt, "%d.%m.%Y %H:%M:%S")
        return datetime.strftime(dt_parsed, "%Y-%m-%d %H:%M:%S")

    def run(self) -> None:
        phone_numbers = self.parse_files()
        with open("report.csv", "w", encoding="cp1251") as output_file:
            output_file.write("phone_number,sum,operation_date\n")
            for e in phone_numbers:
                output_file.write(f"{e}\n")


if __name__ == "__main__":
    e = PhoneNumbersExtractor()
    e.run()
