import json
from datetime import time
from typing import Dict, List

import pandas as pd


class ConfigMaker:
    FILE_NAME = "./xlsx/Alive_TZB.xlsx"

    def make_regions_config(self) -> Dict[str, str]:
        regions = {}

        df = pd.read_excel(self.FILE_NAME, sheet_name="Region-->TZB_Reg_code")

        for _, row in df.iterrows():
            regions[row["Unnamed: 0"].strip()] = row["из проекта ТЗБ"].strip()

        return regions

    def make_region_codes_config(self) -> Dict[str, str]:
        region_codes = {}

        df = pd.read_excel(self.FILE_NAME, sheet_name="Region-->TZB_Reg_code")

        for _, row in df.iterrows():
            if pd.isna(row["Code_region_TZB"]):
                continue

            region_codes[row["Region_TZB"]] = int(row["Code_region_TZB"])

        return region_codes

    def make_operators_config(self) -> Dict[str, str]:
        operators = {}

        df = pd.read_excel(self.FILE_NAME, sheet_name="Oper-->TZB_Oper_Code")

        for _, row in df.iterrows():
            operators[row["OPERATOR"]] = row["GrM_Name"]

        return operators

    def make_operator_codes_config(self) -> Dict[str, int]:
        operator_codes = {}

        df = pd.read_excel(self.FILE_NAME, sheet_name="Oper-->TZB_Oper_Code")

        for _, row in df.iterrows():
            if pd.isna(row["GrS_Name"]):
                continue

            operator_codes[row["GrS_Name"]] = int(row["GrS_Code"])

        return operator_codes

    def make_time_difference_config(self) -> Dict[str, str]:
        time_difference_config = {}

        df = pd.read_excel(self.FILE_NAME, sheet_name="Region-->UTC")

        for _, row in df.iterrows():
            time_difference_config[row["RegionName"]] = row["TimeDifference"]

        return time_difference_config

    def make_intervals_config(self) -> Dict[str, Dict[str, str]]:
        intervals = {}

        df = pd.read_excel(self.FILE_NAME, sheet_name="Region-->Interval")

        for _, row in df.iterrows():
            intervals[row["RegionName"]] = {
                "begin": self.convert_time_to_string(row["CallIntervalBegin"]),
                "end": self.convert_time_to_string(row["CallIntervalEnd"]),
            }

        return intervals

    def convert_time_to_string(self, time: time) -> str:
        if pd.isna(time):
            return ""

        return time.strftime("%H:%M:%S")

    def make_ignore_config(self) -> List[str]:
        ignore = []

        df = pd.read_excel(self.FILE_NAME, sheet_name="Region-->TZB_Reg_code")

        for _, row in df.iterrows():
            if row["Code_region_TZB"] == 0:
                ignore.append(row["Region_TZB"])

        return ignore

    def make_config_file(self) -> None:
        config = {}

        config["regions"] = self.make_regions_config()
        config["region_codes"] = self.make_region_codes_config()
        config["operators"] = self.make_operators_config()
        config["operator_codes"] = self.make_operator_codes_config()
        config["time_difference"] = self.make_time_difference_config()
        config["intervals"] = self.make_intervals_config()
        config["ignores"] = self.make_ignore_config()
        config["allowed_operators"] = {}
        config["forbidden_operators"] = {}

        with open("project_config_tzb.json", "w") as output_file:
            output_file.write(json.dumps(config, ensure_ascii=False, indent=4))

    def run(self) -> None:
        self.make_config_file()


if __name__ == "__main__":
    cm = ConfigMaker()
    cm.run()
