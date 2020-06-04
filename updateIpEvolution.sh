#!/bin/bash
EVOLUTION=$(jq -r .evolution /usr/local/infodes/bin/config.json )
sed -Ei "s/[0-9\.]+.EvoRouter/$EVOLUTION\/EvoRouter/" /etc/asterisk/extensions_custom.conf
asterisk -rx "dialplan reload"
