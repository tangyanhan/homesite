#!/usr/bin/env python
#coding=utf-8

import sqlite3
import sys
import os
from subprocess import Popen, PIPE, STDOUT
import re
import datetime
import traceback
import pdb

import  homesite.settings
os.environ.update({"DJANGO_SETTINGS_MODULE": "homesite.settings"})
import django
django.setup()

from django.db.models import Max

from video.models import Video
from video.models import KeywordCount
from video.models import KeywordVideoId

#TODO: we should make it in a public library like 'supported format'
supported_video_formats = ['mp4','mov','wmv','rmvb','rm','avi']

THUMB_DIR = './static/thumb/'

THUMB_SIZE = '180x135'

gChangeDB = True

file_name_reg = None

VIDEO_ID = 0


class KeywordDictDataObj(object):

	def __init__(self):
		self.count = 0
		self.files = set()


def get_filename_tuple(filePath):
	global file_name_reg
	if file_name_reg is None:
		formats = ''
		first = True
		global supported_video_formats
		for f in supported_video_formats:
			if first:
				first = False
			else:
				formats += r'|'
			formats += f

		file_name_reg = re.compile(r'(.*)/([^/]+)\.('+ formats + r')$', re.UNICODE | re.IGNORECASE)

	match = file_name_reg.match(filePath)

	if match is not None:
		return match.groups()

	return None


def get_thumb_path(fileName):
	global THUMB_DIR
	if not os.path.isdir(THUMB_DIR):
		os.mkdir(THUMB_DIR)

	return './static/thumb/' + str(fileName) + '.png'

# TODO: we should use an advanced method to analyze them
# @return: a list of keywords concaternated together
def get_keywords(baseDir, filePath):
	filePath = str(filePath).replace(baseDir, '') #remove baseDir from filePath
	filePath = os.path.splitext(filePath)[0] #Only keep the part without extension
	filePath = str(filePath).lower()
	filePath = re.sub(r'[/.#]', ' ', filePath) #Replace meaningless symbols to space
	filePath = re.sub(r'\s+', ' ', filePath) #Replace multiple spaces to single one
	keywords = filePath.split(' ')

	return keywords

# Build dict from database
def buildKeywordDict():

	dict = {}
	keywords = KeywordCount.objects.all()

	for key in keywords:
		data = KeywordDictDataObj()
		data.count = key.count
		dict[ key.keyword ] = data

	del keywords

	key_vid_list = KeywordVideoId.objects.all()

	for kv in key_vid_list:
		if kv.keyword in dict:
			data = dict[ kv.keyword ]
			data.files.add(kv.video_id)
		else:
			print '#Keyword not found:', kv

	return dict

def saveDictToDatabase(dict):
	# Save dict to database
	for key in dict:
		data = dict[key]
		print '#', key, '#'
		print 'Count:',data.count
		for vid_id in data.files:
			print "\tvideo_id",vid_id
		if data.count > 0:
			kc = KeywordCount.objects.get(keyword=key)
			if kc is None:
				kc = KeywordCount()
			kc.keyword = key
			kc.count = data.count

			if gChangeDB:
				kc.save()

			for vid_id in data.files:
				files = KeywordVideoId.objects.filter(keyword=key,video_id=vid_id)

				if len(files) == 0:
					kph = KeywordVideoId()
					kph.keyword = key
					kph.video_id = vid_id

					if gChangeDB:
						kph.save()

def nextVideoId():
	global VIDEO_ID
	VIDEO_ID += 1
	return VIDEO_ID

