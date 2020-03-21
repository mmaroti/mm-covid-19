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
import csv
from datetime import datetime
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


from . import lemurs


class DataItaly(lemurs.Frame):
    def __init__(self, data_path=None):
        super(DataItaly, self).__init__()

        self.data_path = data_path
        if not self.data_path:
            self.data_path = os.path.abspath(os.path.join(
                __file__, '..', '..', 'data', 'italy'))
            if not os.path.exists(self.data_path):
                self.data_path = None

        if not self.data_path:
            raise ValueError(
                'https://github.com/pcm-dpc/COVID-19 data path not found')

        self.file_name = os.path.join(
            self.data_path, 'dati-regioni', 'dpc-covid19-ita-regioni.csv')
        if not os.path.exists(self.file_name):
            raise ValueError('dpc-covid19-ita-regioni.csv data file not found')

        self.add_axis('region', increment=1)
        self.add_axis('date')

        # active and positively tested cases
        self.add_table('active_severe', ['region', 'date'], dtype=int)
        self.add_table('active_critical', ['region', 'date'], dtype=int)
        self.add_table('active_home_conf', ['region', 'date'], dtype=int)

        # closed and cumulative, positively tested cases
        self.add_table('closed_recovered', ['region', 'date'], dtype=int)
        self.add_table('closed_deaths', ['region', 'date'], dtype=int)

        # cumulative total tests performed (positive and negative)
        self.add_table('total_tests', ['region', 'date'], dtype=int)

    def load(self):
        with open(self.file_name, newline='') as file:
            rows = csv.reader(file, dialect='excel')

            count = 0
            for row in rows:
                count += 1
                if count == 1:
                    if len(row) != 16 or row[0] != 'data' \
                            or row[3] != 'denominazione_regione' \
                            or row[6] != 'ricoverati_con_sintomi' \
                            or row[7] != 'terapia_intensiva' \
                            or row[9] != 'isolamento_domiciliare' \
                            or row[12] != 'dimessi_guariti' \
                            or row[13] != 'deceduti' \
                            or row[15] != 'tamponi':
                        raise ValueError('unexpected CSV header')
                    continue

                # we keep only the date, ignore time
                date = datetime.strptime(
                    row[0], "%Y-%m-%d %H:%M:%S").date()
                self['date'].add(date)

                region = row[3]
                self['region'].add(region)

                # entries
                self['active_home_conf'][region, date] = row[9]
                self['active_severe'][region, date] = row[6]
                self['active_critical'][region, date] = row[7]
                self['closed_recovered'][region, date] = row[12]
                self['closed_deaths'][region, date] = row[13]
                self['total_tests'][region, date] = row[14]

        self.trim_data()

    @property
    def dates(self):
        """Returns the list of dates used for all tables."""
        return self['date'].data

    @property
    def regions(self):
        """Returns the list of regions used for all tables."""
        return self['region'].data

    @property
    def active_home_conf(self):
        """Returns the numpy array of confirmed active patients in home
        confinement at the given region and time."""
        return self['active_critical'].data

    @property
    def active_severe(self):
        """Returns the numpy array of confirmed active patients with severe conditions in a hospital at the given region and time."""
        return self['active_severe'].data

    @property
    def active_critical(self):
        """Returns the numpy array of confirmed active patients with critical conditions in a hospital at the given region and time."""
        return self['active_critical'].data

    @property
    def active_cases(self):
        """Returns the numpy array of confirmed active cases at the given region and time."""
        return self.active_home_conf + self.active_severe + self.active_critical

    @property
    def closed_recovered(self):
        """Returns the numpy array of cumulative confirmed and recovered patients at the given region and time."""
        return self['closed_recovered'].data

    @property
    def new_closed_recovered(self):
        """Returns the numpy array of confirmed patients moved to recovered status at the given region and time."""
        return np.diff(self.closed_recovered, axis=1, prepend=0)

    @property
    def closed_deaths(self):
        """Returns the numpy array of cumulative confirmed and deceased patients at the given region and time."""
        return self['closed_deaths'].data

    @property
    def new_closed_deaths(self):
        """Returns the numpy array of confirmed patients died at the given region and time."""
        return np.diff(self.closed_deaths, axis=1, prepend=0)

    @property
    def closed_cases(self):
        """Returns the numpy array of cumulative confirmed closed cases at the given region and time."""
        return self.closed_recovered + self.closed_deaths

    @property
    def new_closed_cases(self):
        """Returns the numpy array of closed confirmed cases at the given region on the given time."""
        return np.diff(self.closed_cases, axis=1, prepend=0)

    @property
    def new_active_cases(self):
        """Returns the numpy array of new confirmed active cases at the given region on the given time."""
        return np.diff(self.active_cases, axis=1, prepend=0) + self.new_closed_cases

    @property
    def total_tests(self):
        """Returns the cumulative total tests performed at the given region and time."""
        return self['total_tests'].data

    @property
    def current_tests(self):
        """Returns the number of tests performed at the given region on the given day."""
        return np.diff(self.total_tests, axis=1, prepend=0)

    def plot_closed(self):
        _fig, (ax1, ax2) = plt.subplots(1, 2)

        for idx in range(len(self.regions)):
            ax1.plot(self.closed_recovered[idx, :], label=self.regions[idx])
            ax2.plot(self.closed_deaths[idx, :], label=self.regions[idx])

        ax1.legend()
        ax1.set_xlabel("days")
        ax1.set_ylabel("cases")
        ax1.set_title("cumulative recovered cases")

        ax2.legend()
        ax2.set_xlabel("days")
        ax2.set_ylabel("cases")
        ax2.set_title("cumulative deaths")

        plt.show()

    def plot_new(self):
        _fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True)

        for idx in range(len(self.regions)):
            ax1.plot(self.new_active_cases[idx, :], label=self.regions[idx])
            ax2.plot(self.new_closed_cases[idx, :], label=self.regions[idx])

        ax1.legend()
        ax1.set_xlabel("days")
        ax1.set_ylabel("cases")
        ax1.set_title("new active cases")

        ax2.legend()
        ax2.set_xlabel("days")
        ax2.set_ylabel("cases")
        ax2.set_title("new closed cases")

        plt.show()


def run(args=None):
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--data-path', default=None, metavar='DIR', type=str,
                        help="path of the downloaded "
                        "https://github.com/pcm-dpc/COVID-19.git repository")
    parser.add_argument('--plot-closed', action='store_true',
                        help="plot confirmed closed recovered and death cases")
    parser.add_argument('--plot-new', action='store_true',
                        help="plot confirmed new active and closed cases")
    args = parser.parse_args(args)

    italy = DataItaly(args.data_path)
    italy.load()

    print("Loaded", italy.file_name)
    print(italy.info())
    print("Start date {}, end date {}".format(italy.dates[0], italy.dates[-1]))

    if args.plot_closed:
        italy.plot_closed()
    if args.plot_new:
        italy.plot_new()


if __name__ == '__main__':
    run()