import json
import base64
import hashlib
import mutagen
import unicodedata
# elostr = open('elo.json.bak.json', 'r').read().encode().decode('unicode-escape')

MUSIC_PATH = '../../../Master/'
elo = json.load(open('elo_id.json', 'r', encoding='utf-8'))

for key in elo:
	m = hashlib.shake_256()
	m.update(key.encode())
	elo[key]['id'] = base64.urlsafe_b64encode(m.digest(9)).decode()
	audiofile = mutagen.File(MUSIC_PATH + unicodedata.normalize('NFC', key))
	audiofile.tags.add(mutagen.id3.TXXX(desc='id', text=elo[key]["id"]))
	audiofile.save()

# def fix(d):
# 	new_dict = {}
# 	for key in d:
# 		if type(d[key]) == dict:
# 			new_dict[key] = fix(d[key])
# 		else:
# 			new_dict[fix_string(key)] = fix_string(d[key])
# 	return new_dict

# def fix_string(s):
# 	if type(s) == str:
# 		try:
# 			return s.encode('ascii', 'backslashreplace').decode('unicode-escape')
# 		except UnicodeEncodeError:
# 			print(s)
# 	else:
# 		return s

# new_dict = fix(elo)

# print(str(new_dict)[:1750])

# elostr = json.dumps(elo).replace('"', '\\"')

# print(elostr[:1750])

# elostr = elostr.encode('utf-8').decode('unicode-escape')

# print(elostr[:1750])

# elo = json.loads(elostr)

json.dump(elo, open('elo_id.json', 'w', encoding='utf-8'), ensure_ascii=False)




# json.dump(elo, open('elo.json.bak.json', 'w'))
