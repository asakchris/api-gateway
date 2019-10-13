from botocore.vendored import requests
import json
import os
import uuid
import traceback

print ("Loading token generator")

def lambda_handler(event, context):
    print('event: ', event)

    validate(event)

    # Call OAM to generate token
    request_body = event['body']
    token_response = generate_token(request_body)
    print('token_response: ', token_response)

    # Call Data Services to save token
    app_token = save_token(token_response)
    print('app_token: ', app_token)

    response_body = { "applicationToken": app_token }
    return {
        "statusCode": 200,
        'headers': { 'Content-Type': 'application/json' },
        "body": json.dumps(response_body)
    }

def validate(event):
    http_method = event['httpMethod']
    print('http_method: ', http_method)
    if http_method != 'POST':
        raise Exception('Invalid httpMethod')

    h_content_type = event['headers']['Content-Type']
    print('h_content_type: ', h_content_type)
    if h_content_type != 'application/x-www-form-urlencoded':
        raise Exception('Invalid Content-Type header')

    request_body = event['body']
    print('request_body: ', request_body)
    if not request_body:
        raise Exception('Invalid request body')

def generate_token(request_body):
    token_url = get_env_variable('TOKEN_URL')
    token_host = get_env_variable('TOKEN_HOST')
    client_secret = get_env_variable('CLIENT_SECRET')
    print('token_url: ', token_url, ', token_host: ', token_host, ', client_secret: ', client_secret)

    authz = 'Basic ' + client_secret
    request_headers = { 'Content-type': 'application/x-www-form-urlencoded', 'Authorization': authz, 'Host': token_host }

    try:
        response = requests.post(token_url, data = request_body, headers = request_headers)
        print('response: ', response)
    except Exception:
        print('Exception while calling OAM endpoint to generate token: ', traceback.print_exc())
        raise Exception('Token can not be generated now')

    response_code = response.status_code
    if 200 <= response_code <= 201:
        return json.loads(response.text)
    else:
        print('Non successful response code while calling OAM endpoint to generate token: response_code: ', response_code, traceback.print_exc())
        raise Exception('Token can not be generated now')

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError as err:
        print('Exception while reading env variable: ', var_name, ': ', err)
        raise Exception('Invalid setup')

def save_token(token_response):
    ds_token_url = get_env_variable('CACHE_TOKEN_URL')
    print('ds_token_url: ', ds_token_url)

    app_token = uuid.uuid4().hex
    print('app_token: ', app_token)

    request_body = { "applicationToken": app_token, "accessToken": token_response['access_token'], "refreshToken": token_response['refresh_token'] }
    request_headers = { 'Content-Type': 'application/json' }

    try:
        response = requests.post(ds_token_url, data = json.dumps(request_body), headers = request_headers)
        print('response: ', response)
    except Exception:
        print('Exception while calling caching OAM token in application: ', traceback.print_exc())
        raise Exception('Application Token can not be generated now')

    response_code = response.status_code
    if 200 <= response_code <= 201:
        return app_token
    else:
        print('Non successful response code while calling token cache endpoint to cache token: response_code: ', response_code, traceback.print_exc())
        raise Exception('Application Token can not be generated now')