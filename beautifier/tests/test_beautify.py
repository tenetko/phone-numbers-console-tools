import sys
from unittest.mock import patch

import pandas as pd

from beautifier.beautify import PhoneNumbersBeautifier


def make_test_row():
    row = {
        "num": 79001979228,
        "IdRegion": 83,
        "IdOper": 28,
        "REGION": "Свердловская обл.",
        "OPERATOR": 'ООО "ЕКАТЕРИНБУРГ-2000"',
    }

    return pd.Series(data=row)


def make_test_row_volchiy_kray():
    row = {
        "num": 79001979228,
        "IdRegion": 1000,
        "IdOper": 2000,
        "REGION": "Волчий край",
        "OPERATOR": 'ООО "Рога и Копыта"',
    }

    return pd.Series(data=row)


def make_test_row_for_chukotka():
    row = {
        "num": 79001979228,
        "IdRegion": 104,
        "IdOper": 78,
        "REGION": "Чукотский АО",
        "OPERATOR": 'ПАО "Вымпел-Коммуникации"',
    }

    return pd.Series(data=row)


def make_test_row_for_motiv():
    row = {
        "num": 79011234567,
        "IdRegion": 83,
        "IdOper": 28,
        "REGION": "Курганская обл.",
        "OPERATOR": 'ООО "ЕКАТЕРИНБУРГ-2000"',
    }

    return pd.Series(data=row)


def make_test_row_for_yota_moscow():
    row = {
        "num": 79029876543,
        "IdRegion": 83,
        "IdOper": 28,
        "REGION": "г. Москва * Московская область",
        "OPERATOR": 'ООО "Скартел"',
    }

    return pd.Series(data=row)


def make_test_row_for_yota_krasnodarskiy_kray():
    row = {
        "num": 79029876543,
        "IdRegion": 83,
        "IdOper": 28,
        "REGION": "Краснодарский край",
        "OPERATOR": 'ООО "Скартел"',
    }

    return pd.Series(data=row)


def make_test_row_for_sim_telecom():
    row = {
        "num": 79029876543,
        "IdRegion": 83,
        "IdOper": 28,
        "REGION": "Краснодарский край",
        "OPERATOR": 'ООО "СИМ ТЕЛЕКОМ"',
    }

    return pd.Series(data=row)


row = make_test_row()
sys.argv = ["test_beautify.py", "test.xlsx", "os"]
beautifier = PhoneNumbersBeautifier()
parsed_row = beautifier.parse_row(row)
region = beautifier.get_refined_region(parsed_row)

sys.argv = ["test_beautify.py", "test.xlsx", "tzb"]
beautifier_tzb = PhoneNumbersBeautifier()
parsed_row = beautifier_tzb.parse_row(row)
region = beautifier_tzb.get_refined_region(parsed_row)


def test_parse_row():
    result = beautifier.parse_row(row)
    expected_result = {
        "phone_number": "79001979228",
        "region": "Свердловская обл.",
        "operator": 'ООО "ЕКАТЕРИНБУРГ-2000"',
    }

    assert result == expected_result


def test_check_if_region_is_allowed():
    parsed_row = beautifier_tzb.parse_row(row)
    result = beautifier_tzb.check_if_region_is_allowed(parsed_row)
    expected_result = True

    assert result == expected_result


def test_check_if_region_is_allowed_for_volchiy_kray():
    row = make_test_row_volchiy_kray()
    parsed_row = beautifier_tzb.parse_row(row)
    result = beautifier_tzb.check_if_region_is_allowed(parsed_row)
    expected_result = False

    assert result == expected_result


def test_check_if_region_is_disallowed():
    row_with_chukotka = make_test_row_for_chukotka()
    parsed_row = beautifier_tzb.parse_row(row_with_chukotka)
    result = beautifier_tzb.check_if_region_is_allowed(parsed_row)
    expected_result = False

    assert result == expected_result


