from django.conf import settings
from django.shortcuts import get_object_or_404, render
from googleapiclient.discovery import build

from channel.models import Channel
import json

# Create your views here.

def main_page(request,title):
    channel = get_object_or_404(Channel,title=title)
    youtube = build('youtube', 'v3', developerKey=settings.YT_API_KEY)

    # Request channel information
    yt_request = youtube.channels().list(
        part='snippet,statistics,contentDetails',  # You can add more parts if needed
        id=channel.channel_id  # Use the channel ID to identify the channel
    )

    # Execute the request
    response = yt_request.execute()
    print(response)

    channel.description = response['items'][0]['snippet']['description']
    channel.subscriber_count = int(response['items'][0]['statistics']['subscriberCount'])
    channel.views_count = int(response['items'][0]['statistics']['viewCount'])
    channel.profile_high = response['items'][0]['snippet']['thumbnails']['high']['url']
    channel.profile_medium = response['items'][0]['snippet']['thumbnails']['medium']['url']
    channel.profile_small = response['items'][0]['snippet']['thumbnails']['default']['url']
    channel.save()

    print(response)
    return render(request,"channel/channel.html",{'channel':channel})
