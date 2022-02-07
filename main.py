# This script is meant to SSH into a 'seed' device, then discover the seed-device's CDP neighbors.
# Once it has discovered its neighbors and their physical connections, it then repeats the process 

import yaml
import sys
from pprint import pprint
from getpass import getpass
from cdp_parse_functions import * # These functions are used to parse the CDP data into something usable.

################################################################################
################################################################################
################################################################################
################################################################################

def neighbor_crawler(device):

    try: # SSHs into Seed-Device and collects CDP neighbor info. Stores info into master-dictionary.
        device_output = ssh_cdp(device, username, password)
        master_dictionary['hosts'][device]['cdp_neighbors'] = device_output # logs seed-device's CDP neighbors in master_dictionary

    except:
        print(f"Unable to connect to {device}. Troubleshoot and run script again.")
        sys.exit(1)


    seed_neighbors = device_output.keys() # Grabs neighbor-list from collected info.

    for seed_neighbor in list(seed_neighbors):
        print(f"Discovered neighbor: {seed_neighbor}")

    for seed_neighbor in seed_neighbors: # Loops through seed-device's neighbors.
        discovered_hosts.append(seed_neighbor) # Appends each seed-neighbor to a lightweight tracking list.
        neighbor_capabilities = device_output[seed_neighbor]['capabilities']

        if "Router" in neighbor_capabilities or "Switch" in neighbor_capabilities:
            if seed_neighbor not in master_dictionary['hosts'].keys():
                print(f"SSHing into {seed_neighbor}.")

                try:
                    output = ssh_cdp(seed_neighbor, username, password) #
                    master_dictionary['hosts'][seed_neighbor] = {} # establishes dictionary
                    master_dictionary['hosts'][seed_neighbor]['cdp_neighbors'] = output

                    for seed_neighbor_neighbor in master_dictionary['hosts'][seed_neighbor]['cdp_neighbors'].keys():
                        if seed_neighbor_neighbor not in master_dictionary['hosts']:
                            master_dictionary['hosts'][seed_neighbor_neighbor] = {}

                # pprint(master_dictionary['hosts'][seed_neighbor])

                except:
                    print(f"SSH connection failed to host {seed_neighbor}. Moving onto next host.")
                    continue

            else:
                continue
        else:
            print(f"Don't try SSHing into {seed_neighbor}")


    return(master_dictionary)

################################################################################
################################################################################
################################################################################
################################################################################

username = input("Enter your SSH username: ")
password = getpass()
seed_device = input("Enter the FQDN or IP of your seed device: ")
cred_test_device = input("Enter the FQDN or IP of a device to test your SSH credentials with: ")

credential_test(username, password, cred_test_device)

master_dictionary = { 'hosts': { seed_device: {}}} # This creates the master dictionary which EVERYTHING will be stored inside of.
discovered_hosts = [str(seed_device)]

print(f"Beginning CDP discovery at {seed_device}.")

seed_output = neighbor_crawler(seed_device) # Starts initial neighbor-gather
hosts_discovered_from_seed = seed_output['hosts'].keys()

# pprint(output['hosts'].keys())

for host in seed_output['hosts'].keys():
    if host not in discovered_hosts:
        discovered_hosts.append(seed_output['hosts'].keys())
    else:
        continue

# pprint(discovered_hosts)



for host in list(hosts_discovered_from_seed):
#
# ### HERE IS WHERE YOU NEED TO PICK UP. WRITE A STATEMENT THAT SAYS IF THE CDP_NEIGHBORS KEY EXISTS (THEREBY SKIPPING APS AND HOSTS WE COULDN'T SSH INTO), THEN RUN THE STUFF BELOW. GOOD LUCK!
    if 'cdp_neighbors' in seed_output['hosts'][host].keys(): # If the host has a CDP_NEIGHBORS key...
        for discovered_cdp_neighbor in seed_output['hosts'][host]['cdp_neighbors'].keys(): # Loop through the CDP_NEIGHBORS in the key...
            if 'capabilities' in seed_output['hosts'][host]['cdp_neighbors']:
                discovered_cdp_neighbor_capabilities = seed_output['hosts'][host]['cdp_neighbors']['capabilities']

                if discovered_cdp_neighbor not in discovered_hosts: # If the neighbor has not been discovered yet...
                    if "Router" in discovered_cdp_neighbor_capabilities or "Switch" in discovered_cdp_neighbor_capabilities:
                        output = neighbor_crawler(discovered_cdp_neighbor) # Run the neighbor_crawler function for that neighbor.
                        master_dictionary['hosts'][discovered_cdp_neighbor] = output
                    else:
                        print(f"Don't try SSHing into {discovered_cdp_neighbor}." )

            else:
                print(f"Neighbor {discovered_cdp_neighbor} already discovered. Skipping.")
                continue




pprint(master_dictionary)

with open('host_cdp_data.yml', 'w+') as outfile:
    yaml.dump(master_dictionary, outfile) # Writes the entire master_dictionary into a .yaml file.

l2_mapper('host_cdp_data.yml')

print("Script complete. Closing.")
sys.exit(0)
