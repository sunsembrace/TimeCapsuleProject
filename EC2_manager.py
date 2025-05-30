import boto3
import time 

def ec2_menu():
    while True:
        print("\n EC2 MENU")
        print("1. Launch EC2 instance")
        print("2. Manage EC2 instances")
        print("3. Return to main menu")

        try:
            choice = int(input("Select an option (1-3): ").strip())
        except ValueError:
            print("Please enter a valid number: ")
            continue 

        if choice == 1:
            launch_instance()
        
        elif choice == 2:
            manage_instances()
        
        elif choice == 3:
            print("Returning to main menu...")
            break
        else:
            print("Invalid choice. Please pick a number between 1-3.")


import boto3

def launch_instance():
    ec2 = boto3.client('ec2')

    while True:
        instance_name = input("Enter a name for your EC2 instance: ").strip().lower()
        if not instance_name:
            instance_name = 'DefaultEC2instance'

        try:
            print("\nLaunching EC2 instance...")
            response = ec2.run_instances(
                ImageId='ami-0fc32db49bc3bfbb1',
                MinCount=1,
                MaxCount=1,
                InstanceType='t2.micro',
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': instance_name},
                        {'Key': 'Project', 'Value': 'DigitalTimeCapsule'}
                    ]
                }]
            )

            instance_id = response['Instances'][0]['InstanceId']
            print(f"Created EC2 Instance with ID: {instance_id}")

            print("Waiting 10s for Instance to enter running state...")
            ec2_resource = boto3.resource('ec2')
            instance = ec2_resource.Instance(instance_id)
            instance.wait_until_running()

            instance.load()
            public_ip = instance.public_ip_address
            if not public_ip:
                print("Warning. No public IP assigned. Check subnet settings or use an Elastic IP")

            print(f"Instance is running. Public IP address {public_ip}")
            print("You can now SSH into your instance")
            break  # Exit loop after successful launch

        except Exception as e:
            print("Error launching EC2: ", str(e))
            retry = input("Would you like to try again? (y/n): ").strip().lower()
            if retry != 'y':
                break

##############################
def list_instances():
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()

    instances = []
    print('\n--- Your EC2 Instances ---')
    count = 1 
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            state = instance['State']['Name']
            name = "N/A"
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        name = tag['Value']
            print(f"{count}. ID: {instance_id} | State: {state} | Name: {name}")
            instances.append({
                'InstanceId': instance_id,
                'State': state,
                'Name': name
            })
            count += 1
    return instances

def manage_instances():
    ec2 = boto3.client('ec2')

    instances = list_instances()

    if not instances:
        print("No EC2 instances found.")
        return 

    print("\n Available Instances:")
    for idx, instance in enumerate(instances, start = 1):
        print(f"{idx}. ID: {instance['InstanceId']}, State: {instance['State']}")

    while True: 
        try:
            selection = int(input("Select an instance by number (or 0 to go back): ").strip())
            if selection == 0:
                return
            if selection < 1 or selection > len(instances):
                print(f"Please enter a number between 1 and {len(instances)}.")
                continue
            selected_instance = instances[selection -1]
            break
        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid number.")
            continue
    
    instance_id = selected_instance['InstanceId']
    print(f"\n You selected: {instance_id} (State: {selected_instance['State']}, Name: {selected_instance['Name']})")
    
    while True:   
        print(f"\n What would you like to do?")
        print("1. Start instance")
        print("2. Stop instance")
        print("3. Reboot instance")
        print("4. Terminate instance")
        print("5. back to EC2 Menu")

        try:
            action = int(input("Choose a number between 1-5: ").strip())
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5")
            continue 

        if action == 1:
            start_instance(ec2, instance_id)

        elif action == 2:
            stop_instance(ec2, instance_id)
        
        elif action == 3:
            reboot_instance(ec2, instance_id)
        
        elif action == 4:
            terminate_instance(ec2, instance_id)

        elif action == 5:
            print("Returning to EC2 menu")
            break
        else:
            print("Invalid choice, please select a number between 1 and 5")

def start_instance(ec2, instance_id):
    try:
        ec2.start_instances(InstanceIds=[instance_id])
        print(f"Starting instance {instance_id}")
        waiter = ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        print(f"Instance {instance_id} is now running.")
        new_state = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]['State']['Name']
        print(f"New state of instance {instance_id}: {new_state}")
    except Exception as e:
        print(f"Failed to start instance: {e}")

def stop_instance(ec2, instance_id):
    try:
        ec2.stop_instances(InstanceIds=[instance_id])
        print(f"Stopping instance {instance_id}")
        waiter = ec2.get_waiter('instance_stopped')
        waiter.wait(InstanceIds=[instance_id])
        print(f"Instance {instance_id} has now stopped.")
        new_state = ec2.describe_instances(InstanceIds = [instance_id])['Reservations'][0]['Instances'][0]['State']['Name']
        print(f"New state of instance {instance_id}: {new_state}")
    except Exception as e:
        print(f"Failed to stop instance: {e}")

def reboot_instance(ec2, instance_id):
    try:
        ec2.reboot_instances(InstanceIds=[instance_id])
        print(f"Rebooting instance {instance_id}")
        time.sleep(10)
        waiter = ec2.get_waiter('instance_status_ok')
        waiter.wait(InstanceIds=[instance_id])
        print(f"Instance {instance_id} is back to OK status.")
        new_state = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]['State']['Name']
        print(f"New state of instance {instance_id}: {new_state}")
    except Exception as e:
        print(f"Failed to reboot instance: {e}")

def terminate_instance(ec2, instance_id):
    confirm = input("Are you sure you want to terminate this instance? (y/n): ").strip().lower()
    if confirm == 'y':
        try:
            ec2.terminate_instances(InstanceIds=[instance_id])
            print(f"Terminating instance {instance_id}")
            waiter = ec2.get_waiter('instance_terminated')
            waiter.wait(InstanceIds=[instance_id])
            print(f"Instance {instance_id} has been terminated.")
        except Exception as e:
            print(f"Failed to terminate instance: {e}")
        return 
    elif confirm == 'n':
        print("Termination cancelled.")
        return
    else:
        print("Invalid input. Please enter 'y' for yes or 'n' for no: ")
