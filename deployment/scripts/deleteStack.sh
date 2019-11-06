#!/bin/bash

# This function shows how to invoke this script
show_script_usage()
{
    echo -e "\n************************************************************************************************"
    echo -e "`date` Script error : Incorrect usage"
    echo -e "Script Usage:"
    echo -e "\t ./deleteStack.sh <ENV>\n"
    echo -e "Pass 1 argument to delete Cloudformation stack"
    echo -e "(1) Environment Name (DEV/QA/UAT/PROD/DR)"
    echo -e "************************************************************************************************"
}

# This function invokes readJson.py to get JSON property value
# It takes 2 arguments
# (1) JSON file path
# (2) JSON property name
python_json_property_value() {
    python $scripts_dir/helper/readJson.py "$@"
}

# This function returns JSON property value
# It takes 3 arguments
# (1) JSON file path
# (2) JSON property name
# (3) Variable name in which value to be assigned
get_json_property_value() {
    local __result_var=$3
    local param_value=`python_json_property_value $1 $2`
    eval $__result_var=$param_value
}

# This function sets up all required variables
setup_env() {
    app_name='GW'
    app_environment=$1
    echo app_environment: $app_environment, app_name: $app_name

    # Setup environment specific variables from <ENV>.json file
    local __env_file=$cfn_dir/env/$app_environment/$app_environment.json
    get_json_property_value $__env_file region aws_region
    echo aws_region: $aws_region

    # Setup common variables from common.json file
    local __common_file=$cfn_dir/env/common.json
    get_json_property_value $__common_file SecurityGroupStack stack_sg
    get_json_property_value $__common_file LoadBalancerStack stack_lb
    get_json_property_value $__common_file RoleStack stack_role
    get_json_property_value $__common_file S3Stack stack_s3
    get_json_property_value $__common_file LambdaStack stack_lambda
    get_json_property_value $__common_file EcsClusterStack stack_ecs_cluster
    get_json_property_value $__common_file EcsServiceStack stack_ecs_service
    get_json_property_value $__common_file ApiGwStack stack_api_gw
    echo stack_sg: $stack_sg, stack_lb: $stack_lb \
        stack_role: $stack_role, stack_s3: $stack_s3 \
        stack_lambda: $stack_lambda, stack_ecs_cluster: $stack_ecs_cluster \
        stack_ecs_service: $stack_ecs_service, stack_api_gw: $stack_api_gw
}

# This function deletes given CFN template stack
# It takes 1 argument
# (1) AWS cloudformation stack name
delete_stack() {
    echo Deleting $1 stack...
    aws cloudformation delete-stack --stack-name $1
    echo "Waiting for $1 stack to be deleted, this may take few minutes..."
    aws cloudformation wait stack-delete-complete --stack-name $1
    local __return_code=$?
    echo Successfully deleted $1 stack: $__return_code
}

# This function find S3 bucket created for Lambda
get_lambda_s3_bucket() {
    lambda_s3_bucket=$(aws cloudformation describe-stacks --stack-name ${stack_s3} --query "Stacks[0].Outputs[?OutputKey=='TokenLambdaBucket'].OutputValue" --output text)
    echo lambda_s3_bucket: $lambda_s3_bucket
    if [[ "$lambda_s3_bucket" == "" ]]; then
        echo Lambda S3 bucket does not exist
        exit 1
    fi
}

# Check whether script is called from repository root
scripts_dir='./deployment/scripts'
cfn_dir='./deployment/cfn'
if [[ "`dirname $0`" != "$scripts_dir" ]]; then
    echo "This script must be called from repository root." >&2
    exit 1
fi

# Check number of arguments
if [[ $# -ne 1 ]]
then
    show_script_usage
    exit
fi

# Setup environment
setup_env $1

# Delete API GW stack
delete_stack ${stack_api_gw}

# Delete ECS Service stack
delete_stack ${stack_ecs_service}

# Delete ECS Cluster stack
delete_stack ${stack_ecs_cluster}

# Delete Lambda stack
delete_stack ${stack_lambda}

# Delete Lambda S3 bucket contents
get_lambda_s3_bucket
aws s3 rb s3://${lambda_s3_bucket} --force

# Delete S3 stack
delete_stack ${stack_s3}

# Delete Role stack
delete_stack ${stack_role}

# Delete Load Balancer stack
delete_stack ${stack_lb}

# Delete Security Group stack
delete_stack ${stack_sg}

echo Successfully deleted stacks