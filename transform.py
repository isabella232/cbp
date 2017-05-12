#!/usr/bin/env python

from collections import OrderedDict

import agate

def get_naics_descriptions():
    text = agate.Text()

    columns = OrderedDict([
        ('naics', text),
        ('description', text)
    ])

    return agate.Table.from_csv('naics_descriptions.csv', columns.keys(), columns.values())

def denormalize(table, value_column, lookup):
    table = table.denormalize('naics', 'year', value_column, default_value=None)
    table = table.join(lookup, 'naics')

    column_names = list(table.column_names)
    column_names.pop()
    column_names.insert(1, 'description')

    return table.select(column_names)

def main():
    text = agate.Text()
    number = agate.Number()

    columns = OrderedDict([
        ('year', text),
        ('naics', text),
        ('emp', number),
        ('est', number)
    ])

    print('Loading')
    table = agate.Table.from_csv('merged.csv', columns.keys(), columns.values())
    table = table.where(lambda r: r['naics'] is not None and len(r['naics']) == 6)
    lookup = get_naics_descriptions()

    print('Mean employees per establishment')
    means = table.compute([
        ('mean', agate.Formula(agate.Number(), lambda r: (r['emp'] / r['est']) if (r['emp'] and r['est']) else None))
    ])
    means = denormalize(means, 'mean', lookup)
    means.to_csv('means.csv')
    means = means.where(lambda r: r['1988'] is not None and r['2013'] is not None)
    means.to_json('src/data/means.json', key='naics')

    print('Denormalizing employees')
    employees = denormalize(table, 'emp', lookup)
    employees.to_csv('emp.csv')
    employees = employees.where(lambda r: r['1988'] is not None and r['2013'] is not None)
    employees.to_json('src/data/employees.json', key='naics')

    print('Denormalizing establishments')
    establishments = denormalize(table, 'est', lookup)
    establishments.to_csv('est.csv')
    establishments = establishments.where(lambda r: r['1988'] is not None and r['2013'] is not None)
    establishments.to_json('src/data/establishments.json', key='naics')

if __name__ == '__main__':
    main()
