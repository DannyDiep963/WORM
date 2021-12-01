# CPSC 456 WORM Project

## Group members
Danny Diep

## Prerequisites
Python 3.x

## Start GNS 
Create a topology as following:
![alt text](https://github.com/DannyDiep963/WORM/tree/main/screenshots/Topology.png)

## Configure Router
```
R1# conf t
R1(config)# int f0/0
R1(config-if)# ip add 10.0.0.1 255.255.255.0
R1(config-if)# no shut

R1(config-if)# service dhcp
R1(config)# ip dhcp pool BLUE
R1(dhcp-config)# lease 7 0 0
R1(dhcp-config)# network 10.0.0.0 255.255.255.0
R1(dhcp-config)# default-router 10.0.0.1
R1(dhcp-config)# ip dhcp excluded-address 10.0.0.1
R1(dhcp-config)# do wr
R1(config)# exit
```
## Start ssh services on all hosts (if port 22 is not openned)
```
$ sudo service ssh start
```

## Start Worm.py
```
$ cd ~/path-to-worm.py
$ python3 worm.py
```
## Process of infecting the host within the network
![alt text](https://github.com/DannyDiep963/WORM/tree/main/screenshots/Kali1.png)


## Check if the system is infected
```
$ hostname -I; ls /tmp
```
![alt text](https://github.com/DannyDiep963/WORM/tree/main/screenshots/Kali1.png)
![alt text](https://github.com/DannyDiep963/WORM/tree/main/screenshots/Kali2.png)
![alt text](https://github.com/DannyDiep963/WORM/tree/main/screenshots/Kali3.png)

