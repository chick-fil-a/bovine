import json

def ping(operation, payload):
    operations = {
        'ping': lambda x: 'pong',
        'health': lambda x: 'green',
        'security': lambda x: 'low'
    }

    if operation in operations:
        v = operations[operation](payload)
        return v,200
    else:
        raise ValueError('Unrecognized operation "{}"'.format(operation))

def lambda_handler(event,context):
    query_params = event.get('queryStringParameters')
    operation = query_params.get('operation')
    body,status = ping(operation,operation)
    response = {
        "statusCode": status,
        "body": json.dumps(body)
    }
    return response

if __name__ == "__main__":
    resp = lambda_handler(None,None)
    print resp