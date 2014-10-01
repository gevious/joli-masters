#!/usr/bin/env python
# Aggregates daily volume data into monthly format

import csv

header_list = ['Name']
name_map = {}
run_active = True
orig_file = '/tmp/datastream.csv'
output_file = '/tmp/datastream_final.csv'
month_set = {}  # maps column number to a month set

f = open(output_file, 'w')
with open(orig_file, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    in_header = True
    for row in reader:
        if in_header:
            current_month = row[1][:-3]  # first month in the file
            header_list.append(current_month)
            for i, date in enumerate(row):
                if i == 0:
                    continue  # ignore name
                if i > 1 and int(date[-2:]) < int(row[i-1][-2:]):
                    current_month = date[:-3]
                    header_list.append(current_month)
                month_set[i] = current_month
            header_list.append(current_month)
            in_header = False
            f.write(';'.join(header_list) + "\n")
            continue

        # now aggregate information
        new_row = []
        for i, volume in enumerate(row):
            if i == 0:
                prev_month = header_list[1]
                new_row.append(volume)
                total = 0
                days = 0
                continue  # ignore name
            if month_set[i] == prev_month:
                total += float(volume.replace(',', '.'))
                days += 1

                new_row.append("{0:.2f}".format(round(float(total)/days, 2)))
                total = 0
                days = 0
                prev_month = month_set[i]
        # print 'final date: {}: {} : {}'.format(days, total, prev_month)
        new_row.append("{0:.2f}".format(round(float(total)/days, 2)))
        f.write(';'.join(new_row) + "\n")
f.close()
print header_list
