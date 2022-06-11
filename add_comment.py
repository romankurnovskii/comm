import sys
import json
from datetime import datetime
arguments = sys.argv
file_name = arguments[1]
author = arguments[2]
message = arguments[3]

print(arguments)

a_file = open(file_name, "r")
json_object = json.load(a_file)
a_file.close()
json_object.append({"name": author, "message": message,
                   "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
a_file = open(file_name, "w")
json.dump(json_object, a_file)
a_file.close()
