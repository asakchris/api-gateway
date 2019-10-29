###### AWS
```
aws cloudformation deploy --template-file security-group.yml --stack-name GW-SG 
    --parameter-overrides VpcId=vpc-0f407bc8f5f182a88

aws cloudformation deploy --template-file load-balancer.yml --stack-name GW-LB 
    --parameter-overrides VpcId=vpc-0f407bc8f5f182a88 SubnetList="subnet-03759a6aea1cffc8e, subnet-0239bfced473e911c" 
    SecurityGroupStackName=GW-SG

aws cloudformation deploy --template-file role.yml --stack-name GW-ROLE 
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM --parameter-overrides Environment=DEV
    
aws cloudformation deploy --template-file s3.yml --stack-name GW-S3 --parameter-overrides Environment=DEV

aws s3 ls
aws s3 ls s3://dev-****-web-test-services-token-lambda-us-east-1-01
aws s3 rb s3://dev-****-web-test-services-token-lambda-us-east-1-01 --force

aws cloudformation package --template-file lambda.yml 
    --s3-bucket dev-*****-web-test-services-token-lambda-us-east-1-01 
    --output-template-file lambda-final.yml

aws cloudformation deploy --template-file lambda-final.yml --stack-name GW-LAMBDA 
    --capabilities CAPABILITY_NAMED_IAM 
    --parameter-overrides Environment=DEV RoleStackName=GW-ROLE LoadBalancerStackName=GW-LB

aws cloudformation deploy --template-file ecs-cluster.yml --stack-name GW-ECS

aws cloudformation deploy --template-file service.yml --stack-name GW-SERVICE 
    --parameter-overrides PrivateSubnetList="subnet-03759a6aea1cffc8e, subnet-0239bfced473e911c" 
    SecurityGroupStackName=GW-SG LoadBalancerStackName=GW-LB EcsClusterStackName=GW-ECS RoleStackName=GW-ROLE

aws cloudformation deploy --template-file api-gateway.yml --stack-name GW-API 
    --parameter-overrides Environment=DEV LambdaStackName=GW-LAMBDA LoadBalancerStackName=GW-LB
```