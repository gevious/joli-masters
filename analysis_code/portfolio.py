#!/usr/bin/env python
# -*- coding: utf-8 -*-

# How to use this:
# There are 3 variables to change. The first is the period (in months). For the
# current requirement it is set to 1, 12, 36 and 72.
#
# The next variable is the portfolio_num. This is generally set at 5, but can
# be varied.
#
# One can set calc between 'Equally Weighted' and 'Weighted Average'. This
# setting affects only the way the returns column is calculated. All other
# indicators are always calculated on Equally Weighted terms.
#
# The output can be comprised of either all companies, or all excluding
# financials and basic materials
#
#
# OUTPUT:
# The result will be a csv file with all data as per Jolandi's rule. It will
# output results of companies split into `portfolio_num` portfolios based on
# the relevant indicator. All calculations are then done on a portfolio level.

import os
import csv
from operator import itemgetter

start_file = "2001-12.csv"
src_dir = "/home/nico/Code/joli_masters/analysis_code/data_by_date"
# mapping for old data
# indicators = {
#     "BV_MV": 2,
#     # "Beta": 3,
#     "Debt equity ratio": 4,
#     "Excess return": 5,
#     "Market value": 6,
#     "Price sales": 7,
#     "Monthly return": 8
# }
# mapping for latest data
indicators = {
    "BV_MV": 2,
    "Debt equity ratio": 3,
    # "Market value": 4,  # original mv whic we're not using
    "Market value": 5,  # actually LnMV, but thats our data in this case
    "Price sales": 6,
    # "Beta": 7,
    "Excess return": 8,  # next month's return
    "Monthly return": 9  # next month's return
}


def _get_data(filename, all_companies, indicator, sort=False):
    """Get data from file into list of lists, and sort it by the relevant
       indicator (from smallest to largest)"""
    data = []
    idx = indicators[indicator]
    with open("{}/{}".format(src_dir, filename), 'r') as f:
        indicator_reader = csv.reader(f, delimiter=';', quotechar='"')
        for i, row in enumerate(indicator_reader):
            if i == 0:
                continue
            r = row[0].split(',')
            if not all_companies and \
                    r[1].lower() in ['financials', 'basic materials']:
                continue
            if r[idx] in ['', 0, '0', '#DIV/0!', '#REF!', 'Err:512']:
                continue  # ignore company with no indicator value
            data.append(r)

    # sort data from lowest to highest by indicator
    if sort:
        return sorted(data, key=itemgetter(idx))
    return data


def _setup_portfolios(filename, portfolio_num, all_companies, indicator):
    """Populate global `portfolio_idx` dict with company:idx values for the
       existing sorted dataset"""
    print "Generating portfolio index from {}".format(filename)
    data = _get_data(filename, all_companies, indicator, sort=True)
    l = len(data) / portfolio_num
    r = len(data) % portfolio_num
    nums = []
    for i in range(portfolio_num):
        nums.append(l)
    for i in range(r):
        nums[i] += 1
    idx = 0
    portfolio_idx = {}
    for d in data:
        portfolio_idx[d[0]] = idx
        nums[idx] -= 1
        if nums[idx] <= 0:
            idx += 1

    print "  - {} companies in this portfolios selection".format(
        len(portfolio_idx))
    return portfolio_idx


def _get_portfolios(port_idx, filename, portfolio_num, all_companies, indi):
    """Get a list of `portfolio_num` lists, each containing the list of
       companies in the portfolio. Basically just restructuring of data
       from one blob to portfolio lists"""
    print "Sorting data into portfolios: {}".format(filename)

    portfolios = []
    for i in range(portfolio_num):
        portfolios.append([])
    d = _get_data(filename, all_companies, indi)
    skipped = 0
    added = 0
    missed_keys = port_idx.keys()
    for row in d:
        if row[0] in port_idx:
            k = row[0]
            portfolios[port_idx[k]].append(row)
            missed_keys.remove(k)
            added += 1
        else:
            skipped += 1
            # print "Ignoring {}".format(row[0])

    # For weighted average
    # somewhat inefficient, but usable for now. cycle through portfolios to get
    # the total for the indicator. Then go through the portfolios again and
    # save the company weighting to the last element of the row
    #
    # store weights in {portfolio_idx: total}
    portfolio_total_returns = {}
    if weighted_ave:

        for p_idx, p in enumerate(portfolios):
            i = 'Market value'
            if p_idx not in portfolio_total_returns:
                portfolio_total_returns[p_idx] = 0
            # go through companies in portfolio and add up the totals
            for c in p:
                portfolio_total_returns[p_idx] += float(c[indicators[i]])

    # (1month)(
    # printing out portfolio
