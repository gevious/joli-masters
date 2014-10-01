#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Take the by_date_chopped_indicators data and ignore companies with 0s
# also add column of previous month's excess return and return monthly
import os
import csv

from datetime import date

src_dir = \
    '/home/nico/Code/joli_masters/final_transform/by_date_chopped_percentiles'
output_dir = '/home/nico/Code/joli_masters/final_transform/by_value'
input_files = []
start_date = date(2000, 12, 1)
all_data = {}
col_num = 0
company_num = 550
last_month = []

# load all data into memory
for filename in sorted(os.listdir(src_dir), reverse=True):
    data = []
    print filename
    outfile = open("{}/{}".format(output_dir, filename), 'w')
    with open("{}/{}".format(src_dir, filename), 'r') as f:
        indicator_reader = csv.reader(f, delimiter=',', quotechar='"')
        for i, row in enumerate(indicator_reader):
            data.append(row)
            if i == 0:
                outfile.write(';'.join(row)
                              + ";NM Excess return;NM Monthly return\n")
                continue  # ignore header
            skip_row = True
            for val in row[2:]:
                if val not in [0, '0', '']:
                    skip_row = False
            if not skip_row:
                new_row = ';'.join(row)
                if len(last_month) > 0:
                    new_row += ";{};{}".format(
                        last_month[i][4], last_month[i][8])

                # print row
                outfile.write(new_row + "\n")
    outfile.close()
    last_month = list(data)
