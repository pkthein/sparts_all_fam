# registers the docker runner as admin

import os

file = open('keys.txt', 'r')
displace = ['{', '}', ':', '"']

for line in file:
	os.system('echo ' + line)
	for char in displace:
		line = line.replace(char, '')
	line = line.split()

pri_key = line[1][:-1]
pub_key = line[-1]	

user = os.environ['NAME_']
email = os.environ['EMAIL_']
role = os.environ['ROLE_']

os.system('user register_init {} {} {} allow {}'.format(
	pub_key, user, email, role))
