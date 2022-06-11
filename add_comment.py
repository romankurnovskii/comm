import sys
import json

arguments = sys.argv
file_name = arguments[1]
message = arguments[2]

a_file = open(file_name, "r")
json_object = json.load(a_file)
a_file.close()
json_object.append({"name": "John", "message": message})
a_file = open(file_name, "w")
json.dump(json_object, a_file)
a_file.close()
