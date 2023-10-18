import json
import re
from collections import defaultdict
from typing import Tuple

import pandas as pd
from pandas import DataFrame, Series


class PhoneNumbersQuotasFilter:
    REGION_TYPES = ["Республика", "республика", "область", "край", "АО"]
    FEDERAL_CITY_NAMES = ["Москва", "Санкт-Петербург"]

    def __init__(self):
        self.config = self.get_config()

    @staticmethod
    def get_config():
        with open("config.json", "r") as input_file:
            return json.load(input_file)

    def make_quotas_dictionary(self) -> dict:
        quotas = defaultdict(dict)
        df = self.get_quotas_dataframe()

        for _, row in df.iterrows():
            raw_region_and_quota_name = str(row["Общая статистика"])

            if "Реклама" in raw_region_and_quota_name:
                break

            if not self.check_if_raw_region_name_is_valid(raw_region_and_quota_name):
                continue

            region_name = self.get_region_name(raw_region_and_quota_name)
            quota_name = self.get_quota_name(raw_region_and_quota_name)
            quota_value = self.get_quota_value(row)
            quota_usage = self.get_quota_usage(row)
            quota_age_from, quota_age_to = self.get_quota_age(quota_name)

            quotas[region_name][quota_name] = {
                "gender": self.get_quota_gender(quota_name),
                "age_from": quota_age_from,
                "age_to": quota_age_to,
                "balance": self.get_quota_balance(quota_value, quota_usage),
            }

        return quotas

    def get_quotas_dataframe(self) -> DataFrame:
        return pd.read_excel(self.config["quotas_file"], sheet_name=0)

    def check_if_raw_region_name_is_valid(self, raw_region_name: str) -> bool:
        if "РЕКРУТ" in raw_region_name:
            return False

        if not any(region_type in raw_region_name for region_type in self.REGION_TYPES):
            return False

        return True

    def get_region_name(self, raw_region_name: str) -> str:
        if any(fed_city_name in raw_region_name for fed_city_name in self.FEDERAL_CITY_NAMES):
            # "Москва / Московская область" --> "Москва и Московская область"
            # "Санкт-Петербург/Ленинградская область" --> "Санкт-Петербург и Ленинградская область"
            splitted_string = raw_region_name.split("/")
            city = splitted_string[0]
            region = splitted_string[1].split(">")[0].strip()
            region_name = f"{city} и {region}"

        else:
            # "Абакан/Республика Хакасия" --> "Республика Хакасия"
            splitted_string = raw_region_name.split("/")
            region_name = splitted_string[1].split(">")[0].strip()

        return region_name

    @staticmethod
    def get_quota_name(raw_quota_name) -> str:
        # "Абакан/Республика Хакасия > Женский 16-20" --> "Женский 16-20"
        if ">" not in raw_quota_name:
            return "Весь регион"

        splitted_string = raw_quota_name.split(">")

        return splitted_string[1].strip()

    @staticmethod
    def get_quota_value(row: Series) -> int | str:
        quota_value = row["Unnamed: 1"]
        if pd.isna(quota_value):
            return ""

        return int(quota_value)

    @staticmethod
    def get_quota_usage(row: Series) -> int:
        return int(row["Unnamed: 2"])

    @staticmethod
    def get_quota_balance(quota_value: int, quota_usage: int) -> int | str:
        if quota_value == "":
            return ""

        quota_balance = quota_value - quota_usage
        if quota_balance < 0:
            return 0

        return quota_balance

    @staticmethod
    def get_quota_gender(quota_name: str) -> str:
        if len(quota_name) == 0:
            return ""

        if "Женский" in quota_name:
            return "Женский"

        if "Мужской" in quota_name:
            return "Мужской"

        return ""

    @staticmethod
    def get_quota_age(quota_name: str) -> Tuple[int, int] | Tuple[str, str]:
        if "-" not in quota_name:
            # Билайн
            return "", ""

        if "+" in quota_name:
            # Группа Женский 16-20 + 21-35
            regex = re.compile(
                r"Группа (?P<gender>[а-яА-Я]*)\s?(?P<first_range_from>\d{1,2})-(?P<first_range_to>\d{1,2}) \+ "
                r"(?P<second_range_from>\d{1,2})-(?P<second_range_to>\d{1,2})"
            )
            result = regex.match(quota_name)
            return int(result["first_range_from"]), int(result["second_range_to"])
        else:
            # Женский 16-20
            ages = quota_name.split(" ")[1].split("-")
            return int(ages[0]), int(ages[1])

    def get_phone_numbers(self) -> DataFrame:
        return pd.read_excel(self.config["phone_numbers_file"])

    def filter_phone_numbers(self, phone_numbers: DataFrame, quotas: dict) -> DataFrame:
        new_rows = []
        for _, row in phone_numbers.iterrows():
            new_row = dict(row)
            region_quotas = quotas[row["RegionName"]]

            new_row_with_quota = self.make_new_row_with_quota(new_row, region_quotas)
            new_rows.append(new_row_with_quota)
            print(new_row_with_quota)

        return pd.DataFrame(new_rows)

    def make_new_row_with_quota(self, new_row: dict, region_quotas: dict) -> dict:
        region_quota = region_quotas["Весь регион"]
        if region_quota["balance"] <= 0:
            new_row["IsCallable"] = False
            new_row["Quota"] = f'"Весь регион": {json.dumps(region_quota, ensure_ascii=False)}'

            return new_row

        matching_quotas = dict()
        matching_quotas["Весь регион"] = region_quotas["Весь регион"]
        for quota_name in region_quotas:
            quota = region_quotas[quota_name]
            if self.is_group_quota_match(new_row, quota):
                matching_quotas[quota_name] = quota

        operator = new_row["OperatorName"]
        matching_quotas[operator] = region_quotas[operator]

        if all(
            matching_quotas[quota_name]["balance"] == "" or matching_quotas[quota_name]["balance"] > 0
            for quota_name in matching_quotas
        ):
            new_row["IsCallable"] = True
            new_row["Quota"] = f"{json.dumps(matching_quotas, ensure_ascii=False)}"
        else:
            new_row["IsCallable"] = False
            new_row["Quota"] = f"{json.dumps(matching_quotas, ensure_ascii=False)}"

        return new_row

    @staticmethod
    def is_group_quota_match(new_row: dict, quota: dict) -> bool:
        if (
            new_row["Пол"] == quota["gender"]
            or quota["gender"] == ""
            and isinstance(quota["age_from"], int)
            and isinstance(quota["age_to"], int)
        ) and quota["age_from"] <= new_row["Возраст"] <= quota["age_to"]:
            return True

        return False

    @staticmethod
    def is_quota_balance_zero(quota: dict) -> bool:
        if quota["balance"] == 0:
            return True

        return False

    @staticmethod
    def dump_phone_numbers_to_excel_file(phone_numbers: DataFrame) -> None:
        phone_numbers.to_excel("phone_numbers_filtered.xlsx", index=False)

    def run(self):
        quotas = self.make_quotas_dictionary()
        phone_numbers = self.get_phone_numbers()
        new_phone_numbers = self.filter_phone_numbers(phone_numbers, quotas)
        self.dump_phone_numbers_to_excel_file(new_phone_numbers)


if __name__ == "__main__":
    f = PhoneNumbersQuotasFilter()
    f.run()
