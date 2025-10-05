import re, os
import mastodon
from mastodon import Mastodon
from dotenv import load_dotenv

load_dotenv()


INSTANCE_URL = os.getenv('INSTANCE_URL')
ACCOUNT_INFO = {
    'username': os.getenv('USERNAME'),
    'password': os.getenv('PASSWORD'),
    'token': os.getenv('AUTHORIZATION_TOKEN')
}
BLACKLIST_FILE = os.getenv('BLACKLIST_FILE') if os.getenv('BLACKLIST_FILE') else 'blacklist.txt'

DEBUG_MODE = os.getenv('DEBUG_MODE') if os.getenv('DEBUG_MODE') else False
if DEBUG_MODE == 'True' or DEBUG_MODE == 'true' or DEBUG_MODE == '1':
    DEBUG_MODE = True
else:
    DEBUG_MODE = False

m = Mastodon(access_token=ACCOUNT_INFO['token'], api_base_url=INSTANCE_URL)

def main():
    # Check the account's DMs 
    notifications = m.notifications(limit=50, types=['mention'])
    if len(notifications) == 0:
        print("No mentions found!")
        quit()
        
    for notification in notifications:
        if notification['status']['visibility'] == 'direct':
            if DEBUG_MODE:
                print(notification['status']['visibility'])
                print(notification['status']['id'])
                print(notification['status']['account']['acct'])
            
            # Rudimentary handling for local vs federated accounts:
            if re.search(r'@(\s\w+|\w+)', notification['status']['account']['acct']):
                username = notification['status']['account']['acct']
            else:
                username = notification['status']['account']['acct'] + '@' + re.sub(r'http[s]?://', '', INSTANCE_URL)
            
            with open(BLACKLIST_FILE, "a") as f:
                f.write(username + "\n")
            print(f'Added {username} to blacklist')
            m.notifications_dismiss(notification['id'])

    

if __name__ == "__main__":
    main()