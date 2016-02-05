#!/usr/bin/env python

from collections import OrderedDict

import agate
import proof



def load_data(data):
    text = agate.Text()
    number = agate.Number()

    columns = OrderedDict([
        ('naics', text),
        ('lfo', text),
        ('emp', number),
        ('est', number)
    ])

    tables = OrderedDict()

    # SIC codes before 1998
    # NAICS after that

    for year in range(1998, 2013 + 1):
        rows = []

        with open('data/cbp%sus.txt' % str(year)[-2:]) as f:
            reader = agate.DictReader(f)

            for row in reader:
                if year == 2006:
                    rows.append([
                        row['NAICS'],
                        '-',
                        row['EMP'],
                        row['EST']
                    ])
                elif year >= 2008:
                    rows.append([
                        row['naics'],
                        row['lfo'],
                        row['emp'],
                        row['est']
                    ])
                else:
                    rows.append([
                        row['naics'],
                        '-',
                        row['emp'],
                        row['est']
                    ])

        print(year)
        tables[str(year)] = agate.Table(rows, columns.keys(), columns.values())

    data['tables'] = agate.TableSet(tables.values(), tables.keys(), key_name='year')

    return data

def squish(data):
    data['tables'].merge().to_csv('merged.csv')

def main():
    loaded = proof.Analysis(load_data)
    loaded.then(squish)

    loaded.run()

if __name__ == '__main__':
    main()
