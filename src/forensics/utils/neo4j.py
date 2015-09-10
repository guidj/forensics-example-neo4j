import re

from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import exceptions
import neo4jrestclient.options
from forensics.utils import config

NEO_VAR_NAME_LABEL_REGEX = "^[a-zA-Z_][a-zA-Z0-9_]*$"
re.compile(NEO_VAR_NAME_LABEL_REGEX)


def get_connection():
    """
    Creates a connection object to the graph database using py2neo
    :return: py2neo GraphDatabaseService object
    """

    try:

        neo4j = config.get("neo4j")
    except Exception:
        raise

    username = neo4j["username"]
    password = neo4j["password"]
    host = neo4j["host"]
    port = int(neo4j["port"])
    endpoint = neo4j["endpoint"]
    protocol = neo4j["protocol"]

    try:

        uri = "{0}://{1}:{2}/{3}/".format(protocol, host, port, endpoint)

        db_conn = GraphDatabase(uri, username=username, password=password)

        neo4jrestclient.options.URI_REWRITES = {
            "http://0.0.0.0:7474/": "{0}://{1}:{2}/".format(protocol, host, port)
        }

    except exceptions.TransactionException as exc:
        raise exc
    else:
        return db_conn


def is_valid_label(label):
    """
    :param label:
    :return:
    """

    if re.match(NEO_VAR_NAME_LABEL_REGEX, label):
        return True
    else:
        return False


class Parameter(object):
    """
    """

    def __init__(self, key, value):

        self.key = key
        self.value = value

    def __repr__(self):

        return "Parameter({0}={1})".format(self.key, self.value)

    def __eq__(self, other):

        if isinstance(other, Parameter):
            return self.key == other.key and self.value == other.value
        else:
            return False

    def __ne__(self, other):

        return not self.__eq__(other)

    def __hash__(self):

        return hash(self.__repr__())


class Query(object):
    """
    """

    def __init__(self, statement, params):

        self.statement = statement
        self.params = params


class CypherQuery(object):

    def __init__(self, statement, commit=False):

        self.__statement = statement
        self.__commit = commit

    def __call__(self, f):

        def wrapped_f(*args, **kwargs):

            params = []

            for key in kwargs:
                params.append(Parameter(key, kwargs[key]))

            query = Query(self.__statement, params)

            r = run_query(query, self.__commit)

            return f(result=r, *args, **kwargs)

        return wrapped_f


def run_query(query, commit=True, timeout=30):
    """
    :param query:
    :param commit:
    :param timeout:
    :return:
    """

    graph = get_connection()
    tx = graph.transaction(for_query=True)

    q = query.statement
    p = {param.key: param.value for param in query.params}

    tx.append(q, params=p)

    try:

        result = tx.execute()[0]

    except exceptions.TransactionException as exc:

        # Logger.error("Error initiating transaction:\n\t{0}".format(exc))
        raise exc

    tx.commit()

    return result


def run_batch_query(queries, commit=True, timeout=300):
    """
    :param queries:
    :param commit:
    :param timeout:
    :return:
    """

    #TODO: see if there is a way to set timeout with restneo4jclient
    graph = get_connection()
    tx = graph.transaction(for_query=True)

    for query in queries:
        statement = query.statement
        params = {param.key: param.value for param in query.params}

        tx.append(statement, params)

    try:

        results = tx.execute()

    except exceptions.TransactionException as exc:

        # Logger.error(
        #     'Transaction error:\n\t{0}'.format(
        #         exc
        #     )
        # )

        raise exc

    tx.commit()

    collection = []
    for result in results:

        records = []

        for record in result:

            records.append(record)

        collection.append(records)

    return collection


class Transaction(object):
    # TODO: use neo4jrestclient CypherQuery class
    def __init__(self):
        self.graph = get_connection()
        self.tx = self.graph.transaction(for_query=True)

    def __enter__(self):
        self._instance = self
        return self._instance

    def __exit__(self, type, value, traceback):
        self._instance.commit()

    def execute(self, query):

        try:

            q = query.statement
            p = {param.key: param.value for param in query.params}

            self.tx.append(q, p)
            result = self.tx.execute()[0]

        except neo4jrestclient.exceptions.TransactionException:
            self.tx.rollback()
            raise
        else:
            return result

    def commit(self):
        self.tx.commit()

    def rollback(self):
        self.tx.rollback()


class BatchTransaction(object):
    # TODO: use neo4jrestclient CypherQuery class
    def __init__(self):
        self.graph = get_connection()
        self.tx = self.graph.transaction(for_query=True)

    def __enter__(self):
        self._instance = self
        return self._instance

    def __exit__(self, type, value, traceback):

        self._instance.commit()

    def append(self, query):

        assert isinstance(query, Query)

        q = query.statement
        p = {param.key: param.value for param in query.params}

        self.tx.append(q, p)

    def execute(self):

        try:

            results = self.tx.execute()

        except neo4jrestclient.exceptions.TransactionException:
            self.tx.rollback()
            raise
        else:

            collection = []
            for result in results:

                records = []

                for record in result:

                    records.append(record)

                collection.append(records)

            return collection

    def commit(self):
        self.tx.commit()

    def rollback(self):
        self.tx.rollback()
