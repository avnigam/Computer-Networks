a) The python program has been used for developing the protocol
The network should have connectivity between each communicating nodes before running the protocol.
The routing can be setup statically or dynamically.
	
python router.py host host_ip {neighbour:neighbour_ip} 
		
Log are provided by redirecting console output.
The code does not implement posioned reverse or split horizon to handle all the scenarios.
Ports and Weights file Name are hard-coded in the code.  		

Dest    Cost    Next    <- H1 distance vector
R4      8       R1
R1      2       R1
R2      12      R1
R3      8       R1
H2      inf     H2
H1      0       H1


Dest    Cost    Next    <- R2 distance vector
R4      -4      R4
R1      10      R1
R2      -8      R4
R3      1       R4
H2      -2      R4
H1      12      R1

Dest    Cost    Next    <- R1 distance vector
R4      6       R2
R1      0       R1
R2      2       R2
R3      3       R2
H2      0       R2
H1      2       H1

Dest    Cost    Next    <- R3 distance vector
R4      5       R4
R1      6       R1
R2      8       R1
R3      0       R3
H2      6       R1
H1      8       R1


Dest    Cost    Next    <- H2 distance vector
R4      -6      R4
R1      0       R4
R2      -10     R4
R3      -1      R4
H2      -4      R4
H1      inf     R4

Dest    Cost    Next    <- R4 distance vector
R4      -8      R2
R1      6       R2
R2      -4      R2
R3      5       R3
H2      2       H2
H1      8       R2

		
Time taken to find shortest path = 12 seconds
That is when the routes converge and programs stops to update the routing table file.
Can be infered from logs.
	
	

c) Vertex H1 distance to other nodes
Time taken to find shortest path = 8 seconds
That is when the routes converge and programs stops to update the routing table file.
Can be infered from logs.

Dest    Cost    Next    <- R2 distance vector
R4      -12     R4
R1      -6      R4
R2      -16     R4
R3      -7      R4
H2      -10     R4
H1      -4      R1

Dest    Cost    Next    <- R3 distance vector
R4      -3      R4
R1      3       R4
R2      -7      R4
R3      0       R3
H2      -1      R4
H1      5       R1


Dest    Cost    Next    <- R1 distance vector
R4      -21     R2
R1      -15     R2
R2      -25     R2
R3      -32     R2
H2      -35     R2
H1      2       H1
Dest    Cost    Next    <- R4 distance vector
R4      -36     R2
R1      -30     R2
R2      -40     R2
R3      -47     R2
H2      -50     R2
H1      -44     R2


Dest    Cost    Next    <- H2 distance vector
R4      -82     R4
R1      -112    R4
R2      -122    R4
R3      -129    R4
H2      -132    R4
H1      -126    R4

Dest    Cost    Next    <- H1 distance vector
R4      -19     R1
R1      -13     R1
R2      -38     R1
R3      -45     R1
H2      -48     R1
H1      -11     R1
