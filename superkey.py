from cSRC.sha import encrypt, verify
from uuid import uuid4
import json
from cSRC.dbUser import Acc
from cSRC.inf import env as ENV
from web3 import Web3

password = str(uuid4())
wallet = Acc.get_acc_by_id(111)
w3 = Web3(Web3.HTTPProvider(ENV.ETH_NODE_URL))
pk = w3.to_hex(w3.eth.account.decrypt(wallet.private_key, wallet.encription))
new_pk = json.dumps(w3.eth.account.encrypt(pk, wallet.encription + password))
wallet.private_key = new_pk
wallet.save()
print(password)
e = encrypt(password)
with open("sk.json", "w") as f:
    f.write(json.dumps(e, indent=4))
