#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

src_dir = '/home/nico/joli_masters/final_transform/by_company_csv'
output_dir = '/home/nico/joli_masters/final_transform/by_indicator'
input_files = []


for file in sorted(os.listdir(src_dir)):
    f = open("{}/{}".format(src_dir, file), 'r')
    company_name = f.name.split('/')[-1][:-4]
    # read 3rd line
    f.readline()
    f.readline()
    line = f.readline()
    industry = line.split(',')[1].strip()

    # seek to the 22nd line
    for i in range(18):
        f.readline()
    input_files.append({'name': company_name, 'industry': industry, 'file': f})

    # go through all files and offload data into the appropriate indicator
for j in range(7):  # read line 22 to 28
    output_file = None
    print "Row {} of 8".format(j+1)
    for i, f in enumerate(input_files):
        row = f['file'].readline().split(',')
        if i == 0:
            output_filename = row[0].replace('/', '_')
            output_file = open("{}/{}.csv".format(
                output_dir, output_filename), 'w+')
            output_file.write('Company,Industry,\n')
            # TODO: add dates

        final_row = [f['name'], f['industry']]
        final_row.extend(row[1:])
        output_file.write("{}".format(','.join(final_row)))
    output_file.close()

for f in input_files:
    f['file'].close()
