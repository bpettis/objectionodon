import objection_engine
from objection_engine.renderer import render_comment_list
from objection_engine.beans.comment import Comment
from objection_engine import anim
from bs4 import BeautifulSoup
import requests
import json
import time
import os


INSTANCE_URL = 'https://mastodon.benpettis.ninja'

def main():
    print("Creating Video...")

    # Get a set of posts/replies
    # posts = getPosts('115300524825583508') # just a single reply to one post
    # posts = getPosts('109526457550799007') # longer thread, but only one person
    # posts = getPosts('115306828741823840') # longer thread, and with a few different characters
    posts = getPosts('115307936418829951') # for testing
    
    print(f'Got {str(len(posts))} posts!')

    # Parse these into a list suitable for objection_engine
    comments = parsePosts(posts)

    # Render them
    output = f"output-{int(time.time())}.mp4"
    render_comment_list(comments, output_filename=output, resolution_scale=2)
    
    print(f"File saved to {output}")
    

    
    # Post the video as a reply to the original request
    

    # Cleanup the images that may have been created while parsing the posts
    for comment in comments:
        if comment.evidence_path:
            os.remove(comment.evidence_path)
            
    # Delete the video as well:
    

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

if __name__ == "__main__":
    main()