import re
from glob import glob
from typing import List

from pdfquery import PDFQuery


class PhoneNumbersExtractor:
    def parse_files(self) -> List:
        phone_numbers = []
        for file_name in glob("*.pdf"):
            phone_numbers.append(self.parse_file(file_name))

        return phone_numbers

    def parse_file(self, file_name: str) -> str:
        pdf = PDFQuery(file_name)
        pdf.load()

        text_elements = pdf.pq("LTTextLineHorizontal")
        phone_number = self.extract_phone_number_from_file(text_elements)
        sum = self.extract_sum_from_file(text_elements)

        result = f"{phone_number},{sum}"

        return result

    def extract_phone_number_from_file(self, text_elements):
        for e in text_elements:
            text = e.text
            if len(text) > 0 and text[0] == "+":
                phone_number = self.format_phone_number(text)

                return phone_number

    def extract_sum_from_file(self, text_elements):
        get_next_row = False

        for e in text_elements:
            text = e.text
            if len(text) > 0 and "Сумма платежа" in text:
                get_next_row = True

            if get_next_row is True and len(text) > 0 and "₽" in text:
                payment_sum = self.format_payment_sum(text)

                return payment_sum

    def format_phone_number(self, phone_number: str) -> str:
        return re.sub(r"[()\s\+\-]+", "", phone_number)

    def format_payment_sum(self, sum: str) -> str:
        return sum.replace("₽", "").replace(",", ".")

    def run(self):
        phone_numbers = self.parse_files()
        print("phone_number,sum")
        for e in phone_numbers:
            print(e)


if __name__ == "__main__":
    e = PhoneNumbersExtractor()
    e.run()
