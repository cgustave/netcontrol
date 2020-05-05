### NAME: netcontrol

#### DESCRIPTION:

**'netcontrol'** is a python package to control or configure remote devices through ssh.  
Is has been designed to run Unittest offline using a mocked paramiko package returning predefined files in place of STDIN, STDOUT and STDERR.
Predefined files are located in the subproject (aka: vyosctl, fpocctl, vmctl) directory 'tests/mocked_files'
There name is based on the remote command issued with translations such as :
- space replaced with _
- | replace with -
- / replaced with _

The mocked paramiko package is located in netcontrol/ssh/tests/paramiko.  
Mocked files are located in netcontrol/ssh/tests/mockfiles.  

#### AUTHOR:
Cedric GUSTAVE


#### INSTALL:
- netcontrol should be installed via pip from pypi.org.  
  `pip install netcontrol`
- Project is hosted on github `https://github.com/cgustave/netcontrol`


##### Supported network protocols :
  - ssh (using paramiko)


##### Supported types of remote devices are :
  - fortipoc (using 'fpoc')
  - vyos (using 'vyos')
  - kvm host (using 'vm')
  - fortigate (using 'fortigate')
