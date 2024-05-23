import json
import requests

from time import sleep
from typing import Dict


class OperatorWorkTimeReportGenerator:
    REQUEST_ENDPOINT = "https://api.survey-studio.com/reports/dex/operator-work-time"
    RESULTS_ENDPOINT = (
        "https://api.survey-studio.com/reports/dex/operator-work-time/{request_id}"
    )

    REQUEST_BODY = """{{
        "projectId": null,
        "from": "{from_date}",
        "to": null,
        "isGroupByProject": true,
        "isExportInXlsx": true,
        "showIdInXlsx": true
    }}"""

    HEADERS = {
        "accept": "application/json",
        "Content-Language": "ru",
        "Content-Type": "application/json-patch+json",
    }

    def __init__(self) -> None:
        self.config = self.get_config()
        self.HEADERS["SS-Token"] = self.config["api_token"]

    def get_config(self) -> Dict[str, str]:
        with open("config.json", "r") as input_file:
            return json.load(input_file)

    def make_request(self) -> int:
        result = requests.post(
            self.REQUEST_ENDPOINT,
            data=self.REQUEST_BODY.format(from_date=self.config["from_date"]),
            headers=self.HEADERS,
        )

        return int(result.json()["body"])

    def get_response(self, request_id: int) -> str | None:
        while True:
            result = requests.get(
                self.RESULTS_ENDPOINT.format(request_id=request_id),
                headers=self.HEADERS,
            )
            result = result.json()

            state = result["body"]["state"]
            if result["isSuccess"] and state == 3:
                return result["body"]["fileUrl"]

            if state == 4 or state == 5:
                print(
                    "We received a 4 or 5 state:",
                    "https://api.survey-studio.com/swagger/index.html",
                )
                break

            sleep(5)
            print(f"State: {state}")

    def retrieve_file(self, file_url: str) -> None:
        result = requests.get(file_url)
        file_name = self.get_file_name(file_url)
        with open(file_name, "wb") as output_file:
            output_file.write(result.content)

    def get_file_name(self, file_url: str) -> str:
        return file_url[37:]

    def run(self) -> None:
        request_id = self.make_request()
        print(f"request_id: {request_id}")
        file_url = self.get_response(request_id)
        self.retrieve_file(file_url)


if __name__ == "__main__":
    generator = OperatorWorkTimeReportGenerator()
    generator.run()