#!/usr/bin/env python

import boto3
import sys
from optparse import OptionParser

def depaginate_accounts(boto_handle):
    paginator = boto_handle.get_paginator('list_accounts')
    response_iterator = paginator.paginate()

    results = []
    for response in response_iterator:
        results = results + response['Accounts']

    return results

def usage():
    print """
Usage: aws-organizations.py [options]

Options:
    -l | --list     List AWS accounts
    -e | --email    Email address to create AWS account with
    -a | --account  Name of AWS account, must use with -e
"""

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-e", "--email", dest="email_address", default='', help="Email address for AWS account")
    parser.add_option("-a", "--account", dest="account_name", default='', help="AWS Account name")
    parser.add_option("-l", "--list", dest="list_accounts", action="store_true", default=False, help="List AWS accounts thats not suspended")
    parser.add_option("--list-all", dest="list_all_accounts", action="store_true", default=False, help="List all AWS account")
    (options, args) = parser.parse_args()

    client = boto3.client('organizations')

    # Paginate outputs and dump it into an object
    response = depaginate_accounts(client)

    if options.list_accounts:
        for index in response:
            if index['Status'] != 'SUSPENDED':
                print index['Id'] + ' - ' + index['Email'] + ' (' + index['Name'] + ')'
    elif options.list_all_accounts:
        for index in response:
            print index['Id'] + ' - ' + index['Email'] + ' (' + index['Name'] + ')' + " [" + index['Status'] + "]"
    elif (options.account_name != '') and (options.email_address != ''):
        if not any(index['Email'] == options.email_address for index in response):
            print "Email " + options.email_address + " does not exist, creating account"
            response = client.create_account(
                    Email=options.email_address,
                    AccountName=options.account_name
            )
            print response
    else:
        usage()
        sys.exit(1)