def test_validate_phone_number():
    num1 = "89001234567"
    num2 = "9008889911"

    result_1 = beautifier.try_to_validate_phone_number(num1)
    result_2 = beautifier.try_to_validate_phone_number(num2)

    expected_result_1 = "79001234567"
    expected_result_2 = "79008889911"

    assert result_1 == expected_result_1
    assert result_2 == expected_result_2


def test_check_if_phone_number_is_valid():
    num1 = "79001231231"
    num2 = "7900123123"
    num3 = "89001231231"
    num4 = "8900123123"
    num5 = "74950000000"
    num6 = "88622231231"
    num7 = "69001231231"
    num8 = "кукушкапока"
    num9 = "+79001231231"

    result_1 = beautifier.check_if_phone_number_is_valid(num1)
    result_2 = beautifier.check_if_phone_number_is_valid(num2)
    result_3 = beautifier.check_if_phone_number_is_valid(num3)
    result_4 = beautifier.check_if_phone_number_is_valid(num4)
    result_5 = beautifier.check_if_phone_number_is_valid(num5)
    result_6 = beautifier.check_if_phone_number_is_valid(num6)
    result_7 = beautifier.check_if_phone_number_is_valid(num7)
    result_8 = beautifier.check_if_phone_number_is_valid(num8)
    result_9 = beautifier.check_if_phone_number_is_valid(num9)

    assert result_1 == True
    assert result_2 == False
    assert result_3 == True
    assert result_4 == False
    assert result_5 == False
    assert result_6 == False
    assert result_7 == False
    assert result_8 == False
    assert result_9 == False


def test_get_external_id():
    result = beautifier.get_external_id("+79991234567")
    expected_result = "9991234567"

    assert result == expected_result


def test_get_refined_region():
    result = beautifier.get_refined_region(parsed_row)
    expected_result = "Свердловская область"

    assert result == expected_result


def test_get_region_code():
    result = beautifier.get_region_code(region)
    expected_result = 66

    assert result == expected_result


def test_get_federal_district():
    result = beautifier.get_federal_district(region)
    expected_result = "Уральский"

    assert result == expected_result


def test_get_federal_district_code():
    federal_district = beautifier.get_federal_district(region)
    result = beautifier.get_federal_district_code(federal_district)
    expected_result = 6

    assert result == expected_result


def test_get_filial_code():
    result = beautifier.get_filial_code(region)
    expected_result = 7

    assert result == expected_result


def test_get_operator():
    result = beautifier.get_operator(parsed_row)
    expected_result = 7

    assert result == expected_result


def test_make_tailored_row_for_OS():
    result = beautifier.make_tailored_row_for_OS(parsed_row)
    expected_result = {
        "Number": "79001979228",
        "ВнешнийID": "9001979228",
        "DisplayField1": "Уральский",
        "DisplayField2": "Свердловская область",
        "DisplayField3": 6,
        "filial": 7,
        "obl": 66,
        "CallIntervalBegin": "07:00:00",
        "CallIntervalEnd": "20:00:00",
        "oper": 7,
        "Mark": 66,
    }

    assert result == expected_result


def test_check_if_region_is_ignored_for_OS_for_usual_case():
    tailored_row = beautifier.make_tailored_row_for_OS(parsed_row)
    result = beautifier.check_if_region_is_ignored_for_OS(tailored_row)

    assert result == False


def test_check_if_region_is_ignored_for_OS_for_chukotka():
    row = make_test_row_for_chukotka()
    parsed_row = beautifier.parse_row(row)
    tailored_row = beautifier.make_tailored_row_for_OS(parsed_row)
    result = beautifier.check_if_region_is_ignored_for_OS(tailored_row)

    assert result == True


def test_get_operator_code():
    operator = beautifier_tzb.get_operator(parsed_row)
    result = beautifier_tzb.get_operator_code(operator)
    expected_result = 7

    assert result == expected_result


