import objection_engine
from objection_engine.renderer import render_comment_list
from objection_engine.beans.comment import Comment
from objection_engine import anim
from bs4 import BeautifulSoup
import requests
import json
import time
import os
from dotenv import load_dotenv
import re
import mastodon
from mastodon import Mastodon

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

additional_message = '''
Don't want to see these posts? You can add @objectionodon@benpettis.ninja to your ignore list. DM @objectionodon@benpettis.ninja if you'd like your posts to be excluded from any animations.
'''

m = Mastodon(access_token=ACCOUNT_INFO['token'], api_base_url=INSTANCE_URL)

def main():
    print("Raising Objections...")

    # Get unread notifications and find any mentions
    notifications = m.notifications(limit=50, types=['mention'])
    if len(notifications) == 0:
        print("No mentions found!")
        quit()
        
    for notification in notifications:
        # check that the post is either 'public' or 'unlisted' so we can skip anything private:
        if notification['status']['visibility'] == 'private' or notification['status']['visibility'] == 'direct':
            print("Not a public post! Skipping...")
            continue

        
        print(notification['status']['id'])
        
        starting_id = notification['status']['id']
        if processThread(starting_id):
            # Delete the notification because we've processed it
            m.notifications_dismiss(notification['id'])
        else:
            # Something in the processing went wrong - so keep the notification present
            print("Something went wrong!")
    print("Done")
    
def processThread(starting_id):
    print(f"Processing thread summoned by post #{starting_id}...")
    posts = getPosts(starting_id) # retrieve a list of all the Mastodon post objects in the thread
    
    print(f'Got {str(len(posts))} posts!')
    
    # If the bot has already responded in the thread, skip it
    # for post in posts:
    #     if ACCOUNT_INFO['username'] in post['account']['username']:
    #         return False
    
    # Find the post which matches the starting id and remove it from posts - we don't want to include the one which was just summoning the bot
    for post in posts:
        if post['id'] == starting_id:
            posts.remove(post)
            break
    
    # Remove any posts from the blacklist
    blacklist = [line.rstrip('\n') for line in open(BLACKLIST_FILE, "r").readlines()]


    
    for post in posts:
        print(post['account']['acct'])
        # Most blacklist entries will be in the form of username@server
        # This works fine because any foreign accounts in post['account']['acct'] will be in the form of username@server
        # But if there is a username on the same server as the bot, then post['account']['acct'] will be in the form of username
        # So we need to check if post['account']['acct'] is local to our server (e.g. if it has an @ in it) and if so, append the servername before comparaing against the blacklist
        if not '@' in post['account']['acct']:
            check_name = post['account']['acct'] + '@' + re.sub(r'http[s]?://', '', INSTANCE_URL)
            print(f'Updated local username to {check_name}')
        else:
            check_name = post['account']['acct']
            
        if check_name in blacklist:
            print(f"Skipping post/reply from: {post['account']['acct']}")
            posts.remove(post)

    if len(posts) == 0:
        print("No posts left! Skipping this thread")
        return True

    if DEBUG_MODE:
        for post in posts:
            print(post)
            print("---")

    # Parse these into a list suitable for objection_engine
    comments = parsePosts(posts)
   

    # Render them
    output = f"output-{int(time.time())}.mp4"
    print("Rendering comments using objection_engine...")
    render_comment_list(comments, output_filename=output, resolution_scale=3)
    
    print(f"File saved to {output}")
    

    status = False
    # Post the video as a reply to the original request
    if DEBUG_MODE:
        print(f"Debug mode enabled - not actually posting the video")
    else:
        if postVideo(output, starting_id, posts):
            print("Video was posted!")
            status = True

    # Cleanup the images that may have been created while parsing the posts
    for comment in comments:
        if comment.evidence_path:
            os.remove(comment.evidence_path)
            
    # Delete the video as well:
    if DEBUG_MODE:
        print(f"Debug mode enabled - retaining video file {output}")
    else:
        os.remove(output)
       
    # status = True if video was posted successfully
    # status = False is something went wrong
    return status
    
