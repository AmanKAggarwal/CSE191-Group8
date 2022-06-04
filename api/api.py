# example of DB access and HTTP request 
import os

import pymysql
import pandas as pd
from waitress import serve
import numpy as np
import sys
from pyramid.config import Configurator
from pyramid.response import Response
import json
from datetime import datetime

#
# Constants
#
DAY_VIEW_DATA_CSV_PATH = '/home/group08/api/csvs/day_view_data.csv'

def get_data(query):
    conn = pymysql.connect(
        db='cse191',
        user='root',
        passwd='iotiot',
        host='localhost')

    results = "none"
    try:
        # read all the gateways that have data
        results = pd.read_sql(query, con=conn)
        # print(results)
    except:
        print("Unexpected exception occurred: ", sys.exc_info())

    conn.close()

    return results

def put_data(query):
    conn = pymysql.connect(
        db='cse191',
        user='root',
        passwd='iotiot',
        host='localhost')

    cursor=conn.cursor()
    result = "Insertion failed"
    try:
        # read all the gateways that have data
        cursor.execute(query)
        conn.commit()
        # print(query)
        result = "Insertion success"
    except:
        print("Unexpected exception occurred: ", sys.exc_info())

    conn.close()

    return result

def home(request):
    print("API health call")
    print(datetime.now()) 
    resp = {}
    resp["status"] = "OK"
    resp["ts"] = str(datetime.now())
    resp = Response(json.dumps(resp))
    resp.content_type = 'application/json'
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
        'Access-Control-Allow-Headers': '*,Origin, Content-Type, Accept, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '1728000',
        })
    return resp


def list_devices(request):
    print("list devices")
    print(datetime.now()) 

    if request.params.has_key('gn'):
        gn = request.params['gn']
        print("groupname:",gn)
        query = f"SELECT * FROM devices as S WHERE S.group={gn};"

    else:
        query = "SELECT * FROM devices;"

    dev = get_data(query)
    result = dev.to_json(orient="records")
    resp = Response('{ "devices":'+result+'}')
    resp.content_type = 'application/json'
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
        'Access-Control-Allow-Headers': '*,Origin, Content-Type, Accept, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '1728000',
        })
    return resp


def list_students(request):
    print("list students")
    print(datetime.now()) 

    if request.params.has_key('gn'):
        gn = request.params['gn']
        print("groupname:",gn)
        query = f"SELECT * FROM students as S WHERE S.group={gn};"
    else:
        query = "SELECT * FROM students;"

    dev = get_data(query)
    result = dev.to_json(orient="records")
    resp = Response('{ "students":'+result+'}')
    resp.content_type = 'application/json'
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
        'Access-Control-Allow-Headers': '*,Origin, Content-Type, Accept, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '1728000',
        })
    return resp

def log_devices(request):
    print("Inserting device", request.params)
    print(datetime.now()) 

    if request.params.has_key('gn') and request.params.has_key('mac') and request.params.has_key('rssi'):
        gn = request.params['gn']
        mac = request.params['mac']
        rssi = request.params['rssi']
        
        long, lang, color = None, None, None
        if request.params.has_key('long'):
            long = request.params['long']

        if request.params.has_key('lang'):
            lang = request.params['lang']

        if request.params.has_key('color'):
            color = request.params['color']

        # print("groupname:",gn)
        # print("mac:",mac)
        # print("rssi:",rssi)
        # print("long:", long)
        # print("lang:", lang)
        
        locationStr = ''
        if long and lang:
            locationStr = f", `long` = {long}, `lang` = {lang}"

        colorStr = ''
        if color:
            colorStr = f", color = '{color}'"
            
        query = f"""
UPDATE devices 
SET lastseen_ts = '{datetime.now()}', last_rssi = '{rssi}'{locationStr}{colorStr}
WHERE groupname = '{gn}' AND mac = '{mac}';
        """
        # print(query)
    else:
        query = "SELECT * FROM devices;"

    dev = put_data(query)
    # print(dev)
    # result = dev.to_json(orient="records")
    resp = Response('{ "devices":'+dev+'}')
    resp.content_type = 'application/json'
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
        'Access-Control-Allow-Headers': '*,Origin, Content-Type, Accept, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '1728000',
        })
    return resp