def visitDir(baseDir):
	baseDir = os.path.abspath(baseDir)

	now = datetime.datetime.now()

	dict = buildKeywordDict()

	maxVideoId = Video.objects.all().aggregate(Max('video_id'))['video_id__max']

	if maxVideoId is not None:
		global VIDEO_ID
		VIDEO_ID = maxVideoId

	for (root, dirs, files) in os.walk(sys.argv[1]):
		for fname in files:
			try:
				file = os.path.join(root, fname)

				if os.path.isdir(file):
					continue

				tuple = get_filename_tuple(file)

				if tuple is None:
					continue

				(fileDir, fileName, ext) = tuple

				# skip hidden files (possibly not valid video files)
				if fileName.startswith('.'):
					continue

				needConvert = False
				if ext.lower() != 'mp4':
					needConvert = True
					# Disable video convert for the time being, we should convert them in idle time
					if True:
						mp4Path = os.path.join(fileDir, fileName)
						mp4Path += '.mp4'
						if not convert_video_to_mp4(file, mp4Path):
							print '#Failed to convert file to mp4:', file
							continue
						else:
							needConvert = False
							file = mp4Path
							ext = 'mp4'

				video_id = nextVideoId()

				video = Video.objects.get(video_id=video_id)

				if video is None:
					video = Video()
					video.video_id = video_id
					video.need_convert = needConvert

				thumbPath = get_thumb_path(video_id)

				output = gen_thumb(file,thumbPath)

				if output is None:
					continue

				duration = search_duration_from_text(output)

				del output

				if duration is None:
					print '#Failed to get duration from ',file
					duration = 0

				keywords = get_keywords(baseDir, file)

				print '#Keywords:',keywords
				for key in keywords:
					if len(key) == 0:
						continue
					else:
						print '#Added keyword:', key, '#'

					data = None
					if key in dict:
						data = dict[key]
					else:
						data = KeywordDictDataObj()
						dict[key] = data

					if video_id not in data.files:
						data.count = data.count + 1
						data.files.add(video_id)

				video.title = fileName
				video.path = file
				video.duration = duration

				if gChangeDB:
					video.save()

				print '#Video#', video.title, ' [', video.duration, ']', video.path

			except Exception as e:
				print '#Error while proceeding ', fname
				exc_type, exc_value, exc_traceback = sys.exc_info()
				print "*** print_exception:"
				traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

	saveDictToDatabase(dict)


# Generate thumbnail of given video. Delete thumbPath if thumbPath already exists
# @return: command output of ffmpeg

def gen_thumb(videoPath, thumbPath):
	if os.path.isfile(thumbPath):
		os.remove(thumbPath)

	global THUMB_SIZE
	cmd = ['ffmpeg', '-itsoffset', '-1', '-i', videoPath, '-vframes', '1', '-f', 'apng', '-s', THUMB_SIZE, thumbPath]
	p = Popen(cmd, stdout=PIPE, stderr=PIPE)

	output = p.communicate(input="y\n")[1] # TODO: need a solution to answer questions

	return output

# Convert video to mp4
def convert_video_to_mp4(videoPath,destPath):
	if os.path.isfile(destPath):
		print '#Already converted,skip:',destPath
		return True
	print '#Converting ',videoPath,'=>',destPath

	cmd = ['ffmpeg', '-i', videoPath, '-vcodec', 'h264', '-acodec', 'aac', destPath]
	p = Popen(cmd, stdout=PIPE, stderr=PIPE)

	p.communicate()

	# Remove old if succeeded
	if os.path.isfile(destPath) and os.path.getsize(destPath) > 0:
		os.remove(videoPath)
		return True

	return False

# Search the duration from given text
def search_duration_from_text(text):

	# Match pattern like Duration: 00:24:14.91, s
	regExp = re.compile(r'Duration: (\d{2}):(\d{2}):(\d{2})')

	result = regExp.search(text, re.M | re.U)

	if result is not None:
		(hour,min,sec) = result.groups()
		duration = int(hour) * 3600 + int(min) * 60 + int(sec)
		return duration

	return None

if __name__ == '__main__':
		if len(sys.argv) == 1:
			print 'Arguments: path_to_search [nosave]'
			print 'When nosave is given, no changes will be written to database'
			exit(0)
		searchDir = sys.argv[1]

		if len(sys.argv) > 2:
			if sys.argv[2] == 'nosave':
				gChangeDB = False
		print '###### Begin searching videos in ', searchDir

		visitDir(searchDir)
