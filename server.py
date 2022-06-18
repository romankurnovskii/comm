from flask import request,Flask,render_template,redirect
from pymongo import MongoClient
from bson import json_util 
import datetime
import pprint
from flask_cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'



client = MongoClient()
client = MongoClient('mongodb://localhost:27017/')

db = client['test-database']
posts = db.posts
domains = db.domains
pages = db.pages
comments = db['comments']

print(17, comments)


def get_page_comments(page):
    return comments.find_one({"page": page}, {"_id":0})


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
        print(91, comment_data)
        comment = comment_data.get("comment")
        if comment:
            author = comment_data.get("author") or "Anonymous"
            parent_id = comment_data.get("parent_id")
            comment_id = create_page_comment(comment, referrer, author ,parent_id)
            print('created comment', comment_id)
    elif request.method == 'GET':
        comments_data = []
        comments = get_page_comments(referrer)
        if  comments:
            comments_data = [comment for comment in comments.get("comments", [])]
        return {"page": referrer, "comments": comments_data}


    # comments_data = [comment for comment in comments]

    # print(list(comments))
    # dd = list(comments)

    return {}


@app.route("/")
def hello_world():
    r = request.args
    pprint.pprint([request.url, request.url_root, '----',request.path])
    # data = request.get_json()
    pprint.pprint(r)
    return f"<p>Hello, World!{r}</p>"


if __name__ == "__main__":
    app.run()