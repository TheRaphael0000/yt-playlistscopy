#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import requests
import json

config = json.loads(open("config.ini", "r").read())

youtubeEndpoint = "https://www.googleapis.com/youtube/v3/"

playlistsEndPoint = youtubeEndpoint + "playlists?key={}&part=snippet&maxResults=50&channelId={}&pageToken={}"
playlistItemsEndPoint = youtubeEndpoint + "playlistItems?key={}&part=status,snippet,contentDetails&maxResults=50&playlistId={}&pageToken={}"
channelEndPoint = youtubeEndpoint + "channels?key={}&part=id,snippet&forUsername={}"

def fetch_JSON(url):
    reply = requests.get(url)
    content = json.loads(reply.content)
    return content

def fetch_channel_data(username):
    url = channelEndPoint.format(config['apikey'], username)
    channel = fetch_JSON(url)
    return channel['items']

def fetch_playlists(channelId):
    playlistItems = []
    nextPageToken = ""
    while nextPageToken != None:
        url = playlistsEndPoint.format(config['apikey'], channelId, nextPageToken)
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
    while nextPageToken != None:
        url = playlistItemsEndPoint.format(config['apikey'], playlistId, nextPageToken)
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
    print("Title : " + channel['snippet']['title'])
    print("Description : " + channel['snippet']['description'])
    print("Url : https://www.youtube.com/channel/" + channel['id'])
    if channel['snippet']['customUrl']:
        print("Custom Url : https://www.youtube.com/" + channel['snippet']['customUrl'])
    print("Creation : " + channel['snippet']['publishedAt'])
    print("Country : " + channel['snippet']['country'])
    print("-------------------------------")

def video_infos(video):
    return "[" + video['status']['privacyStatus'] + "] : " + video['snippet']['title'] + " (https://youtu.be/"+ video['contentDetails']['videoId'] +")"

def playlist_infos(playlist):
    return playlist['snippet']['title'] + " (https://www.youtube.com/playlist?list="+ playlist['id'] + ")"

def main():
    notPublicVideos = []

    channel = None

    while channel == None:
        username = input("Username : ")
        data = fetch_channel_data(username)
        if len(data) <= 0:
            print("Invalid channel")
            continue

        channel_infos(data[0])
        response = "-"
        while response != "n":
            response = input("Correct user ? [Y/n] : ").lower()
            if response == "y" or response == "":
                channel = data[0]
                break

    print("Looking for playlists")
    playlists = fetch_playlists(channel['id'])
    videos = []
    for playlist in playlists:
        print("- " + playlist_infos(playlist))
        videoInPlaylist = fetch_playlist_content(playlist['id'])
        videos = videos + videoInPlaylist
        for video in videoInPlaylist:
            if video['status']['privacyStatus'] != 'public':
                print("-- " + video_infos(video))
                notPublicVideos.append((playlist, video))

    print("Summary")
    for playlist, video in notPublicVideos:
        print(video_infos(video) + " in " + playlist_infos(playlist))

if __name__ == '__main__':
    main()
