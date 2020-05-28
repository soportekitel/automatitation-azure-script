#!/bin/bash
sleep 90
mysql -e "update asterisk.kvstore_Sipsettings set val='"$(curl ifconfig.co)"' where \`key\`='externip';"
sleep 90
php /usr/sbin/fwconsole reload --json
