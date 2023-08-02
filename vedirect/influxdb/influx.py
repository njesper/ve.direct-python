from builtins import float, ValueError, int
from datetime import datetime, timezone
from copy import deepcopy



"""
Converts a line read from the wire into an array of influx DB points that can be serialised
"""
def measurements_for_packet(data):
    timestamp = datetime.now(timezone.utc).astimezone().isoformat()

    vedirect_state_keys = [
        'LOAD',  # Load output State (ON/OFF)
        # 'OR',  # Off reason (Vedirect.VICTRON_OFF_REASON)
        'CS',  # State of operation (Vedirect.VICTRON_CS)
        'MPPT',  # Tracker operation mode (Vedirect.VICTRON_MTTP)
        'ERR'  # Error Code (Vedirect.VICTRON_ERROR)
    ]

    vedirect_today_keys = [
        'H20',  # Yield today (0.01 Kwh)
        'H21'  # Maximum power today (W)
    ]

    measurement_keys = [
        'V',  # Battery voltage (mV)
        'VPV',  # Panel voltage (mV)
        'PPV',  # Panel Power (W)
        'IL',  # Load Current (mA)
        'I'  # Battery current (mA)
    ]

    battery_status_keys = [
        'V',  # Battery voltage (mV)
        'VS', # Auxiliary (starter) voltage (mV)
        'I',  # Battery current (mA)
        'P',  # Instantaneous power (W)
        'CE', # Consumed Amp Hours (mAh)
        'SOC',# State-of-charge (%o)
        'TTG',# Time-to-go (min)
        'Alarm',# Alarm condition active
        'Relay',# Relay state
        'AR', # Alarm reason
        'H1', # Depth of the deepest discharge
        'H2', # Depth of the last discharge
        'H3', # Depth of the average discharge
        'H4', # Number of charge cycles
        'H5', # Number of full discharges
        'H6', # Cumulative Amp Hours drawn
        'H7', # Minimum main (battery) voltage (mV)
        'H8', # Maximum main (battery) voltage (mV)
        'H9', # Number of seconds since last full charge
        'H10',# Number of automatic synchronizations 
        'H11',# Number of low main voltage alarms
        'H12',# Number of high main voltage alarms
        'H15',# Minimum auxiliary (battery) voltage (mV)
        'H16',# Maximum auxiliary (battery) voltage (mV)
        'H17',# Amount of discharged energy (0.01 kWh)
        'H18' # Amount of charged energy (0.01 kWh) 
    ]

    measure_base = {
        "measurement": "solar",
        "tags": {
            "sensor": "victron",
            "location": "outdoors"
        },
        "time": timestamp,
        "fields": {}
    }

    measurements = []

    battery_measurement = deepcopy(measure_base)
    battery_measurement['measurement'] = 'battery'
    battery_measurement['fields'] = {key: process_keys(key, data[key]) for key in battery_status_keys}
    measurements.append(battery_measurement)

#    power_measurement = deepcopy(measure_base)
#    power_measurement['measurement'] = 'power'
#    power_measurement['fields'] = {key: process_keys(key, data[key]) for key in measurement_keys}
#    measurements.append(power_measurement)

#    today_measurement = deepcopy(measure_base)
#    today_measurement['measurement'] = 'today'
#    today_measurement['fields'] = {key: process_keys(key, data[key]) for key in vedirect_today_keys}
#    measurements.append(today_measurement)

#    status_measurement = deepcopy(measure_base)
#    status_measurement['measurement'] = 'status'
#    status_measurement['fields'] = {key: process_keys(key, data[key]) for key in vedirect_state_keys}
#    measurements.append(status_measurement)

    return measurements

def process_keys(key, value):
    if key == 'V' or key == 'VS' or key == 'VPV' or key == 'H8' or key == 'H7' or key == 'H15' or key == 'H16':  # mV -> V
        return float(value) / 1000
    elif key == 'IL' or key == 'I':
         return int(value)  # mA
    elif key == 'PPV' or key == 'H21' or key == 'P':  # W
        return int(value)
    elif key == 'H20' or key == 'H18' or key == 'H17':  # 0.01Kw -> Kw
        return float(value) / 100
    elif key == 'CS' or key == 'CE' or key == 'SOC' or key == 'TTG' or key == 'H1' or key == 'H2' or key == 'H3' or key == 'H4' or key == 'H5' or key == 'H6' or key == 'H9' or key == 'H10' or key == 'H11' or key == 'H12':
        return int(value)  # vedirect.Vedirect.VICTRON_CS[value]
    elif key == 'MPPT':
        return int(value)  # vedirect.Vedirect.VICTRON_MTTP[value]
    elif key == 'ERR' or key == 'AR':
        return int(value)  # vedirect.Vedirect.VICTRON_ERROR[value]
    elif key == 'LOAD' or key == 'Alarm' or key == 'Relay':
        return 1 if value == 'ON' else 0  # ON / OFF
    else:
        raise ValueError('Unable to parse key')

