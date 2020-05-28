#!/bin/bash

/usr/sbin/fwconsole backup --list | grep -Pv "Transaction|-{10}" | grep -Po "[0-9a-f\-]{36}" | xargs -I{} /usr/sbin/fwconsole backup --backup="{}"

