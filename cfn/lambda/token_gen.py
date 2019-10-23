from botocore.vendored import requests
import json
import os
import sys
import uuid

print ("Loading token generator")

def lambda_handler(event, context):
    print('event: ', event)
    try:
        validate(event)

        # Call OAM to generate token
        request_body = event['body']
        token_response = generate_token(request_body)
        print('token_response: ', token_response)

        # Call Data Services to cache token
        app_token = cache_token(token_response)
        print('app_token: ', app_token)

        response_body = { "applicationToken": app_token }
        return {
            "statusCode": 200,
            'headers': { 'Content-Type': 'application/json' },
            "body": json.dumps(response_body)
        }
    except TokenException as auth_ex:
        msg = { "message": auth_ex.status_message }
        return {
            "statusCode": auth_ex.status_code,
            'headers': { 'Content-Type': 'application/json' },
            "body": json.dumps(msg)
        }
    except:
        print('Unexpected error: ', sys.exc_info()[0])
        msg = { "message": 'Internal error during token generation' }
        return {
            "statusCode": 500,
            'headers': { 'Content-Type': 'application/json' },
            "body": json.dumps(msg)
        }

def validate(event):
    http_method = event['httpMethod']
    if http_method != 'POST':
        print('http_method: ', http_method)
        raise TokenException('Invalid httpMethod', 401, 'Invalid httpMethod')

    h_content_type = event['headers']['Content-Type']
    if h_content_type != 'application/x-www-form-urlencoded':
        print('h_content_type: ', h_content_type)
        raise TokenException('Invalid Content-Type header', 401, 'Invalid Content-Type header')

    request_body = event['body']
    if not request_body:
        raise TokenException('Invalid request body', 401, 'Invalid request body')

def generate_token(request_body):
    token_url = get_env_variable('TOKEN_URL')
    token_host = get_env_variable('TOKEN_HOST')
    client_secret = get_env_variable('CLIENT_SECRET')
    print('token_url: ', token_url, ', token_host: ', token_host, ', client_secret: ', client_secret)

    authz = 'Basic ' + client_secret
    request_headers = { 'Content-type': 'application/x-www-form-urlencoded', 'Authorization': authz, 'Host': token_host }

    response = requests.post(token_url, data = request_body, headers = request_headers)
    print('response: ', response)
    response_code = response.status_code

    if 200 <= response_code <= 201:
        return json.loads(response.text)
    elif 400 <= response_code <= 499:
        print('4** response code while calling OAM endpoint to generate token: response_code: ', response_code)
        raise TokenException('4** response code while calling OAM endpoint to generate token', 401, 'Invalid username/password')
    else:
        print('Non successful response code while calling OAM endpoint to generate token: response_code: ', response_code)
        raise TokenException('4** response code while calling OAM endpoint to generate token', 500, 'Token can not be generated now')

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError as err:
        print('Exception while reading env variable: ', var_name, ': ', err)
        raise err

def cache_token(token_response):
    ds_token_url = get_env_variable('CACHE_TOKEN_URL')
    print('ds_token_url: ', ds_token_url)

    app_token = uuid.uuid4().hex
    print('app_token: ', app_token)

    request_body = { "applicationToken": app_token, "accessToken": token_response['access_token'], "refreshToken": token_response['refresh_token'] }
    request_headers = { 'Content-Type': 'application/json' }

    response = requests.post(ds_token_url, data = json.dumps(request_body), headers = request_headers)
    print('response: ', response)
    response_code = response.status_code

    if 200 <= response_code <= 201:
        return app_token
    elif 400 <= response_code <= 499:
        print('4** response code while calling token cache endpoint to cache token: response_code: ', response_code)
        raise TokenException('4** response code while calling OAM endpoint to generate token', 503, 'Internal error during token generation')
    else:
        print('Non successful response code while calling token cache endpoint to cache token: response_code: ', response_code)
        raise TokenException('4** response code while calling OAM endpoint to generate token', response_code, 'Internal error during token generation')

class TokenException(Exception):
    """Basic exception for errors raised during token generation"""
    def __init__(self, message, status_code, status_message):
        super().__init__(message)
        self.status_code = status_code
        self.status_message = status_message