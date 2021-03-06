!/bin/sh


# this bash script is designed to detect legitimately the presence of a network connection by checking the operating state of your network interface
# cron schedules this script to run every minute


old_autorsf_name="/usr/local/bin/pexpect_rsf_concept_routingfix.py"

# new name of binary going forward for automatic routersploit
new_autorsf_name="/usr/local/bin/auto_rsf.py"

TIMEFORMAT=%R
timestr=$( date )

# logs detected public IP addresses
# see the discoloration? There is a bug
# something about quoting or escaping
fileip="/var/log/auto_rsf/ip_addr_hacked_routers_'$timestr'.log"

# main output from auto-routersploit
autorsf_log="/var/log/auto_rsf/autorsf_'$timestr'.log"
getipaddr="dig +short myip.opendns.com @resolver1.opendns.com"

# command to check if network is connected
check_netifaces="sudo cat /sys/class/net/wlan1/operstate | grep -xqFe up"

# internal network card that came with pi
default_netiface="/usr/local/bin/pexpect_rsf_concept_routingfix_wlan0.py"

eval $getipaddr >> $fileip

if eval $check_netifaces
then
	eval $getipaddr >> $fileip
	echo "Connected to Target. Autohacking"
	python $new_autorsf_name >> $autorsf_log
else
	echo "No networks detected"
fi

if sudo cat /sys/class/net/wlan2/operstate | grep -xqFe up
then
	eval $getipaddr >> $fileip
	echo "Connected to Target. Autohacking"
	python $new_autorsf_name >> $autorsf_log
else
	echo "No networks detected"
fi

if sudo cat /sys/class/net/wlan0/operstate | grep -xqFe up
then
	eval $getipaddr >> $fileip
	echo "Connected to Target. Autohacking"
	python $default_netiface >> $autorsf_log
else
	echo "No networks detected"
fi
