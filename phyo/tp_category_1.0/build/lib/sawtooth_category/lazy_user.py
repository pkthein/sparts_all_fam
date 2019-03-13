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

os.system('user register_init {} {} {} allow {}'.format(pub_key, user, email, role))

os.system(
	'category create {} genesis start {} {} &&'.format('8000', pri_key, pub_key) +
	'category create {} genesis start {} {} &&'.format('8001', pri_key, pub_key) +
	'category create {} genesis start {} {} &&'.format('8002', pri_key, pub_key) +
	'category create {} genesis start {} {} &&'.format('8003', pri_key, pub_key) +
	'category create {} genesis start {} {} &&'.format('8004', pri_key, pub_key) +
	'category create {} genesis start {} {} &&'.format('8005', pri_key, pub_key) +
	'category create {} genesis start {} {} &&'.format('8006', pri_key, pub_key) +
	'category create {} genesis start {} {} &&'.format('8007', pri_key, pub_key) +
	'category create {} genesis start {} {} &&'.format('8008', pri_key, pub_key) +
	
	'artifact create {} al name type sum lab chain {} {} &&'.format('8000', pri_key, pub_key) +
	'artifact create {} al name type sum lab chain {} {} &&'.format('8001', pri_key, pub_key) +
	'artifact create {} al name type sum lab chain {} {} &&'.format('8002', pri_key, pub_key) +
	'artifact create {} al name type sum lab chain {} {} &&'.format('8003', pri_key, pub_key) +

	'category update 8001 {} {} {} {} &&'.format('phyo', 'troll', pri_key, pub_key) +
	'category update 8001 {} {} {} {} &&'.format('trol', 'phyo', pri_key, pub_key) +
	'category update 8001 {} {} {} {} &&'.format('start', 'genesis', pri_key, pub_key) +
	'category update 8002 {} {} {} {} &&'.format('start', 'genesis', pri_key, pub_key) +
	
	'echo "====================PLEASE RUN THE FOLLOWING CHECKS====================" &&' +
	'echo category update 9000 {} {} {} {} &&'.format('genesis', 'start', pri_key, pub_key) +
	'echo category create 8000 {} {} {} {} &&'.format('start', 'genesis', pri_key, pub_key) +
	'echo category create 9000 {} {} {} {} &&'.format('genesis', 'start', pri_key, pub_key) +
	'echo category update 9000 {} {} {} {} &&'.format('start', 'genesis', pri_key, pub_key) +
	'echo "====================PLEASE RUN THE FOLLOWING CHECKS====================" &&' +
	'echo "======================================================================="'
	)
