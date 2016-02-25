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

    table = table.select(column_names)
    table.to_csv('%s.csv' % value_column)

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
    lookup = get_naics_descriptions()

    print('Denormalizing employees')
    denormalize(table, 'emp', lookup)

    print('Denormalizing establishments')
    denormalize(table, 'est', lookup)


if __name__ == '__main__':
    main()
