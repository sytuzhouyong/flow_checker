import commands
import re


def string_to_number(string):
    if string.startswith('0x'):
        return int(string, 16)
    else:
        return int(string, 10)


def is_number_string(number_string):
    if isinstance(number_string, str):
        if re.match('^0x[0-9a-fA-F]+$', number_string) is not None:
            return True
        if re.match('^[0-9]+$', number_string) is not None:
            return True
    return False


def ip_hex_string(ip_dot_string):
    numbers = ip_dot_string.split('.')
    print(len(numbers))
    if len(numbers) != 4:
        print("error ip string: " + ip_dot_string)
        return ""

    hex_string = '0x'
    for item in numbers:
        string = "%02x" % int(item)
        hex_string += string
    return hex_string


def execute_command(command):
    result = commands.getoutput(command)
    # print(result)
    return result


def ofport_number(port_name):
    result = execute_command('ovs-vsctl get interface %s ofport' % port_name)
    return int(result)


def bridge_name_with_port_name(port_name):
    result = execute_command('ovs-vsctl port-to-br %s' % port_name)
    return result


def flow_of_index(flows, index):
    for flow in flows:
        if flow.table == index:
            return flow
    return None
