#!/usr/bin/env python
# -*- coding: utf-8 -*-
# collate regression information from file per month to file per model

from time import strptime, strftime
import os

src_dir = '/home/nico/Code/joli_masters/regression_transform/Regr eviews'
#  src_dir = \
#    '/home/nico/Code/joli_masters/regression_transform/Regr eviews lss bf'

models = {
    'A': [15, 16, 17, 18, 19, 6],
    'B': [24, 25, 26, 27, 7],
    'C': [33, 34, 35, 36, 8],
    'D': [42, 43, 44, 45, 9],
    'E': [51, 52, 53, 54, 10],
}


def header(model):
    fields = ['Coefficient', 'Std error', 'tstat', 'probability']
    txt = ''
    for k in ['C', 'BVMV', 'DE', 'LNMV', 'PSR']:
        if model == 'B' and k == 'PSR':
            continue
        if model == 'C' and k == 'LNMV':
            continue
        if model == 'D' and k == 'DE':
            continue
        if model == 'E' and k == 'BVMV':
            continue
        txt += "Model {} - {};".format(model, k)
        txt += ';'.join(fields) + ";"
    txt += "Model {};".format(model)
    txt += ';'.join(['R squared', 'R sq_adf', 'SE', 'OBS', 'DW']) + ";"
    return txt

for model in models.keys():
    fo = open('/tmp/model_{}.csv'.format(model), 'w')
    fo.write("{}\n".format(header(model)))
    for filename in sorted(os.listdir(src_dir)):
        with open("{}/{}".format(src_dir, filename), 'r') as f:
            data = []
            for line in f:
                data.append(line.strip())

            d = strftime('%b-%y', strptime(data[1], '%Y-%m'))

            txt = ''
            for row in models[model]:
                rd = filter(lambda x: x.strip() != '', data[row].split(' '))
                txt += "{};{};".format(d, ';'.join(rd[1:]))
            fo.write("{}\n".format(txt))
    fo.close()
