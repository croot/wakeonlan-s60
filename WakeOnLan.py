# PyS60 application to "wake on lan" a computer
# GPL Licensed
# 2009 - Maxime Rafalimanana 

import appuifw,socket,urllib,e32, struct
import sys, traceback
import re

config = {'timeout':15,'accesspoint':None,'accesspoint_name':None,'mac':None,'ip':None}
timer = e32.Ao_timer()

def main():
    global config, timer
    read_settings()
    try:
        display_config()
        WakeOnLan()
        appuifw.note(u"WOL Succeeded" , "conf")
    except:
        timer.cancel()
        appuifw.note(u"WOL Failed" , "error")
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        appuifw.app.body = appuifw.Text(unicode(error))
    
    
def write_settings():
    global config
    CONFIG_FILE='c:\\wakeonlan_settings.cfg'
    f=open(CONFIG_FILE,'wt')
    f.write(repr(config))
    f.close()
    

def read_settings():
    global config
    CONFIG_FILE='c:\\wakeonlan_settings.cfg'
    try:
        f=open(CONFIG_FILE,'rt')
        try:
            print "reading file"
            content = f.read()
            config.update(eval(content))
            print "config : %s" % str(config)
            f.close()
        except:
            print 'can not read file'
            input_config()
    except:
        print 'can not open file'
        input_config()

def display_config():
    global config
    body = "WIFI : %s\n" % config['accesspoint_name']
    body += "IP : %s\n" % config['ip']
    body += "MAC : %s\n" % config['mac']
    body += "Timeout : %s sec\n" % config['timeout']
    appuifw.app.body = appuifw.Text(body)

def input_target_info():
    global config
    mac_is_valid = False
    while not mac_is_valid:
        config['mac'] = appuifw.query(u"MAC address\nex: 02:41:6d:22:12:f1",'text',config['mac'])
        mac_is_valid = validate_mac(config['mac'])
    ip_is_valid = False
    while not ip_is_valid:
        config['ip'] = appuifw.query(u"IP address\nex: 192.168.1.255",'text',config['ip'])
        ip_is_valid = validate_ip(config['ip'])
    config['timeout'] = appuifw.query(u"Timeout : seconds to wait before auto exit",'number', config['timeout'] )

def input_accesspoint():
    global config
    config['accesspoint'] = socket.select_access_point()
    config['accesspoint_name'] = [ap['name'] for ap in socket.access_points() if ap['iapid']==config['accesspoint']][0]

def input_config():
    global timer
    timer.cancel()
    input_accesspoint()
    input_target_info()
    write_settings()
    display_config()

def WakeOnLan():
    global config
    # Construct a six-byte hardware address
    addr_byte = config['mac'].split(':')
    hw_addr = struct.pack('BBBBBB', int(addr_byte[0], 16),
    int(addr_byte[1], 16),
    int(addr_byte[2], 16),
    int(addr_byte[3], 16),
    int(addr_byte[4], 16),
    int(addr_byte[5], 16))

    # Build the Wake-On-LAN "Magic Packet"...

    msg = '\xff' * 6 + hw_addr * 16

    # ...and send it to the broadcast address using UDP
    apo = socket.access_point(config['accesspoint'])    
    socket.set_default_access_point(apo)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(msg, (config['ip'], 9))
    s.close()
    
def validate_mac(mac):
    mac_list = mac.split(':')
    if len(mac_list)!=6:
        appuifw.note(u"Bad mac address format" , "error")
        return False
    for mac_part in mac_list:
        if re.search('^[0-9a-fA-F]{2}$',mac_part) is None:
            appuifw.note(u"Bad mac address : %s is not valid" % mac_part , "error")
            return False
    return True

def validate_ip(ip):
    ip_list = ip.split('.')
    if len(ip_list)!=4:
        appuifw.note(u"Bad ip address format" , "error")
        return False
    for ip_part in ip_list:
        if re.search('^[0-9]{1,3}$',ip_part) is None:
            appuifw.note(u"Bad ip address : %s is not valid" % ip_part , "error")
            return False
    return True


app_lock = e32.Ao_lock()

def quit():
    app_lock.signal()
    appuifw.app.set_exit()

appuifw.app.menu = [(u"Wake Again",main),(u"Configure",input_config)]
appuifw.app.exit_key_handler = quit
timer.after(max(10,config['timeout']), quit)
main()
app_lock.wait()




