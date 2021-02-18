"""
.SYNOPSIS
  Creation of failure domains in a new NSX-T environment
.DESCRIPTION
  Python script to create of failure domains in a new NSX-T environment
    - Create failure domains
    - Add edges nodes to failure domains
    - Configure edge clusters to use failure domain as placement method
.INPUTS
  JSON file
.NOTES
  Version:        1.0
  Author:         Arnaud Gandibleux
  Creation Date:  18/02/2021
  Purpose/Change: Creation of failure domains in a new NSX-T environment and configure edges and edge clusters to work with failure domains
"""

#!/usr/bin/env python3

import json
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import argparse
from cryptography.fernet import Fernet 
import os 

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
parser =  argparse.ArgumentParser()

parser.add_argument("--nsxmanager", "-m", help="IP/FQDN of NSX-T Manager")
args = parser.parse_args()

if args.nsxmanager:
  print("FQDN=",args.nsxmanager)
  nsxmanager = args.nsxmanager
 

#Creds to https://www.geeksforgeeks.org/create-a-credential-file-using-python/
cred_filename = 'CredFile.ini'
key_file = 'key.key'
  
key = '' 
  
with open('key.key','r') as key_in: 
    key = key_in.read().encode() 
  
#If you want the Cred file to be of one  
# time use uncomment the below line 
#os.remove(key_file) 
  
f = Fernet(key) 
with open(cred_filename,'r') as cred_in: 
    lines = cred_in.readlines() 
    config = {} 
    for line in lines: 
        tuples = line.rstrip('\n').split('=',1) 
        if tuples[0] in ('Username','Password'): 
            config[tuples[0]] = tuples[1] 
  
    passwd = f.decrypt(config['Password'].encode()).decode() 
#END of creds

authentication = HTTPBasicAuth(config['Username'], passwd)

def printing(message, output):
  m = f"""
  {'-'*40}
  # Action: {message}
  # Output: {json.dumps(output, indent=2)}
  {'-'*40}
  """

  print(m)

def colored_input(message):
  return input('\x1b[0;30;43m'+ "[INPUT] - " + message + '\x1b[0m')

def show_menu(text, options):
  print('-'*20, text, '-'*20)
  for key in sorted(options.keys()):
    print(key+":" + options[key][0])
  print('-'*20)
  ans = input("Make a choice:")
  options.get(ans,[None,exit])[1]()

def show_main_menu():
  menu = {"1":("Full failure domain configuration",full_flow),
        "2":("Show and execute subfunctions",show_submenu),
        "X":("Exit",exit)
       }
  show_menu("MAIN MENU", menu)
  

def show_submenu():
  menu = {"1":("Get failure domains",get_failure_domains),
        "2":("Create failure domains",create_failure_domain),
        "3":("Delete failure domains",delete_failure_domains),
        "4":("Get edge nodes",get_edges),
        "5":("Get edge clusters", get_edge_clusters),
        "6":("Assign edge nodes to new failure domain", assign_edge_to_failure_domain),
        "7":("Configure edge cluster placement method", set_edge_cluster_placement),
        "B":("Back",show_main_menu),
        "X":("Exit",exit)
       }
  show_menu("SUB MENU", menu)

def exit():
  print('Goodbye...')

def create_failure_domain():
  
  lst = [x for x in colored_input("Failure domain names to create (comma separated  - no spaces):").split(',')] 

  for x in range(len(lst)):
    if lst[x]:
      JSONdata = {}
      JSONdata['display_name'] = lst[x]
      response = requests.post("https://{}/api/v1/failure-domains/".format(nsxmanager), auth=authentication, verify=False, json=JSONdata)
    
    printing("Creation of failure domains", response.json())
  get_failure_domains()



