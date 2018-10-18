#!/usr/bin/python
import os
import requests
import json

def loadConfig():
    return json.loads(open("config.ini", "r").read())

def getEndpoint(config, location):
    return "https://www.googleapis.com/youtube/v3/" + location + "?key=" + config['apikey']

def requestGetUserPlaylistsIds(config, channelId):
    ids = []
    hasNextPage = True
    nextPageToken = ""
    i = 0
    while hasNextPage:
        i = i + 1
        reply = requests.get(getEndpoint(config, "playlists") + "&part=id&maxResults=50&channelId=" + channelId + "&pageToken=" + nextPageToken)
        content = json.loads(reply.content)
        try:
            if 'nextPageToken' in content:
                hasNextPage = True
                nextPageToken = content['nextPageToken']
            else:
                hasNextPage = False
            items = content['items']
            ids = ids + list(map(lambda x: x['id'], items))
        except:
            print(content)
        print("playlist page" + str(i) + " ok")
    return ids

def requestGetVideoFromPlaylist(config, playlistId):
    reply = requests.get(getEndpoint(config, "playlistItems") + "&part=contentDetails&maxResults=50&playlistId=" + playlistId)
    content = json.loads(reply.content)
    try:
        items = content['items']
        videoIds = list(map(lambda x: x['contentDetails']['videoId'], items))
    except:
        print(content)
    return videoIds

def requestIsVideoUnlisted(config, id):
    reply = requests.get(getEndpoint(config, "videos") + "&part=status&maxResults=1&id=" + id)
    content = json.loads(reply.content)
    privacyStatus = ""
    try:
        items = content['items']
        privacyStatus = items[0]['status']['privacyStatus']
    except:
        print(content)
    return "unlisted" == privacyStatus

def main():
    config = loadConfig()
    playlistsIds = requestGetUserPlaylistsIds(config, config['tests']['channel'])
    print(playlistsIds)
    videosListPerPlaylists = list(map(lambda x: requestGetVideoFromPlaylist(config, x), playlistsIds))
    print(videosListPerPlaylists)
    videosList = [item for sublist in videosListPerPlaylists for item in sublist] # merging every video into a single array
    uniqueVideos = list(set(videosList)) # removing doubles videos
    unlistedVideo = list(filter(lambda x: requestIsVideoUnlisted(config, x), uniqueVideos))
    print(unlistedVideo)

if __name__ == '__main__':
    main()
