Name: Aviral Nigam
ID: 110849584
Course: FCN Assignment 1
Implementation Language: Python3


1. External Libraries used:
a. dnspython
b. pycrypto

2. Major Files:
i. resolver.py - This is the DNS resolver written in python. This program takes two arguments: first argument is alias to be resolved; second argument is the type. The code does a resolution on subsequent servers once the first server fails, until it gets the result or servers get exhausted. It does not check the server again once checked for results. We are udp based query for dns implementation with timeout of 1 sec. 

ii. resolver_sec.py - This is the DNSSEC resolver written in python. This program takes one argument i.e., alias to be resolved. The code does a resolution on subsequent servers once the first server fails, until it gets the result or servers get exhausted. It does not check the server again once checked for results and moved on. We are tcp based query for dns implementation with timeout of 1 sec.

iii. mydig - mydig is a bash script which takes two arguments and pass them to resolver.py
	 Use this script to run DNS resolver.
	 Command to run: ./mydig <domain> <type>

iv. mydig_sec - mydig_sec is a bash script which takes one arguments and pass them to resolver_sec.py
	 Use this script to run DNSSEC resolver.
	 Command to run: ./mydig_sec <domain>

v. perf_eval - This is code for performance evaluator which will generate the results for 3 types of DNS resolvers and then generate a CDF graph from the data.

3. Question
a. Write an explanation for why the resolution did not complete in one pass for "google.co.jp".
This happens due to domain resolving to an authoritative dns alias instead of an answer IP address. So, in the next step, we try to resolve this authoritative dns alias, which gives us the exact IP of the domain.