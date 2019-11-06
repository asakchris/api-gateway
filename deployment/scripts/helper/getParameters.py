import sys, json

# Read JSON file
with open(sys.argv[1]) as j_file:
    data = json.load(j_file)

param = ""
for key,value in data.iteritems():
    param += "{}={} ".format(key, value)

print param