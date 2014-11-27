# Take data and truncate indicator values to remove outliers
# Nico Gevers 2014
import csv
import os


class MonthlyAnalysis():

    # mapping of indicator to colum in the data file
    ind_map = {
        "bv_mv": 2,
        "debt equity": 3,
        "market value": 4,
        "lnmv": 5,  # Ln of market value
        "price sales": 6,
        "beta": 7,
        "nm excess return": 8,  # Next month's excess return
        "nm monthly return": 9  # Next month's monthly return
    }
    data = []

    def load_data(self, filename):
        """Load data from the file into memory. Data is sorted by indicator
           from smallest to largest"""
        # print "Loading data from file"
        data = []
        self.current_month = filename.split('/')[-1][:-4]

        return data

src_dir = "/home/nico/Code/joli_masters/analysis_code/data_by_date_pre_trunc"
out_dir = "/home/nico/Code/joli_masters/analysis_code/data_by_date"

# -- start working
a = MonthlyAnalysis()

trunc_values = {
    "bv_mv": (0, 20.6825),
    "debt equity": (0.000358, 23.97034),
    "price sales": (0, 230.1063),
}
for month_no, filename in enumerate(sorted(os.listdir(src_dir))):
    data = []
    header = ''
    # load data
    with open("{}/{}".format(src_dir, filename), 'r') as f:
        indicator_reader = csv.reader(f, delimiter=';', quotechar='"')
        for i, row in enumerate(indicator_reader):
            if i == 0:
                header = row
                continue
            r = row[0].split(',')
            data.append(r)

    # trunc data
    for d in data:
        for i in trunc_values.keys():
            if d[a.ind_map[i]] in ['', 0, '0', '#DIV/0!', '#REF!', 'Err:512']:
                continue
            v1 = float(d[a.ind_map[i]])
            v = max(trunc_values[i][0], v1)
            v = min(trunc_values[i][1], v)
            if v1 != v:  # to avoid floating point changes
                d[a.ind_map[i]] = str(v)

    # write data
    with open("{}/{}".format(out_dir, filename), 'w') as f:
        f.write("{}\n".format(",".join(header)))
        for d in data:
            f.write("{}\n".format(",".join(d)))
