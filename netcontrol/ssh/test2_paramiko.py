from ssh import Ssh
import time

ssh = Ssh(ip='127.0.0.1', user='cgustave', password='', private_key_file='/home/cgustave/.ssh/id_rsa', port=22, debug=True)

ssh.trace_open(filename="myTraceFileChannel.log")
ssh.connect()
ssh.invoke_channel()
ssh.channel_send('nc -l 7890\n')
ssh.shell_read()
time.sleep(5)
ssh.shell_read()
time.sleep(10)
ssh.channel_send('toto\n')
ssh.shell_read()
time.sleep(10)
ssh.close()

