# registers the docker runner as admin

import os

file = open('keys.txt', 'r')

for line in file:
	os.system('echo ' + line)
	line = line.split()
	pri_key = line[line.index('{"private_key":') + 1][1:-2]
	pub_key = line[line.index('"public_key":') + 1][1:-3]	

user = os.environ['NAME_']
email = os.environ['EMAIL_']
role = os.environ['ROLE_']

os.system('user register_init {} {} {} allow {}'.format(
	pub_key, user, email, role))
