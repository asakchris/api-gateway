import sys, json

with open(sys.argv[1]) as j_file:
    data = json.load(j_file)

for x in range(2, len(sys.argv)):
    data = data[sys.argv[x]]

print data