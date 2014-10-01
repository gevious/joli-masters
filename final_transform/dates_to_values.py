#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Take the by_date_chopped_indicators data and ignore companies with 0s
import os
import csv

from datetime import date

src_dir = '/home/nico/joli_masters/final_transform/by_date_chopped_percentiles'
output_dir = '/home/nico/joli_masters/final_transform/by_value'
input_files = []
start_date = date(2000, 12, 1)
all_data = {}
col_num = 0
company_num = 550

# load all data into memory
for filename in sorted(os.listdir(src_dir)):
    print filename
    outfile = open("{}/{}".format(output_dir, filename), 'w')
    with open("{}/{}".format(src_dir, filename), 'r') as f:
        indicator_reader = csv.reader(f, delimiter=',', quotechar='"')
        for i, row in enumerate(indicator_reader):
            if i == 0:
                outfile.write(';'.join(row)+"\n")
                continue  # ignore header
            skip_row = True
            for val in row[2:]:
                if val not in [0, '0', '']:
                    skip_row = False
            if not skip_row:
                print row
                outfile.write(';'.join(row)+"\n")
    outfile.close()
