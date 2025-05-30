import boto3
import botocore
import os

def s3_menu():  
    while True:
        print("\n S3 Menu")
        print("1. Bucket Operations")
        print("2. File operations")
        print("3. Return to main menu")

        try:
            s3menu_choice = int(input("Pick a number between 1-3: ").strip())
        except ValueError:
            print("Invalid input. Please pick a valid integer between 1 to 3: ")
            continue  

        if s3menu_choice == 1:
            bucket_operations_menu()
        
        elif s3menu_choice == 2:
            file_operations_menu()
        
        elif s3menu_choice == 3:
            print("Returning to main menu...")
            break 
        else:
            print("Invalid choice, please try again.")

def bucket_operations_menu():
    while True:
        print("\n Bucket Operations Menu")
        print("1. Create Bucket")
        print("2. List Buckets")
        print("3. Delete buckets")
        print("4. Return to S3 Menu")

        try:
            bucket_operation_choice = int(input("Please pick a number between 1-4: ").strip())
        except ValueError:
            print("Invalid input. Please pick an integer between 1-4: ")
            continue
        
        if bucket_operation_choice == 1:
            create_bucket()
        
        elif bucket_operation_choice == 2:
            list_buckets()
        
        elif bucket_operation_choice == 3:
            delete_buckets()
        
        elif bucket_operation_choice == 4:
            print("Returning to S3 Menu...")
            break
        else:
            print("Invalid choice, please try again.")


def create_bucket():
    session = boto3.session.Session()
    region = session.region_name

    if not region:
        print("No default AWS region found in your config. Set one using aws configure.")

    s3 = boto3.client('s3', region_name=region)
    bucket_name = input("Enter a name for a new bucket: ").strip().lower()

    if not bucket_name or len(bucket_name) <3 or len(bucket_name) > 25:
        print("Bucket name must be between 3 and 25 characters.")
        return
    
    try:
        if region == 'eu-east-1': ## AWS quirk: only us-east-1 throws error if CreateBucketConfiguration is included
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Bucket: {bucket_name} created successfully in region: {region}.")
    except botocore.exceptions.ClientError as e:
        print(f"Error creating bucket: {e.response['Error']['Message']}")
    
def list_buckets():
    s3 = boto3.client('s3')

    try:
        response = s3.list_buckets()
        buckets = response.get('Buckets', [])

        if not buckets:
            print("No S3 buckets were found.")
            return
        
        print ("\n Your buckets: ")
        for idx, bucket in enumerate(buckets, start=1):
            name = bucket['Name']
            created = bucket['CreationDate'].strftime("%Y-%m-%d %H:%M:%S")
            print(f"{idx}.{name} (Created on: {created})")
    
    except botocore.exceptions.ClientError as e:
        print(f"Error listing buckets: {e}")
                          

def delete_buckets():
    s3 = boto3.client('s3')

    try:
        response = s3.list_buckets()
        buckets = response.get('Buckets')

        if not buckets:
            print("No buckets found to delete")
            return
        
        print("\n Buckets available for deletion: ")
        for idx, bucket in enumerate(buckets,start=1):
            print(f"{idx}.{bucket['Name']}")
        
        while True:
            try:
                bucket_choice = int(input(f"Select a bucket to delete by number (1-{len(bucket)}) or 0 to  cancel: ").strip())
                if bucket_choice == 0:
                    print("Deletion cancelled.")
                    return
                if 1 <= bucket_choice <= len(buckets):
                    bucket_name = buckets[bucket_choice -1]['Name']
                    confirm = input(f"Are you sure you want to delete the bucket {bucket_name}? Can't be undone.(y/n): ").strip().lower()
                    if confirm == 'y':
                        s3.delete_bucket(Bucket=bucket_name)
                        print(f"Bucket {bucket_name} was successfully deleted.")
                        return
                    elif confirm == 'n':
                        print("Deletion cancelled")
                        return
                    else:
                        print("invalid input. Please type y or n (for yes or no).")
                else:
                        print(f"Please choose a number between 1 and {len(buckets)}, or 0 to cancel")
            except ValueError:
                print("Invalid input. Please enter an integer (number).")
    except botocore.excerptions.ClientError as e:
        print(f"Error deleting buckets: {e.response['Error']['Message']}")


def file_operations_menu():
    while True:
        print("\n File Operations Menu")
        print("1. Upload file.")
        print("2. List files.")
        print("3. Download files.")
        print("4. Delete file.")
        print("5. Return to S3 menu.")

        try:
            file_operation_choice = int(input("Please pick an option between 1-5: ").strip())
        except ValueError:
            print("Please enter an integer between 1-5: ")
            continue

        if file_operation_choice == 1:
            upload_file()
        
        elif file_operation_choice == 2:
            list_files()
        
        elif file_operation_choice == 3:
            download_files()
        
        elif file_operation_choice == 4:
            delete_file()
        
        elif file_operation_choice == 5:
            print("Returning to S3 Menu...")
            break
        else:
            print("Please pick a number between 1-5: ")


