import re
import json
from collections import Counter
from pprint import pprint
try:
    import requests
    from minet.twitter.utils import TwitterWrapper
except:
    sys.exit("ERROR: you first need to install 'requests' and 'minet' to run this code (using python3), for instance by running `pip install requests minet`")


stopwords_url = "https://raw.githubusercontent.com/stopwords-iso/stopwords-hi/master/stopwords-hi.txt"
stopwords = requests.get(stopwords_url).text.split("\n")
print(stopwords)


# Edit to fill your API keys here
t = TwitterWrapper({
    "access_token": "",
    "access_token_secret": "",
    "api_key": "",
    "api_secret_key": ""
})


# Collect last 200 tweets from a user
#user = "BhimArmyChief"
#cache = "tweets-@%s.json" % user
#try:
#    with open(cache) as f:
#        tweets = json.load(f)
#except:
#    tweets = t.call("statuses/user_timeline", args={"screen_name": user, "count": 200})
#    with open(cache, "w") as f:
#        json.dump(tweets, f)
#pprint(tweets)


# Collect all tweets from the last 8 days with a hashtag
hashtag = "ThanksDrAmbedkar"
cache = "tweets-#%s.json" % hashtag
try:
    with open(cache) as f:
        tweets = json.load(f)
except:
    tweets = []
    max_id = None
    while True:
        args = {"q":"#"+hashtag, "result_type": "recent", "tweet_mode": "extended", "count": 100}
        if max_id:
            args["max_id"] = max_id
        res = t.call("search/tweets", args=args)["statuses"]
        if not res:
            break
        for tw in res:
            tid = int(tw.get('id_str', str(tw.get('id', ''))))
            if not tid:
                continue
            if not max_id or max_id > tid:
                max_id = tid - 1
        tweets += res
        print(len(tweets), " tweets collected")
    with open(cache, "w") as f:
        json.dump(tweets, f)


# Use full_text or text from retweets
for t in tweets:
    if "retweeted_status" in t:
        t["text"] = t["retweeted_status"].get("full_text", t["retweeted_status"].get("text", ""))
    t["text"] = t.get("full_text", t.get("text", ""))
    #if hashtag.lower() not in t["text"].lower():
    #    print(t["text"])


# Remove urls, screennames, punctuation, RT at beginning of retweets and linebreaks
def clean_text(t):
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"@[a-zA-Z_0-9]+", "", t)
    t = re.sub(r"[,\.\?:…।\|\(\)\-]+", "", t)
    t = re.sub(r"^RT ", "", t)
    t = t.replace("\n", " ")
    t = t.replace("\r", " ")
    return t

# Extract top words
number_words = 50
texts = [clean_text(t["text"]) for t in tweets]
words = (" ".join(texts)).lower().split(" ")
keepwords = [w for w in words if w and w not in stopwords]
topwords = Counter(keepwords)
pprint(topwords.most_common(number_words))
