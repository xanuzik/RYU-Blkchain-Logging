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

ip_tobe_added = "10.3.0.10"
uuid_tobe_added = "1111-2dasd-234easdf"

insert_ip_only = "INSERT INTO NODES.nodeinfo (ip) VALUES (%s)"
insert_ip_uuid = "INSERT INTO NODES.nodeinfo (ip,uuid) VALUES (%s,%s)"
insert_ip_bin =  "INSERT into NODES.nodeinfo (ip,IPv4BIN) VALUES (%s,INET6_ATON(%s))" #last two arguments are the same, using the IP twice
update_uuid = """UPDATE nodeinfo SET uuid = %s WHERE ip = %s"""
update_ip = """UPDATE nodeinfo SET ip = %s WHERE uuid = %s"""
list_ip_uuid = "SELECT ip, uuid FROM nodeinfo"

db_connection = conndbmod.connecting_to_db()

#db_crud_func(db_connection, insert_ip_bin, ip_tobe_added, ip_tobe_added)

list_ip_column = "SELECT ip FROM nodeinfo"
ip_list = (db_search_func(db_connection,list_ip_uuid))

print(ip_list)
print(len(ip_list))


# To judge if the new IP/UUID already exits in the DB
# def check_existence(sql_ip_uuid_list, )

i = 0
while i < len(ip_list):
    if ip_tobe_added == ip_list[i][0]: #update uuid according to ip address, [i][0] is ip address
        if uuid_tobe_added == ip_list[i][1]: #[i][1] is uuid
            continue
        else:
            db_crud_func(db_connection, update_uuid, ip_list[i][1], ip_list[i][0])
    else:
        if uuid_tobe_added != ip_list[i][1]:
            continue
        else:
            db_crud_func(db_connection, update_ip, ip_list[i][0], ip_list[i][1])
        print(ip_list[i][0])
        print(i)
        i = i+1

#def



#print(results)
#print(type(results))
#test_function(conn, "SELECT * FROM nodeinfo")
db_connection.close()