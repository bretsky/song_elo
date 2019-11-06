import json
import os
import random
import mutagen
import base64
import hashlib
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
				if not audiofile.tags:
					audiofile.add_tags()
				text = audiofile.tags.getall('TXXX')
				song_id = ''
				for t in text:
					if t.desc == 'id':
						song_id = t.text[0]
				elo = 1000
				for t in text:
					if t.desc == 'elo':
						elo = float(t.text[0])
				artist = str(audiofile.get("TPE1", "Unknown"))
				updated = False
				if song_id:
					print('has_id')
					for key in songs_elo:
						if 'id' in songs_elo[key] and songs_elo[key]['id'] == song_id:
							if songs_elo[key] != {"elo": elo, "title": title, "artist": artist, "n": 0, "filename": path + '/' + item}:
								songs_elo[path + '/' + item] = {"elo": elo, "title": title, "artist": artist, "n": 0, "filename": path + '/' + item}
								songs_elo[path + '/' + item]["elo"] = songs_elo[key]["elo"]
								songs_elo[path + '/' + item]["n"] = songs_elo[key]["n"]
								print("update: ")
								print(key, "->", path + '/' + item)
								del songs_elo[key]
								updated = True
								break
				if not updated:
					m = hashlib.shake_256()
					m.update((path + '/' + item).encode())
					new_id = base64.urlsafe_b64encode(m.digest(9)).decode()
					songs_elo[path + '/' + item] = {"elo": elo, "title": title, "artist": artist, "n": 0, "filename": path + '/' + item, 'id': new_id}
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
	return songs

songs_elo = json.load(open('elo_id.json', 'r', encoding='utf-8'))
crawl('')
# songs_elo = check(songs_elo)
json.dump(songs_elo, open('elo_id.json', 'w', encoding='utf-8'))