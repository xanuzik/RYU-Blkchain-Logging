from asyncio.windows_events import NULL
from ipaddress import ip_address
from operator import mod
import json
import time
from wsgiref.simple_server import WSGIRequestHandler
import mysql
import socket
import conndbmod

#Database operation with arguments
def db_crud_func(connection, query, *args): 
    cur=connection.cursor()
    cur.execute(query,(*args,))
    result = cur.fetchall()
    connection.close() #close the connection after making the amendment
    return result
    
#Database operation without arguments
def db_search_func(connection, query):
    cur = connection.cursor()
    cur.execute(query)
    result = cur.fetchall()
    connection.close()
    return result

query_insert_ip_only = "INSERT INTO NODES.nodeinfo (ip) VALUES (%s)"
query_insert_ip_uuid = "INSERT INTO NODES.nodeinfo (ip,uuid) VALUES (%s,%s)"
query_insert_ip_bin_uuid_timestamp =  "INSERT into NODES.nodeinfo (ip,IPv4BIN,timestamp,uuid) VALUES (%s,INET6_ATON(%s),%s,%s)"
query_insert_ip_bin_uuid_timestamp_date =  "INSERT into NODES.nodeinfo (ip,IPv4BIN,timestamp,uuid,date) \
    VALUES (%s,INET6_ATON(%s),%s,%s,now())" #last two arguments are the same, using the IP twice

query_update_uuid = """UPDATE nodeinfo SET uuid = %s WHERE ip = %s"""
query_update_ip = """UPDATE nodeinfo SET ip = %s WHERE uuid = %s"""

query_list_ip_uuid = "SELECT ip, uuid FROM nodeinfo"
query_list_ip = "SELECT ip FROM nodeinfo"

query_search_ip = "SELECT * FROM nodeinfo WHERE ip = %s"
query_search_uuid = "SELECT * FROM nodeinfo WHERE uuid = %s"

query_delete_entry_based_on_timestamp = "DELETE FROM nodeinfo WHERE timestamp = %s"

query_dedup_ip = "SELECT ip FROM nodeinfo GROUP BY ip HAVING COUNT(*) > 1;"
query_dedup_uuid = "SELECT uuid FROM nodeinfo GROUP BY uuid HAVING COUNT(*) > 1;"

###########################
#Deduplicate Module       #
###########################
# To judge if the new IP/UUID already exits in the DB

def dedup_after_adding_entry(connection, para_query_dedup_ip_or_uuid, para_query_search):
    #para_dedup : is to find the ip/uuid whis appears more than once in the db
    #para_search: is to list the entries according to the designated ip/uuid
    cursor_dedup = connection.cursor() 
    cursor_dedup.execute(para_query_dedup_ip_or_uuid)
    dup_items = cursor_dedup.fetchall()
    if len(dup_items)  == 0:
        print("No duplicated entries")
        connection.close()
    else:
        print("Folling item has multiple entries in DB")
        print(dup_items)
        selected_items = db_crud_func(connection,para_query_search, dup_items[0][0])
        #the connection closed after listing the items using the crud_func
        if selected_items[0][2] > selected_items[1][2]:
            #reopen the connection
            db_connection = conndbmod.connecting_to_db()
            print ("first one is the new entry, deleting 2nd one")
            db_crud_func(db_connection, query_delete_entry_based_on_timestamp, selected_items[1][2])
            #connection closed
        else:
            #reopen the connection
            db_connection = conndbmod.connecting_to_db()
            print ("2nd one large, deleting 1st one")
            db_crud_func(db_connection, query_delete_entry_based_on_timestamp, selected_items[0][2])
            #connection closed
            
##############################
#Send infomation to nodes PART
##############################

def send_node_info(para_local_ipandport,para_remote_ipandport,para_jsondata):
    conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    conn.bind(para_local_ipandport)
    conn.connect(para_remote_ipandport)
    #conn.send(f"This is{localip}, uuid is{hostid}".encode())
    conn.send(bytes(para_jsondata,encoding="utf-8"))
    conn.close()

#DEFINE local inbound and outbound socket
#localip = socket.gethostbyname(socket.gethostname())
localip = "192.168.100.68"
local_outbound_port = 5001 #port can't be str
local_inbound_port = 5002
local_outbound_ipandport = (localip, local_outbound_port)
local_inbound_ipandport = (localip, local_inbound_port)
monitoring = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

######################################
##MAIN LOOP    AND
##Accepting NW connection part
######################################
def client_inbound_connection(para_conn_monitor, para_localipandport):
    para_conn_monitor.bind(para_localipandport)
    para_conn_monitor.listen()
    
    while True:
            (incomingconn, clientip) = para_conn_monitor.accept()
            #while True:
            data = incomingconn.recv(1024)
            print(data)
            recv_json = json.loads(data)

            print(type(recv_json["type"]))

            client_type = recv_json["type"]
            client_ip_address = recv_json["nodeip"]
            client_timestamp = recv_json["nodetimestamp"]
            client_uuid = recv_json["nodeuuid"]
            
            if client_type == "1":
                db_connection = conndbmod.connecting_to_db()
                db_crud_func(db_connection, query_insert_ip_bin_uuid_timestamp_date, \
                    client_ip_address, client_ip_address, client_timestamp, client_uuid)
                db_connection = conndbmod.connecting_to_db()
                dedup_after_adding_entry(db_connection, query_dedup_ip, query_search_ip)
            else:
                pass
            #print(f"in the func {client_ip_address}, {client_uuid}")
            #return recv_json
            #para_conn_monitor.close()

#Send updated infomation according to the list of IP address
def traverse_and_sendinfo():#(para_net_conn, para_query):
    db_connection = conndbmod.connecting_to_db()
    node_list = db_search_func(db_connection, query_list_ip)
    json_raw = {"type":"1","data":node_list}
    json_formatted = json.dumps(json_raw)
    i = 0
    while i < len(node_list):
        try:
            remoteip = node_list[i][0]
            remote_ipandport = (remoteip,5001)
            send_node_info(local_outbound_ipandport,remote_ipandport,json_formatted)
            i = i + 1
        except Exception as e:
            print(e)
            i = i + 1
            continue
    
traverse_and_sendinfo()
    
#send_node_info()

#print(client_inbound_connection(monitoring,localipandport))