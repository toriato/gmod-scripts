import json

from os import environ
from typing import List
from pathlib import Path

from dotenv import load_dotenv
from requests import post

root_dir = Path(__file__).parent
cache_dir = root_dir.parent / 'garrysmod' / 'cache' / 'srcds'

load_dotenv(root_dir / '.env')


def fetch_details (ids: List[str]):
    response = post('https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1', {
        'itemcount': len(ids),
        **{
            f'publishedfileids[{index}]': id for index, id in enumerate(ids)
        }
    })

    payload = json.loads(response.content)
    if payload['response']['result'] != 1:
        raise RuntimeError(f'failed to fetch file, returned {payload.result}')
    
    files = {}

    for details in payload['response']['publishedfiledetails']:
        if details['result'] != 1:
            print(f'failed to fetch file {details['publishedfileid']}, returned {details['result']}')
            continue

        files[details['publishedfileid']] = details

    return files

def fetch_collection (ids: List[str]):
    response = post('https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1', {
        'collectioncount': len(ids),
        **{
            f'publishedfileids[{index}]': id for index, id in enumerate(ids)
        }
    })

    payload = json.loads(response.content)
    if payload['response']['result'] != 1:
        raise RuntimeError(f'failed to fetch colleciton, returned {payload.result}')
    
    child_files = []
    child_collections = []

    for collection in payload['response']['collectiondetails']:
        if collection['result'] != 1:
            print(f'failed to fetch collection {collection['publishedfileid']}, returned {collection['result']}')
            continue

        for child in collection['children']:
            match child['filetype']:
                case 0:
                    child_files.append(child['publishedfileid'])
                case 2:
                    child_collections.append(child['publishedfileid'])
                case _:
                    print(f'unexpected type {child['publishedfileid']}({child['filetype']}) from {collection['publishedfileid']}')

    if child_collections:
        child_files += fetch_collection(child_collections)

    return child_files


print('fetching workshop collection...')
workshop_ids = fetch_collection([environ['WORKSHOP_COLLECTION_ID']])
print(f'fetched {len(workshop_ids)} workshop files')

print('fetching workshop details...')
workshop_details = fetch_details(workshop_ids)

print('deleting unsubscribed files from cache directory...')
for path in cache_dir.glob('*.gma'):
    if path.stem not in workshop_ids:
        detail = workshop_details[path.stem] if path.stem in workshop_details else None
        print(f'{path.stem} - {detail['title']}' if detail else f'{path.stem}')
        path.unlink()
        continue

print('all done :)')
