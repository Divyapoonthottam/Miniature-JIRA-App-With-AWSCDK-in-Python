import json
import boto3
import string
import random
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table_employee = dynamodb.Table('employee')
table_projects = dynamodb.Table('projects')
table_stories = dynamodb.Table('stories')
table_tasks = dynamodb.Table('tasks')
table_comments = dynamodb.Table('comments')


def signup(username,email,password):
    
    table_employee.put_item(
                Item = {
                    'email'     : email,
                    'username'  : username,
                    'password' : password,
                            }
                )
    return"signup successfull,please login to continue!"

def login(email,password):

    response = table_employee.query(KeyConditionExpression=Key('email').eq(email))
    if response:
       for item in response['Items']:
            if item.get('password') == password :
                user_name = item.get('username')
                message = "successfully logged in"
            else:
                message = "try again wrong credentials" 
                email = "invalid email"
                user_name = 'Not a registred user'
    else:
        message = "not found"
        email = "not found "
        user_name = "no such user"            
    return message , email ,user_name


def handler(event, context):
    
    event = json.loads(event['body'])
    action = event["action"]

    
    #signupaction

    if  action == 'signup':
        username = event['username'] 
        email = event['email']
        password = event['password']
        message = signup(username,email,password) 

    #login
    if action == "login": 
        email = event["email"]
        password = event["password"]
        message , primary_email , primary_user = login(email,password)
        # primary email is used to send email to employees

    #list employees                        
    elif action == "employeelist":
                response = table_employee.scan()
                response['Items']
                users = []
                user_email = []
                for elements in response['Items']:
                    users.append(elements.get('username'))
                    user_email.append(elements.get('email'))
                message = users , user_email

    #add project
    elif action == "addproject":
        table_projects.put_item(
            Item = {
                'projectkey' :event["projectkey"],      
                'projectname':event["projectname"],
                'projectmanager':event["projectmanager"],
                'groupmembers': event["groupmembers"],
                "createdby" : event["createdby"]
                    }
                )
        ##sending email to group members
        client = boto3.client('ses' ) 
        name = event["projectmanager"]
        projectname = event["projectname"]  
        groupmembers = event["groupmembers"]   
        source = event["createdby"] 
        subject = 'projectupdate'

        body = f"""<html>
            <head></head>
            <body>
            <h2>'you have been added to project:{projectname}'</var></h2>
            <br/>
             
            </body>
            </html>
            """
    
        destination = groupmembers 

        _message = "Message from: " + name + "\nEmail: " + source + "\nMessage content: " + "added to new project"    
        
        email_message = client.send_email(
            
            Destination={
                'ToAddresses': [destination]
                },
            Message = {
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': body,
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': subject,
                },
            },
            Source=source,
    )
        message = "project added" + _message


    #add story
    elif action == "addstory":
        
        storyid = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = 7))
        table_stories.put_item(
        Item = {
            'projectkey' :event["projectkey"] ,      
            'storyid':storyid,
            'createdby':event["createdby"],
            'storydescription':event["storydescription"]
                    
             }
             )
        message = "story added" 


    #add task
    elif action == "addtask":
        taskid = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = 7))
                          
        table_tasks.put_item(
        Item = {
            'projectkey' :event["projectkey"] ,      
            'taskid':taskid,
            'createdby':event["createdby"],
            'taskdescription':event["taskdescription"],
            'assignedto':event["assignedto"],
            'startdate':event["startdate"],
            'enddate':event["enddate"],
            'taskstatus':event["taskstatus"]
        }
        ) 
        message = "task added"

    #add coment
    elif action == "addcomment":
         
        commentid = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = 7))
                        
        table_comments.put_item(
        Item = {
           'projectkey' :event["projectkey"] ,      
           'commentid':commentid,
           'commentedby':event["commentedby"],
           'comment':event["comment"],
            }
        ) 
        message="comment added"  


     # update task table
    elif action == "update":
        change = event["change"]
        projectkey = event["projectkey"]
        taskid = event["taskid"]
        if change == "startdate":
            table_tasks.update_item(
                Key = {   'projectkey':projectkey,
                        'taskid': taskid,
                    },
                UpdateExpression = "set startdate = :g",
                ExpressionAttributeValues = {
                        ':g': event["date"]
                    },
                ReturnValues = "UPDATED_NEW"
            )
            message = "task startdate changed"

             
        elif change == "enddate":
            table_tasks.update_item(
                    Key = {   'projectkey':projectkey,
                            'taskid': taskid,
                        },
                    UpdateExpression = "set enddate = :g",
                    ExpressionAttributeValues = {
                            ':g': event["date"]
                        },
                    ReturnValues = "UPDATED_NEW"
                )
            message = "task enddate changed"

        elif change == "status":
            table_tasks.update_item(
                    Key = {    'projectkey':projectkey,
                            'taskid': taskid,
                        },
                    UpdateExpression = "set taskstatus = :g",
                    ExpressionAttributeValues = {
                            ':g': event["taskstatus"]
                        },
                    ReturnValues = "UPDATED_NEW"
                )
            message = "task status changed" 


    #delete task by project manager
    elif action == "delete":
         projectkey = event["projectkey"]
         taskid = event["taskid"]
         email = event["email"]
         password = event["password"]

         response = table_projects.query(KeyConditionExpression = Key('projectkey').eq(projectkey))
         for item in response['Items']:
            pm = item.get('projectmanager')

         response = table_employee.query(KeyConditionExpression = Key('email').eq(email))
         for item in response['Items']:
            user = item.get('username')
            pw = item.get("password")
            
         if pm == user and password == pw:
              table_tasks.delete_item(Key = {'projectkey':projectkey, 'taskid': taskid}) 
              message = "item deleted by projectmanager" 
         else:
            message = "please check your credentials,only project managers can delete items from task table."
                

                             
    # list projects
    elif action == "projectlist":
                response = table_projects.scan()
                response['Items']
                p_list = []
                for elements in response['Items']:
                    p_list.append([elements.get('projectname'),elements.get('projetkey')])
                message = p_list
    
                                                          
    #SCRUMPAGE
    # LIST ALL STORIES,TASKS,COMMENTS OF A PROJECT BY TAKING PROJECTKEY AS INPUT.
    elif action == "scrumpage":
        projectkey = event["projectkey"]
        #getting project details
        response = table_projects.query(KeyConditionExpression = Key('projectkey').eq(projectkey))
        for item in response['Items']:
            project = item                                               
        #getting story details
        response = table_stories.query(KeyConditionExpression = Key('projectkey').eq(projectkey))
        stories = []
        for item in response['Items']:
            stories.append(item) 
        #getting tasks details
        tasks = []
        response = table_tasks.query(KeyConditionExpression = Key('projectkey').eq(projectkey))
        for item in response['Items']:
            tasks.append(item) 
        #getting comments
        comments = []
        response = table_comments.query(KeyConditionExpression = Key('projectkey').eq(projectkey))
        for item in response['Items']:
            comments.append(item)          
        message={"project":project,
                 "stories":stories,
                 "tasks":tasks,
                 "comments":comments
               }
                  
     

    response = {
        "statusCode": 200,
        'headers': {'Content-Type': 'application/json'},
        "body": json.dumps(message)
    }            

    return response
