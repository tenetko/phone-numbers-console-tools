import json
from datetime import time
from typing import Dict, Tuple

import pandas as pd


class ConfigMaker:
    FILE_NAME = "./xlsx/Alive.xlsx"

    def make_regions_configs(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        regions = {}
        region_codes = {}

        df = pd.read_excel(self.FILE_NAME, sheet_name="Region-->OS_Region")

        for _, row in df.iterrows():
            regions[row["Region"].strip()] = row["из проекта ОС"].strip()

            if pd.isna(row["Region_Code"]):
                continue
            region_codes[row["из проекта ОС"]] = int(row["Region_Code"])

        return regions, region_codes

    def make_federal_districts_config(self) -> Dict[str, str]:
        federal_districts = {}
        df = pd.read_excel(self.FILE_NAME, sheet_name="Obl_OS-->FO_Name")

        for _, row in df.iterrows():
            federal_districts[row["Obl_Os"]] = row["FO_Name"]

        return federal_districts

    def make_federal_districts_codes_config(self) -> Dict[str, str]:
        federal_districts_codes = {}
        df = pd.read_excel(self.FILE_NAME, sheet_name="FO_Name-->FO_Code")

        for _, row in df.iterrows():
            federal_districts_codes[row["FO_Name"]] = row["FO_Code"]

        return federal_districts_codes

    def make_filials_config(self) -> Dict[str, str]:
        filials = {}

        df = pd.read_excel(self.FILE_NAME, sheet_name="OS_Obl-->filial")

        for _, row in df.iterrows():
            filials[row["Obl_OS"]] = row["mgFil_Code"]

        return filials

    def make_operators_config(self) -> Dict[str, str]:
        operators = {}

        df = pd.read_excel(self.FILE_NAME, sheet_name="Oper-->OS_Oper_Code")

        for _, row in df.iterrows():
            operators[row["OPERATOR"]] = row["Code"]

        return operators

    def make_intervals_config(self) -> Dict[str, Dict[str, str]]:
        intervals = {}

        df = pd.read_excel(self.FILE_NAME, sheet_name="OS_Region-->Interval")

        for _, row in df.iterrows():
            intervals[row["Obl_OS"]] = {
                "begin": self.convert_time_to_string(row["CallIntervalBegin"]),
                "end": self.convert_time_to_string(row["CallIntervalEnd"]),
            }

        return intervals

    def make_ignore_config(self) -> List[str]:
        ignore = []

        df = pd.read_excel(self.FILE_NAME, sheet_name="Region-->OS_Region")

        for _, row in df.iterrows():
            if row["Region_Code"] == 0:
                ignore.append(row["из проекта ОС"])

        return ignore

    def convert_time_to_string(self, time: time) -> str:
        if pd.isna(time):
            return ""

        return time.strftime("%H:%M:%S")

    def make_config_file(self) -> None:
        config = {}

        config["regions"], config["region_codes"] = self.make_regions_configs()
        config["federal_districts"] = self.make_federal_districts_config()
        config["federal_districts_codes"] = self.make_federal_districts_codes_config()
        config["filials"] = self.make_filials_config()
        config["operators"] = self.make_operators_config()
        config["intervals"] = self.make_intervals_config()
        config["ignores"] = self.make_ignore_config()

        with open("project_config_os.json", "w") as output_file:
            output_file.write(json.dumps(config, ensure_ascii=False, indent=4))

    def run(self) -> None:
        self.make_config_file()


if __name__ == "__main__":
    cm = ConfigMaker()
    cm.run()
