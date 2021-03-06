#!/usr/bin/env python3
# Copyright (C) 2020, Miklos Maroti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import sys

from . import data_italy
from . import data_population
from . import seir_simple
from . import seir_simple2
from . import seir_test


def run():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'command', choices=['data-italy', 'data-population', 'seir-test',
                            'seir-simple', 'seir-simple2'],
        help="subcommand to execute")

    args = parser.parse_args(sys.argv[1:2])

    # hack the program name for subcommand
    sys.argv[0] += ' ' + args.command

    if args.command == 'data-italy':
        data_italy.run(sys.argv[2:])
    elif args.command == 'data-population':
        data_population.run(sys.argv[2:])
    elif args.command == 'seir-simple':
        seir_simple.run(sys.argv[2:])
    elif args.command == 'seir-simple2':
        seir_simple2.run(sys.argv[2:])
    elif args.command == 'seir-test':
        seir_test.run(sys.argv[2:])


if __name__ == '__main__':
    run()
