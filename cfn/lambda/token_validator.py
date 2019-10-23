from botocore.vendored import requests
import json
import base64
import os
import sys

print ("Loading token validator")

def lambda_handler(event, context):
    print('event: ', event)
    try:
        # Validate request
        validate(event)

        # Get OAM token from cache
        application_token = event['authorizationToken']
        access_token = get_token_from_cache(application_token)

        # Call OAM to validate token
        principal_id = validate_token(access_token)
        print('principal_id: ', principal_id)

        # Generate policy and return
        idm_header = { 'uid': principal_id }
        res_policy = generate_policy(principal_id, idm_header, 'Allow', '*')
        return res_policy
    except TokenException as ex:
        print ('TokenException: ', ex)
        raise Exception('Unauthorized')
    except:
        print('Unexpected error: ', sys.exc_info()[0])
        raise

def validate(event):
    if 'authorizationToken' in event:
        application_token = event['authorizationToken']
        if not application_token:
            print('application_token: ', application_token)
            raise TokenException('Token header is blank', 'Unauthorized')
    else:
        print('Token header is missing')
        raise TokenException('Token header is missing', 'Unauthorized')

def get_token_from_cache(application_token):
    ds_token_url = get_env_variable('CACHE_TOKEN_URL')
    print('ds_token_url: ', ds_token_url)

    request_param = { "applicationToken": application_token }

    response = requests.get(ds_token_url, params = request_param)
    response_code = response.status_code

    if response_code == 200:
        j_response = json.loads(response.text)
        print('j_response: ', j_response)
        access_token = j_response['accessToken']
        return access_token
    elif 400 <= response_code <= 499:
        print('Token not found in cache: ', application_token)
        raise TokenException('Token not found in cache', 'Invalid token')
    else:
        print('Non successful response code while getting token from cache: ', application_token, ', response_code: ', response_code)
        raise TokenException('Non successful response code while getting token from cache', 'Internal error')

def get_stage_variable(var_name):
    try:
        return event['stageVariables'][var_name]
    except KeyError as err:
        print('Exception while reading stage variable: ', var_name, ': ', err)
        raise err

def validate_token(access_token):
    token_url = get_env_variable('TOKEN_URL')
    token_host = get_env_variable('TOKEN_HOST')
    client_secret = get_env_variable('CLIENT_SECRET')
    print('token_url: ', token_url, ', token_host: ', token_host, ', client_secret: ', client_secret)

    authz = 'Basic ' + client_secret
    request_headers = { 'Content-type': 'application/x-www-form-urlencoded', 'Authorization': authz, 'Host': token_host }
    request_data = 'oracle_token_action=validate&grant_type=oracle-idm:/oauth/grant-type/resource-access-token/jwt&oracle_token_attrs_retrieval=exp prn exp firstname lastname spAppGroup isMemberOf iat oracle.oauth.client_origin_id&assertion=' + access_token
    response = requests.post(token_url, data = request_data, headers = request_headers)
    print('response: ', response)
    response_code = response.status_code

    if 200 <= response_code <= 201:
        j_response = json.loads(response.text)
        print('j_response: ', j_response)

        if 'successful' in j_response:
            if check_client_id_parity(authz, j_response):
                principal_id = j_response['oracle_token_attrs_retrieval']['prn']
                return principal_id
            else:
                print("Token issued with another client_id")
                raise TokenException('Token issued with another client_id', 'Unauthorized')
        else:
            print("Invalid Token or Client Key")
            raise TokenException('Invalid Token or Client Key', 'Unauthorized')
    elif 400 <= response_code <= 499:
        print('4** response code while validating token: ', access_token, ', response_code: ', response_code)
        raise TokenException('4** response code while validating token', 'Unauthorized')
    else:
        print('Non successful response code while validating token: ', access_token, ', response_code: ', response_code)
        raise TokenException('Non successful response code while validating token', 'Internal error')

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError as err:
        print('Exception while reading env variable: ', var_name, ': ', err)
        raise err

def check_client_id_parity(authz, j_response):
    org_cid = j_response['oracle_token_attrs_retrieval']['oracle.oauth.client_origin_id']
    req_cid = str(base64.standard_b64decode(authz[6:]), 'utf-8').split(':')[0] # trimming 'Basic '' spliting : getting only first part
    return org_cid.lower() == req_cid.lower()

def generate_policy(principal_id, idm_header, effect, method_arn):
    policy_document = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': method_arn
                }
            ]
        },
        'context': {
            'uid': principal_id,
            'idm_header': json.dumps(idm_header)
        }
    }
    return policy_document

class TokenException(Exception):
    """Basic exception for errors raised during token validation"""
    def __init__(self, message, status_message):
        super().__init__(message)
        self.status_message = status_message