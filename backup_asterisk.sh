#!/bin/bash
set -e

backup_dir="/var/spool/asterisk/backup"

for i in $(ls $backup_dir/*.tar.gz | grep -Po "(?<=/)\d+(?=\-)" | grep "$(date  +%Y%m%d)"); do
    backup_database_dir="/tmp"

    backup_database_file="asterisk_database_"$(date  +%Y%m%d)"_.sql"
    backup_asterisk_file="asterisk_file_"$(date  +%Y%m%d)"_.zip"

    mysqldump -u admin  asterisk  > $backup_database_dir/$backup_asterisk_file
    zip -r $backup_dir/$backup_asterisk_file $backup_database_dir/$backup_database_file /etc/asterisk /var/lib/astersik/agi_bin

    rm -f $backup_database_dir/$backup_asterisk_file

    ls /var/spool/asterisk/backup/*.tar.gz | grep -Po "(?<=/)\d+(?=\-)" | paste -d"|" -s | xargs -I{} bash -c "ls /var/spool/asterisk/backup/asterisk_file* | grep -Pv '{}'" | xargs -I{} rm -f {}

    break

done
