import datetime
import json
import os
import os.path
import random
import uuid

from faker import Factory

from forensics.entities import Person, Employment, PhoneCall, Flight
from forensics.utils import config, neo4j

fake = Factory.create()

N = {
    'people': 10**3,
    'calls': 10**4,
    'flights': 10**4,
    'employment': int((10**3)*.88)
}

# generate timestamp within a year
timestamp = lambda: datetime.datetime(2014, 12, 31, 11, 59, 59) - datetime.timedelta(
    hours=random.randint(0, (365+1)*24)
)

INDEXES = [
    'CREATE INDEX ON :`Person`(id);',
    'CREATE INDEX ON :`Person`(name);',
    'CREATE INDEX ON :`Person`(sex);',
    'CREATE INDEX ON :`PhoneNumber`(number);',
    'CREATE INDEX ON :`Country`(name);',
    'CREATE INDEX ON :`City`(name);',
    'CREATE INDEX ON :`Flight`(number);',
    'CREATE INDEX ON :`Company`(name);'
]


def timestamp_in_weekday(weekday):

    tmstp = timestamp()

    while tmstp.weekday() != weekday:
        tmstp = timestamp()

    return tmstp


def generate_data():

    # people

    people = [
        Person(
            id=str(uuid.uuid4()),
            name=profile['name'],
            sex=profile['sex'],
            number=fake.phone_number()
        ) for profile in [fake.simple_profile() for _ in range(0, N['people'])]
    ]

    # other random folk
    random_folk = random.sample(people, 2)

    # companies
    companies = [
        fake.company() for _ in range(0, (10**2)*2)
    ]

    companies.extend(
        ['WT Enterprises', 'Enterprise XYZ']
    )

    # employment
    employment = [
        Employment(
            person=random.sample(people, 1)[0].id,
            company=random.sample(companies, 1)[0],
            since=tmstmp.timestamp(),
            until=(tmstmp + datetime.timedelta(days=random.randint(90, 3650))).timestamp() if random.randint(0,
                                                                                                             1) else -1
        ) for tmstmp in map(lambda _: (
            datetime.datetime(2014, 12, 31, 11, 59, 59) - datetime.timedelta(
                hours=random.randint(0, (10 * 365 + 1) * 24))
        ), range(0, N['employment']))
    ]

    # data of people of interest
    representative = Person(
        id=str(uuid.uuid4()),
        name='Adi Segan',
        sex='F',
        number='+911-123-987-468'
    )

    seller = Person(
        id=str(uuid.uuid4()),
        name='Kiran Trope',
        sex='M',
        number='+502-987-123-753'
    )

    people.extend(
        [representative, seller]
    )

    # employment of POI: first worked at WT Enterprises, and then quit and later in 2014 joined Enterprise XYZ
    employment.extend(
        [
            Employment(
                person=seller.id,
                company='WT Enterprises',
                since=datetime.datetime(2013, 7, 1).timestamp(),
                until=datetime.datetime(2014, 9, 30).timestamp()
            ),
            Employment(
                person=seller.id,
                company='Enterprise XYZ',
                since=datetime.datetime(2014, 11, 1).timestamp(),
                until=-1
            )
        ]
    )

    # phone activity
    phone_activity = [
        PhoneCall(
            source=random.sample(people, 1)[0].number,
            target=random.sample(people, 1)[0].number,
            weekday=tmstmp.weekday(),
            hour=tmstmp.hour,
            timestamp=tmstmp.timestamp()
        ) for tmstmp in map(lambda _: timestamp(), range(0, N['calls']))
    ]

    # POI phone calls source, target
    phone_activity.extend(
        [
            PhoneCall(
                source=seller.number,
                target=representative.number,
                weekday=tmstmp.weekday(),
                hour=tmstmp.hour,
                timestamp=tmstmp.timestamp()
            ) for tmstmp in map(lambda _: timestamp_in_weekday(2), range(0, 17))
        ]
    )

    phone_activity.extend(
        [
            PhoneCall(
                source=folk.number,
                target=representative.number,
                weekday=tmstmp.weekday(),
                hour=tmstmp.hour,
                timestamp=tmstmp.timestamp()
            ) for tmstmp, folk in map(lambda folk: (timestamp_in_weekday(2), folk), random_folk)
        ]
    )

    # locations
    locations = []
    with open(os.path.join(config.PROJECT_BASE, 'data/locations.json'), encoding='latin-1') as fp:

        entries = json.load(fp)

        for entry in entries:

            tokens = entry.split(',')
            city, country = tokens[0], ''.join(tokens[1:])

            locations.append(
                {
                    'city': city.strip(),
                    'country': country.strip()
                }
            )

    # flights

    flight_activity = []
    for _ in range(0, N['flights']):

        departure = random.sample(locations, 1)[0]
        destination = random.sample(locations, 1)[0]
        while departure == destination:
            destination = random.sample(locations, 1)[0]

        flight_activity.append(
            Flight(
                number=fake.ssn(),
                timestamp=timestamp().timestamp(),
                departure=departure,
                destination=destination,
                person=random.sample(people, 1)[0].id
            )
        )

    # flight data of POI
    flight_activity.extend(
        [
            Flight(
                number=fake.ssn(),
                timestamp=timestamp().timestamp(),
                departure={
                    'country': 'United States',
                    'city': 'Arizona',
                },
                destination={
                    'country': 'Japan',
                    'city': 'Ôsaka',
                },
                person=seller.id
            ) for _ in range(0, 3)
        ]
    )

    # bogus data of someone else that was in contact with the rep of Enterprise XYZ and flew there, but doesn't work at
    # WT Enterprises

    flight_activity.extend(
        [
            Flight(
                number=fake.ssn(),
                timestamp=timestamp().timestamp(),
                departure=random.sample(locations, 1)[0],
                destination={
                    'country': 'Japan',
                    'city': 'Ôsaka',
                },
                person=random.sample(people, 1)[0].id
            ) for _ in range(0, 2)
        ]
    )

    # random folk flights
    flight_activity.extend(
        [
            Flight(
                number=fake.ssn(),
                timestamp=timestamp().timestamp(),
                departure=random.sample(locations, 1)[0],
                destination={
                    'country': 'Japan',
                    'city': 'Ôsaka',
                },
                person=folk.id
            ) for folk in random_folk
        ]
    )

    print('Generated data...')
    print('\t# People:', len(people))
    print('\t# Calls:', len(phone_activity))
    print('\t# Flights:', len(flight_activity))
    print('\t# Employment:', len(employment))

    return people, phone_activity, flight_activity, employment


