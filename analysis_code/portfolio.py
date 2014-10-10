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
# Todo: build another indicator to select a limited company set by industry.
#
#
# OUTPUT:
# The result will be a csv file with all data as per Jolandi's rule. It will
# output results of companies split into `portfolio_num` portfolios based on
# the relevant indicator. All calculations are then done on a portfolio level.

import os
import csv
from operator import itemgetter

period = 72
portfolio_num = 10
calc = "Equally Weighted"
# calc = "Weighted Average"  # TODO
start_file = "2001-12.csv"
src_dir = "/home/nico/Code/joli_masters/analysis_code/data_by_date"
indicators = {
    "BV_MV": 2,
    # "Beta": 3,
    "Debt equity ratio": 4,
    "Excess return": 5,
    "Market value": 6,
    "Price sales": 7,
    "Monthly return": 8
}
output_filename = "{} - {}months ({} portfolios).csv".format(
    calc, period, portfolio_num)
output_data = []


def _get_data(filename, sort=False):
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
            if r[idx] in ['', 0, '0', '#DIV/0!', '#REF!']:
                continue  # ignore company with no indicator value
            data.append(r)

    # sort data from lowest to highest by indicator
    if sort:
        return sorted(data, key=itemgetter(idx))
    return data


def _setup_portfolios(filename):
    """Populate global `portfolio_idx` dict with company:idx values for the
       existing sorted dataset"""
    print "Generating portfolio index from {}".format(filename)
    data = _get_data(filename, sort=True)
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


def _get_portfolios(port_idx, filename):
    """Get a list of `portfolio_num` lists, each containing the list of
       companies in the portfolio. Basically just restructuring of data
       from one blob to portfolio lists"""
    print "Sorting data into portfolios: {}".format(filename)

    portfolios = []
    for i in range(portfolio_num):
        portfolios.append([])
    d = _get_data(filename)
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

    print "  - Added: {}/{}".format(added, len(port_idx))
    print "  - Skipped: {} (not in initial selection)".format(skipped)
    print "  - Missed: {} (company folded)".format(len(missed_keys))
    print "  - Totals: {},{},{},{},{}".format(
        len(portfolios[0]), len(portfolios[1]), len(portfolios[2]),
        len(portfolios[3]), len(portfolios[4]))
    return portfolios


def _annualised(data, month_num):
    """Returns annualised data.
         total / (month_num/12)
         = 12 * total / month_num ( for yearly figures)
    """
    return float(12 * 12 * data['sum'] / data['companies']) / month_num


for indicator in indicators.keys():
    # cycle through indicators which to use to order companies by in portfolio
    if indicator in ['Excess return', 'Monthly return']:
        continue
    start_analysis = False
    month_num = 0
    total_months = 0
    portfolio = {}

    result = []  # stores the results for each portfolio
    for i in range(portfolio_num):
        result.append({})
    for filename in sorted(os.listdir(src_dir)):
        if filename == start_file:
            start_analysis = True
            # load data so we can generate the portfolio
            port_idx = _setup_portfolios(filename)
            continue
        if not start_analysis:
            continue

        # get data in portfolio format
        portfolios = _get_portfolios(port_idx, filename)
        for p_num, p in enumerate(portfolios):
            # get the summation of all values and add them to the result
            company_num = 0
            for i, i_idx in indicators.iteritems():
                v = 0
                l = len(p)
                for company in p:
                    t = company[i_idx]
                    if t in [0, 'O', '#DIV/0!', '#REF!', '']:
                        l -= 1
                    else:
                        v += float(t)
                company_num += l
                if calc == 'Weighted Average' \
                        and i in ['Excess returns', 'Monthly returns']:
                    # Calculate this result as weighted average
                    pass
                else:
                    # Using Equally Weighted calculation
                    if i not in result[p_num]:
                        result[p_num][i] = {'sum': v, 'companies': l}
                    else:
                        result[p_num][i]['sum'] += v
                        result[p_num][i]['companies'] += l
            result[p_num]['ave_companies'] = company_num / len(indicators)

        # reset portfolios
        month_num += 1
        total_months += 1
        if month_num == period:
            month_num = 0
            port_idx = _setup_portfolios(filename)

    # now that we have collated all information, lets print it out nicely
    output_data.append(
        "Indicator order: {}, returns calc: {}, period: {} months".format(
            indicator, calc, period))
    output_data.append(
        "Name;Excess Return;Monthly Return;PSR;D/E;MV;BV/MV;Ave Companies")
    for p_num, r in enumerate(result):
        output_data.append("Portfolio {};{};{};{};{};{};{};{}".format(
            p_num+1,
            _annualised(r['Excess return'], total_months),
            _annualised(r['Monthly return'], total_months),
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
