""" Simple ping endpoint. """
import json


def ping(operation, payload):
    """ Ping endpoint
    :param operation: Ping endpoint operation
    :param payload: Ping endpoing response payload
    """
    operations = {
        'ping': lambda x: 'pong',
        'health': lambda x: 'green',
        'security': lambda x: 'low'
    }

    if operation in operations:
        value = operations[operation](payload)
        return value, 200
    else:
        raise ValueError('Unrecognized operation "{}"'.format(operation))


def lambda_handler(*kwargs):
    """ Ping endpoint lambda
    :param event: Lambda event
    :param context: Lambda context
    """
    query_params = kwargs[0].get('queryStringParameters')
    operation = query_params.get('operation')
    body, status = ping(operation, operation)
    response = {
        "statusCode": status,
        "body": json.dumps(body)
    }
    return response
