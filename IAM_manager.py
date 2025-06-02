import boto3
import json
import os 
from botocore.exceptions import ClientError

iam = boto3.client('iam')
ec2 = boto3.client ('ec2')
s3 = boto3.client ('s3')


def register_user():
    username = input("Enter a username to register: ").strip()
    
    #Checks if username exists.
    try:
        iam.get_user(Username=username)
        print(f'User "{username}" already exists. Please try a different username.')
        return None
    except ClientError as e:
        if e.response['Error']['Code'] != 'NoSuchEntity':
            print(f"Unexpected error checking under: {e}")
            return None
        #if error is NosuchEntity, it means user doesnt exist so continue.

    #Now create user.
    try:
        iam.create_user(Username=username)
        print(f'IAM user "{username}" created')
        return username
    except ClientError as e:
        print(f"Error creating IAM user: {e}")
        return None


def attach_policies(username):
    # Define custom S3 policy to restrict to user's own bucket
    s3_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                f"arn:aws:s3:::timecapsule-{username}",
                f"arn:aws:s3:::timecapsule-{username}/*"
            ]
        }]
    }

    # Define custom EC2 policy allowing actions only on instances tagged with Owner=username
    ec2_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:DescribeInstances",
                "ec2:TerminateInstances"
            ],
            "Resource": "*",  # EC2 requires '*' resource with condition to restrict access
            "Condition": {
                "StringEquals": {
                    "ec2:ResourceTag/Owner": username
                }
            }
        }]
    }

    try:
        # Attach S3 inline policy
        iam.put_user_policy(
            UserName=username,
            PolicyName=f"{username}-S3-OwnBucketAccess",
            PolicyDocument=json.dumps(s3_policy)
        )
        # Attach EC2 inline policy
        iam.put_user_policy(
            UserName=username,
            PolicyName=f"{username}-EC2-TaggedInstanceAccess",
            PolicyDocument=json.dumps(ec2_policy)
        )
        print(f"Attached custom S3 and EC2 policies to user '{username}'")
    except ClientError as e:
        print(f"Error attaching policies: {e}")




########################

def create_access_keys(username):
    try:
        response = iam.create_access_key(UserName=username)
        access_key = response['AccessKey']['AccessKeyId']
        secret_key = response['AccessKey']['SecretAccessKey']
        print("Access keys generated.")
        return access_key, secret_key
    except ClientError as e:
        print(f"Error creating access keys: {e}")
        return None, None
    
def create_user_session(access_key, secret_key):
    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        return session
    except Exception as e:
        print(f"Error creating session: {e}")
        return None


def login():
    access_key = input("Please enter your access key: ").strip()
    secret_key = input("Please enter your secret key: ").strip()

    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

        sts_client = session.client('sts')
        sts_client.get_caller_identity()
        print("Login succesful")
        return session
    except Exception as e:
        print(f"Login failed: {e}")
        return None 

def delete_user(username):
    try:
        keys_response = iam.list_access_keys(UserName=username)
        for key in keys_response['AccessKeyMetadata']:
            iam.delete_access_key(UserName=username, AccessKeyID=key['AccessKeyId'])
            print(f"Deleted access key: {key['AccessKeyId']}")
    
        inline_policies = iam.list_user_policies(UserName=username)
        for policy_name in inline_policies['PolicyNames']:
            iam.delete_user_policy(UserName=username, PolicyName=policy_name)
            print(f"Deleted inline policy: {policy_name}")
        
        attached_policies = iam.list_attached_user_policies(UserName=username)
        for policy in attached_policies['AttachedPolicies']:
            iam.detach_user_policy(Username=username, PolicyArn=policy['PolicyArn'])
        
        iam.delete_user(Username=username)
        print(f"Deleted user {username} successfully.")
    
    except ClientError as e:
        print(f"Error deleting user {username}: {e}")


def logout_user():
    try:
        if os.path.exists("session_credentials.json"):
            os.remove("session_credentials.json")
            print("User logged out. Credential files deleted.")
        else:
            print("No session file found.")
    except Exception as e:
        print(f"Error logging out: {e}")




#MAYBE def list_users() for admin optional.