"""
CLI Entry point
"""
import argparse
import datetime

from vedirect.influxdb import influx
from vedirect.vedirect import Vedirect
from influxdb import InfluxDBClient

influx_client = None
influx_db = None
lastsend = datetime.datetime.min
args = None

def main():
    """
    Invoke the parser
    :return:
    """
    print("Startup...")
    global args
    parser = argparse.ArgumentParser(description='Parse VE.Direct serial data')
    parser.add_argument('-i', '--influx', help='Influx DB host')
    parser.add_argument('-d', '--database', help='InfluxDB database')
    parser.add_argument('-p', '--port', help='Serial port')
    parser.add_argument('-s', '--send-interval', help='send interval seconds',default=5, type=int)
    parser.add_argument('-n', '--print-only', help='dont send anything to influxdb, just print', action='store_true')
    args = parser.parse_args()

    if not args.print_only:
        global influx_db, influx_client
        influx_client = InfluxDBClient(host=args.influx, port=8086)
        influx_db = args.database

    ve = Vedirect(args.port)
    ve.read_data_callback(on_victron_data_callback)

def mean(nums):
    return sum(nums, 0.0) / len(nums)

def on_victron_data_callback(data):
    global lastsend, args
    diff = datetime.datetime.now()-lastsend
    if diff.seconds > (2 * args.send_interval):
        print ("Gap of:",diff)
    if diff.seconds > args.send_interval:
        measurements = influx.measurements_for_packet(data)
        if not args.print_only:
            influx_client.write_points(measurements, database=influx_db)
        #print(measurements)
        lastsend=datetime.datetime.now()
    else:
        #print ("Skipped measurement")
        pass


if __name__ == "__main__":
    main()
