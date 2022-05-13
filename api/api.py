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
        print(results)
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
        print(query)
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

    if request.params.has_key('gn') and request.params.has_key('mac') and  request.params.has_key('rssi'):
        gn = request.params['gn']
        mac = request.params['mac']
        rssi = request.params['rssi']
        
        print("groupname:",gn)
        print("mac:",mac)
        print("rssi:",rssi)

        query = f"""
UPDATE devices 
SET lastseen_ts = '{datetime.now()}', last_rssi = '{rssi}'
WHERE groupname = '{gn}' AND mac = '{mac}';
        """
        # print(query)
    else:
        query = "SELECT * FROM devices;"

    dev = put_data(query)
    print(dev)
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

        config.add_route('logBeacon', '/logbeacons')
        config.add_view(log_beacon, route_name='logBeacon', renderer='json')
        
        app = config.make_wsgi_app()

    print(datetime.now(), "Starting server...Group 08")
    print('Web server started on: http://0.0.0.0:8008 OR http://localhost:8008')
    #server = make_server('0.0.0.0', 8008, app)
    #server.serve_forever()
    serve(app, host='0.0.0.0', port='8008', threads=32)
