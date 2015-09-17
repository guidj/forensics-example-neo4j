import datetime
import time

from forensics.utils import neo4j

PATTERNS = {
    1: '\n**Find the top 20 people that took more than 1 flight between ~Jan - Jun 2014, to any destination.'
       ' Results are ordered by number of flights to each country',
    2: '\n**Find people that took more than 1 flight to any country each month, between ~Jan - Aug 2014',
    3: '\n**Find a phone number that has made calls on Wednesdays, between 6pm and 10pm to the representative of XYZ',
    4: '\n**Among the people that called the representative, find those that have flown in or out of '
       'one of enterprise XYZ offices in Japan, or the UK',
    5: '\n**Among the people that called the representative, and flew in or out of one of Enterprise XYZ\'s subsidiaries'
       ', find those that have an employment history at WT Enterprises'
}


def patterns():

    for k, v in PATTERNS.items():
        print(
            k, '=>', v
        )

    print('\n')


def one():

    # find the top 20 people that took more than 1 flight between Jan & Jun 2014, to any destination.
    # Order results by number of flights to each country

    msg = PATTERNS[1]

    print(msg)

    statements = [
        'MATCH (person :`Person`)-[:TOOK]->(flight :`Flight`)-[:TO]-(:`City`)-[:IN]->(country :`Country`)',
        'WHERE flight.timestamp >= {{startDate}} AND flight.timestamp < {{endDate}}',
        'WITH person.name AS person, COUNT(flight) AS n, country.name AS destination',
        'WHERE n > {{count}}',
        'RETURN person, n, destination',
        'ORDER BY n DESC',
        'LIMIT {{limit}}'
    ]

    statement = '\n'.join(statements).format()

    print(statement)

    start_date = datetime.datetime(2014, 1, 1)
    end_date = datetime.datetime(2014, 6, 30)

    params = [
        neo4j.Parameter('startDate', start_date.timestamp()),
        neo4j.Parameter('endDate',  end_date.timestamp()),
        neo4j.Parameter('count',  1),
        neo4j.Parameter('limit',  20)
    ]

    query = neo4j.Query(statement, params)

    start = time.time()*1000

    with neo4j.Transaction() as tx:

        rs = tx.execute(query)

        if rs:
            print('\t', ['Person', 'No. Flights', 'Destination'])
            for row in rs:
                print('\t', row)
        else:
            print('\t', 'No matching patterns found')

    end = time.time()*1000

    print('Took {0:.2f}ms'.format(end-start))


def two():

    # find people that took more than 1 flight to any destination each month, for the past ~8 months
    msg = PATTERNS[2]
    print(msg)

    statements = [
        'MATCH (person :`Person`)-[:TOOK]->(flight :`Flight`)-[:TO]-(:`City`)-[:IN]->(country :`Country`)',
        'WHERE flight.timestamp >= {{startDate}} AND flight.timestamp < {{endDate}}',
        'WITH person.name AS person, COUNT(flight) AS n, country.name AS destination',
        'WHERE n > {{count}}',
        'RETURN person, n, destination'
    ]

    statement = '\n'.join(statements).format()

    print(statement)

    queries = []
    start_date = datetime.datetime(2014, 8, 1)
    end_date = datetime.datetime(2014, 8, 31)

    for i in reversed(range(0, 8)):

        params = [
            neo4j.Parameter('startDate', (start_date - datetime.timedelta(days=30*i)).timestamp()),
            neo4j.Parameter('endDate',  (end_date - datetime.timedelta(days=30*i)).timestamp()),
            neo4j.Parameter('count', 1)
        ]

        query = neo4j.Query(statement, params)
        queries.append(query)

    start = time.time()*1000

    with neo4j.BatchTransaction() as tx:

        for query in queries:
            tx.append(query)

        resultsets = tx.execute()

        for rs, query in zip(resultsets, queries):

            print(
                'Between',
                datetime.datetime.fromtimestamp(query.params[0].value).strftime('%Y-%m-%d'),
                'and',
                datetime.datetime.fromtimestamp(query.params[1].value).strftime('%Y-%m-%d'),
            )

            if rs:
                print('\t', ['Person', 'No. Flights', 'Destination'])
                for row in rs:
                    print('\t', row)
            else:
                print('\t', 'No matching patterns found')

    end = time.time()*1000

    print('Took {0:.2f}ms'.format(end-start))


def three():

    # find a phone number that has made calls on between 6pm and 10pm to the representative
    msg = PATTERNS[3]
    print(msg)

    statements = [
        'MATCH (poi)<-[:REGISTERED_TO]-(poiPhone :`PhoneNumber`)-[call :CONTACTED]->'
        '(repPhone :`PhoneNumber` {{number: {{repNumber}}}})',
        'WHERE call.weekday = {{weekday}}',
        'RETURN poi.name AS subjectName, COUNT(call) AS numberOfCalls'
    ]
    #  AND call.hour >= {{startInterval}} AND call.hour <= {{endInterval}}

    statement = '\n'.join(statements).format()

    print(statement)

    query = neo4j.Query(
        statement,
        [
            neo4j.Parameter('repNumber', '+911-123-987-468'),
            neo4j.Parameter('weekday', 2)
        ]
    )

    start = time.time()*1000

    with neo4j.Transaction() as tx:

        rs = tx.execute(query)

        if rs:
            print('\t', ['Subject\'s Name', 'No. Calls'])
            for row in rs:
                print('\t', row)
        else:
            print('\t', 'No matching patterns found')

    end = time.time()*1000

    print('Took {0:.2f}ms'.format(end-start))