def clean_database():

    # with neo4j.BatchTransaction() as tx:
    statements = ['MATCH (n)',
                  'WITH n',
                  'LIMIT {limit}',
                  'OPTIONAL MATCH (n)-[r]-(x)',
                  'DELETE r, n']

    query = neo4j.Query('\n'.join(statements), [neo4j.Parameter('limit', 10000)])

    tx = neo4j.Transaction()
    while tx.execute(query):
        tx = neo4j.Transaction()

    tx.execute(query)
    tx.commit()

    statements = ['MATCH (n)',
                  'WITH n',
                  'LIMIT {limit}',
                  'DELETE n']

    query = neo4j.Query('\n'.join(statements), [neo4j.Parameter('limit', 10000)])

    tx = neo4j.Transaction()
    while tx.execute(query):
        tx = neo4j.Transaction()
    tx.commit()


def seed():

    def run_transaction(dataset):

        limit = 5000
        c = 0
        with neo4j.BatchTransaction() as tx:
            for instance in dataset:
                tx.append(instance.cypher())

                c += 1

                if c % limit == 0:
                    tx.execute()

            if c % limit != 0:
                tx.execute()

    # index database
    print('Creating db indexes')
    with neo4j.BatchTransaction() as tx:
        for index in INDEXES:

            query = neo4j.Query(index, [])
            tx.append(query)

        tx.commit()

    print('Emptying database')
    clean_database()

    # generate random data
    print('Generating random data')
    people, phone_activity, flight_activity, employment_data = generate_data()

    print('Seeding people')
    run_transaction(people)

    print('Seeding phone activity')
    run_transaction(phone_activity)

    print('Seeding flight data')
    run_transaction(flight_activity)

    print('Seeding employment data')
    run_transaction(employment_data)


def dump():

    class JSEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__

    people, phone_activity, flight_activity, employment_data = generate_data()

    base_dir = os.path.join(config.PROJECT_BASE, 'data', 'out')

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    with open(os.path.join(base_dir, 'people.json'), 'w') as fp:

        json.dump(people, fp, indent=3, cls=JSEncoder)

    with open(os.path.join(base_dir, 'calls.json'), 'w') as fp:

        json.dump(phone_activity, fp, indent=3, cls=JSEncoder)

    with open(os.path.join(base_dir, 'flights.json'), 'w') as fp:

        json.dump(flight_activity, fp, indent=3, cls=JSEncoder)

    with open(os.path.join(base_dir, 'employment.json'), 'w') as fp:

        json.dump(employment_data, fp, indent=3, cls=JSEncoder)


if __name__ == '__main__':
    dump()
