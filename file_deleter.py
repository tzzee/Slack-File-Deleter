"""
The script deletes all files uploaded to your slack team, older than a given number of weeks.
Default number of weeks is 4.

USAGE:
python file_delete.py token [number_of_weeks]

PARAMS:
---
token (REQUIRED): Slack API token, available at https://api.slack.com/web
number_of_weeks (OPTIONAL): Integer - Defaults to 4.
"""
__author__ = 'TetraEtc'
from slacker import Slacker, Error
import sys
from datetime import timedelta, datetime
import argparse

def main(token, weeks, dry_run):
    """
    Main function
    :param token: Available at. https://api.slack.com/web. REQUIRED
    :param weeks: Optional number of weeks. Defaults to 4
    :return:
    """
    slack = Slacker(token)
    # Get list of all files available for the user of the token
    total = slack.files.list(count=1).body['paging']['total']
    num_pages = int(round(total/1000.00 + .5)) # Get number of pages
    print("{} files to be processed, across {} pages".format(total, num_pages))
    # Get files
    files_to_delete = []
    ids = set() # For checking that the API doesn't return duplicate files (Don't think it does, doesn't hurt to be sure
    count = 1
    for page in range(num_pages):
        print ("Pulling page number {}".format(page + 1))
        files = slack.files.list(count=1000, page=page+1).body['files']
        for file in files:
            print("Checking file number {}".format(count))
            # Checking for duplicates
            if file['id'] not in ids:
                ids.add(file['id'])
                if datetime.fromtimestamp(file['timestamp']) < datetime.now() - timedelta(weeks=weeks):
                    files_to_delete.append(file)
                    print("File No. {} will be deleted".format(count))
                    print("\"{}\"@{}".format(file['name'], datetime.fromtimestamp(file['timestamp'])))
                else:
                    print ("File No. {} will not be deleted".format(count))
            count+=1

    print("All files checked\nProceeding to delete files")
    print("{} files will be deleted!".format(len(files_to_delete)))
    for count,file in enumerate(files_to_delete):
        print("Deleting file {} of {}".format(count+1, len(files_to_delete)))
        if dry_run:
            pass
        else:
            try:
                response=slack.files.delete(file_=file['id'])
                if response.body['ok']:
            	    print("Deleted Successfully")
                else:
                    print("Delete Failed")
            except Error as e:
                print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--dry-run', dest='dry_run', help='show what would have been deleted', action='store_true')
    parser.add_argument('token', nargs=1, help='Slack API token')
    parser.add_argument('weeks', nargs='?', type=int, default=4, help='Number of weeks')
    args = parser.parse_args()

    main(args.token, args.weeks, args.dry_run)
