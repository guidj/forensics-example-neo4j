import random
import os
import json
import csv

from forensics.utils import config


def prep_flight_sample():

    rgbcolor = lambda: random.randint(0, 255)
    color = lambda: '#%02X%02X%02X' % (rgbcolor(), rgbcolor(), rgbcolor())

    countries = []

    with open(os.path.join(config.PROJECT_BASE, 'data/locations.json'), encoding='latin-1') as fp:

        entries = json.load(fp)

        for entry in entries:

            tokens = entry.split(',')
            _, country = tokens[0], ''.join(tokens[1:])

            countries.append(country.strip())

    countries = set(random.sample(countries, 12))

    with open(os.path.join(config.PROJECT_BASE, 'src/html/countries.csv'), 'w', encoding='latin-1') as fp:

        writer = csv.writer(fp)
        writer.writerow(['name', 'color'])

        for country in countries:
            writer.writerow([country, color()])

    with open(os.path.join(config.PROJECT_BASE, 'src/html/matrix.json'), 'w', encoding='utf-8') as fp:

        all_flights_count = []

        for departure in countries:

            flight_count = []

            for destination in countries:

                flight_count.append(random.randint(1, 200))

            all_flights_count.append(flight_count)

        json.dump(all_flights_count, fp, indent=1)


def prep_call_sample():

    months = ['January', 'February', 'March', 'April']
    weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    periods = ['Morning', 'Afternoon', 'Night']

    data = {
        'name': 'Calls',
        'children': [

            {
                'name': month,
                'children': [
                    {
                        'name': weekday,
                        'children': [
                            {
                                'name': period,
                                'size': random.randint(0, 500)
                            } for period in periods
                            ]
                    } for weekday in weekdays

                    ]
            } for month in months

        ]
    }

    with open(os.path.join(config.PROJECT_BASE, 'src/html/calls.json'), 'w') as fp:

        json.dump(data, fp, indent=3)


if __name__ == '__main__':

    # flight sample data
    prep_flight_sample()

    # call sample data
    prep_call_sample()
