#!/usr/bin/env python
# Take directory of spreadsheets with the category name and rows of companies
# and output a spreadsheet per company, each with the category data in it
import os


class DataTransformer():
    src_dir = "/home/nico/joli_masters/new_data/by_category"
    dest_dir = "/home/nico/joli_masters/new_data/by_company"
    delimiter = ';'
    output_files = []

    def __init__(self, *args, **kwargs):
        # create a file in destdir for each company
        is_first = True
        for file in os.listdir(self.src_dir):
            f = open("{}/{}".format(self.src_dir, file), 'r')
            header = f.readline()
            if is_first:
                self.create_output_files(f.readlines())
                self.load_header(header)
                f.seek(0)
                f.readline()
                is_first = False

            # add category data to each company file
            category_name = file.split('.')[0]
            for row, company in zip(f.readlines(), self.output_files):
                row = row.split(self.delimiter)
                row[0] = category_name
                cf = open(company, 'a')
                cf.write(self.delimiter.join(row))
                cf.close()
            f.close()

    def get_company(self, txt):
        return txt.split(self.delimiter)[0].lower().strip() \
                  .replace(' ', '_').replace('.', '')

    def load_header(self, header):
        for of in self.output_files:
            f = open(of, 'w')
            f.write(header)
            f.close()

    def create_output_files(self, rows):
        for r in rows:
            filename = self.get_company(r) + '.csv'
            self.output_files.append("{}/{}".format(self.dest_dir, filename))
            open("{}/{}".format(self.dest_dir, filename), 'w').close()

DataTransformer()
