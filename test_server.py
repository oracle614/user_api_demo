import paramiko


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
client.connect('192.168.100.241', 22, username='root', password='1234567', timeout=4)
stdin, stdout, stderr = client.exec_command('cat /proc/meminfo')
print(stdout.read())
client.close()
