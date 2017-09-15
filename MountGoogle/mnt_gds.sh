#!/bin/bash

google-drive-ocamlfuse -label gds ~/gds_enc/
ENCFS6_CONFIG="/home/jeremy/.config/enc/.encfs6.xml" encfs /home/jeremy/gdc_enc/backup /home/jeremy/gdc_dec --extpass="/home/jeremy/.config/enc/k" -o nonempty
