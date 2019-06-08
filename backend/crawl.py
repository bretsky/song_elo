import json
import os
import random
import mutagen
import mutagen.mp3

MUSIC_PATH = '../../../Master/' # Mac or Linux


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
						elo = float(t.text[0])
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
			print(songs[item]["elo"])
			remove.append(item)
	for item in remove:
		del songs[item]

songs_elo = json.load(open('new_elo.json', 'r', encoding='utf-8'))
check(songs_elo)
# json.dump(songs_elo, open('new_elo.json', 'w', encoding='utf-8'))