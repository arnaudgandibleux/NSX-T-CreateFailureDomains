# Python script to create VMware NSX-T Failure Domains

Python script to create of failure domains in a new NSX-T environment
  - Create failure domains
  - Add edges nodes to failure domains
  - Configure edge clusters to use failure domain as placement method
  
## Installation

Install Python3.   
Be sure to have following modules installed:
  - json
  - requests
  - urllib3
  - cryptography

## Usage

Open a terminal and run

### Generate credential file
```sh
$ python3 createCred.py
```
ref: https://www.geeksforgeeks.org/create-a-credential-file-using-python/

### Configure failure domains
```sh
$ python3 configureFailureDomains.py -m [IP/FQDN of NSX-T manager]
```

### Options

Different options are possible within configureFailureDomains.py.
  - A full run through the configuratation of failure domains and immediatly attach it to edge nodes
  - Run every function seperatly:
    * 1:Get failure domains
    * 2:Create failure domains
    * 3:Delete failure domains
    * 4:Get edge nodes
    * 5:Get edge clusters
    * 6:Assign edge nodes to new failure domain
    * 7:Configure edge cluster placement method


## Development

See any bugs or do you want to improve it?  
Feel free to contribute!

