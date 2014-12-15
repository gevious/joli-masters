# Generate output for analysis along with intermediary data for checks
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

    def load_data(self, filename, indicator, industries):
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
                new_row = []
                for z in r:
                    try:
                        new_row.append(float(z))
                    except ValueError:
                        new_row.append(z)

                data.append(new_row)

        # sort data from lowest to highest by indicator
        self.data = sorted(data, key=itemgetter(idx))

    def _get_company_value(self, data, indicator):
        v = data[self.ind_map[indicator]]
        if v in ['', 0, '0', '#DIV/0!', '#REF!', 'Err:512']:
            return 0
        return v

    def allocate_companies(self, portfolio_num, **kwargs):
        """Divides companies into `portfolio_num` portfolios"""
        l = len(self.data) / portfolio_num
        r = len(self.data) % portfolio_num
        nums = [l for i in range(portfolio_num)]
        for i in range(r):
            nums[i] += 1

        # now that we have the number of companies for each portfolio
        # we allocate the companies to each portfolio
        # portfolios looks like this:
        # portfolios = [{'name': <company name>, 'mr': <monthly return>
        #                   'er': <excess return>, 'weight': <weight of mr>}]
        #
        p_idx = 0
        portfolios = {}
        for i in range(portfolio_num):
            portfolios[i] = {'companies': []}
            for k in ['mr', 'mv', 'er', 'psr', 'de', 'mv', 'bv_mv', 'c']:
                portfolios[i]['total '+k] = 0
        for i, d in enumerate(self.data):
            portfolios[p_idx]['companies'].append({
                'name': d[0], 'mr': d[self.ind_map['nm monthly return']],
                'er': d[self.ind_map['nm excess return']],
                'psr': d[self.ind_map['price sales']],
                'mv': d[self.ind_map['market value']], 'weight': 1
            })
            portfolios[p_idx]['total c'] += 1
            portfolios[p_idx]['total mr'] += \
                self._get_company_value(d, 'nm monthly return')
            portfolios[p_idx]['total er'] += \
                self._get_company_value(d, 'nm excess return')
            portfolios[p_idx]['total mv'] += \
                self._get_company_value(d, 'market value')
            portfolios[p_idx]['total psr'] += \
                self._get_company_value(d, 'price sales')
            portfolios[p_idx]['total de'] += \
                self._get_company_value(d, 'debt equity')
            portfolios[p_idx]['total bv_mv'] += \
                self._get_company_value(d, 'bv_mv')
            if portfolios[p_idx]['total c'] == nums[p_idx]:
                # we have the correct num of companies in this portfolio. NEXT
                p_idx += 1

        # add the company weighting into the structure in case we need it
        for i, p in portfolios.iteritems():
            for c in p['companies']:
                c['weight'] = float(c['mv']) / p['total mv']

        if 'output' in kwargs:
            for i in range(portfolio_num):
                with open("/tmp/joli/{}-P{}.txt".format(
                        self.current_month, i+1), 'w') as f:
                    h = "Total companies; {};;Total return;{};;Total MV:{}\n"
                    f.write(h.format(
                        portfolios[i]['total c'], portfolios[i]['total mr'],
                        portfolios[i]['total mv']))
                    h = "Company;Monthly Return;Expected Return;"
                    h += "Market Value;Weight;PSR\n"
                    f.write(h)
                    for d in portfolios[i]['companies']:
                        f.write("{};{};{};{};{};{}\n".format(
                            d['name'], d['mr'], d['er'], d['mv'], d['weight'],
                            d['psr']))

        self.portfolios = portfolios
        return portfolios

    def sort_data(self):
        """produce self.sorted_data which is the data organised by portfolio
           so we can get the results"""
        self.sorted_data = {}
        for p_num in self.portfolios.keys():
            self.sorted_data[p_num] = []
            for c in self.portfolios[p_num]['companies']:
                for d in self.data:
                    if d[0] == c['name']:
                        x = {
                            'name': d[0],
                            'mr': d[self.ind_map['nm monthly return']],
                            'er': d[self.ind_map['nm excess return']],
                            'psr': d[self.ind_map['price sales']],
                            'de': d[self.ind_map['debt equity']],
                            'bv_mv': d[self.ind_map['bv_mv']],
                            'mv': d[self.ind_map['market value']],
                            'weight': c['weight']
                        }
                        self.sorted_data[p_num].append(x)
                        break

    def get_portfolios(self):
        return self.portfolios

    def monthly_return(self, portfolio_no):
        p = self.sorted_data[portfolio_no]
        total = 0
        for c in p:
            total += c['mr']
        # print "Sum: {}".format(total)
        return total / len(p)

    def monthly_return_wa(self, portfolio_no):
        p = self.sorted_data[portfolio_no]
        total = 0
        for c in p:
            total += c['mr'] * c['weight']
        return total

    def excess_return(self, portfolio_no):
        p = self.sorted_data[portfolio_no]
        total = 0
        for c in p:
            total += c['er']
        return total / len(p)

    def price_sales(self, portfolio_no):
        """Gets the cumulative psr """
        p = self.sorted_data[portfolio_no]
        total = 0
        for c in p:
            total += c['psr']
        return total / len(p)

    def debt_equity(self, portfolio_no):
        p = self.sorted_data[portfolio_no]
        total = 0
        for c in p:
            total += c['de']
        return total / len(p)

    def market_value(self, portfolio_no):
        p = self.sorted_data[portfolio_no]
        total = 0
        for c in p:
            total += c['mv']
        return total / len(p)

    def book_value_mv(self, portfolio_no):
        p = self.sorted_data[portfolio_no]
        total = 0
        for c in p:
            total += c['bv_mv']
        return total / len(p)

    def total_c_num(self, portfolio_no):
        p = self.sorted_data[portfolio_no]
        return len(p)


