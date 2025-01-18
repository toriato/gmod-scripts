import json

from os import environ
from typing import List
from pathlib import Path

from dotenv import load_dotenv
from requests import post

root_dir = Path(__file__).parent
cache_dir = root_dir / 'garrysmod' / 'cache' / 'srcds'

load_dotenv(root_dir / '.env')


def fetch_workshop_collection (ids: List[str]):
    response = post('https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1', {
        'collectioncount': len(ids),
        **{
            f'publishedfileids[{index}]': id for index, id in enumerate(ids)
        }
    })

    payload = json.loads(response.content)
    if payload['response']['result'] != 1:
        raise RuntimeError(f'failed to fetch workshop colleciton with {payload.result}')
    
    child_files = []
    child_collections = []

    for collection in payload['response']['collectiondetails']:
        if collection['result'] != 1:
            print(f'failed to fetch workshop collection {collection['publishedfileid']} with {collection['result']}')
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
        child_files += fetch_workshop_collection(child_collections)

    return child_files


workshop_file_ids = fetch_workshop_collection([environ['WORKSHOP_COLLECTION_ID']])
print(f'fetched {len(workshop_file_ids)} workshop files')

for path in cache_dir.glob('*.gma'):
    if path.stem not in workshop_file_ids:
        print(f'{path.stem} is gone, deleting {path.name}')
        path.unlink()
        continue

print('all done :)')
