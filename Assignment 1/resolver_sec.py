import dns
import dns.name
import dns.query
import dns.dnssec
import dns.resolver
from dns.exception import DNSException
import time
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


# This function takes in the domain and server as function parameters.
# This function is used for building chain of trust.
# It returns the DS and Algorithm.
def resolve_component_parent(domain_search, server):
    result = []
    ds = None
    algorithm = -1
    try:
        query = dns.message.make_query(domain_search,
                                       dns.rdatatype.DNSKEY,
                                       want_dnssec=True)
        response = dns.query.tcp(query, server, timeout=1)

        rcode = response.rcode()
        if rcode != dns.rcode.NOERROR:
            raise Exception('Error in response')

        # Extract DS and Algorithm from the authority section of the response.
        if len(response.authority) > 0:
            for rrset in response.authority:
                rr = rrset[0]
                if rrset.rdtype == dns.rdatatype.DS:
                    ds = rr
                    algorithm = rr.digest_type

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
            if len(response.additional) > 0:
                rrset = response.additional
                for rr in rrset:
                    result.append(rr[0].to_text())
            else:
                result = resolve_dns(authority)

    except Exception:
        return None, None, None

    return result, ds, algorithm

# Query for DNSKEY and RRSIG(DNSKEY) from the child server.
# This data is used for verifying chain of trust.
# Also used for verifying the DNSKEY of the child server.
def resolve_component_child(domain_search, server):
    dnskey = None
    rrsig_dnskey = None
    dnskey_record = None
    try:
        query = dns.message.make_query(domain_search,
                                       dns.rdatatype.DNSKEY,
                                       want_dnssec=True)
        response = dns.query.tcp(query, server, timeout=1)

        rcode = response.rcode()
        if rcode != dns.rcode.NOERROR:
            if rcode == dns.rcode.NXDOMAIN:
                raise Exception('Error in response')

        if len(response.answer) > 0:
            for rrset in response.answer:
                if rrset.rdtype == dns.rdatatype.DNSKEY:
                    dnskey_record = rrset
                    for r in rrset:
                        if r.flags == 257:
                            dnskey = r
                elif rrset.rdtype == dns.rdatatype.RRSIG:
                    rrsig_dnskey = rrset

    except Exception:
        return None, None, None

    return dnskey, rrsig_dnskey, dnskey_record

# Validate the root server.
# Static chain of trust test is done.
# DNSKEY verification done by querying for '.' against the root server.
def validate_root_server(server):
    ds1 = '19036 8 2 49AAC11D7B6F6446702E54A1607371607A1A41855200FD2CE1CDDE32F24E8FB5'
    ds2 = '20326 8 2 E06D44B80B8F1D39A95C0B0D7C65D08458E880409BBC683457104237C7F8EC8D'

    (dnskey, rrsig_dnskey, dnskey_record) = resolve_component_child('.', server)
    if not dnskey:
        return False

    hash_key = dns.dnssec.make_ds('.', dnskey, 'sha256')
    if str(hash_key) == ds1.lower() or str(hash_key) == ds2.lower():
        name = dns.name.from_text('.')
        try:
            dns.dnssec.validate(dnskey_record, rrsig_dnskey, {name: dnskey_record})
        except dns.dnssec.ValidationFailure:
            print('DNSSEC verification failed')
            return False
        return True
    else:
        return False

def resolve_dns(domain):
    domain_name = dns.name.from_text(domain)
    root_index = 0

    domain_parts = str(domain_name).split('.')

    result_server = None
    algorithm = None
    ds = None
    del domain_parts[-1]
    domain_search = domain_parts[-1] + '.'

    # Iterate over the list of root servers until you get a response.
    # Terminate if iterated over all the servers.
    while not result_server:
        server = root_server_list[root_index]

        if validate_root_server(server):
            (result_server, ds, algorithm) = resolve_component_parent(domain_search, server)

        root_index += 1

        if root_index == len(root_server_list):
            return None

    del domain_parts[-1]
    domain_parts = ['@'] + domain_parts
    for part in reversed(domain_parts):
        server_index = 0
        result = None
        dnskey = None
        rrsig_dnskey = None

        # Query for the DNSKEY and RRSIG(DNSKEY) from the child server.
        # If DNSKEY or RRSIG(DNSKEY) does not exist, it mean DNSSEC is not supported.
        while not dnskey or not rrsig_dnskey:
            (dnskey, rrsig_dnskey, dnskey_record) = resolve_component_child(domain_search, result_server[server_index])
            server_index += 1
            if server_index == len(result_server):
                print("DNSSEC not supported")
                return None

        # Check for chain of trust between parent and child.
        # For this we are creating DS from child's DNSKEY and compare it against DS from parent.
        # If anything fails in this step, it means that DNSSEC verification failed.
        if algorithm and ds and dnskey and rrsig_dnskey:
            if algorithm == 1:
                algorithm = 'sha1'
            else:
                algorithm = 'sha256'
            hash_key = dns.dnssec.make_ds(domain_search, dnskey, algorithm)
            if hash_key != ds:
                print("DNSSEC verification failed")
                return None

            name = dns.name.from_text(domain_search)
            try:
                dns.dnssec.validate(dnskey_record, rrsig_dnskey, {name: dnskey_record})
            except dns.dnssec.ValidationFailure:
                print('DNSSEC verification failed')
                return None
        else:
            print("DNSSEC not supported")
            return None

        if part == '@':
            break

        domain_search = part + '.' + domain_search
        while not result:
            try:
                # Query for the DS, Algorithm and nameserver address from the server.
                # This will be used later for verifying chain of trust.
                (result, ds, algorithm) = resolve_component_parent(domain_search, result_server[server_index])
                if result:
                    result_server = result
                else:
                    raise Exception('Result Empty')
            except Exception:
                server_index += 1
                if server_index == len(result_server):
                    return None

    return result_server


def my_dig(domain):
    server_list = resolve_dns(domain)
    if server_list:
        query = dns.message.make_query(domain, 'A')
        response = None
        server_index = 0
        while not response:
            try:
                response = dns.query.tcp(query, server_list[server_index], timeout=1)
            except:
                server_index += 1
                if server_index == len(server_list):
                    break

        return response


if __name__ == '__main__':
    domain = sys.argv[1]

    if domain:
        result = my_dig(domain)
        if result:
            print(result)
