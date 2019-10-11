# Deploy Spring Boot Application in AWS API Gateway with Lambda Authorizer

### Build
###### Build application and create local image
```
mvn clean package dockerfile:build
```

###### Build application and push image to remote repository
```
mvn clean package dockerfile:push
```

### Run
###### Local
Token Service
```
VM Options: -Dserver.port=8000 -Dmanagement.server.port=8001
```

Cache Service
```
VM Options: -Dserver.port=8002 -Dmanagement.server.port=8003
```

Welcome Service
```
VM Options: -Dserver.port=8004 -Dmanagement.server.port=8005
```

Random Service
```
VM Options: -Dserver.port=8006 -Dmanagement.server.port=8007
```

###### docker compose
```
docker-compose up -d

docker-compose ps

docker-compose down

docker-compose logs -f --tail="all"
docker-compose logs -f --tail="100"

docker-compose logs -f --tail="all" token
docker-compose logs -f --tail="100" cache
```

###### AWS
```
aws cloudformation create-stack --stack-name GW-SG --template-body file://security-group.yml
    --parameters ParameterKey=VpcId,ParameterValue=vpc-0f407bc8f5f182a88

aws cloudformation create-stack --stack-name GW-LB --template-body file://load-balancer.yml
    --parameters ParameterKey=VpcId,ParameterValue=vpc-0f407bc8f5f182a88
    ParameterKey=SubnetList,ParameterValue='subnet-07c3fe07c002037ad,subnet-091106e5ad4b9abc1'
    ParameterKey=SecurityGroupStackName,ParameterValue=GW-SG

aws cloudformation create-stack --stack-name GW-ROLE --template-body file://role.yml
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

aws cloudformation create-stack --stack-name GW-ECS --template-body file://ecs-cluster.yml

aws cloudformation create-stack --stack-name GW-SERVICE --template-body file://service.yml
    --parameters ParameterKey=PrivateSubnetList,ParameterValue='subnet-03759a6aea1cffc8e,subnet-0239bfced473e911c'
    ParameterKey=SecurityGroupStackName,ParameterValue=GW-SG ParameterKey=LoadBalancerStackName,ParameterValue=GW-LB
    ParameterKey=EcsClusterStackName,ParameterValue=GW-ECS ParameterKey=RoleStackName,ParameterValue=GW-ROLE
```

### Test
###### Local
Token Service
```
curl -X POST \
  http://localhost:8000/api/v1/gw/token/tokens \
  -H 'Authorization: Basic T0FVVEhfRVhUX0dXOlBhc3NediE/REB6Q1RhKllKP3pDVCZ1eQ==' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Host: tt.execute-api.us-east-1.amazonaws.com' \
  -d 'scope=UserProfile.me&grant_type=password&username=foo%40bar.com&password=Foo1234'
  
curl -X POST \
  http://localhost:8000/api/v1/gw/token/tokens \
  -H 'Authorization: Basic T0FVVEhfRVhUX0dXOlBhc3NediE/REB6Q1RhKllKP3pDVCZ1eQ==' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Host: tt.execute-api.us-east-1.amazonaws.com' \
  -d 'oracle_token_action=validate&grant_type=oracle-idm%3A%2Foauth%2Fgrant-type%2Fresource-access-token%2Fjwt&oracle_token_attrs_retrieval=exp%20prn%20exp%20firstname%20lastname%20isMemberOf%20iat%20oracle.oauth.client_origin_id&assertion=0d16d1eb-6412-4cee-8ff9-f7421ebd45e0'
  
http://localhost:8001/actuator/health
```

Cache Service
```
curl -X POST \
  http://localhost:8002/api/v1/gw/cache/tokens \
  -H 'Content-Type: application/json' \
  -d '{
	"applicationToken": "e706cbc771c84ee99f2640fe909d585b",
	"accessToken": "0d16d1eb-6412-4cee-8ff9-f7421ebd45e0",
	"refreshToken": "91b8a03b-e3c5-47c6-bfe3-4daa9b389736"
}'

curl -X GET \
  'http://localhost:8002/api/v1/gw/cache/tokens?applicationToken=e706cbc771c84ee99f2640fe909d585b'

http://localhost:8003/actuator/health
```

Welcome Service
```
curl -X GET \
  http://localhost:8004/api/v1/gw/welcome/message \
  -H 'authuid: foo@bar.com'

http://localhost:8005/actuator/health
```

Random Service
```
curl -X GET \
  http://localhost:8006/api/v1/gw/random/number \
  -H 'authuid: foo@bar.com'

http://localhost:8007/actuator/health
```