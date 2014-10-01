#!/usr/bin/env python
# Transforms bloomberg from dates vs companies to company vs dates

import csv

header_list = []
name_map = {}
run_active = True
orig_file = '/tmp/bloomberg.csv'
output_file = '/tmp/bloomberg_final.csv'

with open(orig_file, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    for row in reader:
        if header_list == []:
            header_list = row
            continue
        for i, filename in enumerate(row):
            if filename in name_map:
                name_map[filename].append(header_list[i])
            else:
                name_map[filename] = [header_list[i]]

keys = name_map.keys()
keys.sort()
f = open(output_file, 'w')
for k in keys:
    if k.strip() == '':
        continue
    txt = "{},{}\n".format(k, ','.join(name_map[k]))
    f.write(txt)
f.close()
