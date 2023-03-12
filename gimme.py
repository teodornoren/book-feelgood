import os

data = open("file", "w")
for q in (os.getenv("MY_VAL")):
    print(q)
    data.write(q)