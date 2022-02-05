#!/bin/sh
#-------------------------------------------------------------------------
# Author: IU1BOW - Corrado Gerbaldo
#.........................................................................
# Script for monitoring dxspider system
#
# To use this script you need to install and configure ssmtp
# for enable sending mail using gmail (with 2-factor autentication):
# 1. Log-in into Gmail with your account
# 2. Navigate to https://security.google.com/settings/security/apppasswords
# 3. In 'select app' choose 'custom', give it an arbitrary name and press generate
# 4. It will give you 16 chars token.
# 5. put the token in your config file
#-------------------------------------------------------------------------
DISK=/dev/sda1       # <--- CHANGE WITH YOUR DRIVE !!!

#...................................................
CONFIG=../cfg/config.json
SSMTP=/usr/sbin/ssmtp
LIM_DISK=80
LIM_MEMPERC=80
LIM_DATE=1800

DIR=$(realpath -s $0|sed 's|\(.*\)/.*|\1|')
echo Absolute path: ${DIR}
cd ${DIR}

WARNING=false
trap 'rm -f "$TMPFILE"' EXIT
TMPFILE=$(mktemp)|| exit 1

#echo 'Subject: This is dxspider monitor '>>${TMPFILE}

echo >> ${TMPFILE}
echo 'RAM:' >> ${TMPFILE}
mon_memperc=$(free | grep Mem | awk '{print $3/$2 * 100}')
mon_memperc=$(echo ${mon_memperc}| awk '{ printf "%d\n",$1 }')
free -h>>${TMPFILE}
if [ ${mon_memperc} -gt ${LIM_MEMPERC} ]
then
	WARNING=true
	echo "WARNING: RAM space is critical!">> ${TMPFILE}
fi
echo  >> ${TMPFILE}

echo 'DISK' >> ${TMPFILE}
mon_diskperc=$(df ${DISK} | tail -n 1 | grep -E "[[:digit:]]+%" -o | grep -E "[1-9]+" -o)
df ${DISK} -h>>${TMPFILE}
if [ ${mon_diskperc} -gt ${LIM_DISK} ]
then
	WARNING=true
	echo "WARNING: Disk space is critical!">> ${TMPFILE}
fi
echo  >> ${TMPFILE}

echo 'SERVICES' >> ${TMPFILE}
ps -ef|head -1>> ${TMPFILE}
ps -ef | grep cluster.pl | grep -v grep >> ${TMPFILE}
mon_cluster=$?
ps -ef | grep mysqld | grep -v grep >> ${TMPFILE}
mon_mariadb=$?
ps -ef | grep "wsgi.py" | grep -v grep >> ${TMPFILE}
mon_wsgi=$?
ps -ef | grep "nginx: worker" | grep -v grep >> ${TMPFILE}
mon_nginx=$?

echo  >> ${TMPFILE}

if [ ${mon_mariadb} -ne 0 ]  
then
	WARNING=true
	echo "ERROR: maria db is not running!">> ${TMPFILE}
else 
	echo 'Mysql dxspider' >> ${TMPFILE}
	password=$(grep -Po '"passwd":.*?[^\/]",' ${CONFIG}|cut -d '"' -f 4)
	user=$(grep -Po '"user":.*?[^\/]",' ${CONFIG}|cut -d '"' -f 4)
	mon_sqlres=$(mysql --user=$user --password=$password -Bse "use dxcluster;select time from spot order by 1 desc limit 1;")

	current_date=$(date +"%s")
	date_diff=$((current_date - mon_sqlres))
	echo 'Last spot received: ' ${date_diff}' seconds ago' >> ${TMPFILE}
	if [ ${date_diff} -gt ${LIM_DATE} ]
	then
		WARNING=true
		echo 'WARNING: mysql is not UPDATED!' >> ${TMPFILE}
	fi
fi

if [ ${mon_cluster} -ne 0 ]  
then
	WARNING=true
	echo "ERROR: cluster is not running!">> ${TMPFILE}
fi

if [ ${mon_wsgi} -ne 0 ]  
then
	WARNING=true
	echo "ERROR: WSGI is not running!">> ${TMPFILE}
fi

if [ ${mon_nginx} -ne 0 ]  
then
	WARNING=true
	echo "ERROR: NGINX is not running!">> ${TMPFILE}
fi

if [ ${WARNING} = true ] ; then
	echo "$(echo 'Subject: [WARNING]: Spider monitor'; cat ${TMPFILE})" > ${TMPFILE}
else   
	echo "$(echo 'Subject: Spider monitor'; cat ${TMPFILE})" > ${TMPFILE}
fi

mailto=$(grep -Po '"mail":.*?[^\/]",' ${CONFIG}|cut -d '"' -f 4)
mail_token=$(grep -Po '"mail_token":.*?[^\/]",' ${CONFIG}|cut -d '"' -f 4)
echo ${mailto}
#${SSMTP} ${mailto} < ${TMPFILE}
${SSMTP} ${mailto} -au${mailto} -ap${mail_token} < ${TMPFILE}
cat ${TMPFILE}
rm ${TMPFILE}