def log_beacon(request):
        print("logging beacons")
        print(datetime.now())
    
        input = json.loads(request.body.decode("utf-8"))

        gn = input["groupname"] 
        dev_mac = input["dev_mac"]

        for beacon in input["beacons"]:
            ble_mac = beacon['mac']
            ble_rssi = beacon['rssi']
            query = f"INSERT INTO ble_logs (device_mac, ble_rssi, ble_mac, groupname, log_ts) VALUES ('{dev_mac}', '{ble_rssi}', '{ble_mac}', '{gn}', '{datetime.now()}')"
            valid = put_data(query)
        
        resp = Response("{ result: " + valid + " }")
        resp.content_type = 'application/json'
        resp.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
            'Access-Control-Allow-Headers': '*,Origin, Content-Type, Accept, Authorization',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Max-Age': '1728000',
            })
        return resp


def fetch_day_view_data():
    print("Fetching day view data")
    query = """
select dev.mac, dev.location, ble_logs.ble_mac, ble_logs.log_ts as total from (
	select * from cse191.ble_logs
    where ble_rssi > -70
) as ble_logs
inner join (
	select * from cse191.devices
    where mac in ('3C:71:BF:6C:5E:DC', '80:7D:3A:BB:06:40', 'C4:4F:33:0E:42:65', 'CC:50:E3:B0:21:94')
) as dev
on dev.mac = ble_logs.device_mac and dev.location is not null;
"""
    result = get_data(query)
    times = pd.to_datetime(result.total)
    grouped_data = result.groupby(['location', times.dt.hour])['ble_mac'].nunique()

    grouped_data.to_csv(DAY_VIEW_DATA_CSV_PATH, sep=',', encoding='utf-8')

def dayViewData(request):
    try:
        if not os.path.exists(DAY_VIEW_DATA_CSV_PATH):
            fetch_day_view_data()
        df = pd.read_csv(DAY_VIEW_DATA_CSV_PATH, sep=',', encoding='utf-8')

        response = Response(df.to_json())
        response.content_type = 'application/json'
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
            'Access-Control-Allow-Headers': '*,Origin, Content-Type, Accept, Authorization',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Max-Age': '1728000',
            })
        return response
    except:
        print("Unexpected exception occurred: ", sys.exc_info())
    return None

def getCountOfDates(request):
    result = "none"
    try:
        results = pd.read_csv('/home/group08/api/csvs/file.csv')
        print(results)
        result = results.to_json()
        resp = Response(result)
        resp.content_type = 'application/json'
        resp.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
            'Access-Control-Allow-Headers': '*,Origin, Content-Type, Accept, Authorization',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Max-Age': '1728000',
            })
        return resp
    except:
        print("Unexpected exception occurred: ", sys.exc_info())
    return None

if __name__ == '__main__':
    with Configurator() as config:
        config.include('pyramid_jinja2')
        config.add_jinja2_renderer('.html')

        config.add_route('health', '/health')
        config.add_view(home, route_name='health', renderer='json')

        config.add_route('listStudents', '/liststudents')
        config.add_view(list_students, route_name='listStudents', renderer='json')

        config.add_route('listDevices', '/listdevices')
        config.add_view(list_devices, route_name='listDevices', renderer='json')

        config.add_route('logdevices', '/logdevices')
        config.add_view(log_devices, route_name='logdevices', renderer='json')

        config.add_route('logBeacons', '/logBeacons')
        config.add_view(log_beacon, route_name='logBeacons', renderer='json')
        
        config.add_route('getCountOfDates', '/getCountOfDates')
        config.add_view(getCountOfDates, route_name='getCountOfDates', renderer='json')
        
        config.add_route('dayViewData', 'dayViewData')
        config.add_view(dayViewData, route_name='dayViewData', renderer='json')

        app = config.make_wsgi_app()

    print(datetime.now(), "Starting server...Group 08")
    print('Web server started on: http://0.0.0.0:8008 OR http://localhost:8008')
    #server = make_server('0.0.0.0', 8008, app)
    #server.serve_forever()
    serve(app, host='0.0.0.0', port='8008', threads=32)

