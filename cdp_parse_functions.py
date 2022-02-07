def ssh_cdp(device, username, password):
    import pprint
    from netmiko import ConnectHandler
    host_dictionary = {}
    command = "show cdp entry *"

    connection_details = { # This establishes SSH connection settings for the device.
        "device_type": "cisco_ios",
        "host": device,
        "username": username,
        "password": password,

    }

    with ConnectHandler(**connection_details) as net_connect:
        cdp_output = net_connect.send_command(command) # this stores all the CDP data collected from the host into a single variable

    ################################################################################

    dict_list = parse_cdp_out(cdp_output.splitlines()) # This sends all of the host's CDP data collected above through the CDP parsing functions, then stores the formatted data into a list of dictionaries.


    host_dictionary = {
        'cdp_neighbors': {}
    }

    host_cdp_neighbors_dict = host_dictionary['cdp_neighbors'] # This just helps shorten up the diciontary assignments below. It gets super long and messy without this line.

    for dict in dict_list:

        neighbor_hostname = dict['remote_id'] # Uses the remote_id key of each dictionary as a unique value to reference it by.

        if neighbor_hostname not in host_cdp_neighbors_dict.keys(): # This builds the entry for the device in the master dictionary if it does not exist yet.

            host_cdp_neighbors_dict[neighbor_hostname] = {}
            host_cdp_neighbors_dict[neighbor_hostname]['connections'] = {}
            host_cdp_neighbors_dict[neighbor_hostname]['capabilities'] = dict['capabilities']
            host_cdp_neighbors_dict[neighbor_hostname]['platform'] = dict['platform']
            host_cdp_neighbors_dict[neighbor_hostname]['remote_id'] = dict['remote_id']
            host_cdp_neighbors_dict[neighbor_hostname]['remote_ip'] = dict['remote_ip']
            host_cdp_neighbors_dict[neighbor_hostname]['version'] = dict['version']
            host_cdp_neighbors_dict[neighbor_hostname]['multiple_connections'] = False
            host_cdp_neighbors_dict[neighbor_hostname]['connection_counter'] = 1


            host_cdp_neighbors_dict[neighbor_hostname]['connections']['connection' + str(host_cdp_neighbors_dict[neighbor_hostname]['connection_counter'])] = {
                'local_int': dict['local_int'],
                'remote_int': dict['remote_int']
            }



        else: # If the device already exists in the master dictionary, this section simply adds extra info about its multiple connections to the host device.
            host_cdp_neighbors_dict[neighbor_hostname]['connection_counter'] += 1
            host_cdp_neighbors_dict[neighbor_hostname]['multiple_connections'] = True # set to True instead of False


            host_cdp_neighbors_dict[neighbor_hostname]['connections']['connection' + str(host_cdp_neighbors_dict[neighbor_hostname]['connection_counter'])] = {
                'local_int': dict['local_int'],
                'remote_int': dict['remote_int']
            }


    return(host_cdp_neighbors_dict)

def credential_test(username, password, cred_test_device):
    from netmiko import ConnectHandler
    import sys
    import time

    credential_test_connection_details = {
        "device_type": "cisco_ios",
        "host": cred_test_device,
        "username": username,
        "password": password,
    }

    with ConnectHandler(**credential_test_connection_details) as net_connect: # Uses the ConnectHandler function from netmiko. This line passes in the connection_details dictionary defined above to create a connection to the given host.

        try:
            net_connect.find_prompt()
            time.sleep(1)
            print(f"Connection to device {cred_test_device} successful. Proceeding with script.")

        except:
            print(f"Unable to connect to {cred_test_device} with supplied credentials. Verify SSH connectivity and re-enter your SSH credentials.")
            sys.exit(1)


