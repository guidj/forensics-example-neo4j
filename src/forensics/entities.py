from forensics.utils import neo4j


class Person(object):

    def __init__(self, id, name, sex, number):
        self.id = id
        self.name = name
        self.sex = sex
        self.number = number

    def cypher(self):

        statements = ['MERGE (p :`Person` {{id: {{personId}} }})',
                      'SET p.name = {{name}}',
                      'SET p.sex = {{sex}}',
                      'MERGE (n :`PhoneNumber` {{number: {{number}} }})',
                      'MERGE (n)-[:REGISTERED_TO]->(p)']

        statement = '\n'.join(statements).format()

        params = [
            neo4j.Parameter('personId', self.id),
            neo4j.Parameter('name', self.name),
            neo4j.Parameter('sex', self.sex),
            neo4j.Parameter('number', self.number)
        ]

        return neo4j.Query(statement, params)


class PhoneCall(object):

    def __init__(self, source, target, weekday, hour, timestamp):

        self.source = source
        self.target = target
        self.weekday = weekday
        self.hour = hour
        self.timestamp = timestamp

    def cypher(self):

        statements = ['MERGE (n1 :`PhoneNumber` {{ number: {{number1}} }})',
                      'MERGE (n2 :`PhoneNumber` {{ number: {{number2}} }})',
                      'CREATE (n1)-[r :CONTACTED]->(n2)',
                      'SET r.weekday = {{weekday}}',
                      'SET r.hour = {{hour}}',
                      'SET r.timestamp = {{timestamp}}']

        statement = '\n'.join(statements).format()

        params = [
            neo4j.Parameter('number1', self.source),
            neo4j.Parameter('number2', self.target),
            neo4j.Parameter('weekday', self.weekday),
            neo4j.Parameter('hour', self.hour),
            neo4j.Parameter('timestamp', self.timestamp)
        ]

        return neo4j.Query(statement, params)


class Flight(object):

    def __init__(self, number, timestamp, departure, destination, person):

        self.number = number
        self.timestamp = timestamp
        self.departure = departure
        self.destination = destination
        self.person = person

    def cypher(self):

        statements = ['MERGE (country1 :`Country` {{ name:{{co1}} }})',
                      'MERGE (country2 :`Country` {{ name:{{co2}} }})',
                      'MERGE (city1 :`City` {{ name:{{ci1}} }})',
                      'MERGE (city2 :`City` {{ name:{{ci2}} }})',
                      'MERGE (city1)-[:IN]->(country1)',
                      'MERGE (city2)-[:IN]->(country2)',
                      'MERGE (person :`Person` {{id: {{personId}} }})',
                      'MERGE (flight :`Flight` {{number: {{flightNo}} }})'
                      'SET flight.timestamp = {{timestamp}}',
                      'MERGE (flight)-[:FROM]->(city1)',
                      'MERGE (flight)-[:TO]->(city2)',
                      'MERGE (person)-[:TOOK]->(flight)'
                      ]

        statement = '\n'.join(statements).format()

        params = [
            neo4j.Parameter('co1', self.departure['country']),
            neo4j.Parameter('co2', self.destination['country']),
            neo4j.Parameter('ci1', self.departure['city']),
            neo4j.Parameter('ci2', self.destination['city']),
            neo4j.Parameter('flightNo', self.number),
            neo4j.Parameter('personId', self.person),
            neo4j.Parameter('timestamp', self.timestamp)
        ]

        return neo4j.Query(statement, params)


class Employment(object):

    def __init__(self, person, company, since, until):

        self.person = person
        self.company = company
        self.since = since
        self.until = until

    def cypher(self):

        statements = ['MERGE (person :`Person` {{ id: {{personId}} }})',
                      'MERGE (company :`Company` {{ name:{{companyName}} }})',
                      'CREATE (person)-[emp :EMPLOYEE_AT]->(company)',
                      'SET emp.since = {{since}}',
                      'SET emp.until = {{until}}'
                      ]

        statement = '\n'.join(statements).format()

        params = [
            neo4j.Parameter('personId', self.person),
            neo4j.Parameter('companyName', self.company),
            neo4j.Parameter('since', self.since),
            neo4j.Parameter('until', self.until),
        ]

        return neo4j.Query(statement, params)
