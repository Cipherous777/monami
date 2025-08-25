import praw
import json

reddit = praw.Reddit(
    client_id='56h2QdVyxm4zH-_BwYIFGw',
    client_secret='MgVIRhxU9F7K__Ji-DpacmrKN7okUA',
    user_agent='MonamiDataBot/0.1 by Cipherous'
)

# Choose subreddits
subreddits = ['teenagers', 'offmychest', 'depression', 'Anxiety']

dataset = []

for sub in subreddits:
    subreddit = reddit.subreddit(sub)
    for post in subreddit.hot(limit=50):  # top 50 posts
        if post.selftext:
            # Combine title + selftext
            post_text = f"{post.title}\n{post.selftext}".strip()
            
            # Collect top-level comments (skip deleted or removed)
            comments = []
            post.comments.replace_more(limit=0)  # flatten the comment tree
            for comment in post.comments.list():
                if comment.body not in ["[deleted]", "[removed]"]:
                    comments.append(comment.body.strip())
            
            # Create AI dataset entries
            if comments:
                for comment_text in comments:
                    dataset.append({
                        "text": f"User: {post_text}\nAI: {comment_text}"
                    })
            else:
                # If no comments, just include the post
                dataset.append({
                    "text": f"User: {post_text}\nAI: "
                })

# Save to JSON
with open("reddit_monami.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print("Dataset saved with post + top-level comments!")
