### NAME: netcontrol

#### DESCRIPTION:

'netcontrol' is a python package to control or configure remote devices through a network protocol
Unittest can be done offline using a mocked paramiko package returning predefined files in place of 
STDIN, STDOUT and STDERR.
Predefined files are located in the subproject (aka: vyosctl, fpocctl, vmctl) directory 'tests/mocked_files'
There name is based on the remote command issued with translations such as :
- space replaced with _
- | replace with -
- / replaced with _

The mocked paramiko package is located in netcontrol/ssh/tests/paramiko

#### AUTHOR:
Cedric GUSTAVE (cgustave@free.fr)


##### Supported network protocols :
  - ssh (using paramiko)


##### Supported types of remote devices are :
  - fortipoc (using 'fpoctcl')
  - vyos (using 'vyosctl')
  - kvm host (using 'vmctl')