#    print "COMPANIES:"
#    for p_idx, p in enumerate(portfolios):
#        print " -Portfolio {}".format(p_idx+1)
#        for c in p:
#            print "   {}".format(c[0])

    print "  - Added: {}/{}".format(added, len(port_idx))
    print "  - Skipped: {} (not in initial selection)".format(skipped)
    print "  - Missed: {} (company folded)".format(len(missed_keys))
    print "  - Totals: {},{},{},{},{}".format(
        len(portfolios[0]), len(portfolios[1]), len(portfolios[2]),
        len(portfolios[3]), len(portfolios[4]))
    return portfolios, portfolio_total_returns


def _annualised(data, month_num, weighted=False):
    """Returns annualised data.
         total / (month_num/12)
         = 12 * total / month_num ( for yearly figures)
    """
    if weighted:
        # ignore companies divisor for weighted, since we don't use it
        return float(12 * 12 * data['sum']) / month_num
    return float(12 * 12 * data['sum'] / data['companies']) / month_num


def _get_weighted_average(company, p_idx, ptr):
    return float(company[indicators['Monthly return']]) * \
        float(company[indicators['Market value']]) / \
        ptr[p_idx]


def generate_output(period, portfolio_num, all_companies, weighted_ave):
    output_data = []
    output_filename = "{} ({}) - {}months ({} portfolios).csv".format(
        'weighted average' if weighted_ave else 'equally weighted',
        'all companies' if all_companies else 'fin&materials',
        period, portfolio_num)

    for indicator in indicators.keys():
        # cycle through indicators to use to order companies by in portfolio
        if indicator in ['Excess return', 'Monthly return']:
            continue
        start_analysis = False
        month_num = 0
        total_months = 0

        # stores the results for each portfolio
        # [{<indicator>:{sum: companies:}, ...}, {...}]
        result = []
        for i in range(portfolio_num):
            result.append({})
        for filename in sorted(os.listdir(src_dir)):
            if filename == start_file:
                start_analysis = True
                # load data so we can generate the portfolio
                port_idx = _setup_portfolios(filename, portfolio_num,
                                             all_companies, indicator)
                continue
            if not start_analysis:
                continue

            # get data in portfolio format ( same format as the file)
            # only split by portfolio in memory.
            portfolios, portfolio_total_returns = \
                _get_portfolios(port_idx, filename, portfolio_num,
                                all_companies, indicator)
            for p_num, p in enumerate(portfolios):
                # get the summation of all values and add them to the result
                company_num = 0
                for i, i_idx in indicators.iteritems():
                    v = 0
                    l = len(p)
                    for company in p:
                        t = company[i_idx]
                        if t in [0, 'O', '#DIV/0!', '#REF!', '', 'Err:512']:
                            l -= 1
                        else:
                            if weighted_ave and i in ['Monthly return']:
                                # using weighted average for monthly
                                # returns
                                # Calculate this result as weighted average
                                # v contains the new value, l gets reset to 1

                                # calculation:
                                # (company return * company market value)
                                # ---------------------------------------
                                #       portfolio market value
                                #
                                v += _get_weighted_average(
                                    company, p_num, portfolio_total_returns)
                            else:
                                # average weighted
                                v += float(t)
                    company_num += l
                    if i not in result[p_num]:
                        # first month
                        result[p_num][i] = {'sum': v, 'companies': l}
                    else:
                        # rest of the months
                        result[p_num][i]['sum'] += v
                        result[p_num][i]['companies'] += l
                result[p_num]['ave_companies'] = company_num / len(indicators)

            # reset portfolios
            month_num += 1
            # ---
            total_months += 1
            # (1month)
    #                    if total_months == 2:
    #                        break
            if month_num == period:
                month_num = 0
                port_idx = _setup_portfolios(filename, portfolio_num,
                                             all_companies, indicator)

        # now that we have collated all information, lets print it out nicely
        output_data.append(
            "Indicator order: {}, returns calc: {}, period: {} months".format(
                indicator,
                'weighted ave' if weighted_ave else 'equally weighted',
                period))
        output_data.append(
            "Name;Excess Return;Monthly Return;PSR;D/E;MV;BV/MV;Ave Companies")
        for p_num, r in enumerate(result):
            output_data.append("Portfolio {};{};{};{};{};{};{};{}".format(
                p_num+1,
                _annualised(r['Excess return'], total_months),
                _annualised(r['Monthly return'], total_months, weighted_ave),
                _annualised(r['Price sales'], total_months),
                _annualised(r['Debt equity ratio'], total_months),
                _annualised(r['Market value'], total_months),
                _annualised(r['BV_MV'], total_months),
                r['ave_companies']
            ))
        output_data.append("")

    with open("/tmp/joli/{}".format(output_filename), 'w') as f:
        for o in output_data:
            f.write(o + "\n")

# --- start here
# period = 1
# portfolio_num = 5
# all_companies=True
# weighted_ave = True # False for Equally weighted return
for period in [1, 12, 36, 72]:
    for portfolio_num in [5, 10]:
        for all_companies in [True, False]:
            for weighted_ave in [True, False]:
                generate_output(period, portfolio_num, all_companies,
                                weighted_ave)
