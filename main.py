import yaml
from copy import deepcopy
import time

import settings
import utils.log_handler as logger
log = logger.log
from utils.auth_utils import Auth
import utils.input_utils as input
import utils.general_utils as utils
import api


def input_tag_additional_tags(tags: list) -> None:
    if input.user_options(f'Would you like to add another tag?', f'Invalid option', ["y", "n"]) != "y":
        return None
    
    tag = input.prompt_user("Please enter a tag")
    clean_tag = utils.format_key(tag)
    if tag != clean_tag:
        if input.continue_anyways(f'You might have enter an invalid tag string. \'{tag}\' is ideally formatted \'{clean_tag}\''):
            tags.append(tag)
            log.info(f'Current tags: {tags}')
        else:
            log.info(f'Skipping tag \'{tag}\'')
            log.info(f'Current tags: {tags}')

    input_tag_additional_tags(tags)
    return None


def get_page_of_clients(page: int, clients: list = [], total_clients: int = -1) -> None:
    payload = {
        "pagination": {
            "offset": page*100,
            "limit": 100
        }
    }
    response = api._v2.clients.list_clients(auth.base_url, auth.get_auth_headers(), payload)
    if response['status'] != "success":
        log.critical(f'Could not retrieve clients from instance. Exiting...')
        exit()
    if len(response['data']) > 0:
        clients += deepcopy(response['data'])
        total_clients = response['meta']['pagination']['total']

    if len(clients) != total_clients:
        return get_page_of_clients(page+1, clients, total_clients)
    
    return None
    

# shape of client object
# {
#     "client_id": 1963,
#     "name": "Evidence Test",
#     "tags": [
#         "test"
#     ]
# }
def filter_mode_1(client: object) -> bool:
    """
    Mode 1: Delete all clients that contain at least one of the selected tags

    Returns a boolean whether the client passed in should be included in the list of clietns to delete based on the client tags and the delete mode
    """
    global tags
    delete_client = False
    for tag in tags:
        if tag in client.get('tags', []):
            delete_client = True

    return delete_client
    

def filter_mode_2(client: object) -> bool:
    """
    Mode 2: Delete all clients that contain all of the selected tags

    Returns a boolean whether the client passed in should be included in the list of clietns to delete based on the client tags and the delete mode
    """
    global tags
    delete_client = True
    for tag in tags:
        if tag not in client.get('tags', []):
            delete_client = False

    return delete_client



if __name__ == '__main__':
    for i in settings.script_info:
        print(i)

    with open("config.yaml", 'r') as f:
        args = yaml.safe_load(f)

    auth = Auth(args)
    auth.handle_authentication()

    # select tags to filter clients by
    tags = []

    print("")
    print(f'This script will delete clients based on certain client tags. You can select 1 or multiple tags. You can then run the script in 1 of 2 modes.')
    print(f'Mode 1: Delete all clients that contain at least one of the selected tags')
    print(f'Mode 2: Delete all clients that contain all of the selected tags')
    tag = input.prompt_user("Please enter a tag")
    clean_tag = utils.format_key(tag)
    if tag != clean_tag:
        if input.continue_anyways(f'You might have enter an invalid tag string. \'{tag}\' is ideally formatted \'{clean_tag}\''):
            tags.append(tag)
            log.info(f'Current tags: {tags}')
        else:
            log.info(f'Skipping tag \'{tag}\'')
            log.info(f'Current tags: {tags}')
    tags.append(tag)
    log.info(f'Current tags: {tags}')

    input_tag_additional_tags(tags)


    # select which filtering mode to determine which clients to delete
    mode = input.user_options("Would you like to delete clients in Mode 1 or Mode 2?", "Invalid option", ["1", "2"])
    log.info(f'Selected Mode {mode}')


    # reading clients from instance
    log.info(f'Loading clients...')

    clients = []
    get_page_of_clients(0, clients=clients)
    if len(clients) < 1:
        log.critical(f'There are no clients in the instance. Exiting...')
        exit()
    log.debug(f'num of clients founds: {len(clients)}')

    
    # filter list of clients to selected tags
    if mode == "1":
        filtered_clients = list(filter(filter_mode_1, clients))
    elif mode == "2":
        filtered_clients = list(filter(filter_mode_2, clients))
    
    log.info(f'Loaded {len(clients)} client(s) from Plextrac')
    if mode == "1":
        log.info(f'Found {len(filtered_clients)} client(s) that have at least 1 of the tags {tags}')
    elif mode == "2":
        log.info(f'Found {len(filtered_clients)} client(s) that each have all the tags {tags}')
    
    if input.continue_anyways(f'Would you like to delete these clients from your Plextrac instance'):
        total = len(filtered_clients)
        time_start = time.time()
        for index, client in enumerate(filtered_clients):
            log.info(f'[{index+1}/{total}] Deleteing client \'{client["name"]}\'...')
            response = api._v1.clients.delete_client(auth.base_url, auth.get_auth_headers(), client['client_id'])
            if type(response) == dict and response.get('status') == "success":
                log.success(f'Deleted client')
            else:
                log.exception(f'Could not delete client. Skipping...')

            if index > 3:
                total_time = time.time() - time_start
                avg_delete_time = total_time/(index+1)
                time_remaining = avg_delete_time * (total - (index+1))
                log.debug(f'Elasped time: {round(total_time/60, 1)} minutes - Est. Time Remaining: {round(time_remaining/60, 1)} minutes')
