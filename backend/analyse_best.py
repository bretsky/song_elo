import json


top_song_history = []
with open('best.json', 'r') as best_file:
	top_song_history = json.load(best_file)

all_songs = []
for instance in top_song_history:
	for song in instance:
		if song[0] not in all_songs:
			all_songs.append(song[0])

print(len(all_songs))


for song in all_songs:
	song_history = [song]
	for instance in top_song_history:
		elo = 0
		for song_pair in instance:
			elo = song_pair[1]
			if song_pair[0] == song:
				break
		song_history.append(elo)
	print(';'.join([str(i) for i in song_history]))