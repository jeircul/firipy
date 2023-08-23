import os
from firipy import FiriAPI


token = os.environ['API_KEY_FIRI']
f = FiriAPI(token)
print(f.btc_Address())
