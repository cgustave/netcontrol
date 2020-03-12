
from ssh import Ssh

myssh = Ssh(ip='127.0.0.1', user='cgustave', password='', debug=True)
myssh.trace_open(filename="test4File.log")
myssh.mock(context='default')
myssh.connect()
myssh.execute(["ps -ef"])
myssh.shell_read()
myssh.close()
