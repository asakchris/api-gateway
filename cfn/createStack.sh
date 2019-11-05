#!/bin/bash

# This function shows how to invoke this script
show_script_usage()
{
    echo -e "\n************************************************************************************************"
    echo -e "`date` Script error : Incorrect usage"
    echo -e "Script Usage:"
    echo -e "\t ./createStack.sh <ENV> <ImageVersion>\n"
    echo -e "Pass 2 arguments to create/update Cloudformation stack"
    echo -e "(1) Environment Name (DEV/QA/UAT/PROD/DR)"
    echo -e "(2) Docker Image Version"
    echo -e "************************************************************************************************"
}

# This function invokes readJson.py to get JSON property value
# It takes 2 arguments
# (1) JSON file path
# (2) JSON property name
python_json_property_value() {
    python helper/readJson.py "$@"
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
    image_version=$2
    echo app_environment: $app_environment, image_version: $image_version, app_name: $app_name

    # Setup environment specific variables from <ENV>.json file
    local __env_file=env/$app_environment/$app_environment.json
    get_json_property_value $__env_file region aws_region
    echo aws_region: $aws_region

    # Setup common variables from common.json file
    local __common_file=env/common.json
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

# This function invokes getParameters.py to get all JSON property and values
# It takes 1 argument
# (1) JSON file path
python_json_properties() {
    python helper/getParameters.py "$@"
}

# This function returns JSON property value
# It takes 1 argument
# (1) JSON file path
get_parameter_value() {
    local param_value=`python_json_properties $1`
    param_values=`eval echo ''${param_value}''`
    echo param_values: $param_values
}

# This function executes given CFN deploy command
# It takes 1 argument
# (1) AWS cloudformation deploy command
deploy_cfn() {
    echo "Executing $1 command"
    eval $1
    local __return_code=$?
    if [[ $__return_code -ne 0 ]]
    then
        echo "Exiting due to error: $__return_code"
        exit $__return_code
    fi
}

get_lambda_s3_bucket() {
    lambda_s3_bucket=`aws cloudformation describe-stacks --stack-name ${stack_s3} --query "Stacks[0].Outputs[?OutputKey=='TokenLambdaBucket'].OutputValue" --output text`
    echo lambda_s3_bucket: $lambda_s3_bucket
}

# Check number of arguments
if [[ $# -ne 2 ]]
then
    show_script_usage
    exit
fi

# Setup environment
setup_env $1 $2

# Execute Security Group template
get_parameter_value env/$app_environment/SecurityGroupParam.json
sg_command="aws --region $aws_region cloudformation deploy --template-file security-group.yml --stack-name ${stack_sg} --parameter-overrides ${param_values} --no-fail-on-empty-changeset"
deploy_cfn "${sg_command}"

# Execute Load Balancer template
get_parameter_value env/$app_environment/LoadBalancerParam.json
lb_command="aws --region $aws_region cloudformation deploy --template-file load-balancer.yml --stack-name ${stack_lb} --parameter-overrides ${param_values} --no-fail-on-empty-changeset"
deploy_cfn "${lb_command}"

# Execute Role template
get_parameter_value env/$app_environment/RoleParam.json
role_command="aws --region $aws_region cloudformation deploy --template-file role.yml --stack-name ${stack_role} --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM --parameter-overrides ${param_values} --no-fail-on-empty-changeset"
deploy_cfn "${role_command}"

# Execute S3 template
get_parameter_value env/$app_environment/S3Param.json
s3_command="aws --region $aws_region cloudformation deploy --template-file s3.yml --stack-name ${stack_s3} --parameter-overrides ${param_values} --no-fail-on-empty-changeset"
deploy_cfn "${s3_command}"

# Upload Lambda code into S3 bucket
umask 002
chmod 744 lambda/*.py
get_lambda_s3_bucket
lambda_deploy_command="aws cloudformation package --template-file lambda.yml --s3-bucket ${lambda_s3_bucket} --output-template-file lambda-final.yml"
deploy_cfn "${lambda_deploy_command}"

# Execute Lambda template
get_parameter_value env/$app_environment/LambdaParam.json
lambda_command="aws --region $aws_region cloudformation deploy --template-file lambda-final.yml --stack-name ${stack_lambda} --capabilities CAPABILITY_NAMED_IAM --parameter-overrides ${param_values} --no-fail-on-empty-changeset"
deploy_cfn "${lambda_command}"

# Execute ECS Cluster template
get_parameter_value env/$app_environment/EcsParam.json
ecs_command="aws --region $aws_region cloudformation deploy --template-file ecs-cluster.yml --stack-name ${stack_ecs_cluster} --parameter-overrides ${param_values} --no-fail-on-empty-changeset"
deploy_cfn "${ecs_command}"

# Execute ECS Service template
get_parameter_value env/$app_environment/ServiceParam.json
ecs_service_command="aws --region $aws_region cloudformation deploy --template-file service.yml --stack-name ${stack_ecs_service} --parameter-overrides ${param_values} --no-fail-on-empty-changeset"
deploy_cfn "${ecs_service_command}"

# Execute API GW template
get_parameter_value env/$app_environment/ApiGatewayParam.json
api_gw_command="aws --region $aws_region cloudformation deploy --template-file api-gateway.yml --stack-name ${stack_api_gw} --parameter-overrides ${param_values} --no-fail-on-empty-changeset"
deploy_cfn "${api_gw_command}"

echo Successfully created/updated stacks