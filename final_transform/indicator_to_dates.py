#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import csv
import math

from datetime import date
from dateutil.relativedelta import relativedelta

src_dir = '/home/nico/Code/joli_masters/final_transform/by_indicator'
output_dir = '/home/nico/Code/joli_masters/final_transform/by_date'
input_files = []
start_date = date(2000, 12, 1)
all_data = {}
col_num = 0
company_num = 550
chop_percentiles = True  # convert > 99th perc to 99th, < 1st perc to 1st

if chop_percentiles:
    output_dir += '_chopped_percentiles'

# load all data into memory
for filename in sorted(os.listdir(src_dir)):
    with open("{}/{}".format(src_dir, filename), 'r') as f:
        indicator_reader = csv.reader(f, delimiter=',', quotechar='"')
        indicator_name = f.name.split('/')[-1][:-4]
        all_data[indicator_name] = []
        for i, row in enumerate(indicator_reader):
            if i == 0:
                continue
            all_data[indicator_name].append(row)
            col_num = len(row)

# all data is in memory, lets write date files
col_num -= 2  # remove company name and industry name
indicators = sorted(all_data.keys())
for col in range(col_num-1):
    # print "Column: {}".format(col)
    file_data = []
    new_row = ["Company name", "Industry"] + indicators
    # f.write("Company name,Industry,{}\n".format(",".join(indicators)))
    # now cycle through every file and grab the column matching the date
    for c in range(company_num):
        # print "\tCompany {}".format(c)
        new_row = []
        for i in indicators:
            # print "\t\tIndicator: {}".format(i)
            row = all_data[i][c]
            if new_row == []:
                new_row.append(row[0])
                new_row.append(row[1])
            new_row.append(row[3+col])
        # print ",".join(new_row)
        file_data.append(new_row)

    current_date = start_date + relativedelta(months=col)
    current_date = current_date.strftime('%Y-%m')

    ignored_fields = ['0', '', '#DIV/0!', '#REF!']
    if chop_percentiles:
        # Get data per column so we can calculate and chop percentiles
        for k in range(2, len(indicators)+2):
            col_data = []
            print "Threshold for {} ({})".format(indicators[k-2], current_date)
            percentile_thresholds = []
            # lets get the range
            for file_row in file_data:
                # print file_row
                if file_row[k].strip() not in ignored_fields:
                    col_data.append(float(file_row[k]))
            # sort the data and calculate percentiles
            if len(col_data) < 1:
                continue
            col_data = sorted(col_data)
            for perc in [0.01, 0.99]:
                idx = int(math.ceil(perc * len(col_data))) - 1
                percentile_thresholds.append(col_data[idx])
            # replace values within file_data
            replacements = 0
            for file_row in file_data:
                if file_row[k].strip() in ignored_fields:
                    continue
                # print "{} : {}".format(file_row[k], float(file_row[k]))
                if float(file_row[k]) < percentile_thresholds[0]:
                    file_row[k] = str(percentile_thresholds[0])
                    # print 'replacing lower: {}'.format(file_row[k])
                    replacements += 1
                elif float(file_row[k]) > percentile_thresholds[1]:
                    file_row[k] = str(percentile_thresholds[1])
                    replacements += 1
                    # print 'replacing higher: {}'.format(file_row[k])
            print "Replaced {} values".format(replacements)

    print '='*40
    f = open("{}/{}.csv".format(output_dir, current_date), 'w')
    f.write("Company name,Industry,{}\n".format(",".join(indicators)))
    for file_row in file_data:
        f.write(",".join(file_row) + "\n")
    f.close()
