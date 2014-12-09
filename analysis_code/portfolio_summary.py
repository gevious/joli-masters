# Generate output of average monthly return per portfolio per month
# Year1,Year2
# company1, company2
# company2, company1
# Uses the newer set of data
# Nico Gevers 2014
import csv
import os
from operator import itemgetter


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

    def load_data(self, filename, indicator, industries=['*']):
        """Load data from the file into memory. Data is sorted by indicator
           from smallest to largest"""
        # print "Loading data from file"
        data = []
        self.current_month = filename.split('/')[-1][:-4]
        idx = self.ind_map[indicator]
        with open(filename, 'r') as f:
            indicator_reader = csv.reader(f, delimiter=';', quotechar='"')
            for i, row in enumerate(indicator_reader):
                if i == 0:
                    continue
                r = row[0].split(',')

                if '*' not in industries and r[1].lower() not in industries:
                    # skip company if its industry doesn't match
                    continue
                if r[idx] in ['', 0, '0', '#DIV/0!', '#REF!', 'Err:512']:
                    continue  # ignore company with no indicator value
                data.append(r)

        # sort data from lowest to highest by indicator
        self.data = sorted(data, key=itemgetter(idx))

    def get_portfolios(self, portfolio_num, **kwargs):
        """Divides companies into `portfolio_num` portfolios"""
        l = len(self.data) / portfolio_num
        r = len(self.data) % portfolio_num
        nums = [l for i in range(portfolio_num)]
        for i in range(r):
            nums[i] += 1

        p_idx = 0
        portfolios = {}
        total_c = 0
        for i in range(portfolio_num):
            portfolios[i] = []
        for i, d in enumerate(self.data):
            portfolios[p_idx].append(d[0])
            total_c += 1
            if total_c == nums[p_idx]:
                # we have the correct num of companies in this portfolio. NEXT
                p_idx += 1
                total_c = 0
        return portfolios

src_dir = "/home/nico/Code/joli_masters/analysis_code/data_by_date"
rebalance_period = 1  # how many months to test before rebalancing portfolios
industries = ['*']
# industries = ['financials', 'basic materials']

# -- start working
total_months = 0
a = MonthlyAnalysis()
portfolio_num = 5
port_filename = "/tmp/portfolio_summary_{}.csv"
reporting_indicators = ['market value', 'price sales', 'debt equity', 'bv_mv']

# Load the output file and store breakdown per portfolio
portfolios = {}
for rebalance_period in [1, 12, 36, 72]:
    with open(port_filename.format(rebalance_period), 'w') as f:
        # write header
        header = ""
        for i in reporting_indicators:
            for j in range(5):
                header += ";Portfolio {} {}".format(i, j+1)
            header += ';'
        f.write(header + "\n")
        for month_no, filename in enumerate(sorted(os.listdir(src_dir))):
            current_month = filename.split('/')[-1][:-4]
            row_data = ""
            # for indicator in reporting_indicators:
            for indicator in reporting_indicators:
                row_data += "{};".format(current_month)
                a.load_data("{}/{}".format(src_dir, filename), indicator)
                if month_no % rebalance_period == 0:
                    portfolios[indicator] = a.get_portfolios(portfolio_num)

                # get the actual data in a simple array
                final_data = []
                for r in range(portfolio_num):
                    final_data.append(portfolios[indicator][r])

                # produce a mapping of the data of company_name:monthly return
                company_map = \
                    {d[0]: d[a.ind_map['nm monthly return']] for d in a.data}

                # now that we have the map, lets calculate the monthly average
                # for each portfolio and save it to the row
                for portfolio in final_data:
                    c_sum = 0
                    c_count = 0
                    for company in portfolio:
                        if company not in company_map:
                            continue
                        c_count += 1
                        c_sum += float(company_map[company])
                    row_data += "{};".format(float(c_sum) / c_count)
            f.write(row_data + "\n")