src_dir = "/home/nico/Code/joli_masters/analysis_code/data_by_date"


def annualised(total, month_num):
    return 12 * total / month_num


def print_output(totals, indicator, rebalance_period, month_no,
                 industries, pn):
    t = "Indicator order: {}, period: {} months\n".format(
        indicator, rebalance_period)
    t += "Name;Monthly return (WA);Monthly return;Excess Return;PSR;" \
         "D/E;MV;BV/MV;Ave Companies\n"
    for k, v in totals.iteritems():
        t += "Portfolio {};{};{};{};{};{};{};{};{}\n".format(
            k+1,
            annualised(v['mr_wa'], month_no),
            annualised(v['mr'], month_no),
            annualised(v['er'], month_no),
            annualised(v['psr'], month_no)/12,
            annualised(v['de'], month_no)/12,
            annualised(v['mv'], month_no)/12,
            annualised(v['bv_mv'], month_no)/12,
            int(round(float(v['total_co']) / month_no))
        )
    t += "\n"
    return t

month_break = 1  # run analysis for x months. if x == 0, then run for all
a = MonthlyAnalysis()
# ignore_2008_9 = False
# rebalance_period = 1  # how many months to test before rebalancing portfolios
# industries = ['*']
# industries = ['financials', 'basic materials']

for rebalance_period in [1, 12, 36, 72]:
    for industries in [['*'], ['financials', 'basic materials']]:
        for ignore_2008_9 in [True, False]:
            summary_output = []
            for portfolio_num in [5]:
                for indicator in ['price sales', 'bv_mv',
                                  'debt equity', 'market value']:
                    totals = {}
                    # reset totals to 0 at the beginning of this operation
                    for i in range(portfolio_num):
                        totals[i] = {}
                        for k in ['mr', 'mr_wa', 'er', 'psr', 'de',
                                  'mv', 'bv_mv', 'total_co']:
                            totals[i][k] = 0
                    for month_no, filename in enumerate(
                            sorted(os.listdir(src_dir))):
                        if ignore_2008_9:
                            if filename.find('2008') > -1 or \
                                    filename.find('2009') > -1:
                                continue
                        a.load_data("{}/{}".format(src_dir, filename),
                                    indicator, industries)
                        if month_no % rebalance_period == 0:
                            a.allocate_companies(portfolio_num, output=True)
                        a.sort_data()
                        print a.sorted_data[0]
                        print len(a.sorted_data[0])
                        for p in range(portfolio_num):
                            totals[p]['mr_wa'] += a.monthly_return_wa(p)
                            totals[p]['mr'] += a.monthly_return(p)
                            totals[p]['er'] += a.excess_return(p)
                            totals[p]['psr'] += a.price_sales(p)
                            totals[p]['de'] += a.debt_equity(p)
                            totals[p]['mv'] += a.market_value(p)
                            totals[p]['bv_mv'] += a.book_value_mv(p)
                            totals[p]['total_co'] += a.total_c_num(p)
                        if month_break > 0 and (month_no + 1) == month_break:
                            break

                    summary_output.append(
                        print_output(totals, indicator, rebalance_period,
                                     month_no, industries, portfolio_num))

                filename = "/tmp/results/{}month_{}{}.csv".format(
                    rebalance_period, 'all' if industries == ['*'] else 'fb',
                    '_excl89' if ignore_2008_9 else '')
                with open(filename, 'w') as f:
                    for s in summary_output:
                        f.write(s)