def upload_file():
    s3 = boto3.client('s3')

    file_path = input("Enter the full path of the file to upload (or type 'back' to return): ").strip().lower()
    if file_path == 'back':
        return 
    
    if not os.path.isfile(file_path):
        print("The file does not exist. Please check the path again.")
        return
    
    file_name = os.path.basename(file_path)

    bucket_name = input("Enter the name of the bucket to upload your file in (or type back to return): ").strip().lower()
    if bucket_name == 'back':
        return
    
    filename_askey = input(f"what should filename be named in the bucket? (Press enter to use {file_name}: ").strip().lower()
    if not filename_askey:
        filename_askey = file_name

    try:
        s3.upload_file(file_path,bucket_name,filename_askey)
        print(f"Successfully uploaded {file_path} to {bucket_name} as {filename_askey}.")
    except botocore.exceptions.ClientError as e:
        print(f"Failed to upload {e.response['Error']['Message']}")

def list_files():
    s3 = boto3.client('s3')

    bucket_name = input("Please enter the bucket that you're looking for (or enter 'back' to return): ").strip().lower()
    if bucket_name == 'back':
        return
    
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        contents = response.get('Contents')

        if not contents:
            print(f'No files found in bucket "{bucket_name}".')
            return
    
        print(f"\nFiles in bucket {bucket_name}")
        for idx, file in enumerate(contents, start=1):
            filename_askey = file['Key']
            size_kb = file['Size'] / 1024
            print(f"{idx}. {filename_askey}. ({size_kb})")

    except botocore.exceptions.ClientError as e:
        print()

def download_files():
    s3 = boto3.client('s3')
    
    bucket_name = input("Enter name of the bucket that you're calling from (or type 'back' to return): ").strip().lower()
    if bucket_name == 'back':
        return
    
    try:
        response = s3.list_objectsv2(Bucket=bucket_name)
        contents = response.get('Contents')

        if not contents:
            print(f"There is no file in {bucket_name}")
            return
        
        print(f"\nFiles availble in bucket: {bucket_name}.")
        for idx, file in enumerate(contents,start=1):
            print(f"{idx}.{file['Key']} ({file['Size'] / 1024:.2f} KB.")

        while True:
            try:
                file_choice = int(input(f"Pick a file from (1-{len(contents)} or 0 to cancel: )").strip())
                if file_choice == 0:
                    print("Download cancelled.")
                    return
                
                if 1 <= file_choice >= len(contents):
                    filename_askey = contents[file_choice - 1]['Key']
                    local_filename = input(f"What should the file be saved as locally? (enter to use {filename_askey} as default): ").strip().lower()
                    if not local_filename:
                        local_filename = filename_askey

                    s3.download_file(bucket_name,filename_askey,local_filename)
                    print(f"file {filename_askey} downloaded successfuly as {local_filename}")
                    return
                else:
                    print(f"Enter a number between 1 and {len(contents)} or 0 to cancel: ").strip().lower() #selfnote ask why u cant do .strip().lower() again.

            except ValueError:
                print("Invalid input, Please enter an integer.")

    except botocore.exceptions.ClientError as e:
        print(f"Error: {e.response['Error']['Message']}")

def delete_file():
    s3 = boto3.client('s3')

    bucket_name = input("Which bucket is the file you'd like to delete in? (or type 'back' to return): ").strip().lower()
    if bucket_name == 'back':
        return
    
    try:
        response = s3.list_objectsv2(Bucket=bucket_name)
        contents = response.get('Contents')

        if not contents:
            print(f"No contents exist in the {bucket_name}.")
            return
        
        print(f"\nFiles in bucket {bucket_name}: ")
        for idx,file in enumerate (contents,start=1):
            print(f"{idx}.{file['Key']} ({file['Size'] / 1024:.2f} KB.")

        while True:
            try: 
                file_choice = int(input(f"\nPick a file to delete (1-{len(contents)} or 0 to cancel): ").strip())
                if file_choice == 0:
                    return
                
                if 1<= file_choice >= len(contents):
                    filename_askey = contents[file_choice - 1]['Key']
                    confirm = input("Are you sure you want to permanently delete this file? (y / n): ").strip().lower()
                    if confirm == 'y':
                        s3.delete_object(Bucket=bucket_name, Key=filename_askey)
                        print(f"File {filename_askey} has been permanently deleted.")
                        return
                    
                    if confirm == 'n':
                        print("Deletion cancelled.")
                        return
                    
                    else:
                        print("Invalid input, please enter either the letter 'y' or 'n'. ")
                else:
                    print(f"Enter a valid number between 1-{len(contents)} or 0 to cancel.")
            except ValueError:
                print("Invalid input. Please enter an integer.")
    except botocore.exceptions.ClientError as e:
        print(f"Error: {e.response}['Error']['Message]")






