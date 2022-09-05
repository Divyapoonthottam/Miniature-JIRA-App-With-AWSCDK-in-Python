from distutils import core
from importlib import resources
from attr import Attribute
from constructs import Construct
from aws_cdk import (
    
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_ses as _ses,aws_iam as iam,
    
    
)
from .env import mail_list


class MinijiraAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
       #define  aws resourse1: aws lambda
        my_lambda = _lambda.Function( self, 'JiraHandler',
            runtime = _lambda.Runtime.PYTHON_3_8,
            code = _lambda.Code.from_asset('lambda'),
            handler = 'jira.handler',
            
        )
        my_lambda.add_to_role_policy(iam.PolicyStatement(
            effect = iam.Effect.ALLOW,
            actions = [
          'ses:SendEmail',
          'ses:SendRawEmail',
          'ses:SendTemplatedEmail',
        ],
         
         resources = mail_list , 
        )
        )
        
        apigw.LambdaRestApi(
            self, 'Endpoint',
            handler = my_lambda,
        )
        #employee table
        employeetable = dynamodb.Table(self,
        id = 'dynamodbtable',
        table_name = "employee",
        partition_key = dynamodb.Attribute(
            name = 'email',
            type = dynamodb.AttributeType.STRING
        )
        )
        employeetable.grant_read_write_data(my_lambda)
        
        #project table
        projecttable = dynamodb.Table(self,
        id = 'dynamodbtable2',
        table_name = "projects",
        partition_key = dynamodb.Attribute(
            name = 'projectkey',
            type = dynamodb.AttributeType.STRING
        )
        )
        projecttable.grant_read_write_data(my_lambda)
         
       #story table
        storytable = dynamodb.Table(self,
        id = 'dynamodbtable3',
        table_name = "stories",
        partition_key = dynamodb.Attribute(
            name = 'projectkey',
            type = dynamodb.AttributeType.STRING
        ),
        sort_key = dynamodb.Attribute(
            name = 'storyid',
            type = dynamodb.AttributeType.STRING
        )
        )
        storytable.grant_read_write_data(my_lambda)

        #task table
        tasktable = dynamodb.Table(self,
        id = 'dynamodbtable4',
        table_name = "tasks",
        partition_key=dynamodb.Attribute(
            name ='projectkey',
            type = dynamodb.AttributeType.STRING
        ),
        sort_key = dynamodb.Attribute(
            name = 'taskid',
            type = dynamodb.AttributeType.STRING
        )
        )
        tasktable.grant_read_write_data(my_lambda)
        
        #comment table
        commenttable = dynamodb.Table(self,
        id ='dynamodbtable1',
        table_name = "comments",
        partition_key = dynamodb.Attribute(
            name = 'projectkey',
            type = dynamodb.AttributeType.STRING
        ),
        sort_key = dynamodb.Attribute(
            name = 'commentid',
            type = dynamodb.AttributeType.STRING
        )
        )
        commenttable.grant_read_write_data(my_lambda)
        
        