# -*- coding: utf-8 -*-
"""
Created on Fev 25, 2020
@author: cgustave

Driver for FortiGate
"""

from netcontrol.ssh.ssh import Ssh
import logging as log
import re

class Fortigate(object):
    """
    classdocs
    """
    def __init__(self, ip='', port=22, user='admin', password='', private_key_file='', mock=False, debug=False):
        '''
        Constructor
        '''
        # create logger
        log.basicConfig(
            format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-7.7s.%(funcName)-30.30s:%(lineno)5d] %(message)s',
            datefmt='%Y%m%d:%H:%M:%S',
            filename='debug.log',
            level=log.NOTSET)

        if debug:
            self.debug = True
            log.basicConfig(level='DEBUG')

        log.info("Constructor with ip={}, port={}, user={}, password={}, private_key_file={}, debug={}".
                 format(ip, port, user, password, private_key_file, debug))

        # public attributs
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.private_key_file = private_key_file
        self.moke_context = ''
        self.debug = debug
        self.ssh = Ssh(ip=ip, port=port, user=user, password=password, private_key_file=private_key_file, debug=debug)

        # private attributs

    def connect(self):
        self.ssh.connect()

    # Tracing wrapper on ssh
    def trace_open(self, filename="tracefile.log"):
        self.ssh.trace_open(filename=filename)

    def trace_write(self, line):
         self.ssh.trace_write(line)

    def trace_mark(self, mark):
        self.ssh.trace_mark(mark)

    def close(self):
        if self.ssh:
            self.ssh.close()

    def cli(self, commands=[]):
        """
        Sends a list of commands to FortiGate CLI
        Commands are sent one after each others
          ex : myFgt.cli(commands=['exec date', 'exec time'])
          ex : myFgt.cli(commands=['get system status'])
        """
        log.info("Enter with commands={}".format(commands))

        # Send command
        if not self.ssh.connected:
            self.ssh.connect()

        # issue command and capture output
        for command in commands:
            command = command + "\n"
            self.run_op_mode_command(command)

            log.info("command={} output={}".format(command, self.ssh.output))

    def enter_vdom(self, vdom=None):
        """
        Enters a specific vdom
        Uses : end -> config vdom -> edit VDOM
       
        ex: 
		FGT-1B2-9 # config vdom
        FGT-1B2-9 (vdom) # edit customer
        current vf=customer:1
        FGT-1B2-9 (customer) #
        """
        log.info("Enter with vdom={}".format(str(vdom)))
        result = False

        if not vdom:
            log.error("please provide vdom name")
            raise SystemExit

        if not self.ssh.connected:
            self.ssh.connect()
        
        # Leave current vdom or global section
        self.run_op_mode_command("end\n")
        # Enter vdom
        self.run_op_mode_command("config vdom\n")
        self.run_op_mode_command("edit "+str(vdom)+"\n")

        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))
            match_vdom = re.search("\s\((?P<vd>\S+)\)\s", line)
            if match_vdom:
                vd = match_vdom.group('vd')
                log.debug("Found vd={} in line={}".format(str(vd), line)) 
                if vd == vdom:
                    log.debug("Confirmed vdom prompt")
                    result = True

        return result

    def enter_global(self):
        """
        Enters global section
        Uses : end -> config global

        ex:
        FGT-1B2-9 # config global
        FGT-1B2-9 (global) #
        """
        log.info("Enter")
        result = False

        if not self.ssh.connected:
            self.ssh.connect()

        # Leave current vdom or global section
        self.run_op_mode_command("end\n")

        # Enter global
        self.run_op_mode_command("config global\n")

        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))
            match_global = re.search("\s\(global\)\s", line)
            if match_global:
               log.debug("Confirmed global prompt")
               result = True

        return result

    def get_status(self):
        """
        Returns a dictionary with FortiGate version, license status
        ex : v6.2.3,build1066,191219
        Uses "get system status"
        return : { 'version' = 'v6.2.3,build1066,191219',
                   'license' = True|false
                }
        """
        log.info("Enter")
        result = {} 
        result['version'] = ""
        result['license'] = ""
        found_version = False
        found_license = False

        if not self.ssh.connected:
            self.ssh.connect()

        self.run_op_mode_command("get sys status | grep '^Version\|License St'\n")
        #
        # FGT-B1-1 # get sys status | grep '^Version\|License St'
        #Version: FortiGate-VM64-KVM v6.2.3,build8348,200304 (GA)
        # License Status: Valid

        match_version = re.search("(?:Version:\s[A-Za-z0-9-]+)\s(?P<version>\S+)",self.ssh.output)
        if match_version:
            found_version = True
            result['version'] = match_version.group('version')
            log.debug("found version={}".format(result['version']))

        match_license = re.search("(?:License\sStatus:\s)(?P<license>\S+)",self.ssh.output)
        if match_license:
            found_license = True
            result['license'] = False
            license = match_license.group('license')
            log.debug("found license={}".format(license))
            if license == 'Valid':
                result['license'] = True
        
        if not found_version:
            log.error("Could not extract version")

        if not found_license:
            log.error("Could not extract license status")

        log.debug("result={}".format(result))
        return result

    def get_ike_and_ipsec_sa_number(self):
        """
        Returns a dictionary with the number of 'created' and 'connected' ike and ispec SA
        Uses diagnose vpn ike status
        FGT-B1-1 #  diagnose vpn ike status
        connection: 3/348
        IKE SA: created 3/348  established 3/3  times 0/2083/3220 ms
        IPsec SA: created 3/348  established 3/3  times 0/2083/3220 ms
        For each line 'IKE SA' and 'IPsec SA' we look at 'x' in established x/y 
        ex : { 'ike': { 'created' : 3, 'established' : 3}, 'ipsec': { 'created' : 3, 'established' : 3}}
        """
        log.info("Enter")
        result = {'ike': {}, 'ipsec' : {} }

        if not self.ssh.connected:
            self.ssh.connect()

        self.run_op_mode_command("diagnose vpn ike status\n")
        # FGT-B1-1 #  diagnose vpn ike status
        #connection: 3/348
        #IKE SA: created 3/348  established 3/3  times 0/2083/3220 ms
        #IPsec SA: created 3/348  established 3/3  times 0/2083/3220 ms
        #
        # FGT-B1-1 #
        match_ike_sa = re.search("(?:IKE\sSA:\screated\s)(?P<created>\d+)(?:/\d+\s+established\s)(?P<established>\d+)", self.ssh.output)
        if match_ike_sa:
            ike_sa_created = match_ike_sa.group('created')
            ike_sa_established = match_ike_sa.group('established')
            log.debug("IKE SA : created={} established={}".format(ike_sa_created, ike_sa_established))
            result['ike']['created'] = ike_sa_created
            result['ike']['established'] = ike_sa_established
        else:
            log.debug("Could not extract IKE SA numbers")

        match_ipsec_sa = re.search("(?:IPsec\sSA:\screated\s)(?P<created>\d+)(?:/\d+\s+established\s)(?P<established>\d+)", self.ssh.output)
        if match_ipsec_sa:
            ipsec_sa_created = match_ipsec_sa.group('created')
            ipsec_sa_established = match_ipsec_sa.group('established')
            log.debug("IPsec SA : created={} established={}".format(ipsec_sa_created, ipsec_sa_established))
            result['ipsec']['created'] = ipsec_sa_created
            result['ipsec']['established'] = ipsec_sa_established
        else:
            log.debug("Could not extract IPsec SA numbers")

        log.debug("result={}".format(result))
        return result

    def get_bgp_routes(self, vrf='0'):
       """
       Returns information on BGP routes for the given VRF like :
       result = { 'total' = 6,
                  'subnet' : ['10.0.0.0/24', '10.0.2.0/24'],
                  'nexthop' : ['10.255.0.253','10.255.1.253','10.255.2.253', '10.255.0.2','10.255.1.2','10.255.2.2'],
                  'interface' : ['vpn_mpls','vpn_isp1','vpn_isp2']
                } 

       For :
	    FGT-B1-1 # get router info routing-table bgp

	    Routing table for VRF=0
		B       10.0.0.0/24 [200/0] via 10.255.0.253, vpn_mpls, 00:02:54
							[200/0] via 10.255.1.253, vpn_isp1, 00:02:54
							[200/0] via 10.255.2.253, vpn_isp2, 00:02:54
		B       10.0.2.0/24 [200/0] via 10.255.0.2, vpn_mpls, 00:02:54
							[200/0] via 10.255.1.2, vpn_isp1, 00:02:54
							[200/0] via 10.255.2.2, vpn_isp2, 00:02:54

        FGT-B1-1 #
        
        Case for recursive routes:
        FGT-1B2-9 (customer) # get router info routing-table bgp

		Routing table for VRF=0
		B       10.1.1.0/24 [200/0] via 10.255.0.1, sgwn_mpls1, 05:02:33
							[200/0] via 10.255.1.1, sgwn_inet1, 05:02:33
							[200/0] via 10.255.2.1, sgwn_inet2, 05:02:33
							[200/0] via 10.255.0.1, sgwn_mpls1, 05:02:33
		B       10.2.1.0/24 [200/0] via 10.254.0.1 (recursive is directly connected, sgwn_mpls1), 00:28:01
							[200/0] via 10.254.1.2 (recursive is directly connected, sgwn_inet1), 00:28:01
							[200/0] via 10.254.2.2 (recursive is directly connected, sgwn_inet2), 00:28:01
							[200/0] via 10.254.0.1 (recursive is directly connected, sgwn_mpls1), 00:28:01
		B       10.2.2.0/24 [200/0] via 10.254.0.2 (recursive is directly connected, sgwn_mpls1), 03:14:43
							[200/0] via 10.254.1.1 (recursive is directly connected, sgwn_inet1), 03:14:43
							[200/0] via 10.254.2.1 (recursive is directly connected, sgwn_inet2), 03:14:43
							[200/0] via 10.254.0.2 (recursive is directly connected, sgwn_mpls1), 03:14:43
       """
       log.info("Enter with vrf={}".format(vrf))
       result = { 'total' : {}, 'subnet' : [], 'nexthop' : [], 'interface' : [] }
    
       if not self.ssh.connected:
            self.ssh.connect()

       self.run_op_mode_command("get router info routing-table bgp\n")

       # Start checking routes when seeing "VRF=xxx"
       vrf_flag = False
       nb_route = 0
       nb_recursive_route = 0
       for line in self.ssh.output.splitlines():
           log.debug("line={}".format(line)) 
           if not vrf_flag:
               match_vrf = re.search("Routing\stable\sfor\sVRF="+str(vrf),line)
               if match_vrf:
                   log.debug("Found VRF={} in line={}".format(str(vrf), line))
                   vrf_flag = True
           else:
 
               # Look for a subnet
               match_subnet = re.search("^(?:B\s+)(?P<subnet>[0-9./]+)", line) 
               if match_subnet:
                   subnet = match_subnet.group('subnet')
                   log.debug("found subnet={}".format(subnet))
                   result['subnet'].append(subnet)
 
               # Look for nexthop and interface + count number of routes

               # Track non recursive routes
               match_nexthop = re.search("]\s+via\s+(?P<nexthop>[0-9.]+),\s+(?P<interface>\w+)",line)
               if match_nexthop:
                   nexthop = match_nexthop.group('nexthop')
                   interface = match_nexthop.group('interface')
                   nb_route = nb_route + 1
                   log.debug("found nexthop={} interface={} nb_route={} nb_recursive={}".format(nexthop, interface, nb_route, nb_recursive_route))
                   if nexthop not in result['nexthop']:
                       result['nexthop'].append(nexthop)
                   if interface not in result['interface']:
                       result['interface'].append(interface)

               # Track recursive routes
               match_nexthop = re.search("]\s+via\s+(?P<nexthop>[0-9.]+)\s+\(recursive\s.+\,\s+(?P<interface>\w+)\),",line)
               if match_nexthop:
                   nexthop = match_nexthop.group('nexthop')
                   interface = match_nexthop.group('interface')
                   nb_route = nb_route + 1
                   nb_recursive_route = nb_recursive_route + 1
                   log.debug("found nexthop={} interface={} nb_route={} nb_recursive={}".format(nexthop, interface, nb_route, nb_recursive_route))
                   if nexthop not in result['nexthop']:
                       result['nexthop'].append(nexthop)
                   if interface not in result['interface']:
                       result['interface'].append(interface)

       result['total'] = nb_route        
       result['recursive'] = nb_recursive_route
       log.debug("result={}".format(result))
       return result
      
    def get_sdwan_service(self, service=1):
        """
        Returns a dictionary with information from 
        diagnose sys viirtual-wan-link service <service>
            FGT-B1-1 # diagnose sys virtual-wan-link service 1
            Service(1): Address Mode(IPV4) flags=0x0
              Gen(1), TOS(0x0/0x0), Protocol(0: 1->65535), Mode(sla)
              Service role: standalone
              Member sub interface:
              Members:
                1: Seq_num(1 vpn_isp1), alive, sla(0x1), cfg_order(0), cost(0), selected
                2: Seq_num(2 vpn_isp2), alive, sla(0x1), cfg_order(1), cost(0), selected
                3: Seq_num(3 vpn_mpls), alive, sla(0x1), cfg_order(2), cost(0), selected
              Src address:
                    10.0.1.0-10.0.1.255

              Dst address:
                    10.0.2.0-10.0.2.255

            FGT-B1-1 #
        """
        log.info("Enter")
        result = {'members': {}, 'mode':''}
        members_flag = False         
        mode = ''

        if not self.ssh.connected:
            self.ssh.connect()

        self.run_op_mode_command("diagnose sys virtual-wan-link service {}\n".format(service))

        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))

            # Get mode
            match_mode = re.search("(?:,\sMode\()(?P<mode>\S+)(?:\))", line)
            if match_mode:
                mode = match_mode.group('mode')
                log.debug("found mode={}".format(mode))
                result['mode']=mode
         
            # Get members details
            if members_flag:
                match_member = re.search("(?:\s+)(?P<order>\d+)(?::\sSeq_num\()(?P<seq>\d+)(?:\s\S+)?(?:\),\s)(?P<status>alive|dead)",line)
                if match_member:
                    order = match_member.group('order')
                    seq = match_member.group('seq')
                    status = match_member.group('status')
                    log.debug("Found order={} seq={} status={}".format(order, seq, status))
                    result['members'][order] = {}
                    result['members'][order]['seq_num'] = seq
                    result['members'][order]['status'] = status 

                    # If sla mode, get sla value
                    if mode == 'sla':
                        log.debug("sla mode, get sla value")
                        match_sla_value = re.search("(?:,\ssla\()(?P<sla>0x[0-9a-z]+)(?:\),)",line)
                        if match_sla_value:
                            sla = match_sla_value.group('sla')
                            log.debug("Found sla={}".format(sla))
                            result['members'][order]['sla'] = sla
                        else:
                            log.error("Could not extract sla value from member")

            # Get members
            match_member_section = re.search("\s\sMembers:",line)
            if match_member_section:
                log.debug("found start of members section")
                members_flag = True

        return result

    def get_session(self, filter={}):
        """
        Filter and retrieve a session from the session list
        The provided filter dictionary is based on session filter keywords :

        FGT-CGUSTAVE # diagnose sys session filter
        vd                Index of virtual domain. -1 matches all.
        sintf             Source interface.
        dintf             Destination interface.
        src               Source IP address.
        nsrc              NAT'd source ip address
        dst               Destination IP address.
        proto             Protocol number.
        sport             Source port.
        nport             NAT'd source port
        dport             Destination port.
        policy            Policy ID.
        expire            expire
        duration          duration
        proto-state       Protocol state.
        session-state1    Session state1.
        session-state2    Session state2.
        ext-src           Add a source address to the extended match list.
        ext-dst           Add a destination address to the extended match list.
        ext-src-negate    Add a source address to the negated extended match list.
        ext-dst-negate    Add a destination address to the negated extended match list.
        clear             Clear session filter.
        negate            Inverse filter.

        Returns a dictionary with the elements of the returned get_sessions
        ex : {
            'src' : '8.8.8.8',
            'dst' : '10.10.10.1',
            'sport' : 63440,
            'dport' : 53,
            'proto' : 17,
            'state' : '01',
            'flags' : ['may_dirty', 'dirty'],
            'dev'   : '7->8',
            'gwy'   : '10.10.10.1->8.8.8.8',
            'duration' : 30,

        session sample :

            FGT-CGUSTAVE # diagnose sys session filter dport 222

            FGT-CGUSTAVE # diagnose sys session list

            session info: proto=6 proto_state=01 duration=233 expire=3599
            timeout=3600 flags=00000000 sockflag=00000000 sockport=0 av_idx=0
            use=4
            origin-shaper=
            reply-shaper=
            per_ip_shaper=
            class_id=0 ha_id=0 policy_dir=0 tunnel=/ vlan_cos=8/8
            state=log local may_dirty
            statistic(bytes/packets/allow_err): org=11994/132/1
            reply=12831/87/1 tuples=2
            tx speed(Bps/kbps): 33/0 rx speed(Bps/kbps): 43/0
            orgin->sink: org pre->in, reply out->post dev=28->24/24->28
            gwy=10.199.3.1/0.0.0.0
            hook=pre dir=org act=noop
            10.199.3.10:36714->10.199.3.1:222(0.0.0.0:0)
            hook=post dir=reply act=noop
            10.199.3.1:222->10.199.3.10:36714(0.0.0.0:0)
            pos/(before,after) 0/(0,0), 0/(0,0)
            misc=0 policy_id=4294967295 auth_info=0 chk_client_info=0 vd=0
            serial=010d3b7f tos=ff/ff app_list=0 app=0 url_cat=0
            rpdb_link_id = 00000000
            dd_type=0 dd_mode=0
            npu_state=00000000
            no_ofld_reason:  local
            total session 1

            FGT-CGUSTAVE #

        """
        log.info("Enter with filter={}".format(filter))

        result = {}
        allowed_keys = ['vd','sintf','dintf','src','nsrc','dst','proto','sport','nport','dport','policy','expire','duration','proto-state','session-state1','session-state2','ext-src','ext-dst','ext-src-negate','ext-dst-negate','negate']

        command_list = [ "diagnose sys session filter clear\n" ]
        
        for key in filter:
            log.debug("key={} value={}".format(key, filter[key]))
            if key not in allowed_keys:
                log.error("unknown session key={}".format(key))
                raise SystemExit
            else:
                command_list.append("diagnose sys session filter "+key+" "+str(filter[key])+"\n")
            
        command_list.append("diagnose sys session list\n") 
        self.ssh.shell_send(command_list)        
        result = self._session_analysis()
        return (result)

        
    def run_op_mode_command(self, cmd):
        """
        Use netcontrol shell to send commands to vyos

        """
        log.info("Enter run_op_mode_command with cmd={}".format(cmd))
        self.ssh.shell_send([cmd])
        return(self.ssh.output)

    def _session_analysis(self):
        """
        Returns a json reflecting the session
        Takes self.ssh.output as input
        """
        log.info("Enter")
        result = {}

        # Parse and build session json
        for line in self.ssh.output.splitlines():
            log.debug("line={}".format(line))
            
            # session info: proto=6 proto_state=01 duration=375 expire=3599 timeout=3600 flags=00000000 sockflag=00000000 sockport=0 av_idx=0 use=4
            match_session_info = re.search("^session\sinfo:\sproto=(?P<proto>\d+)\sproto_state=(?P<proto_state>\d+)\sduration=(?P<duration>\d+)\sexpire=(?P<expire>\d+)\stimeout=(?P<timeout>\d+)",line)
            if match_session_info:
                proto = match_session_info.group('proto')
                proto_state = match_session_info.group('proto_state')
                duration = match_session_info.group('duration')
                expire = match_session_info.group('expire')
                timeout = match_session_info.group('timeout')
                log.debug("session-info : proto={} proto_state={} duration={} expire={} timeout={}".format(proto, proto_state, duration, expire, timeout))
                result['proto'] = proto
                result['proto_state'] = proto_state
                result['duration'] = duration
                result['expire'] = expire 
                result['timeout'] = timeout

            # state=log local may_dirty
            match_state = re.search("^state=(?P<state>.+)", line)
            if match_state:
                states = []
                session_states = match_state.group('state')
                log.debug("states: {}".format(session_states))
                for flag in session_states.split():
                    log.debug("flag={}".format(flag))
                    states.append(flag)
                result['state'] = states

            # statistic(bytes/packets/allow_err): org=28670/369/1 reply=21275/200/1 tuples=2
            match_statistic = re.search("^statistic\(bytes/packets/allow_err\):\sorg=(?P<org_byte>\d+)/(?P<org_packet>\d+)/\d\sreply=(?P<reply_byte>\d+)/(?P<reply_packet>\d+)",line)
            if match_statistic:
                stats = {}
                org_byte = match_statistic.group('org_byte')
                org_packet = match_statistic.group('org_packet')
                reply_byte = match_statistic.group('reply_byte')
                reply_packet = match_statistic.group('reply_packet')
                log.debug("org_byte={} org_packet={} reply_byte={} reply_packet={}".format(org_byte, org_packet, reply_byte, reply_packet))
                stats['org_byte'] = org_byte
                stats['org_packet'] = org_packet
                stats['reply_byte'] = reply_byte
                stats['reply_packet'] = reply_packet
                result['statistics'] = stats

            # orgin->sink: org pre->in, reply out->post dev=28->24/24->28 gwy=10.199.3.1/0.0.0.0
            match_dev_gw = re.search("\sdev=(?P<dev>[0-9-/>]+)\sgwy=(?P<gwy>[0-9./]+)",line)
            if match_dev_gw:
                dev = match_dev_gw.group('dev')
                gwy = match_dev_gw.group('gwy')
                log.debug("dev={} gwy={}".format(dev, gwy))

            # hook=pre dir=org act=noop 10.199.3.10:36990->10.199.3.1:222(0.0.0.0:0)
            match_ip = re.search("^hook=pre\sdir=org\sact=noop\s(?P<src>[0-9.]+):(?P<sport>\d+)->(?P<dest>[0-9.]+):(?P<dport>\d+)",line)
            if match_ip:
                src = match_ip.group('src')
                sport = match_ip.group('sport')
                dest =  match_ip.group('dest')
                dport = match_ip.group('dport')
                result['src'] = src
                result['sport'] = sport
                result['dest'] = dest 
                log.debug("src={} sport={} dest={} dport={}".format(src,sport,dest,dport))
                  
            # Total session (should be 1 ideally)
            match_total_session = re.search("^total\ssession\s(?P<total>\d+)", line)
            if match_total_session:
                total = match_total_session.group('total')
                result['total'] = total

        log.debug("result={}".format(result))
        return result

"""
Class sample code
"""
if __name__ == '__main__':  # pragma: no cover
    pass
