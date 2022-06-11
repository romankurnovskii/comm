import sys
import json
from datetime import datetime
import argparse

parser = argparse.ArgumentParser("parser")
parser.add_argument("file_name", help="")
parser.add_argument("author", help="")
parser.add_argument("message", help="")

args = parser.parse_args()

print(args)

a_file = open(args.file_name, "r")
json_object = json.load(a_file)
a_file.close()
json_object.append({"author": args.author, "message": args.message,
                   "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
a_file = open(args.file_name, "w")
json.dump(json_object, a_file)
a_file.close()
