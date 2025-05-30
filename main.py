import sys
import EC2_manager
import S3_manager
import IAM_manager


def login_menu():
    print("\nWelcome to the Digital Time Capsule!")
    while True:
        print("\n1.Login")
        print("2.Register")
        print("3.Exit")

        try:
            choice = int(input("Which number would you like to select (1-3): ").strip())
        except ValueError:
            print("Invalid input. Please choose an integer between 1-3.")
            continue 

        if choice == 1:
            return handle_login()
        
        if choice == 2:
            return register_login()

        if choice == 3:
            print("Exiting programme, goodbye!")
            sys.exit()
        else:
            print("Invalid option. Choose an integer 1-3. ")
            return 
        
def handle_login():
    username, session = IAM_manager.login_user()
    if session:
        return username, session
    print("Login failed. Try again")
    return None, None

def register_login():
    username, session = IAM_manager.register_user()
    if session:
        return username, session
    print("Registration failed. Try again.")
    return None, None


def main_menu():
    while True:
        print("\n DIGITAL TIME CAPSULE MENU")
        print("1. EC2 Menu")
        print("2. S3 Menu")
        print("3. Logout")
        print("4. Exit)")

        try:
            choice = int(input("Which number would you like to select (1-4): ").strip())
        except ValueError:
            print("Please enter a valid number.")
            continue

        if choice == 1:
            EC2_manager.ec2_menu()
        
        elif choice == 2:
            S3_manager.s3_menu()
        
        elif choice == 3:
            print("Logging out...")
            return
        
        elif choice == 4:
            print("Goodbye")
            break
        else:
            print("Invalid choice please select a number between 1 and 4.")

if __name__ == "__main__":
    main_menu()
    while True:
        username, session = login_menu()
        main_menu(session,username)
