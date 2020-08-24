from ssh import Ssh

# Sample code to test paramiko on a real ssh device using the 'shell' channel

myssh = Ssh(ip='10.5.0.31', user='root', password='fortinet', port=22,
            debug=True)
myssh.connect()
myssh.shell_send(["ps -xww | grep qemu-system-x86\n"])
print (myssh.output) 
for line in myssh.output.splitlines():
    print ("\nline={}".format(line)) 

myssh.close()


