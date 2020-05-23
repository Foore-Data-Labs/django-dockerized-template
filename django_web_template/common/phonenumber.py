
import phonenumbers as py_phonenumbers

# https://github.com/daviddrysdale/python-phonenumbers

CONST_COUNTY_CODE_INDIA = 91


def is_valid_indian_number(mob_num):
    is_valid_number, parsed_e164, country_code, indian_national_number = validate_and_return_param(
        mob_num)
    return (is_valid_number and (country_code == CONST_COUNTY_CODE_INDIA)), parsed_e164, indian_national_number


def get_region_code_for_country_code(country_code):
    region_code = None
    if country_code:
        try:
            region_code = py_phonenumbers.COUNTRY_CODE_TO_REGION_CODE[country_code][0]
        except KeyError:
            pass
    return region_code


# Used most of the time
# if validation fails, then its  a failure
# if passes, save the parsed_e164


def validate_and_return_param(input_phonenumber):
    return validate_and_return_param_for_country(input_phonenumber, None)

# Ideally not required to be used directly


def validate_and_return_param_for_country(input_phonenumber, region_code):
    is_valid_number = parsed_e164 = country_code = national_number = None
    try:
        phonenumber_instance = py_phonenumbers.parse(
            input_phonenumber, region_code)
        is_valid_number = py_phonenumbers.is_valid_number(phonenumber_instance)
        if is_valid_number:
            parsed_e164 = py_phonenumbers.format_number(
                phonenumber_instance, py_phonenumbers.PhoneNumberFormat.E164)
            country_code = phonenumber_instance.country_code
            national_number = phonenumber_instance.national_number
    except py_phonenumbers.phonenumberutil.NumberParseException:
        is_valid_number = False
    return is_valid_number, parsed_e164, country_code, national_number
