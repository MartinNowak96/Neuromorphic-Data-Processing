import re


def parse_frequency(input_str: str, append_if_found: str = "") -> str:
    frequency = re.search("[0-9]{1,} ?hz", input_str, re.IGNORECASE)

    if frequency:
        frequency = re.search("[0-9]{1,}", frequency.group()).group()
        return frequency + append_if_found
    else:
        return ""


def parse_voltage(input_str: str, append_if_found: str = "") -> str:
    voltage = re.search("[0-9]{1,} ?m?v", input_str, re.IGNORECASE)

    if voltage:
        voltage = voltage.group().lower()

        multiplier = 0.001 if 'mv' in voltage else 1

        voltage = str(
            int(re.search("[0-9]{1,}", voltage).group()) * multiplier
            )

        return voltage + append_if_found
    else:
        return ""


def parse_waveform(input_str: str, append_if_found: str = "") -> str:
    waveform = re.search("(burst|sine|square|triangle|noise)", input_str, re.IGNORECASE)
    return waveform.group() + append_if_found if waveform else ""


def parse_degrees(input_str: str, append_if_found: str = "") -> str:
    degrees = re.search("[0-9]{1,} ?deg", input_str, re.IGNORECASE)

    if degrees:
        degrees = re.search("[0-9]{1,}", degrees.group()).group()
        return degrees + append_if_found
    else:
        return ""


def parse_slots(input_str: str, append_if_found: str = "") -> str:
    slots = re.search("[0-9]{1,}sl", input_str, re.IGNORECASE)

    if slots:
        slots = re.search("[0-9]{1,}", slots.group()).group()
        return slots + append_if_found
    else:
        return ""


def parse_threshold(input_str: str, append_if_found: str = "") -> str:
    threshold = re.search("m?[0-9]{1,}t(hreshold)?", input_str, re.IGNORECASE)

    if threshold:
        threshold = re.search("m?[0-9]{1,}", threshold.group()).group()
        threshold = threshold.replace("m", "-")
        return threshold + append_if_found
    else:
        return ""
