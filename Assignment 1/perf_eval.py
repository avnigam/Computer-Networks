import dns.resolver
import time
import socket
import matplotlib.pyplot as plt
import numpy as np
from src.resolver import my_dig

alexa_sites = ['www.google.co.uk',
               'www.reddit.com',
               'www.google.de',
               'www.jd.com',
               'www.sina.com.cn',
               'www.yahoo.co.jp',
               'www.instagram.com',
               'www.360.cn',
               'www.linkedin.com',
               'www.twitter.com',
               'www.vk.com',
               'www.live.com',
               'www.taobao.com',
               'www.google.co.jp',
               'www.sohu.com',
               'amazon.com',
               'www.qq.com',
               'www.tmall.com',
               'www.google.co.in',
               'www.wikipedia.org',
               'yahoo.com',
               'baidu.com',
               'facebook.com',
               'www.youtube.com',
               'www.google.com']

def resolve_local(domain):
    answer = socket.gethostbyname(domain)
    return answer


def resolve_google(domain):
    ip_list = []
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8']

    answer = resolver.query(domain, 'A')
    for ans in answer:
        ip_list.append(ans)

    return ip_list


results_local = []
results_google = []
results_mydig = []

for domain in alexa_sites:
    print(domain)
    local_avg_time = 0
    google_avg_time = 0
    my_dig_avg_time = 0
    for i in range(0, 10):
        start_time = time.time()
        resolve_local(domain)
        end_time = time.time()

        local_avg_time += (end_time - start_time)

        start_time = time.time()
        resolve_google(domain)
        end_time = time.time()

        google_avg_time += (end_time - start_time)

        start_time = time.time()
        my_dig(domain, 'A')
        end_time = time.time()

        my_dig_avg_time += (end_time - start_time)

    results_local.append((1000 * local_avg_time)/10.0)
    results_google.append((1000 * google_avg_time)/10.0)
    results_mydig.append((1000 * my_dig_avg_time)/10.0)


X1, b1 = np.histogram(results_local, bins=1000)
X2, b2 = np.histogram(results_google, bins=1000)
X3, b3 = np.histogram(results_mydig, bins=1000)

print(results_local)
print(results_google)
print(results_mydig)

#evaluate the cumulative
cumulative_x1 = np.cumsum(X1)
cumulative_x2 = np.cumsum(X2)
cumulative_x3 = np.cumsum(X3)

plt.xlabel('Time (msec.)')
plt.ylabel('Cumulative Frequency')

# plot the cumulative function
plt.plot(b1[:-1], cumulative_x1, c='green', label='Local DNS')
plt.plot(b2[:-1], cumulative_x2, c='blue', label='Google DNS')
plt.plot(b3[:-1], cumulative_x3, c='red', label='My DNS')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.show()
