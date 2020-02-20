from ssh import Ssh
import time

ssh = Ssh(ip='127.0.0.1', user='cgustave', password='',
          private_key_file='/home/cgustave/.ssh/id_rsa', port=22, debug=True)

ssh.trace_open(filename="myTraceFileChannel.log")
#ssh.connect()
#ssh.invoke_channel()
ssh.channel_send('ls -la\n')
data = ssh.channel_read()
print("received {}".format(data))
ssh.close()
