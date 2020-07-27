#!/usr/bin/env python3

from sys import stdout
from urllib.request import urlopen
from urllib.parse import urljoin
import os, posixpath, tempfile
import json, re, random, argparse

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--board")
parser.add_argument("-p", "--playlist", action="store_true")
args = parser.parse_args()

CHAN_HOST = "http://2ch.hk/"
board = args.board or "a"
player_string = "mpv --really-quiet "
player_playlist_options = "--shuffle --playlist="

# Internal variables
ATTACH_VIDEO = 6
catalog = urljoin(CHAN_HOST, posixpath.join(board, "catalog_num.json"))
catalog_data = json.loads(urlopen(catalog).read().decode('utf-8'))
webm_match = lambda s : re.match(r'^[^\.]*WEBM', s, re.IGNORECASE)

def get_vids(board):
    '''Retrieve list of webms on the board in {path, fullname} format'''

    webmthreads = []
    webms = []

    for thr in catalog_data['threads']:
        if webm_match(thr['subject']) or webm_match(thr['comment']):
            webmthreads.append(thr['num'])

    for thr in webmthreads:
        thr_url = urljoin(CHAN_HOST, posixpath.join(board, "res", thr + ".json"))
        thr_data = json.loads(urlopen(thr_url).read().decode('utf-8'))
        for post in thr_data['threads'][0]['posts']:
            for attach in post['files']:
                if attach['type'] == ATTACH_VIDEO and attach['nsfw'] == 0:
                    webms.append({'path': urljoin(CHAN_HOST, attach['path']), 'fullname': attach['fullname']})
    return webms

def make_playlist(vids):
    '''Make a playlist in PLS format with an iterator'''

    yield '[playlist]\n'
    for idx, webm in enumerate(vids):
        yield 'File{0}={1}\n'.format(idx, webm['path'])
        yield 'Title{0}={1}\n'.format(idx, webm['fullname'])
        yield '\n'
    yield 'NumberOfEntries={}\n'.format(len(vids))
    yield 'Version=2\n'

if __name__ == '__main__':
    pl_file = None
    vids = get_vids(board)

    if args.playlist:
        pl_file = tempfile.NamedTemporaryFile('wt')
        pl_file.writelines(make_playlist(vids))
        player_string += player_playlist_options
        destination = pl_file.name
        print('Playing all webms on /{}/...'.format(board))
    else:
        vid = random.choice(vids)
        destination = vid['path']
        print('Playing {}...'.format(vid['fullname']))

    os.system(player_string + destination)
    pl_file.close() if args.playlist else False
