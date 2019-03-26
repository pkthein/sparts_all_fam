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

os.system('user register_init {} {} {} allow {}'.format(pub_key, user, email, role))

os.system(
	# 'category create {} genesis start {} {} &&'.format('8000', pri_key, pub_key) +
	# 'category create {} genesis start {} {} &&'.format('8001', pri_key, pub_key) +
	# 'category create {} genesis start {} {} &&'.format('8002', pri_key, pub_key) +
	# 'category create {} genesis start {} {} &&'.format('8003', pri_key, pub_key) +
	# 'category create {} genesis start {} {} &&'.format('8004', pri_key, pub_key) +
	# 'category create {} genesis start {} {} &&'.format('8005', pri_key, pub_key) +
	# 'category create {} genesis start {} {} &&'.format('8006', pri_key, pub_key) +
	# 'category create {} genesis start {} {} &&'.format('8007', pri_key, pub_key) +
	# 'category create {} genesis start {} {} &&'.format('8008', pri_key, pub_key) +
	
	# 'artifact create {} al name type sum lab chain {} {} &&'.format('8000', pri_key, pub_key) +
	# 'artifact create {} al name type sum lab chain {} {} &&'.format('8001', pri_key, pub_key) +
	# 'artifact create {} al name type sum lab chain {} {} &&'.format('8002', pri_key, pub_key) +
	# 'artifact create {} al name type sum lab chain {} {} &&'.format('8003', pri_key, pub_key) +
	
	# 'organization create {} al name type des url {} {} &&'.format('8000', pri_key, pub_key) +
	# 'organization create {} al name type des url {} {} &&'.format('8001', pri_key, pub_key) +
	# 'organization create {} al name type des url {} {} &&'.format('8002', pri_key, pub_key) +
	# 'organization create {} al name type des url {} {} &&'.format('8003', pri_key, pub_key) +
	
	# 'pt create {} name sum ver al lic lab des {} {} &&'.format('8000', pri_key, pub_key) +
	# 'pt create {} name sum ver al lic lab des {} {} &&'.format('8001', pri_key, pub_key) +
	# 'pt create {} name sum ver al lic lab des {} {} &&'.format('8002', pri_key, pub_key) +
	# 'pt create {} name sum ver al lic lab des {} {} &&'.format('8003', pri_key, pub_key) +
	
	# 'category amend 8001 {} {} {} {} &&'.format('phyo', 'troll', pri_key, pub_key) +
	# 'category amend 8001 {} {} {} {} &&'.format('trol', 'phyo', pri_key, pub_key) +
	# 'category amend 8001 {} {} {} {} &&'.format('start', 'genesis', pri_key, pub_key) +
	# 'category amend 8002 {} {} {} {} &&'.format('start', 'genesis', pri_key, pub_key) +
	
	# 'artifact amend {} {} name type sum lab chain {} {} &&'.format('8001', 'ali', pri_key, pub_key) +
	# 'artifact amend {} {} name type sum lab chain {} {} &&'.format('8001', 'alia', pri_key, pub_key) +
	# 'artifact amend {} {} name type sum lab chain {} {} &&'.format('8001', 'alias', pri_key, pub_key) +
	# 'artifact amend {} {} name type sum lab chain {} {} &&'.format('8002', 'ali', pri_key, pub_key) +
	
	# 'organization amend {} {} name type des url {} {} &&'.format('8001', 'ali', pri_key, pub_key) +
	# 'organization amend {} {} name type des url {} {} &&'.format('8001', 'alia', pri_key, pub_key) +
	# 'organization amend {} {} name type des url {} {} &&'.format('8001', 'alias', pri_key, pub_key) +
	# 'organization amend {} {} name type des url {} {} &&'.format('8002', 'ali', pri_key, pub_key) +
	
	# 'pt amend {} name sum ver {} lic lab des {} {} &&'.format('8001', 'ali', pri_key, pub_key) +
	# 'pt amend {} name sum ver {} lic lab des {} {} &&'.format('8001', 'alia', pri_key, pub_key) +
	# 'pt amend {} name sum ver {} lic lab des {} {} &&'.format('8001', 'alias', pri_key, pub_key) +
	# 'pt amend {} name sum ver {} lic lab des {} {} &&'.format('8002', 'ali', pri_key, pub_key) +
	
	# 'organization AddPart {} {} {} {} &&'.format('8000', '8000', pri_key, pub_key) +
	# 'organization AddPart {} {} {} {} &&'.format('8000', '8001', pri_key, pub_key) +
	# 'organization AddPart {} {} {} {} &&'.format('8000', '8002', pri_key, pub_key) +
	# 'organization AddPart {} {} {} {} &&'.format('8001', '8003', pri_key, pub_key) +
	
	# 'pt AddSupplier {} {} {} {} &&'.format('8000', '8000', pri_key, pub_key) +
	# 'pt AddSupplier {} {} {} {} &&'.format('8001', '8000', pri_key, pub_key) +
	# 'pt AddSupplier {} {} {} {} &&'.format('8002', '8000', pri_key, pub_key) +
	# 'pt AddSupplier {} {} {} {} &&'.format('8003', '8001', pri_key, pub_key) +
	
	# 'pt AddArtifact {} {} {} {} &&'.format('8000', '8000', pri_key, pub_key) +
	# 'pt AddArtifact {} {} {} {} &&'.format('8001', '8000', pri_key, pub_key) +
	# 'pt AddArtifact {} {} {} {} &&'.format('8002', '8000', pri_key, pub_key) +
	# 'pt AddArtifact {} {} {} {} &&'.format('8003', '8001', pri_key, pub_key) +
	
	# 'pt AddCategory {} {} {} {} &&'.format('8000', '8000', pri_key, pub_key) +
	# 'pt AddCategory {} {} {} {} &&'.format('8001', '8000', pri_key, pub_key) +
	# 'pt AddCategory {} {} {} {} &&'.format('8002', '8000', pri_key, pub_key) +
	# 'pt AddCategory {} {} {} {} &&'.format('8003', '8001', pri_key, pub_key) +
	
	# 'artifact AddArtifact {} {} {} {} {} &&'.format('8000', '8000', 'path', pri_key, pub_key) +
	# 'artifact AddArtifact {} {} {} {} {} &&'.format('8001', '8000', 'path', pri_key, pub_key) +
	# 'artifact AddArtifact {} {} {} {} {} &&'.format('8002', '8000', 'path', pri_key, pub_key) +
	# 'artifact AddArtifact {} {} {} {} {} &&'.format('8003', '8001', 'path', pri_key, pub_key) +
	
	# 'artifact AddURI {} {} {} {} {} {} {} {} {} &&'.format('8000', '000', 'cs', 'ct', 'size', 'ut', 'loc', pri_key, pub_key) +
	# 'artifact AddURI {} {} {} {} {} {} {} {} {} &&'.format('8001', '000', 'cs', 'ct', 'size', 'ut', 'loc', pri_key, pub_key) +
	# 'artifact AddURI {} {} {} {} {} {} {} {} {} &&'.format('8002', '000', 'cs', 'ct', 'size', 'ut', 'loc', pri_key, pub_key) +
	# 'artifact AddURI {} {} {} {} {} {} {} {} {} &&'.format('8003', '000', 'cs', 'ct', 'size', 'ut', 'loc', pri_key, pub_key) +
	
	'echo "====================PLEASE RUN THE FOLLOWING CHECKS====================" &&' +
	'echo category amend 9000 {} {} {} {} &&'.format('genesis', 'start', pri_key, pub_key) +
	'echo category create 8000 {} {} {} {} &&'.format('start', 'genesis', pri_key, pub_key) +
	'echo category create 9000 {} {} {} {} &&'.format('genesis', 'start', pri_key, pub_key) +
	'echo category amend 9000 {} {} {} {} &&'.format('start', 'genesis', pri_key, pub_key) +
	'echo "====================PLEASE RUN THE FOLLOWING CHECKS====================" &&' +
	'echo "======================================================================="'
	)
