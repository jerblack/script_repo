#!/bin/bash

mkdir -p ~/gdc_enc ~/gdc_dec
google-drive-ocamlfuse -label gdc ~/gdc_enc/
ENCFS6_CONFIG="/home/jeremy/.config/enc/.encfs6.xml" encfs /home/jeremy/gdc_enc/backup /home/jeremy/gdc_dec --extpass="/home/jeremy/.config/enc/k" -o nonempty