def get_ip (input):
    import re
    return(re.findall(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', input))

def fix_for_ciscoconfparse(cdp_output):
    cdp_str = ""
    confparse_formatted_output = []

    for line in cdp_output:
        if "---" not in line:
            line = "     "+line
        formatted_line = cdp_str+line
        confparse_formatted_output.append(formatted_line)

    return(confparse_formatted_output)

def parse_cdp_out(cdp_output):

    from ciscoconfparse import CiscoConfParse

    cdp_parse = {}
    discovered_hosts = []
    formatted_cdp_output = CiscoConfParse(fix_for_ciscoconfparse(cdp_output))
    strip_these = ("[","]","'", "", "\n")
    cdp_entries = formatted_cdp_output.find_objects("-----")
    all_cdp_entries = []

    for cdp_entry in cdp_entries:
        next_line = False
        cdp_parse = {}

        for cdp_line in cdp_entry.all_children:

            if "Device ID: " in cdp_line.text:
                id_start = str(cdp_line.text).find(":")+2
                remote_id = str(cdp_line.text)[id_start:]
                # if remote_id in discovered_hosts:
                #     break
                # else:
                #     discovered_hosts.append(remote_id)
                cdp_parse['remote_id'] = remote_id

            if "IP" in cdp_line.text:
                ip = str(get_ip (str(cdp_line.text)))
                for each in strip_these:
                    ip = ip.strip(each)
                cdp_parse['remote_ip'] = ip

            if "Platform: " in cdp_line.text:
                platform_start = str(cdp_line.text).find(":")+2
                tmp = str(cdp_line.text)[platform_start:]
                platform_end = tmp.find(",")
                platform = tmp[:platform_end]
                cdp_parse['platform'] = platform

            if "Capabilities: " in cdp_line.text:
                capabilities_start = str(cdp_line.text).find("Capabilities:")+14
                capabilities = str(cdp_line.text)[capabilities_start:]
                cdp_parse['capabilities'] = capabilities

            if "Interface: " in cdp_line.text:
                interface_start = str(cdp_line.text).find(":")+2
                interface_end = str(cdp_line.text).find(",")
                local_int = str(cdp_line.text)[interface_start:interface_end]
                cdp_parse['local_int'] = local_int

            if "Port ID (outgoing port): " in cdp_line.text:
                interface_start = str(cdp_line.text).find("Port ID (outgoing port):")+25
                remote_int = str(cdp_line.text)[interface_start:]
                cdp_parse['remote_int'] = remote_int

            if next_line == True:
                version = str(cdp_line.text).lstrip(' ')
                cdp_parse['version'] = version
                next_line = False

            if "Version :" in cdp_line.text:
                next_line = True


        all_cdp_entries.append(cdp_parse)
    return all_cdp_entries

def l2_mapper(file):

    import yaml
    import pprint
    from N2G import drawio_diagram

    with open(file, 'r') as f:
        data_dict = yaml.load(f, Loader=yaml.FullLoader)

    diagram = drawio_diagram()
    diagram.add_diagram("Page-1")

    for node in data_dict['hosts'].keys():
        diagram.add_node(id=f'{node}', label=f'{node}')

        if 'cdp_neighbors' in data_dict['hosts'][node].keys():
            node_cdp_neighbors = data_dict['hosts'][node]['cdp_neighbors'].keys()

            for cdp_neighbor in node_cdp_neighbors:
                for connection in data_dict['hosts'][node]['cdp_neighbors'][cdp_neighbor]['connections'].keys():

                    local_int = data_dict['hosts'][node]['cdp_neighbors'][cdp_neighbor]['connections'][connection]['local_int']
                    remote_int = data_dict['hosts'][node]['cdp_neighbors'][cdp_neighbor]['connections'][connection]['remote_int']

                    # print(f"{node} local_int: {local_int} remote_int: {remote_int}")
                    diagram.add_link(source=node, target=cdp_neighbor, label=f'{node}:{local_int} --- {cdp_neighbor}{remote_int}')
        else:
            continue
    diagram.layout(algo="large_graph")
    diagram.dump_file(filename="output_drawio.drawio", folder="./diagrams/")
