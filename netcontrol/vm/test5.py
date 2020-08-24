import json
from vm import Vm

vm = Vm(ip='10.5.0.31', port='22', user='root', password='fortinet', debug=True)
vm.connect()

result = json.loads(vm.get_vms_statistics())
vm.dump_vms()
vm.close()



