#!/usr/bin/env python

from collections import OrderedDict

import agate
from bidict import bidict

def get_sic_crosswalk():
    """
    We only want to crosswalk codes that were neither split nor merged. They
    must be one-to-one mappings.
    """
    walk = bidict()
    ignore_sic = []
    ignore_naics = []

    with open('data/2002_NAICS_to_1987_SIC.csv') as f:
        reader = agate.DictReader(f)

        for row in reader:
            try:
                sic = str(int(float(row['SIC'])))
                naics = str(int(float(row['2002 NAICS'])))
            except ValueError:
                continue

            print(sic, naics)

            if sic in ignore_sic:
                continue
            elif naics in ignore_naics:
                continue
            elif sic in walk or naics in walk.inv:
                walk.pop(sic, None)
                walk.inv.pop(naics, None)

                ignore_sic.append(sic)
                ignore_naics.append(naics)

                continue
            else:
                walk[sic] = naics

    return walk

def main():
    sic_walk = get_sic_crosswalk()

    text = agate.Text()
    number = agate.Number()

    columns = OrderedDict([
        ('naics', text),
        ('emp', number),
        ('est', number)
    ])

    tables = OrderedDict()

    # SIC codes before 1998
    for year in range(1986, 1998):
        rows = []

        with open('data/cbp%sus.txt' % str(year)[-2:]) as f:
            reader = agate.DictReader(f)

            for row in reader:
                try:
                    naics = sic_walk[row['sic']]
                except KeyError:
                    continue

                rows.append([
                    naics,
                    row['emp'],
                    row['est']
                ])

        table = agate.Table(rows, columns.keys(), columns.values())

        print(year)
        tables[str(year)] = table

    # NAICS years
    for year in range(1998, 2013 + 1):
        rows = []

        with open('data/cbp%sus.txt' % str(year)[-2:]) as f:
            reader = agate.DictReader(f)

            for row in reader:
                # Recent data has rows for each organization type
                if year >= 2008:
                    # Only include "all establishments" rows
                    if row['lfo'] != '-':
                        continue

                if year == 2006:
                    naics = row['NAICS']
                    emp = row['EMP']
                    est = row['EST']
                    empflag = row['EMPFLAG']
                else:
                    naics = row['naics']
                    emp = row['emp']
                    est = row['est']
                    empflag = row['empflag']

                # Suppressed data is 0 by default. Replace with None.
                if empflag:
                    emp = None

                rows.append([
                    naics,
                    emp,
                    est
                ])

        table = agate.Table(rows, columns.keys(), columns.values())

        clean_table = table.compute([
            ('clean_naics', agate.Formula(text, lambda r: r['naics'].strip('-/')))
        ]).select(['clean_naics', 'emp', 'est']).rename({ 'clean_naics': 'naics'})

        print(year)
        tables[str(year)] = clean_table

    tables = agate.TableSet(tables.values(), tables.keys(), key_name='year')

    tables.merge().to_csv('merged.csv')

if __name__ == '__main__':
    main()
