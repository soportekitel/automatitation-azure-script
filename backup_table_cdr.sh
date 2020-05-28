#!/bin/bash

backup_dir="/var/spool/asterisk/cdr_backup/"$(date -d "-1 months" +%Y)
backup_file="CDR_"$(date -d "-1 months" +%Y)"_"$(date -d "-1 months" +%m)".csv"

[ ! -d $backup_dir ] && mkdir -p $backup_dir && chown asterisk: $backup_dir && chmod 777 $backup_dir

mysql -u root -e "select GROUP_CONCAT(CONCAT(\"\",COLUMN_NAME,\"\")) as col_names from INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'cdr' AND TABLE_SCHEMA ='asteriskcdrdb' ORDER BY ORDINAL_POSITION" | grep -v col_names | sed 's/,/","/g' | sed -E 's/^|$/"/g' > $backup_dir"/"$backup_file"_header"

mysql -u root asteriskcdrdb -e "SELECT * from cdr where DATE_FORMAT(calldate , '%Y-%m') = '"$(date -d "-1 months" +%Y-%m)"' INTO OUTFILE  '"$backup_dir"/"$backup_file"_data' FIELDS TERMINATED BY ','  ENCLOSED BY '\"' LINES TERMINATED BY '\n'"

mysql -u root asteriskcdrdb -e "DELETE * from cdr where DATE_FORMAT(calldate , '%Y-%m') = '"$(date -d "-3 months" +%Y-%m)"';"
mysql -u root asteriskcdrdb -e "OPTIMIZE TABLE cdr;"
mysql -u root asteriskcdrdb -e "ANALYZE TABLE cdr;"

cat $backup_dir"/"$backup_file"_header"  $backup_dir"/"$backup_file"_data" | sed 's/\\"/_#_/g' | sed "s/_#_/'/g" > "$backup_dir/$backup_file" && rm -f $backup_dir/*[data,header]
