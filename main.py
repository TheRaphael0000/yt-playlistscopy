#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json

config = json.loads(open("config.ini", "r").read())

youtubeEndpoint = "https://www.googleapis.com/youtube/v3/"

playlistsEndPoint = youtubeEndpoint + \
    "playlists?key={}&part=snippet&maxResults=50&channelId={}&pageToken={}"
playlistItemsEndPoint = youtubeEndpoint + \
    "playlistItems?key={}&part=status,snippet,contentDetails&maxResults=50&playlistId={}&pageToken={}"
channelEndPoint = youtubeEndpoint + "channels?key={}&part=id,snippet,statistics"


def fetch_JSON(url):
    reply = requests.get(url)
    code = str(reply.status_code)
    content = json.loads(reply.content)
    if code[0] == "4" or code[0] == "5":
        print(url)
        print("Error : ", str(content["error"]["code"]))
        for er in content["error"]["errors"]:
            print("Domain :", er["domain"])
            print("Reason :", er["reason"])
            print("Message :", er["message"])
        exit()
    return content


def fetch_channel_data(usernameOrId):
    url = channelEndPoint.format(
        config['apikey']) + "&forHandle=" + usernameOrId
    channel = fetch_JSON(url)
    if len(channel['items']) > 0:
        return channel['items'][0]
    else:
        url = channelEndPoint.format(config['apikey']) + "&id=" + usernameOrId
        channel = fetch_JSON(url)
        if len(channel['items']) > 0:
            return channel['items'][0]
        else:
            return None


def fetch_playlists(channelId):
    playlistItems = []
    nextPageToken = ""
    while nextPageToken != None:
        url = playlistsEndPoint.format(
            config['apikey'], channelId, nextPageToken)
        playlists = fetch_JSON(url)
        try:
            if 'nextPageToken' in playlists:
                nextPageToken = playlists['nextPageToken']
            else:
                nextPageToken = None
            playlistItems = playlistItems + playlists['items']
        except:
            print(playlists)
    return playlistItems


def fetch_playlist_content(playlistId):
    videosItems = []
    nextPageToken = ""
    while nextPageToken is not None:
        url = playlistItemsEndPoint.format(
            config['apikey'], playlistId, nextPageToken)
        videos = fetch_JSON(url)
        try:
            if 'nextPageToken' in videos:
                nextPageToken = videos['nextPageToken']
            else:
                nextPageToken = None
            videosItems = videosItems + videos['items']
        except:
            print(videos)
    return videosItems


def channel_infos(channel):
    print("-------------------------------")
    print(f"Title : {channel['snippet']['title']}")
    print(f"Description : {channel['snippet']['description']}")
    print(f"Url : https://www.youtube.com/channel/{channel['id']}")
    if "customUrl" in channel['snippet']:
        print(
            f"Custom Url : https://www.youtube.com/{channel['snippet']['customUrl']}")
    print(f"Creation : {channel['snippet']['publishedAt']}")
    if "county" in channel['snippet']:
        print(f"Country : {channel['snippet']['country']}")
    print(
        f"Number of subscribers : {channel['statistics']['subscriberCount']}")
    print(f"Number of views : {channel['statistics']['viewCount']}")
    print(f"Number of videos : {channel['statistics']['videoCount']}")
    print("-------------------------------")


def video_infos(video):
    return f"[{video['status']['privacyStatus']}] : {video['snippet']['title']} (https://youtu.be/{video['contentDetails']['videoId']})"


def playlist_infos(playlist):
    return f"{playlist['snippet']['title']} (https://www.youtube.com/playlist?list={playlist['id']})"


def analyse():
    notPublicVideos = []

    channel = None

    while channel is None:
        username = input("Username/Channel ID : ")
        channel_data = fetch_channel_data(username)
        if channel_data is None:
            print("Invalid channel")
            continue

        channel_infos(channel_data)
        response = "-"
        while response != "n":
            response = input("Correct user ? [Y/n] : ").lower()
            if response == "y" or response == "":
                channel = channel_data
                break

    print("Looking for playlists...")
    playlists = fetch_playlists(channel['id'])

    if len(playlists) <= 0:
        print("No playlists found !")
        exit()

    videos = []
    for playlist in playlists:
        print("- " + playlist_infos(playlist))
        videoInPlaylist = fetch_playlist_content(playlist['id'])
        videos = videos + videoInPlaylist
        for video in videoInPlaylist:
            if 'status' in video:
                if video['status']['privacyStatus'] != 'public':
                    print("-- " + video_infos(video))
                    notPublicVideos.append((playlist, video))
            else:
                print("-- [deleted video]")

    notPublicVideos.sort(key=lambda v: v[1]['status']['privacyStatus'])

    print("Summary")
    if len(notPublicVideos) <= 0:
        print("No videos found !")
    for playlist, video in notPublicVideos:
        print(video_infos(video) + " in " + playlist_infos(playlist))


if __name__ == '__main__':
    while True:
        analyse()
