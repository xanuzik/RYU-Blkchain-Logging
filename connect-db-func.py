from ipaddress import ip_address
from operator import mod
import json
import time
from wsgiref.simple_server import WSGIRequestHandler
import mysql
import conndbmod

#To add uncertain parameters in different columns to an entry
def db_crud_func(connection, query, *args): 

    cur=connection.cursor()
    cur.execute(query,(*args,))
#    result = cur.fetchall()
#    return result
    connection.close() #close the connection after making the amendment

#The function to query DB without arguments
def db_search_func(connection, query):
    cur = connection.cursor()
    cur.execute(query)
    result = cur.fetchall()
    return result
    connection.close()

ip_tobe_added = "1.2.3.4"
uuid_tobe_added = "1234544"

query_insert_ip_only = "INSERT INTO NODES.nodeinfo (ip) VALUES (%s)"
query_insert_ip_uuid = "INSERT INTO NODES.nodeinfo (ip,uuid) VALUES (%s,%s)"
query_insert_ip_bin =  "INSERT into NODES.nodeinfo (ip,IPv4BIN) VALUES (%s,INET6_ATON(%s))" #last two arguments are the same, using the IP twice
query_update_uuid = """UPDATE nodeinfo SET uuid = %s WHERE ip = %s"""
query_update_ip = """UPDATE nodeinfo SET ip = %s WHERE uuid = %s"""
query_list_ip_uuid = "SELECT ip, uuid FROM nodeinfo"

db_connection = conndbmod.connecting_to_db()

#db_crud_func(db_connection, insert_ip_bin, ip_tobe_added, ip_tobe_added)

list_ip_column = "SELECT ip FROM nodeinfo"
ip_list = (db_search_func(db_connection,query_list_ip_uuid)) #get a list of ip and uuid

print(f"ip list is {ip_list}")
print(len(ip_list))


# To judge if the new IP/UUID already exits in the DB

def db_pre_deduplicate(connection, para_query_update_uuid, para_query_update_ip, db_uuid_ip_list, new_ip, new_uuid): #1 the list of uuid and ip(may add timestamp later?), 2and3 are the info of the new node
    
    i = 0
    
    while i < len(db_uuid_ip_list):
        
        if new_ip == db_uuid_ip_list[i][0]: #update uuid according to ip address, [i][0] is ip address
            if new_uuid == db_uuid_ip_list[i][1]: #[i][1] is uuid
                print("Same host in DB!")
                break
            else:
                print("Same ip in DB, updating UUID!")
                db_crud_func(connection, para_query_update_uuid, new_uuid, new_ip)
                i=i+1
            
        else:
            if new_uuid != db_uuid_ip_list[i][1]:
                print("This is a whole new host! Will be added to the DB")
                i=i+1
            else:
                print("Same UUID in DB, updating Host!")
                db_crud_func(connection, para_query_update_ip, new_ip, new_uuid)
                i = i+1
            # print(db_uuid_ip_list[i][0])
            # print(i)
            # i = i+1

db_pre_deduplicate(db_connection, query_update_uuid, query_update_ip, ip_list, ip_tobe_added, uuid_tobe_added)

db_connection.close()