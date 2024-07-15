import subprocess

import re

# run python gmm.py
res = subprocess.run(["python", "gmm.py"], stdout=subprocess.PIPE)
res = res.stdout.decode()
pattern = r"\{.*?\}"
res = re.findall(pattern, res)

# convert res to dict
print(res[-1])
print(type(res[-1]))
