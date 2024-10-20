from django.contrib.auth.decorators import login_required
from django.shortcuts import Http404, get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from channel.models import Channel
from account.models import Account
from page.models import Video
import json

from account.models import Account

from googleapiclient.discovery import build

def index(request):
	# If no account exists redirect to signin
	try:
		account : Account = get_object_or_404(Account,user=request.user)
	except:
		return redirect("/account/signin")

	# getRandomVideos(account)
	video = Video.objects.order_by('?')[:40]

	return render(request, "page/home.html", {'videos': video, "vert": False})

def format_videos(response):
	"""
	Will preforme a search to youtube with the search string and
	return a list of videos in a nicer format.
	"""
	import urllib.parse

	videos = []
	for item in response['items']:
		if 'contentDetails' in item and not item['contentDetails'].get('embeddable', True):
			continue

		## in some request the video id is in the resouceId
		try:
			video_id = item['id']['videoId']
		except:
			video_id = item['snippet']['resourceId']['videoId']

		print(item)	#

		thumbnails = item['snippet']['thumbnails']
		default_thumbnail = thumbnails['default']['url'] if 'default' in thumbnails else None
		medium_thumbnail = thumbnails['medium']['url'] if 'medium' in thumbnails else None
		high_thumbnail = thumbnails['high']['url'] if 'high' in thumbnails else None


		video_data = {
			'title': item['snippet']['title'],
			'video_id': video_id,
			'channel_id':item['snippet']['channelId'],
			'channel_title':item['snippet']['channelTitle'],
			'description': item['snippet']['description'],
			'thumbnail': medium_thumbnail,  # Higher resolution thumbnail
			'embed_url': f"https://www.youtube.com/embed/{video_id}"
		}
		video_data['json'] = json.dumps(video_data)
		video_data['get'] = urllib.parse.urlencode(video_data)
		videos.append(video_data)

	return videos
def search(request):
	_term = request.GET.get('term', 'christ is king')
	videos = format_videos(performSearch(_term))

	return render(request, "page/home.html", {"videos": videos, "vert": True})

def performSearch(_term, _maxRes = 50):
	youtube = build('youtube', 'v3', developerKey=settings.YT_API_KEY)
	request = youtube.search().list(
		q=_term,
		part="snippet",
		type="video",
		maxResults=_maxRes
	)
	return request.execute()

def getRandomVideos(account: Account):
	videos = format_videos(performSearch(account.home_screen_tags))

	for item in videos:
			# Store the video in the database
		video, created = Video.objects.get_or_create(
			video_id=item['videoId'],
			defaults={
				'title': item['title'],
				'description': item['description'],
				'thumbnail': item['thumbnail']
			}
		)

def showVideo(request, video_id):
	embed_url = f"https://www.youtube.com/embed/{video_id}"
	videos = Video.objects.order_by('?')[:20]
	return render(request, "page/video.html", {'video': Video.objects.get(video_id=video_id), 'embed_url': embed_url, 'recommended': videos})

def addor_and_show(request):
	video_data = request.GET

	video, created = Video.objects.get_or_create(
		video_id=video_data['video_id'],
		defaults={
			'title': video_data['title'],
			'description': video_data['description'],
			'thumbnail': video_data['thumbnail']
		}
	)
	channel,channel_created = Channel.objects.get_or_create(channel_id=video_data['channel_id'],title=video_data['channel_title'])
	video.channel = channel
	video.save()

	return redirect(f'/video/{video.video_id}/')
#	response = HttpResponse()
#	response.headers['Hx-Redirect'] = f'/video/{video.video_id}/'
#
#	return response
