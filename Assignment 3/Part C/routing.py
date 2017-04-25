import socket
import threading
import pdb
import time
import sys
import os
import json

def bellmanford(name, data, sender):
    lock.acquire()
    global counter
    flag = False

    if counter == 16:
        data = {}

    for key in data.keys():
        new_distance = distance_vector[sender][0] + data[key][0]
        if distance_vector[key][0] > new_distance:
            distance_vector[key] = (new_distance, sender)
            flag = True

    if flag is True:
        print_vector(name)
        send_neighbours(json.dumps((distance_vector, name)))
        counter += 1
    lock.release()


def send_neighbours(data):
    for host in neighbours.keys():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((neighbours[host], 9200))
            s.sendall(data.encode('utf8'))
        except:
            print 'exception while sending', sys.exc_info()
    pass


def print_vector(name):
    s = 'Dest\tCost\tNext\t<- %s distance vector\n' % name
    s += dashes
    for i in distance_vector.keys():
        cost = distance_vector[i][0]
        if cost > (sys.maxint / 2):
            cost = 'inf'
        else:
            cost = str(cost)
        s += '%s\t%s\t%s\n' % (i, cost, distance_vector[i][1])
    s += dashes
    print s

def update_from_file(name, data):
    lock.acquire()
    changed = False
    for key in distance_vector.keys():
        cost, hop = distance_vector[key]
        if hop in data.keys():
            distance_vector[key] = (data[hop], hop)
            changed = True

    if changed is True:
        send_to_neighbours(json.dumps((distance_vector, name)))
    lock.release()


def fetch_weights(filename, name):
    f = open(filename, 'r')
    data = {}

    for line in f:
        elem = line.split(',')
        if elem[0] == name:
            data[elem[1]] = int(elem[2])
        elif elem[1] == name:
            data[elem[0]] = int(elem[2])

    f.close()
    return data

def monitor_distance(name):
    time.sleep(1)
    filename = 'topology.txt'
    mtime = 0

    while stop is False:
        cur_mtime = os.stat(filename).st_mtime
        if mtime < cur_mtime:
            mtime = cur_mtime
            data = fetch_weights(filename, name)
            update_from_file(name, data)
        time.sleep(2)

def setup_distance_vectors(distance_vector, name):
    hosts = ['H1', 'H2', 'R1', 'R2', 'R3', 'R4']
    for host in hosts:
        if host == name:
            distance_vector[host] = (0, name)
        else:
            distance_vector[host] = (sys.maxint, host)


def start_listening():
    global neighbours, distance_vector, stop
    name = sys.argv[1]
    ip = sys.argv[2]
    neighbours = json.loads(sys.argv[3])
    setup_distance_vectors(distance_vector, name)

    print 'Starting server on ip %s' % ip
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, 9200))
    server.listen(5)

    monitor = threading.Thread(target=monitor_distance, args=(name,))
    monitor.start()

    try:
        while True:
            (client, address) = server.accept()
            data_received = client.recv(4096).decode('utf8')
            data_received, sender = json.loads(data_received)
            bellmanford(name, data_received, sender)
            client.close()
    except:
        print 'in exception of %s with exception %s' % (ip, sys.exc_info())
        stop = True
        server.close()
        monitor.join()


lock = threading.Lock()
neighbours = {}
distance_vector = {}
stop = False
counter = 0

if __name__ == '__main__':
    start_listening()
