from air_mgmt import get_hygrometer_reading, get_outdoor_weather
from api import add_air_log, get_day_equip, upload_daily_equipment


def log_climate_records():
    inside_temp, inside_humid = get_hygrometer_reading()
    outdoor_temp, outdoor_brightness = get_outdoor_weather()

    log = {
        'inside_temp': inside_temp,
        'inside_humid': inside_humid,
        'outside_temp': outdoor_temp
    }

    print(log)
    add_air_log(log)

def calculate_daily_equip_usage():
    logs, equip_list = get_day_equip()
    equip_usage = {}
    for equip in equip_list:
        equip_usage[equip] = {
            'equip_id': equip,
            'runtime': 0
        }
    for log in logs:
        equip_usage[log.equipment_id]['runtime'] += log.duration

    upload_daily_equipment(equip_list, equip_usage)

    