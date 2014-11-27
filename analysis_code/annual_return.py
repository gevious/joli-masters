# Gives the annual return per company along with beginning of year indicators
# The results are all stored in one file
# Nico Gevers 2014
import csv
import os

src_dir = "/home/nico/Code/joli_masters/analysis_code/data_by_date"
output = "/tmp/output.csv"

os.unlink(output)


def save_year(year, data):
    """Write data of year to file"""
    with open(output, 'a') as o:
        o.write(year + "\n")
        for k in sorted(data.keys()):
            data[k][8] = str(data[k][8])
            data[k][9] = str(data[k][9])
            o.write("{}\n".format(":".join(data[k])))
        o.write("\n")


year = "2001"
data = {}
for month_no, filename in enumerate(sorted(os.listdir(src_dir))):
    if filename[:4] != year:
        # new year
        if month_no > 0:
            save_year(year, data)
        year = filename[:4]
        data = {}
        new_year = True

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
    new_year = False

save_year(year, data)
