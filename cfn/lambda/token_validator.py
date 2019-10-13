from botocore.vendored import requests
import json
import base64
import os
import traceback

print ("Loading token validator")

def lambda_handler(event, context):
    print('event: ', event)

    # Validate request
    validate(event)

    # Get OAM token from cache
    application_token = event['authorizationToken']
    access_token = get_token_from_cache(application_token)

    # Call OAM to validate token
    principalId = validate_token(access_token)
    print('principalId: ', principalId)

    # Generate policy and return
    idmHeader = { 'uid': principalId }
    res_policy = generate_policy(principalId, idmHeader, 'Allow', '*')
    return res_policy

def validate(event):
    if 'authorizationToken' in event:
        application_token = event['authorizationToken']
        print('application_token: ', application_token)
        if not application_token:
            raise Exception('Invalid token')
    else:
        print('Token header is missing')
        raise Exception('Invalid token')

def get_token_from_cache(application_token):
    ds_token_url = get_env_variable('CACHE_TOKEN_URL')
    print('ds_token_url: ', ds_token_url)

    request_param = { "applicationToken": application_token }

    try:
        response = requests.get(ds_token_url, params = request_param)
        response_code = response.status_code

        if response_code == 200:
            j_response = json.loads(response.text)
            print('j_response: ', j_response)
            access_token = j_response['accessToken']
            return access_token
        if response_code == 404:
            print('Token not found in cache: ', application_token)
            raise Exception('Invalid token')
        elif 500 <= response_code <= 599:
            print('Response code 5** while getting token from cache: ', application_token)
            raise Exception('Internal error')
        else:
            print('Invalid response status code while getting token from cache: ', application_token, ': code: ', response_code)
            raise Exception('Internal error')
    except Exception:
        print('Exception while getting token from cache: ', traceback.print_exc())
        raise Exception('Internal error')

def get_stage_variable(var_name):
    try:
        return event['stageVariables'][var_name]
    except KeyError as err:
        print('Exception while reading stage variable: ', var_name, ': ', err)
        raise Exception('Invalid setup')

def validate_token(access_token):
    token_url = get_env_variable('TOKEN_URL')
    token_host = get_env_variable('TOKEN_HOST')
    client_secret = get_env_variable('CLIENT_SECRET')
    print('token_url: ', token_url, ', token_host: ', token_host, ', client_secret: ', client_secret)

    authz = 'Basic ' + client_secret
    request_headers = { 'Content-type': 'application/x-www-form-urlencoded', 'Authorization': authz, 'Host': token_host }

    request_data = 'oracle_token_action=validate&grant_type=oracle-idm:/oauth/grant-type/resource-access-token/jwt&oracle_token_attrs_retrieval=exp prn exp firstname lastname spAppGroup isMemberOf iat oracle.oauth.client_origin_id&assertion=' + access_token

    try:
        response = requests.post(token_url, data = request_data, headers = request_headers)
        print('response: ', response)
        response_code = response.status_code

        if 200 <= response_code <= 201:
            j_response = json.loads(response.text)
            print('j_response: ', j_response)

            if 'successful' in j_response:
                if(check_client_id_parity(authz, j_response)):
                    principalId = j_response['oracle_token_attrs_retrieval']['prn']
                    return principalId
                else:
                    print("Token issued with another client_id")
                    raise Exception('Unauthorized')
            else:
                print("Invalid Token or Client Key")
                raise Exception('Unauthorized')
        if response_code == 401:
            print('Unauthorized response code while validating token: ', access_token)
            raise Exception('Unauthorized')
        elif 500 <= response_code <= 599:
            print('Response code 5** while validating token: ', access_token)
            raise Exception('Internal error')
        else:
            print('Invalid response status code while validating token: ', access_token, ': code: ', response_code)
            raise Exception('Internal error')
    except Exception:
        print('Exception while calling OAM endpoint to validate token: ', traceback.print_exc())
        raise Exception('Internal error')

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError as err:
        print('Exception while reading env variable: ', var_name, ': ', err)
        raise Exception('Invalid setup')

def check_client_id_parity(authz, j_response):
    orgCid = j_response['oracle_token_attrs_retrieval']['oracle.oauth.client_origin_id']
    reqCid = str(base64.standard_b64decode(authz[6:]), 'utf-8').split(':')[0] # trimming 'Basic '' spliting : getting only first part
    return (orgCid.lower() == reqCid.lower())

def generate_policy(principalId, idmHeader, effect, methodArn):
    policyDocument = {
        'principalId': principalId,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': methodArn
                }
            ]
        },
        'context': {
            'uid': principalId,
            'idm_header': json.dumps(idmHeader)
        }
    }
    return policyDocument
