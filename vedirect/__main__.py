"""
CLI Entry point
"""
import argparse
import datetime

from vedirect.influxdb import influx
from vedirect.vedirect import Vedirect
from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt
import json

influx_client = None
influx_db = None
lastsend = datetime.datetime.min
args = None
mqtt_client = None

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
    parser.add_argument('-n', '--print-only', help='dont send anything to influxdb or mqtt, just print', action='store_true')
    parser.add_argument('--broker', help='Broker IP address')
    parser.add_argument('--client-id', help='Unique mqtt client id')
    parser.add_argument('--username', help='Username for mqtt broker')
    parser.add_argument('--password', help='Password for mqtt broker')
    args = parser.parse_args()

    if not args.print_only:
        if args.influx:
            print("Influx init...")
            global influx_db, influx_client
            influx_client = InfluxDBClient(host=args.influx, port=8086, timeout=5)
            influx_db = args.database
        if args.broker:
            global mqtt_client
            print("MQTT init...")
            mqtt_client = mqtt.Client(args.client_id)
            if args.username is not None and args.password is not None:
                mqtt_client.username_pw_set(args.username, args.password)
            mqtt_client.connect(args.broker)
            mqtt_client.loop_start()


    ve = Vedirect(args.port)
    ve.read_data_callback(on_victron_data_callback)

def mean(nums):
    return sum(nums, 0.0) / len(nums)

def on_victron_data_callback(data):
    global lastsend, args, influx_client, mqtt_client
    diff = datetime.datetime.now()-lastsend
    if diff.seconds > (2 * args.send_interval):
        print ("Gap of:",diff)
    if diff.seconds > args.send_interval:
        measurements = influx.measurements_for_packet(data)
        if not args.print_only:
            if influx_client:
                influx_client.write_points(measurements, database=influx_db)
            if mqtt_client:
                for m in measurements:
                    mqtt_client.publish('bob/victron/mppt/'+m['measurement'],json.dumps(m['fields']),1)
        if args.print_only:
            print(measurements)
            for m in measurements:
                print("MQTT:",'bob/victron/mppt/'+m['measurement'],json.dumps(m['fields']))
        lastsend=datetime.datetime.now()
    else:
        #print ("Skipped measurement")
        pass


if __name__ == "__main__":
    main()