def getPosts(start_id):
    try:
        r =  requests.get(INSTANCE_URL + "/api/v1/statuses/" + str(start_id))
        data = r.json()

        
        posts = []
        posts.append(data)
        
        if data['in_reply_to_id']:
            posts.extend(getPosts(data['in_reply_to_id']))
        
        # Put these in chronological order
        # Sort by the data['created_at'] value:
        posts.sort(key=lambda x: x['created_at'])
        return posts
    except Exception as e:
        print(e)
        return [] 

def parsePosts(posts):
    print("Parsing posts...")
    comments = []
    for post in posts:
        print(post['id'])
        has_image = False
        if len(post['media_attachments']) > 0:
            if post['media_attachments'][0]['type'] == 'image':
                if downloadImage(post['media_attachments'][0]['url'], post['id']):
                    has_image = True

        
        # TO-DO: See if there's an easy-ish way to get a thumbnail for a URL in the post - and use that as the "evidence_path"
        comments.append(
            Comment(
                user_name="@" + post['account']['acct'],
                text_content=formatText(post['content']),
                evidence_path="image-" + str(post['id']) + ".jpg" if has_image else None
        ))
    return comments

def formatText(text):
    text = stripHtml(text)
    text = re.sub(r'@(\s\w+|\w+)', '', text) # Remove any @usernames
    text = re.sub(r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])', '[Link from \\2]', text) # replace any URLs with a shorter version
    text.replace("\n", " ") # Replace newlines with spaces
    
    # But there's a possibility that the text is entirely blank! And that will cause the renderer to break. So let's check if the text is empty and fix it:
    if len(text) == 0:
        text = "..."
    return text

def stripHtml(text):
    # Make the HTML to just plain text
    soup = BeautifulSoup(text, 'html.parser')
    # Remove anything with class="invisible"
    for tag in soup.find_all(class_="invisible"):
        tag.decompose()
        
    # Find any <a> tags and replace them with their href attribute -- so we can process the URL later on
    for tag in soup.find_all('a'):
        # Check if it has the class "mention" and skip this next part if so - otherwise we'll end up with gross [Link to .... ] anytime there is an @mention
        if tag.has_attr('class') and 'mention' in tag['class']:
            continue
        tag.replace_with(tag['href'])
        
    text = soup.get_text(separator=' ')
    return text

def downloadImage(url, id):
    r = requests.get(url)
    
    if r.status_code != 200:
        print(f"Failed to download image {url}")
        return False
    
    name = f"image-{id}.jpg"
    with open(name, "wb") as f:
        f.write(r.content)
    return True

def authorize(ACCOUNT_INFO):
    # curl -X POST \
	# -F 'client_id=your_client_id_here' \
	# -F 'client_secret=your_client_secret_here' \
	# -F 'redirect_uri=urn:ietf:wg:oauth:2.0:oob' \
	# -F 'grant_type=client_credentials' \
	# https://mastodon.example/oauth/token
 
    r = requests.post(
        INSTANCE_URL + "/oauth/token",
        data={
            'client_id': ACCOUNT_INFO['client_id'],
            'client_secret': ACCOUNT_INFO['client_secret'],
            'grant_type': 'client_credentials',
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob'
        }
    )
    data = r.json()
    ACCOUNT_INFO['token'] = data['access_token']
    print('Authorized successfully!')
    return

def postVideo(output, start_id, posts):
    print("Posting video...")
    
    
    usernames = []
    
    for post in posts:
        usernames.append('@' + post['account']['acct'])
    # Join the usernames into a single string
    # use set() to remove any duplicates -- avoids spamming names multiple times.
    usernames = " ".join(set(usernames))
    
    
    # TO-DO: Add a check to see if this message exceeds the character limit - and if so trim the usernames list
    message = "OBJECTION! \n\nYour video is now ready. \n\n\n" + usernames + '\n\n\n' + additional_message
    print(message)

    
    # Upload the video
    try:
        media = m.media_post(output, "video/mp4")
    except Exception as e:
        print(e)
    
    # Sleep for a few seconds to make sure it's uploaded
    # TO-DO: Come up with a way to just check the status of the media and use that to decide when to continue
    time.sleep(30)
    
    # Post the status
    # , in_reply_to_id=start_id
    try:
        m.status_post(message, media_ids=[media['id']], in_reply_to_id=start_id)
        return True
    except Exception as e:
        print(e)
        return False

if __name__ == "__main__":
    main()