def four():

    # among the people that called the representative, find those that have flown in or out of
    # one of enterprise XYZ offices in Japan, or the UK
    msg = PATTERNS[4]

    print(msg)

    statements = [
        'MATCH (poi :`Person`)<-[:REGISTERED_TO]-(poiPhone :`PhoneNumber`)-[call :CONTACTED]->'
        '(repPhone :`PhoneNumber` {{number: {{repNumber}}}})',
        'WHERE call.weekday = {{weekday}}',
        'WITH poi, COUNT(call) AS numberOfCalls',
        'MATCH (poi)-[:TOOK]->(flight :`Flight`)-[:TO]-(:`City`)-[:IN]->(country :`Country`)',
        'WHERE country.name IN {{countries}} AND flight.timestamp >= {{startDate}} AND flight.timestamp < {{endDate}}',
        'RETURN poi.name as subjectName, poi.id AS ID, COUNT(flight) AS flights, country.name AS country'
    ]

    statement = '\n'.join(statements).format()

    print(statement)

    query = neo4j.Query(
        statement,
        [
            neo4j.Parameter('repNumber', '+911-123-987-468'),
            neo4j.Parameter('weekday', 2),
            neo4j.Parameter('countries', ['Japan', 'UK']),
            neo4j.Parameter('startDate', datetime.datetime(2014, 1, 1).timestamp()),
            neo4j.Parameter('endDate', datetime.datetime(2014, 12, 31).timestamp())
        ]
    )

    start = time.time()*1000

    with neo4j.Transaction() as tx:

        rs = tx.execute(query)

        if rs:
            print('\t', ['Name', 'ID', 'No. of Flights'])
            for row in rs:
                print('\t', row)
        else:
            print('\t', 'No matching patterns found')

    end = time.time()*1000

    print('Took {0:.2f}ms'.format(end-start))


def five():

    msg = PATTERNS[5]

    print(msg)

    statements = [
        'MATCH (poi :`Person`)<-[:REGISTERED_TO]-(poiPhone :`PhoneNumber`)-[call :CONTACTED]->'
        '(repPhone :`PhoneNumber` {{number: {{repNumber}}}})',
        'WHERE call.weekday = {{weekday}}',
        'WITH poi, COUNT(call) AS numberOfCalls',
        'MATCH (poi)-[:TOOK]->(flight :`Flight`)-[:TO]-(:`City`)-[:IN]->(country :`Country`)'
        'WHERE country.name IN {{countries}} AND flight.timestamp >= {{startDate}} AND flight.timestamp < {{endDate}}',
        'WITH poi',
        'MATCH (poi)-[employment :EMPLOYEE_AT]->(company: `Company` {{name: {{companyName}} }})',
        'WHERE employment.since < {{activitiesStartPeriod}} OR employment.until > {{activitiesStartPeriod}}',
        'WITH DISTINCT employment, poi, company',
        'RETURN poi.name as subjectName, poi.id AS ID, employment.since AS since, employment.until AS until'
    ]

    statement = '\n'.join(statements).format()

    print(statement)

    query = neo4j.Query(
        statement,
        [
            neo4j.Parameter('repNumber', '+911-123-987-468'),
            neo4j.Parameter('weekday', 2),
            neo4j.Parameter('countries', ['Japan', 'UK']),
            neo4j.Parameter('companyName', 'WT Enterprises'),
            neo4j.Parameter('startDate', datetime.datetime(2014, 1, 1).timestamp()),
            neo4j.Parameter('endDate', datetime.datetime(2014, 12, 31).timestamp()),
            neo4j.Parameter('activitiesStartPeriod', datetime.datetime(2014, 1, 1).timestamp())
        ]
    )

    start = time.time()*1000

    with neo4j.Transaction() as tx:

        rs = tx.execute(query)

        if rs:
            print('\t', ['Name', 'ID', 'Since', 'Until'])
            for row in rs:
                print(
                    '\t',
                    [
                        row[0], row[1],
                        datetime.datetime.fromtimestamp(row[2]).strftime('%Y-%m-%d'),
                        datetime.datetime.fromtimestamp(row[3]).strftime('%Y-%m-%d')
                    ]
                )
        else:
            print('\t', 'No matching patterns found')

    end = time.time()*1000

    print('Took {0:.2f}ms'.format(end-start))


def run_analysis(pattern):

    if pattern == str(1):
        one()

    elif pattern == str(2):
        two()

    elif pattern == str(3):
        three()

    elif pattern == str(4):
        four()

    elif pattern == str(5):
        five()

    elif pattern == '*':
        for step in [one, two, three, four, five]:
            step()

    # TODO: step 6, find current employment of anyone that used to work at WT Enterprises, who contacted the rep

    else:

        print('\nUnrecognized pattern: `{0}`'.format(pattern))
        patterns()
        exit(1)
