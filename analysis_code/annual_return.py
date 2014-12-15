# Gives the annual return per company along with beginning of year indicators
# The results are all stored in one file
# Nico Gevers 2014
import csv
import os

src_dir = "/home/nico/Code/joli_masters/analysis_code/data_by_date"
output = "/tmp/output.csv"

try:
    os.unlink(output)
except OSError:
    pass


def save_year(year, data):
    """Write data of year to file"""
    with open(output, 'a') as o:
        o.write(year + "\n")
        # headers
        o.write("Company name;Industry;BV_MV;DE;MV;LnMV;PSR;Beta;")
        o.write("Excess Return;Monthly Return\n")
        for k in sorted(data.keys()):
            data[k][8] = str(data[k][8])
            data[k][9] = str(data[k][9])
            o.write("{}\n".format(";".join(data[k])))
        o.write("\n")


year = "2002"
data = {}
year_sum = 1  # how many years to sum together
year_count = 0
for month_no, filename in enumerate(sorted(os.listdir(src_dir))):
    if filename[:4] != year:
        year_count += 1
        # new year
        if year_count >= year_sum:
            save_year(year, data)
            year_count = 0
        year = filename[:4]
        data = {}

    with open("{}/{}".format(src_dir, filename), 'r') as f:
        indicator_reader = csv.reader(f, delimiter=',', quotechar='"')
        for i, row in enumerate(indicator_reader):
            if row[0].lower().strip() == 'company name':
                continue
            if row[0] not in data:
                data[row[0]] = row
                data[row[0]][8] = float(data[row[0]][8])
                data[row[0]][9] = float(data[row[0]][9])
            else:
                # sum excess return; sum monthly return
                data[row[0]][8] += float(row[8])
                data[row[0]][9] += float(row[9])

save_year(year, data)