def delete_failure_domains():
  get_failure_domains(1)
  lst = [x for x in colored_input("Failure domain IDs to remove (comma separated - no spaces):").split(',')] 
  for x in range(len(lst)):
    print("Remove", lst[x])
    convert = get_failure_domains(0)
    for k, v in convert.items():
      if lst[x] == k:
        response = requests.delete("https://{}/api/v1/failure-domains/{}".format(nsxmanager, k), auth=authentication, verify=False)
    
    try:
      a_json = json.loads(response.content)
      printing("Deletion of failure domain:", response.json())
    except:
      printing("Deletion of failure domain:", response.status_code)
    

  get_failure_domains(1)


def get_failure_domains(prnt=1):
  response = requests.get("https://{}/api/v1/failure-domains/".format(nsxmanager), auth=authentication, verify=False)
  
  JSONdata = {}

  obj = response.json()["results"]

  for x in obj:
    for y in x:
      if y == "id":
        id = x[y]
      if y == "display_name":
        name = x[y]
        
    JSONdata[id] = name
  if prnt == 1:
    printing("Get failure domains...", JSONdata)
  return JSONdata

def get_edges(prnt=1):
  response = requests.get("https://{}/api/v1/transport-nodes/".format(nsxmanager), auth=authentication, verify=False)
  JSONdata = {}

  obj = response.json()["results"]
  
  for x in obj:
    fd = None
    for y in x:
      if y == "node_id":
        id = x[y]
      if y == "display_name":
        name = x[y]
      if y == "failure_domain_id":
        fd = x[y]
    if fd is not None:
      JSONdata[id] = {"name": name, "fdomain": fd}
  if prnt == 1:  
    printing("Get edge nodes...", JSONdata)
  return JSONdata

def assign_edge_to_failure_domain():

  get_edges()
  lst = [x for x in colored_input("Give edge IDs to connect to failure domain specified in the next step (comma separated - no spaces):").split(',')] 

  get_failure_domains()
  fd = colored_input("Specify the failure domain id to connect the edges to:")

  for x in range(len(lst)):
    print("Linking...", lst[x])

    convert = get_edges(0)
    for k, v in convert.items():
      if lst[x] == k:
        response = requests.get("https://{}/api/v1/transport-nodes/{}".format(nsxmanager, k), auth=authentication, verify=False)

        obj = response.json()

        JSONdata = obj
        for p, q in obj.items():
          if p == "failure_domain_id":
            q = fd
            JSONdata[p] = q
          
        requests.put("https://{}/api/v1/transport-nodes/{}".format(nsxmanager, k), auth=authentication, verify=False, json=JSONdata)

  get_edges()

def get_edge_clusters():
  response = requests.get("https://{}/api/v1/edge-clusters/".format(nsxmanager), auth=authentication, verify=False)
  JSONdata = {}

  obj = response.json()["results"]
  for x in obj:
    for y, z in x.items():
      if y == "id":
        id = z
      if y == "display_name":
        name = z
    JSONdata[id] = name
        
  printing("Get edge clusters...", JSONdata)      

def set_edge_cluster_placement():
  get_edge_clusters()

  id = colored_input("Give an edge cluster ID of the cluster which will use allocation based on failure domain:")

  response = requests.get("https://{}/api/v1/edge-clusters/{}".format(nsxmanager, id), auth=authentication, verify=False)
  JSONdata = {}

  obj = response.json()

  for x, y in obj.items():
    if x == "allocation_rules":
      y = [{
        'action':{
          'enabled':True,
          'action_type':'AllocationBasedOnFailureDomain'
        }
      }]

    JSONdata[x] = y
    
  response2 = requests.put("https://{}/api/v1/edge-clusters/{}".format(nsxmanager, id), auth=authentication, verify=False, json=JSONdata)
  
  printing("Set edge cluster placement method...", response2.json())

def full_flow():
  create_failure_domain()
  assign_edge_to_failure_domain()
  set_edge_cluster_placement()


def main():
  show_main_menu()

if __name__ == "__main__":
    main()