def test_get_time_difference():
    result = beautifier_tzb.get_time_difference(region)
    expected_result = "UTC +5"

    assert result == expected_result


def test_get_tzb_group():
    operator = beautifier_tzb.get_operator(parsed_row)
    result = beautifier_tzb.get_tzb_group(region, operator)
    expected_result = "Свердловская область_Мотив"

    assert result == expected_result


def test_get_tzb_mark():
    operator = beautifier_tzb.get_operator(parsed_row)
    operator_code = beautifier_tzb.get_operator_code(operator)
    region_code = beautifier_tzb.get_region_code(region)
    result = beautifier_tzb.get_tzb_mark(region_code, operator_code)
    expected_result = "12_7"

    assert result == expected_result


def test_make_tailored_row_for_TZB():
    result = beautifier_tzb.make_tailored_row_for_TZB(parsed_row)
    expected_result = {
        "Number": 79001979228,
        "RegionName": "Свердловская область",
        "OperatorName": "Мотив",
        "TimeDifference": "UTC +5",
        "Region": 12,
        "Operator": 7,
        "CallIntervalBegin": "08:00:00",
        "CallIntervalEnd": "20:00:00",
        "Group": "Свердловская область_Мотив",
        "CHECK": 9001979228,
        "Mark": "12_7",
    }


def test_check_if_operator_is_forbidden_for_TZB_for_motiv_kurganskaya_oblast():
    row = make_test_row_for_motiv()
    parsed_row = beautifier_tzb.parse_row(row)
    tailored_row = beautifier_tzb.make_tailored_row_for_TZB(parsed_row)
    result = beautifier_tzb.check_if_operator_is_forbidden_for_TZB(tailored_row)
    expected_result = True

    assert result == expected_result


def test_check_if_operator_is_forbidden_for_TZB_for_any_other_combination():
    row = make_test_row()
    parsed_row = beautifier_tzb.parse_row(row)
    tailored_row = beautifier_tzb.make_tailored_row_for_TZB(parsed_row)
    result = beautifier_tzb.check_if_operator_is_forbidden_for_TZB(tailored_row)
    expected_result = False

    assert result == expected_result


def test_check_if_operator_is_allowed_for_TZB_for_yota_moscow():
    row = make_test_row_for_yota_moscow()
    parsed_row = beautifier_tzb.parse_row(row)
    tailored_row = beautifier_tzb.make_tailored_row_for_TZB(parsed_row)
    result = beautifier_tzb.check_if_operator_is_allowed_for_TZB(tailored_row)
    expected_result = True

    assert result == expected_result


def test_check_if_operator_is_allowed_for_TZB_for_yota_krasnodarskiy_kray():
    row = make_test_row_for_yota_krasnodarskiy_kray()
    parsed_row = beautifier_tzb.parse_row(row)
    tailored_row = beautifier_tzb.make_tailored_row_for_TZB(parsed_row)
    result = beautifier_tzb.check_if_operator_is_allowed_for_TZB(tailored_row)
    expected_result = False

    assert result == expected_result


def test_check_if_operator_is_other_for_TZB_for_yota_moscow():
    row = make_test_row_for_yota_moscow()
    parsed_row = beautifier_tzb.parse_row(row)
    tailored_row = beautifier_tzb.make_tailored_row_for_TZB(parsed_row)
    result = beautifier_tzb.check_if_operator_is_other_for_TZB(tailored_row)
    expected_result = False

    assert result == expected_result


def test_check_if_operator_is_other_for_TZB_for_sim_telecom():
    row = make_test_row_for_sim_telecom()
    parsed_row = beautifier_tzb.parse_row(row)
    tailored_row = beautifier_tzb.make_tailored_row_for_TZB(parsed_row)
    result = beautifier_tzb.check_if_operator_is_other_for_TZB(tailored_row)
    expected_result = True

    assert result == expected_result
