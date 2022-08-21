import os
import sys
import socket
import json
import time
from tkinter import W
import click
import uuid
from zmq import STREAM
import json

serverip = '10.0.0.11' #ip must be str
serverport = 5001 #port can't be str
serveripandport =  (serverip,serverport)
hostid = uuid.uuid4()
hostid_str = str(hostid)

localip = socket.gethostbyname(socket.gethostname())
localport = 5002
localipandport =  [localip, localport]
print(localipandport)

client_json = {"localip":localip,"uuid":hostid_str}
client_json_data = json.dumps(client_json)


# def connect_to_server(myipandport,remoteipandport):
#     conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#     conn.bind(myipandport)
#     conn.connect(remoteipandport)
#     conn.send(f"This is{localip}, uuid is{hostid}".encode())
#     conn.send(bytes(client_json_data,encoding="utf-8"))

def connect_to_server(myipandport,remoteipandport,jsondata):
    conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    conn.bind(myipandport)
    conn.connect(remoteipandport)
    conn.send(f"This is{localip}, uuid is{hostid}".encode())
    conn.send(bytes(jsondata,encoding="utf-8"))
    conn.close()


connect_to_server(localipandport,serveripandport,client_json_data)

#log内容可能是空，记得要加上如何处理空none的步骤
def node_or_log_broadcast_info_json(para_local_ip, para_local_uuid, para_local_logstr, para_timestamp):
    para_json = {"type":"1","nodeip":para_local_ip,"nodeuuid":para_local_uuid, "nodelog":para_local_logstr,"nodetimestamp":para_timestamp}
    para_json_data = json.dumps(para_json)
    return para_json_data

def self_hash_info_json(para_local_ip, para_local_uuid, para_local_logstr, para_timestamp, para_nonce, para_hash_value):
    para_json = {"type":"2","nodeip":para_local_ip,"nodeuuid":para_local_uuid, "nodelog":para_local_logstr,"nodetimestamp":para_timestamp,\
        "nodeonce":para_nonce,"nodehash":para_nonce}
    para_json_data = json.dumps(para_json)
    return para_json_data

import sqlite

#check if nodeinfodb exsit (sqlite)
sqlite_nodeinfo_exists = os.path.exists('nodeinfo.db')
if sqlite_nodeinfo_exists == True:
    pass
else:
    with open('nodeinfo.db','w') as nodedb:
        pass