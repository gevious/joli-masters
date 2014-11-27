# Generate portfolios breakdown for each year
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
rebalance_period = 12  # how many months to test before rebalancing portfolios
industries = ['*']
# industries = ['financials', 'basic materials']

# -- start working
total_months = 0
a = MonthlyAnalysis()
portfolio_num = 5
port_filename = "/tmp/portfolio_{}.csv"
# load portfolio breakdown into memory then write to file at the end
for indicator in ['market value']:
    portfolios = []  # [(year-month, [[portfolio1], [portfolio2]])]
    for month_no, filename in enumerate(sorted(os.listdir(src_dir))):
        current_month = filename.split('/')[-1][:-4]
        a.load_data("{}/{}".format(src_dir, filename), indicator)
        if month_no % rebalance_period == 0:
            portfolios.append((current_month, a.get_portfolios(portfolio_num)))

    # sort portfolios by keys
    with open(port_filename.format(indicator.replace(' ', '_')), 'w') as f:
        # write header
        f.write("{}".format(';'.join([t[0] for t in portfolios])))

        # get the actual data in a simple array
        final_data = []
        for p in portfolios:
            final_data.append(p[1])
        # final_data is now in the following format
        # [<month names>[<portfolios>[<company names>]]]
        #
        # now that we have just the data, we want to transpose it into the
        # following format
        # [<portfolios>[<month names>[<company names>]]]

        # get max company num for each portfolio so we can format the rows
        # nicely
        max_companies = [0 for i in range(portfolio_num)]
        for m in final_data:
            for r in range(portfolio_num):
                max_companies[r] = max(max_companies[r], len(m[r]))
        for portfolio_no in range(portfolio_num):
            row_data = []
            f.write("\nPortfolio {}\n".format(portfolio_no + 1))
            # get nth company from each month
            for company in range(max_companies[portfolio_no]):
                row = []
                for month in range(len(portfolios)):
                    x = final_data[month][portfolio_no]
                    if company >= len(x):
                        row.append("")
                    else:
                        row.append(x[company])
                f.write("{}\n".format(";".join(row)))
