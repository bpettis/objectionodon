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
import mastodon
from mastodon import Mastodon

load_dotenv()


INSTANCE_URL = os.getenv('INSTANCE_URL')
ACCOUNT_INFO = {
    'username': os.getenv('USERNAME'),
    'password': os.getenv('PASSWORD'),
    'token': os.getenv('AUTHORIZATION_TOKEN')
}

m = Mastodon(access_token=ACCOUNT_INFO['token'], api_base_url=INSTANCE_URL)

def main():
    print("Creating Video...")


    # 115300524825583508 # just a single reply to one post
    # 109526457550799007 # longer thread, but only one person
    # 115306828741823840 # longer thread, and with a few different characters
    # 115307936418829951 - small thing for testing 

    starting_id = '115308156905626354'
    

    

    posts = getPosts(starting_id) # for testing
    
    print(f'Got {str(len(posts))} posts!')
    # Find the post which matches the starting id and remove it from posts - we don't want to include the one which was just summoning the bot
    for post in posts:
        if post['id'] == starting_id:
            posts.remove(post)
            break
    
    

    # Parse these into a list suitable for objection_engine
    comments = parsePosts(posts)

    # Render them
    output = f"output-{int(time.time())}.mp4"
    render_comment_list(comments, output_filename=output, resolution_scale=2)
    
    print(f"File saved to {output}")
    

    
    # Post the video as a reply to the original request
    postVideo(output, starting_id, ACCOUNT_INFO)

    # Cleanup the images that may have been created while parsing the posts
    for comment in comments:
        if comment.evidence_path:
            os.remove(comment.evidence_path)
            
    # Delete the video as well:
    os.remove(output)

    print("Done")
    
    
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
    comments = []
    for post in posts:
        if post['media_attachments']:
            downloadImage(post['media_attachments'][0]['url'], post['id'])
        comments.append(
            Comment(
                user_name="@" + post['account']['acct'],
                text_content=stripHtml(post['content']),
                evidence_path="image-" + str(post['id']) + ".jpg" if post['media_attachments'] else None
        ))
    return comments

def stripHtml(text):
    # Make the HTML to just plain text
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()
    text.replace("\n", " ")
    return text

def downloadImage(url, id):
    r = requests.get(url)
    name = f"image-{id}.jpg"
    with open(name, "wb") as f:
        f.write(r.content)

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

def postVideo(output, start_id, account_info):
    print("Posting video...")
        
    # Upload the video
    try:
        media = m.media_post(output, "video/mp4")
    except Exception as e:
        print(e)
    
    # Sleep for a few seconds to make sure it's uploaded
    time.sleep(5)
    
    # Post the status
    # , in_reply_to_id=start_id
    try:
        m.status_post("OBJECTION! \n\nYour video is now ready:", media_ids=[media['id']], in_reply_to_id=start_id)
    except Exception as e:
        print(e)
        return

if __name__ == "__main__":
    main()