import re

with open("ids.txt", "r") as file:
    lines = file.readlines()
id_pattern = r"(\d+)"
ids = [
    re.search(id_pattern, line).group(1)
    for line in lines
    if re.search(id_pattern, line)
]
from cSRC.dbUser import dbUser, Acc

for i in ids:
    i = int(i)
    user_data = dbUser.get_user_by_id(i)
    user_data.delete()
    print(f"user deleted {i}")
    acc_data = Acc.get_acc_by_id(i)
    acc_data.delete()
    print(f"account_deleted {i}")
