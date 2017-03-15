import dpkt
import struct

# This is the Packet class with TCP header and data attributes.
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
    mss = 0
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
    len_buf = 0


f = open('assignment2.pcap')
pcap = dpkt.pcap.Reader(f)

packets = []

# This loop gets each packet, parses it and adds it to a list of packets.
# The library used for parsing is struct library.
for ts, buf in pcap:
    packet = Packet()

    packet.ts = ts
    packet.header_len = struct.unpack(">b", buf[46])[0] / 4
    packet.src_ip = str(struct.unpack(">B", buf[26])[0]) + '.' + str(struct.unpack(">B", buf[27])[0]) + '.' + str(struct.unpack(">B", buf[28])[0]) + '.' + str(struct.unpack(">B", buf[29])[0])
    packet.dest_ip = str(struct.unpack(">B", buf[30])[0]) + '.' + str(struct.unpack(">B", buf[31])[0]) + '.' + str(struct.unpack(">B", buf[32])[0]) + '.' + str(struct.unpack(">B", buf[33])[0])
    packet.src_port = struct.unpack(">H", buf[34:36])[0]
    packet.dest_port = struct.unpack(">H", buf[36:38])[0]
    packet.src_port = struct.unpack(">H", buf[34:36])[0]
    packet.dest_port = struct.unpack(">H", buf[36:38])[0]
    packet.seq_num = struct.unpack(">I", buf[38:42])[0]
    packet.ack_num = struct.unpack(">I", buf[42:46])[0]

    packet.header_len = struct.unpack(">B", buf[46])[0] / 4
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
    packet.fin = opt_bits[15]

    if packet.syn == '1' and packet.ack == '1':
        packet.mss = struct.unpack(">H", buf[56:58])[0]

    packet.window_size = struct.unpack(">H", buf[48:50])[0]
    packet.checksum = struct.unpack(">c", buf[50])[0] + struct.unpack(">c", buf[51])[0]
    packet.urg_ptr = struct.unpack(">c", buf[52])[0] + struct.unpack(">c", buf[53])[0]
    packet.len_buf = len(buf)

    packets.append(packet)

packet_dict = {}
# Create list of each unique tuple of src_ip, dest_ip, src_port and dest_port
for packet in packets:
    tuple = (packet.src_ip, packet.dest_ip, packet.src_port, packet.dest_port)
    list = []
    if tuple in packet_dict.keys():
        list = packet_dict[tuple]

    list.append(packet)
    packet_dict[tuple] = list

no_of_tcp_flows = 0
packets_list = []
for tuple in packet_dict.keys():
    if tuple[0] == '130.245.145.12':
        new_tuple = (tuple[1], tuple[0], tuple[3], tuple[2])
        src_list = packet_dict[tuple]
        dest_list = packet_dict[new_tuple]

        print "Total No. of Packets: " + str(len(src_list))

        total_data = 0
        for packet in packet_dict[tuple]:
            total_data += packet.len_buf

        connection_list = []
        for packet in dest_list:
            if packet.src_ip == tuple[1] and packet.dest_ip == tuple[0] and packet.src_port == tuple[3] and packet.dest_port == tuple[2]:
                if packet.ack == '1' and packet.syn == '1':
                    no_of_tcp_flows += 1
                    print "MSS: " + str(packet.mss)
                    print "Window Size: " + str(packet.window_size)

        for i in range(0, len(packets)):
            if (packets[i].src_ip == tuple[0] and packets[i].dest_ip == tuple[1] and packets[i].src_port == tuple[2] and packets[i].dest_port == tuple[3]) or \
               (packets[i].src_ip == tuple[1] and packets[i].dest_ip == tuple[0] and packets[i].src_port == tuple[3] and packets[i].dest_port == tuple[2]):
                connection_list.append(packets[i])

        next_set = set()
        for p1 in range(2, len(src_list)):
            for p2 in range(1, len(dest_list)):
                if src_list[p1].seq_num + src_list[p1].len_buf - 34 == dest_list[p2].ack_num:
                    next_set.add((src_list[p1].seq_num, src_list[p1].ack_num, dest_list[p2].seq_num, dest_list[p2].ack_num, src_list[p1].window_size))

            if len(next_set) == 2:
                break

        for data in next_set:
            print data

        print "Total Data: " + str(total_data)
        print "Time: " + str(dest_list[len(dest_list) - 1].ts - src_list[0].ts)
        through_put = total_data / (dest_list[len(dest_list) - 1].ts - src_list[0].ts)
        print "Throughput: " + str(through_put)

        packet_seq_rtt_dict = dict()
        packet_ack_rtt_dict = dict()
        for p in src_list:
            if p.seq_num in packet_seq_rtt_dict:
                continue
            else:
                packet_seq_rtt_dict[p.seq_num] = p.ts

        for p in dest_list:
            if p.ack_num in packet_ack_rtt_dict:
                continue
            else:
                packet_ack_rtt_dict[p.ack_num] = p.ts

        pac_cnt = 0
        total_time = 0
        for key in packet_seq_rtt_dict:
            if key in packet_ack_rtt_dict:
                pac_cnt += 1
                total_time += (packet_ack_rtt_dict[key] - packet_seq_rtt_dict[key])

        print "Average RTT: " + str(total_time / pac_cnt)

        # Calculate Total No. of  Retransmissions
        # Also differentiate between retransmission due to triple ack and no ack.
        seq_list = []
        loss_count = 0
        for i in range(2, len(src_list)):
            if src_list[i].seq_num in seq_list:
                loss_count += 1
            else:
                seq_list.append(src_list[i].seq_num)

        print "Total Unique Packets Retransmitted: " + str(loss_count)

        packet_seq_loss_dict = dict()
        packet_ack_loss_dict = dict()
        for p in src_list:
            if p.seq_num in packet_seq_loss_dict:
                packet_seq_loss_dict[p.seq_num] += 1
            else:
                packet_seq_loss_dict[p.seq_num] = 1

        for p in dest_list:
            if p.ack_num in packet_ack_loss_dict:
                packet_ack_loss_dict[p.ack_num] += 1
            else:
                packet_ack_loss_dict[p.ack_num] = 1

        triple_loss = 0
        no_ack_loss = 0
        for key in packet_seq_loss_dict.keys():
            if key in packet_ack_loss_dict.keys():
                if packet_ack_loss_dict[key] > 2:
                    triple_loss += 1


        print "Triple Ack Loss: " + str(triple_loss)
        print "No Ack Loss: " + str(loss_count - triple_loss)

        syn_seq = 0
        count = 0
        # Calculate Congestion Window
        for packet in connection_list:
            if packet.src_ip == '130.245.145.12':
                syn_seq = packet.seq_num

            if packet.dest_ip == '130.245.145.12' and syn_seq != 0 and syn_seq - packet.ack_num > 0:
                count += 1
                print "Congestion Window: " + str(syn_seq - packet.ack_num)
                syn_seq = 0

            if count == 5:
                break

        print ""

print "No. of TCP Flows: " + str(no_of_tcp_flows)
