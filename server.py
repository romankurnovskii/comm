import os
from flask import request,Flask,render_template,redirect
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
import datetime

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


MONGO_CONNECTION_STRING = os.environ.get("MONGO_CONNECTION_STRING", default='mongodb://localhost:27017/')
MONGO_DB_COLLECTION = os.environ.get("MONGO_DB_COLLECTION", default="test-database")

client = MongoClient()
client = MongoClient(MONGO_CONNECTION_STRING)

db = client[MONGO_DB_COLLECTION]
posts = db.posts
domains = db.domains
pages = db.pages
comments = db['comments']

print(17, comments)


def get_page_comments(page):
    return comments.find_one({"page": page}, {"_id":0})

def update_page_view_count(page):
    comments.update_one(
        {"page": page},
        {
            "$inc": {"views": 1},
        },
        upsert=True)


def create_page_comment(comment, page=None, author=None, parent_id=None):
    comment_data = {
        "author": author or "Anonymous",
        "comment": comment,
        "date": datetime.datetime.utcnow()
    }
    if parent_id:
        comment_data["parent_id"] = parent_id

    res = comments.update_one(
        {"page": page}, 
        {"$push": {"comments": comment_data}},
        upsert=True)
    print( res.modified_count, res, comments.count_documents({})) 

    return res


def create_url_domain(url):
    domain_data = {
        "url": url,
        "date": datetime.datetime.utcnow()
    }
    return domains.insert_one(domain_data)



def create_comment(comment, author=None, parent_id=None):
    comment_data = {
        "author": author or "Anonymous",
        "comment": comment,
        "date": datetime.datetime.utcnow()
    }
    if parent_id:
        comment_data["parent_id"] = parent_id
    return comments.insert_one(comment_data)

def create_url_page(url, domain_id):
    page_data = {
        "url": url,
        "domain_id": domain_id,
        "date": datetime.datetime.utcnow()
    }
    return pages.insert_one(page_data)

@app.route("/comments", methods=['GET', 'POST'])
def comments_handler():

    # print(request.form)
    # print(request.data)
    # print(request.headers)
    referrer = request.args.get('page')
    # print(request.get_json())

    comment = None

    if request.method == 'POST':
        comment_data = request.get_json()
        comment = comment_data.get("comment")
        if comment:
            author = comment_data.get("author") or "Anonymous"
            parent_id = comment_data.get("parent_id")
            comment_id = create_page_comment(comment, referrer, author ,parent_id)
            print('created comment', comment_id)
    elif request.method == 'GET':
        update_page_view_count(referrer)
        comments_data = []
        result = {"page": referrer, "comments": comments_data}
        comments_fetched = get_page_comments(referrer)
        if  comments_fetched:
            comments_data = [comment for comment in comments_fetched.get("comments", [])]
            result['page_views'] = comments_fetched.get('views', 0)
            result['comments'] = comments_data
        return result


    # comments_data = [comment for comment in comments]

    # print(list(comments))
    # dd = list(comments)

    return {}


@app.route("/")
def hello_world():
    r = request.args
    return f"<p>Hello, World!{r}</p>"


if __name__ == "__main__":
    app.run()