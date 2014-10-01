#!/usr/bin/env python
# Transforms bloomberg from dates vs companies to company vs dates

import csv

header_list = []
name_map = {}
year_map = {}
run_active = True
orig_file = '/tmp/bloomberg.csv'
output_file = '/tmp/bloomberg_final.csv'

with open(orig_file, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        if header_list == []:
            header_list = row
            continue
        for i, details in enumerate(row):
            if i % 2 == 0:

                # company code
                if details in year_map:
                    year_map[details].append(header_list[i])
                else:
                    year_map[details] = [header_list[i]]
            else:
                # company name
                code = row[i-1]
                if code not in name_map:
                    name_map[code] = details

keys = name_map.keys()
keys.sort()
f = open(output_file, 'w')
for k in keys:
    if k.strip() == '':
        continue
    year_map[k].sort()
    gap = int(year_map[k][0]) - 2001
    gap = ','*gap
#    print gap
    txt = "{},{},{}{}\n".format(k, name_map[k], gap, ','.join(year_map[k]))
    f.write(txt)
f.close()
