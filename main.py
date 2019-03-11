import json
import os
import random
import mutagen
import mutagen.mp3
import subprocess
import sys
import threading
import time

from pygame import mixer


K_FACTOR = 128
MUSIC_PATH = '../../'



# old_songs_elo = json.load(open('elo.json.bak.json', 'r'))


def crawl(path):
	for item in os.listdir(path):
		if os.path.isfile(path + '/' + item):
			if item.split('.')[-1].lower() == 'mp3' and path + '/' + item not in songs_elo:
				# print("adding new song")
				audiofile = mutagen.File(path + '/' + item)
				title = str(audiofile.get("TIT2", "Unknown"))
				artist = str(audiofile.get("TPE1", "Unknown"))
				songs_elo[item] = {"elo": 1000, "title": title, "artist": artist}
		else:
			crawl(path + '/' + item)

def check(songs):
	remove = []
	for item in songs:
		if not os.path.isfile(MUSIC_PATH + item):
			print(item.encode('ascii', 'ignore').decode())
			remove.append(item)
	for item in remove:
		del songs[item]


def largest(songs):
	max_elo = 0
	largest = None
	for song in songs:
		if songs[song]['elo'] > max_elo:
			max_elo = songs[song]['elo']
			largest = song
			song_string = " ".join((song, ':', str(songs[song])))
			try:
				print(song_string)
			except UnicodeEncodeError:
				print(song_string.encode('ascii', 'ignore').decode())

def not_pristine_elos(songs):
	return len(list(filter(lambda x: songs[x]['elo'] != 1000, songs)))

songs_elo = {}

try:
	songs_elo = json.load(open('elo.json.bak.json', 'r', encoding='utf-8'))
except FileNotFoundError:
	crawl(MUSIC_PATH)


largest(songs_elo)

print(str(len(songs_elo)))


# check(songs_elo)


# print(str(len(songs_elo)))

# for key in old_songs_elo:
# 	if key in songs_elo:
# 		songs_elo[key]["elo"] = old_songs_elo[key]["elo"]

# json.dump(songs_elo, open('elo.json', 'w'))

def expected(a, b):
	return 1 / (1 + 10 ** ((b - a) / 400))

def update(a, b, result):
	return K_FACTOR * (result - expected(a, b))

user_input = ""

accepted_inputs = ['a', 'b', 'c', 'end', 's']
value = {'a': 1, 'b': 0, 'c': 0.5}

play_state = True




while user_input != 'end':

	song_a = random.choice(list(songs_elo.keys()))
	song_b = random.choice(list(songs_elo.keys()))
	song_string = " ".join(("A:", song_a, ":", str(songs_elo[song_a])))
	try:
		print(song_string)
	except UnicodeEncodeError:
		print(song_string.encode('ascii', 'ignore').decode())
	song_string = " ".join(("B:", song_b, ":", str(songs_elo[song_b])))
	try:
		print(song_string)
	except UnicodeEncodeError:
		print(song_string.encode('ascii', 'ignore').decode())
	print("C: random")
	user_input = ""
	while user_input not in accepted_inputs:
		user_input = input("Choose one: ").lower()
		if user_input.lower() == 'p':
			play_state = not play_state
			print("play state is", play_state)
		if user_input.lower() == 't':
			test_song_input = ""
			while test_song_input not in ('a', 'b', 'end', 's'):
				test_song_input = input("Which song?: ")
			test_thread = None
			if test_song_input == 'a':
				# test_thread = threading.Thread(target=subprocess.call, args=(["chrome", MUSIC_PATH + song_a],), kwargs={'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL})
				test_thread = threading.Thread(target=subprocess.call, args=(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", MUSIC_PATH + song_a],), kwargs={'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL})
			elif test_song_input == 'b':
				# test_thread = threading.Thread(target=subprocess.call, args=(["chrome", MUSIC_PATH + song_b],), kwargs={'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL})
				test_thread = threading.Thread(target=subprocess.call, args=(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", MUSIC_PATH + song_b],), kwargs={'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL})
			if test_thread:
				test_thread.start()

	if user_input != 'end' and user_input != 's':
		songs_elo = json.load(open('elo.json.bak.json', 'r', encoding='utf-8'))
	
		diff = update(songs_elo[song_a]["elo"], songs_elo[song_b]["elo"], value[user_input])
		songs_elo[song_a]["elo"] += diff
		songs_elo[song_b]["elo"] -= diff
		print("{0:.2f}".format(100*not_pristine_elos(songs_elo)/len(songs_elo)))
		json.dump(songs_elo, open('elo.json.bak.json', 'w', encoding='utf-8'), ensure_ascii=False)
		print(("+" if diff >= 0 else "") + str(diff))
		
		if play_state:
			song = song_a if user_input == 'a' else song_b if user_input == 'b' else random.choice((song_a, song_b))
			mp3_song = mutagen.mp3.MP3((MUSIC_PATH + song))
			# print(mp3_song.info.sample_rate)
			# mixer.init(frequency=mp3_song.info.sample_rate)
			# mixer.music.load((MUSIC_PATH + song).encode('utf-8'))
			# mixer.music.set_volume(0.05)
			# song_thread = threading.Thread(target=mixer.music.play)
			song_thread = threading.Thread(target=subprocess.call, args=(["afplay", MUSIC_PATH + song],))
			
			length = mp3_song.info.length
			song_thread.start()
			
			i = 0
			start = time.time()
			while i < 64:
				sys.stdout.write("\r[{0}]".format("=" * i + " " * (63 - i)))				
				sys.stdout.flush()
				if time.time() - start > (i + 1) / 64 * length:
					i += 1
			mixer.quit()
			print()
			

