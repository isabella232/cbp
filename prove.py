#!/usr/bin/env python

import agate
import proof

def load_data(data):
    return data

def main():
    loaded = proof.Analysis(load_data)

    loaded.run()

if __name__ == '__main__':
    main()
