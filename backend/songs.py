import json
import os
import random
import mutagen
import mutagen.mp3
import subprocess
import sys
import threading
import time
import unicodedata
import win32gui, win32console
import win32con
from win32com.client import Dispatch
import pywintypes
from flask import Flask

K_FACTOR = 128
MUSIC_PATH = '../../../Master/' # Mac or Linux
# MUSIC_PATH = '..\\..\\Master\\'
history = []




# old_songs_elo = json.load(open('elo.json.bak.json', 'r'))


def crawl(path):
	for item in os.listdir(MUSIC_PATH + path):
		if os.path.isfile(MUSIC_PATH + path + '/' + item):
			if item.split('.')[-1].lower() == 'mp3' and path + '/' + item not in songs_elo:
				print("adding new song")

				audiofile = mutagen.File(MUSIC_PATH + path + '/' + item)
				title = str(audiofile.get("TIT2", "Unknown"))
				print(title)
				print(item)
				text = audiofile.tags.getall('TXXX')
				elo = 1000
				for t in text:
					if t.desc == 'elo':
						elo = t.text
				artist = str(audiofile.get("TPE1", "Unknown"))
				songs_elo[path + '/' + item] = {"elo": elo, "title": title, "artist": artist, "n": 0}
		elif os.path.isdir(MUSIC_PATH + path + '/' + item):
			print(path + '/' + item)
			crawl(path + '/' + item)

def check(songs):
	remove = []
	for item in songs:
		if not os.path.isfile(MUSIC_PATH + item):
			print(item)
			remove.append(item)
	for item in remove:
		del songs[item]


def minmax(songs):
	elos = [songs[song]["elo"] for song in songs]
	max_elo = min(elos)
	min_elo = max(elos)
	largest = None
	smallest = None
	for song in songs:
		if songs[song]['elo'] > max_elo:
			max_elo = songs[song]['elo']
			largest = song
			song_string = " ".join((song, ':', str(songs[song])))
			try:
				print(song_string)
			except UnicodeEncodeError:
				print(song_string.encode('ascii', 'ignore').decode())
		if songs[song]['elo'] < min_elo:
			min_elo = songs[song]['elo']
			smallest = song
			song_string = " ".join((song, ':', str(songs[song])))
			try:
				print(song_string)
			except UnicodeEncodeError:
				print(song_string.encode('ascii', 'ignore').decode())


def not_pristine_elos(songs):
	return len(list(filter(lambda x: songs[x]['elo'] != 1000, songs)))

def stddev(songs):
	return (sum((songs[s]["elo"] - 1000) ** 2 for s in songs) / len(songs)) ** (1/2)

def round_to(x, base=50):
    return base * round(x/base)


def get_dist(songs):
	elos = [songs[song]["elo"] for song in songs]
	min_elo = round_to(min(elos))
	max_elo = round_to(max(elos))
	dist = {}
	for i in range(min_elo, max_elo + 50, 50):
		dist[i] = 0
	for song in songs:
		dist[round_to(songs[song]["elo"])] += 1
	for i in range(min_elo, max_elo + 50, 50):
		print(i, dist[i])


songs_elo = {}

try:
	songs_elo = json.load(open('new_elo.json', 'r', encoding='utf-8'))
except FileNotFoundError:
	crawl('')


def expected(a, b):
	return 1 / (1 + 10 ** ((b - a) / 400))

def update(a, b, result):
	return K_FACTOR * (result - expected(a, b))

def get_weights(songs, keys):
	weights = []
	for key in keys:
		weights.append(expected(songs[key]["elo"], 1000))
	return weights

def get_new_pair():
	keys = list(songs_elo.keys())
	weights = get_weights(songs_elo, keys)
	song_a = random.choices(keys, weights)[0]
	# print(weights[keys.index(song_a)] / sum(weights) * 100)
	# print(weights[keys.index(song_a)] / sum(weights) * len(weights))
	song_b = random.choice(list(songs_elo.keys()))
	response = {}
	a_dict = songs_elo[song_a]
	a_dict['filename'] = song_a
	b_dict = songs_elo[song_b]
	b_dict['filename'] = song_b
	response = {'a': a_dict, 'b': b_dict}
	with open('current.json', 'w') as current:
		json.dump(response, current)
	return response

def get_current_songs():
	try:
		with open('current.json', 'r') as current:
			response = json.load(current)
	except FileNotFoundError:
		response = get_new_pair()
	return response

def print_data(data):
	print(data)

def get_from_queue():
	try:
		with open('queue.json', 'r') as current:
			queue = json.load(current)
	except FileNotFoundError:
		queue = []
	return queue

def clear_queue():
	with open('queue.json', 'w') as queue_file:
		json.dump([], queue_file)
	return []

def add_to_queue(song):
	try:
		with open('queue.json', 'r') as current:
			queue = json.load(current)
			queue.append(song)
	except FileNotFoundError:
		queue = [song]
	with open('queue.json', 'w') as queue_file:
		json.dump(queue, queue_file)
	return queue

def remove_from_queue(index):
	try:
		with open('queue.json', 'r') as current:
			queue = json.load(current)
			if len(queue) > index:
				queue = queue[:index] + queue[index + 1:]
	except FileNotFoundError:
		queue = []
	with open('queue.json', 'w') as queue_file:
		json.dump(queue, queue_file)
	return queue

def adjust_elo(a, b, result):
	diff = update(songs_elo[a]["elo"], songs_elo[b]["elo"], result)
	songs_elo[a]["elo"] += diff
	songs_elo[a]["n"] += 1
	audiofile = mutagen.File(MUSIC_PATH + unicodedata.normalize('NFC', a))
	audiofile.tags.add(mutagen.id3.TXXX(desc='elo', text=str(songs_elo[a]["elo"])))
	audiofile.save()

	songs_elo[b]["elo"] -= diff
	songs_elo[b]["n"] += 1
	audiofile = mutagen.File(MUSIC_PATH + unicodedata.normalize('NFC', b))
	audiofile.tags.add(mutagen.id3.TXXX(desc='elo', text=str(songs_elo[b]["elo"])))
	audiofile.save()
	history.append(((a, diff), (b, -diff)))
	# print("{0:.2f}".format(100*not_pristine_elos(songs_elo)/len(songs_elo)))
	# print(sum((songs_elo[song]['n'] for song in songs_elo))/len(songs_elo))
	# print(sum((songs_elo[song]['elo'] for song in songs_elo))/len(songs_elo))
	# print(stddev(songs_elo))
	json.dump(songs_elo, open('new_elo.json', 'w', encoding='utf-8'), ensure_ascii=False)
	return diff


def get_replaygain(filename):
	file = mutagen.File(unicodedata.normalize('NFC', filename))
	text = file.tags.getall('TXXX')
	gain = 0
	for t in text:
		if t.desc == 'replaygain_track_gain':
			gain = t.text
	return float(gain[0].split()[0])
	# return 10 ** (float(gain[0].split()[0]) / 10)

def get_songs_stats():
	percent_rated = 100*not_pristine_elos(songs_elo)/len(songs_elo)
	mean_ratings = sum((songs_elo[song]['n'] for song in songs_elo))/len(songs_elo)
	elo_stddev = stddev(songs_elo)
	return {"percent_rated": percent_rated, "mean_ratings": mean_ratings, "stddev": elo_stddev}
