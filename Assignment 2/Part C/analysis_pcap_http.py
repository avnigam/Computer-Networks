import dpkt
import struct

# This is the Packet class with TCP/HTTP header and data attributes.
class Packet:
    timestamp = 0
    header_len = 0
    src_ip = ''
    dest_ip = ''
    src_port = 0
    dest_port = 0
    seq_num = 0
    ack_num = 0
    data_offset = 0
    reserved = 0
    ns = 0
    cwr = 0
    ece = 0
    urg = 0
    ack = 0
    psh = 0
    rst = 0
    syn = 0
    fin = 0
    window_size = 0
    checksum = ''
    urg_ptr = 0
    options = ''
    version = ''
    len_buf = 0
    request = ''
    response = ''
    data = ''

# This function parses the packet and create object of Packet Class
# This in turn will create two list of tcp data and http data
def get_packet_list(pcap):
    tcp_packets = []
    http_packets = []

    for ts, buf in pcap:
        packet = Packet()

        packet.ts = ts
        packet.src_ip = str(struct.unpack(">B", buf[26])[0]) + '.' + str(struct.unpack(">B", buf[27])[0]) + '.' + str(struct.unpack(">B", buf[28])[0]) + '.' + str(struct.unpack(">B", buf[29])[0])
        packet.dest_ip = str(struct.unpack(">B", buf[30])[0]) + '.' + str(struct.unpack(">B", buf[31])[0]) + '.' + str(struct.unpack(">B", buf[32])[0]) + '.' + str(struct.unpack(">B", buf[33])[0])
        packet.src_port = struct.unpack(">H", buf[34:36])[0]
        packet.dest_port = struct.unpack(">H", buf[36:38])[0]
        packet.src_port = struct.unpack(">H", buf[34:36])[0]
        packet.dest_port = struct.unpack(">H", buf[36:38])[0]
        packet.seq_num = struct.unpack(">I", buf[38:42])[0]
        packet.ack_num = struct.unpack(">I", buf[42:46])[0]

        packet.header_len = struct.unpack(">B", buf[46])[0]/4
        options = struct.unpack(">H", buf[46:48])[0]
        opt_bits = "{0:b}".format(options)

        packet.data_offset = int(opt_bits[0:4], 2)
        packet.reserved = opt_bits[4:7]
        packet.ns = opt_bits[7]
        packet.cwr = opt_bits[8]
        packet.ece = opt_bits[9]
        packet.urg = opt_bits[10]
        packet.ack = opt_bits[11]
        packet.psh = opt_bits[12]
        packet.rst = opt_bits[13]
        packet.syn = opt_bits[14]
        if len(opt_bits) > 15:
            packet.fin = opt_bits[15]

        packet.window_size = struct.unpack(">H", buf[48:50])[0]
        packet.checksum = struct.unpack(">c", buf[50])[0] + struct.unpack(">c", buf[51])[0]
        packet.urg_ptr = struct.unpack(">c", buf[52])[0] + struct.unpack(">c", buf[53])[0]
        packet.len_buf = len(buf)

        if len(buf) > 66:
            packet.request = str(struct.unpack(">s", buf[66])[0]) + str(struct.unpack(">s", buf[67])[0]) + str(struct.unpack(">s", buf[68])[0])
            packet.response = str(struct.unpack(">s", buf[66])[0]) + str(struct.unpack(">s", buf[67])[0]) + str(struct.unpack(">s", buf[68])[0]) + str(struct.unpack(">s", buf[69])[0])

            if packet.request == 'GET' or packet.response == 'HTTP':
                for i in range(66, len(buf)):
                    packet.data += str(struct.unpack(">s", buf[i])[0])

                http_packets.append(packet)

        tcp_packets.append(packet)

    return tcp_packets, http_packets


f = open('http_8092_temp.pcap')
pcap1 = dpkt.pcap.Reader(f)
(tcp_packets, http_packets) = get_packet_list(pcap1)

packet_dict = {}
# This creates a combination of src_port/dest_port and list of packets associated with this combination.
for packet in tcp_packets:
    if packet.src_port == 8092:
        tuple = (packet.src_port, packet.dest_port)
        list = []
        if tuple in packet_dict.keys():
            list = packet_dict[tuple]

        list.append(packet)
        packet_dict[tuple] = list

request_list = []
result = []
# This will create HTTP request/response pair.
for packet in http_packets:
    if packet.request == 'GET':
        request_list.append(packet)

    if packet.response == 'HTTP':
        result.append((request_list.pop(0), packet))


final_result = []
for res in result:
    tcp_data = set()
    packet_list = packet_dict[(res[1].src_port, res[1].dest_port)]
    for packet in packet_list:
        if packet.len_buf > packet.header_len + 34:
            tcp_data.add((packet.src_ip, packet.src_port, packet.dest_ip, packet.dest_port, packet.seq_num, packet.ack_num))

    final_result.append((res, tcp_data))

print len(final_result)

no_of_http_connections_8092 = 0
total_data = 0
unique_set = set()
last_time = 0
for packet in tcp_packets:
    if packet.len_buf > 200:
        last_time = packet.ts

    total_data += packet.len_buf

    if packet.ack == '1' and packet.syn == '1':
        no_of_http_connections_8092 += 1

total_time = last_time - tcp_packets[0].ts
print "Time 8092: " + str(total_time)
print "Packets 8092: " + str(len(tcp_packets))
print "Data 8092: " + str(total_data)

f = open('http_8093_temp.pcap')
pcap2 = dpkt.pcap.Reader(f)
packets2 = get_packet_list(pcap2)[0]

no_of_http_connections_8093 = 0
total_data = 0
last_time = 0
for packet in packets2:
    if packet.len_buf > 200:
        last_time = packet.ts

    total_data += packet.len_buf
    if packet.ack == '1' and packet.syn == '1':
        no_of_http_connections_8093 += 1

total_time = last_time - packets2[0].ts
print "Time 8093: " + str(total_time)
print "Packets 8093: " + str(len(packets2))
print "Data 8093: " + str(total_data)

f = open('http_8094_temp.pcap')
pcap3 = dpkt.pcap.Reader(f)
packets3 = get_packet_list(pcap3)[0]

no_of_http_connections_8094 = 0
total_data = 0
last_time = 0
for packet in packets3:
    if packet.len_buf > 200:
        last_time = packet.ts

    total_data += packet.len_buf
    if packet.ack == '1' and packet.syn == '1':
        no_of_http_connections_8094 += 1

total_time = last_time - packets3[0].ts
print "Time 8094: " + str(total_time)
print "Packets 8094: " + str(len(packets3))
print "Data 8094: " + str(total_data)

print "No. of TCP Connections 8092: " + str(no_of_http_connections_8092)
print "No. of TCP Connections 8093: " + str(no_of_http_connections_8093)
print "No. of TCP Connections 8094: " + str(no_of_http_connections_8094)

for res in final_result:
    print res[0][0].data
    print res[0][1].data
    for data in res[1]:
        print data
    print '#############################################################################################################'

