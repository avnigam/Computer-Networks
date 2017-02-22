import dns
import dns.name
import dns.query
import dns.resolver
import sys

root_server_list = ['198.41.0.4',
                    '192.228.79.201',
                    '192.33.4.12',
                    '199.7.91.13',
                    '192.203.230.10',
                    '192.5.5.241',
                    '192.112.36.4',
                    '198.97.190.53',
                    '192.36.148.17',
                    '192.58.128.30',
                    '193.0.14.129',
                    '199.7.83.42',
                    '202.12.27.33']


# Take arguments and return the ip address responsible for the domain.
# domain_search - Domain Name to be searched.
# server - The server responsible for the domain name.
# category - The flag for the answer type.
def resolve_component(domain_search, server, category):
    result = []
    try:
        query = dns.message.make_query(domain_search, category)
        response = dns.query.udp(query, server, timeout=1)

        rcode = response.rcode()
        if rcode != dns.rcode.NOERROR:
            raise Exception('Error in response')

        if len(response.authority) > 0:
            rrset = response.authority[0]
        else:
            rrset = response.answer[0]

        rr = rrset[0]
        if rr.rdtype == dns.rdatatype.SOA:
            result.append(server)
        elif len(response.answer) > 0:
            result.append(server)
        else:
            authority = rr.target.to_text()
            # Check if additional section exist.
            # If not, resolve the authority completely again.
            if len(response.additional) > 0:
                rrset = response.additional
                for rr in rrset:
                    result.append(rr[0].to_text())
            else:
                result = resolve_dns(authority, category)

    except Exception:
        return None

    return result

# This function takes the arguments and return the server for the domain.
def resolve_dns(domain, category):
    domain_name = dns.name.from_text(domain)
    root_index = 0

    # Split the domain by '.'
    domain_parts = str(domain_name).split('.')

    result_server = None
    del domain_parts[-1]
    domain_search = domain_parts[-1] + '.'

    # Iterate over the list of root servers until you get a response.
    # Terminate if iterated over all the servers.
    # Search for last component of the domain.
    while not result_server:
        server = root_server_list[root_index]
        result_server = resolve_component(domain_search, server, category)
        root_index += 1

        if root_index == len(root_server_list):
            break

    del domain_parts[-1]

    # Iterate over remaining parts of the domain.
    for part in reversed(domain_parts):
        domain_search = part + '.' + domain_search
        server_index = 0
        result = None
        if not result_server:
            break

        while not result:
            try:
                result = resolve_component(domain_search, result_server[server_index], category)
                if result:
                    result_server = result
            except:
                server_index += 1
                if server_index == len(result_server):
                    break

    return result_server


def my_dig(domain, category):
    server_list = resolve_dns(domain, category)
    query = dns.message.make_query(domain, category)
    response = None
    server_index = 0
    if server_list:
        while not response:
            try:
                # Query the server responsible for the domain.
                # This will provide type specific results.
                response = dns.query.udp(query, server_list[server_index], timeout=1)
            except:
                server_index += 1
                if server_index == len(server_list):
                    break

        return response

if __name__ == '__main__':
    domain = sys.argv[1]
    flag = sys.argv[2]

    if domain and flag:
        result = my_dig(domain, flag)
        if result:
            print(';QUESTION')
            for ques in result.question:
                print(ques)
            print(';ANSWER')
            for ans in result.answer:
                print(ans)
