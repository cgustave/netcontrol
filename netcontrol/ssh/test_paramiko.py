from ssh import Ssh

# Sample code to test paramiko on a real ssh device using the 'shell' channel

myssh = Ssh(ip='10.205.10.120', user='vyos', password='vyos', port=10106,
            debug=False)
myssh.connect()
myssh.shell_send(['show configuration commands | grep network-emulator'])
myssh.shell_read()
print (myssh.output)
myssh.close()


