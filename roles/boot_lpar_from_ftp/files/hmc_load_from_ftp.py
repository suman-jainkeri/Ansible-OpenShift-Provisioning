#!/usr/bin/env python3

"""
Ths scripts required an config file with the following yaml syntax:
---
host:
userid:
password:
ftp_config:
  host:
  username:
  password:
  file_path:
lpar:
"""

import os
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import sys
import yaml
import zhmcclient


PROG_NAME = os.path.basename(sys.argv[0])


def usage():
    """
    Display usage information for the script.
    """
    print(f"Usage: {PROG_NAME} <yaml config file\n")
    print(f"  e.g. {PROG_NAME} a3elp71.yaml")


def main(argv):
    """
    Main function to execute the script.

    :param argv: Command line arguments. Contains config file path.
    """

    if len(argv) == 1:
        usage()
        sys.exit(1)

    config_filepath = argv[1]
    print('Load config file ...')
    with open(config_filepath) as f:
        config = yaml.safe_load(f)

    print('Login to HMC...')
    session = zhmcclient.Session(config['host'], config['userid'], config['password'], verify_cert=False)
    client = zhmcclient.Client(session)
    console = client.consoles.console

    print('Get LPAR information...')
    lpar = []
    for item in console.list_permitted_lpars():
        if item.properties.get("name") == config['lpar']:
            lpar = item
            break
    if not lpar:
        print("ERROR: LPAR not found!")
        sys.exit(1)

    # Load from ftp is supported in HMC API version 2.16.0 and above
    if (2, 16, 0) > tuple(map(int, lpar.properties.get("se-version").split('.'))):
        print("ERROR: CPC SE version is too old. Need 2.16.0 or higher.")
        sys.exit(1)

    print("Load from ftp server...")
    ftp_config = config['ftp_config']
    try:
        # load_from_ftp(host, username, password, load_file, protocol='ftp',
        # wait_for_completion=True, operation_timeout=None, status_timeout=None,
        # allow_status_exceptions=False)
        lpar.load_from_ftp(host=ftp_config['host'], username=ftp_config['username'],
                           password=ftp_config['password'], load_file=ftp_config['file_path'],
                           protocol=ftp_config['protocol'],
                           wait_for_completion=True)
    except Exception as e:
        print('Error: %s' % e)
        sys.exit(1)
    print('Load executed. Please wait until OS is fully loaded...')


if __name__ == "__main__":
    main(sys.argv)
