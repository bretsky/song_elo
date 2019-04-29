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

from pygame import mixer


K_FACTOR = 128
MUSIC_PATH = '../../Master/' # Mac or Linux
# MUSIC_PATH = '..\\..\\Master\\'




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
			print(item.encode('ascii', 'ignore').decode())
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


# for key in songs_elo:
# 	if songs_elo[key]['elo'] != 1000:
# 		songs_elo[key]['elo'] = float(songs_elo[key]["elo"][0])
# 	# exit()

# json.dump(songs_elo, open('new_elo.json', 'w', encoding='utf-8'), ensure_ascii=False)


# exit()

# crawl(MUSIC_PATH)

minmax(songs_elo)

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

def get_weights(songs, keys):
	weights = []
	for key in keys:
		weights.append(expected(songs[key]["elo"], 1000))
	return weights

# Moves window to foreground (only on Windows)
def set_foreground(handle):
        win32gui.ShowWindow(handle, win32con.SW_RESTORE)
        win32gui.SetWindowPos(handle, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)  
        win32gui.SetWindowPos(handle, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)  
        win32gui.SetWindowPos(handle, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
        shell = Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(handle)

user_input = ""

accepted_inputs = ['a', 'b', 'c', 'end', 's']
value = {'a': 1, 'b': 0, 'c': 0.5}

play_state = True


history = []

while user_input != 'end':
	keys = list(songs_elo.keys())
	weights = get_weights(songs_elo, keys)
	song_a = random.choices(keys, weights)[0]
	print(weights[keys.index(song_a)] / sum(weights) * 100)
	print(weights[keys.index(song_a)] / sum(weights) * len(weights))
	song_b = random.choice(list(songs_elo.keys()))
	# song_a = unicodedata.normalize('NFC', song_a)
	# song_b = unicodedata.normalize('NFC', song_b)
	song_string = " ".join(("A:", song_a, ":", str(songs_elo[song_a])))
	try:
		print(unicodedata.normalize('NFC', song_string))
	except UnicodeEncodeError:
		print(song_string.encode('ascii', 'ignore').decode())
	song_string = " ".join(("B:", song_b, ":", str(songs_elo[song_b])))
	try:
		print(unicodedata.normalize('NFC', song_string))
	except UnicodeEncodeError:
		print(song_string.encode('ascii', 'ignore').decode())
	print("C: random")
	user_input = ""
	window = win32console.GetConsoleWindow()
	print(window)
	set_foreground(window)
	while user_input not in accepted_inputs:
		try:
			user_input = input("Choose one: ").lower().strip()
		except EOFError:
			time.sleep(0.1)
			user_input = input().lower().strip()
		if user_input == 'u':
			if history:
				last = history.pop()
				for pair in last:
					songs_elo = json.load(open('new_elo.json', 'r', encoding='utf-8'))
					songs_elo[pair[0]]["elo"] -= pair[1]
					songs_elo[pair[0]]["n"] -= 1
					json.dump(songs_elo, open('new_elo.json', 'w', encoding='utf-8'), ensure_ascii=False)
		if user_input == 'd':
			get_dist(songs_elo)
		if user_input == 'p':
			play_state = not play_state
			print("play state is", play_state)
		if user_input == 't':
			test_song_input = ""
			while test_song_input not in ('a', 'b', 'end', 's'):
				test_song_input = input("Which song?: ")
			test_thread = None
			if test_song_input == 'a':
				test_thread = threading.Thread(target=subprocess.call, args=(["C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe", unicodedata.normalize('NFC', MUSIC_PATH + song_a)],), kwargs={'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}) # Windows
				# test_thread = threading.Thread(target=subprocess.call, args=(["google-chrome", MUSIC_PATH + unicodedata.normalize('NFC', song_a)],), kwargs={'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}) # Linux
				# test_thread = threading.Thread(target=subprocess.call, args=(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", MUSIC_PATH + song_a],), kwargs={'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}) # Mac
			elif test_song_input == 'b':
				test_thread = threading.Thread(target=subprocess.call, args=(["C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe", unicodedata.normalize('NFC', MUSIC_PATH + song_b)],), kwargs={'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}) # Windows
				# test_thread = threading.Thread(target=subprocess.call, args=(["google-chrome", MUSIC_PATH + unicodedata.normalize('NFC', song_b)],), kwargs={'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}) # Linux
				# test_thread = threading.Thread(target=subprocess.call, args=(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", MUSIC_PATH + song_b],), kwargs={'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}) # Mac
			if test_thread:
				test_thread.start()

	if user_input != 'end' and user_input != 's':
		songs_elo = json.load(open('new_elo.json', 'r', encoding='utf-8'))
	
		diff = update(songs_elo[song_a]["elo"], songs_elo[song_b]["elo"], value[user_input])
		songs_elo[song_a]["elo"] += diff
		songs_elo[song_a]["n"] += 1
		audiofile = mutagen.File(MUSIC_PATH + unicodedata.normalize('NFC', song_a))
		audiofile.tags.add(mutagen.id3.TXXX(desc='elo', text=str(songs_elo[song_a]["elo"])))
		audiofile.save()

		songs_elo[song_b]["elo"] -= diff
		songs_elo[song_b]["n"] += 1
		audiofile = mutagen.File(MUSIC_PATH + unicodedata.normalize('NFC', song_b))
		audiofile.tags.add(mutagen.id3.TXXX(desc='elo', text=str(songs_elo[song_b]["elo"])))
		audiofile.save()
		history.append(((song_a, diff), (song_b, -diff)))
		print("{0:.2f}".format(100*not_pristine_elos(songs_elo)/len(songs_elo)))
		print(sum((songs_elo[song]['n'] for song in songs_elo))/len(songs_elo))
		print(sum((songs_elo[song]['elo'] for song in songs_elo))/len(songs_elo))
		print(stddev(songs_elo))
		json.dump(songs_elo, open('new_elo.json', 'w', encoding='utf-8'), ensure_ascii=False)
		print(("+" if diff >= 0 else "") + str(diff))
		
		if play_state:
			song = song_a if user_input == 'a' else song_b if user_input == 'b' else random.choice((song_a, song_b))
			mp3_song = mutagen.mp3.MP3((MUSIC_PATH + unicodedata.normalize('NFC', song)))
			print(mp3_song.info.sample_rate)
			# mixer.init(frequency=mp3_song.info.sample_rate)
			# mixer.music.load((MUSIC_PATH + unicodedata.normalize('NFC', song)).encode('utf-8'))
			# mixer.music.set_volume(0.5)
			# song_thread = threading.Thread(target=mixer.music.play)
			song_thread = threading.Thread(target=subprocess.call, args=(["mpg123", "--rva-mix", MUSIC_PATH + unicodedata.normalize('NFC', song)],), kwargs={'stdin': subprocess.DEVNULL, 'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL})
			
			length = mp3_song.info.length

			song_thread.start()
			
			i = 0
			start = time.time()
			while i < 64:
				sys.stdout.write("\r[{0}]".format("=" * i + " " * (63 - i)))				
				sys.stdout.flush()
				if time.time() - start > (i + 1) / 64 * length:
					i += 1
				time.sleep(length / 256)
			mixer.quit()
			print()
			

