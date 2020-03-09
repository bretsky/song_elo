from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from flask_cors import CORS

import unicodedata

from songs import *


app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
	return render_template('index.html')

@app.route('/get_songs', methods=['GET'])
def get_songs():
	songs = get_current_songs()
	return jsonify(songs)

@app.route('/new_songs', methods=['GET'])
def new_songs():
	songs = get_new_pair()
	return jsonify(songs)

@app.route('/song/<path:filename>', methods=['GET'])
def play_song(filename):
	return send_from_directory('../../../../Master', unicodedata.normalize('NFC', filename))

@app.route('/song/<path:filename>/replaygain', methods=['GET'])
def replaygain(filename):
	return jsonify({'replaygain': get_replaygain('../../../../Master/' + unicodedata.normalize('NFC', filename))})

@app.route('/elo', methods=['POST'])
def elo():
	diff = adjust_elo(request.get_json().get('a'), request.get_json().get('b'), request.get_json().get('result'))
	return jsonify({'result': diff})

@app.route('/queue', methods=['GET', 'POST', 'DELETE'])
def queue():
	# print_data(request.args.keys())
	# print(request.args.keys())
	if request.method == 'GET':
		print('get')
		return jsonify(get_from_queue())
	elif request.method == 'POST':
		return jsonify(add_to_queue(request.get_json().get('song')))
	elif request.method == 'DELETE':
		app.logger.error('delete')
		print('delete')
		return jsonify(clear_queue())
		
@app.route('/queue/<path:index>', methods=['DELETE'])
def remove_song(index):
	if request.method == 'DELETE':
		return jsonify(remove_from_queue(int(index)))

@app.route('/stats', methods=['GET'])
def get_stats():
	return jsonify(get_songs_stats())

@app.route('/top', methods=['GET'])
def get_top():
	n = 10
	if request.args.get('n'):
		n = int(request.args.get('n'))
	return jsonify(get_top_songs(n))

@app.route('/worst', methods=['GET'])
def get_worst():
	n = 10
	if request.args.get('n'):
		n = int(request.args.get('n'))
	return jsonify(get_top_songs(n, False))

@app.route('/song/<path:filename>/rank', methods=['GET'])
def get_rank(filename):
	return jsonify(get_song_rank('/' + filename))




if __name__ == '__main__':
	app.run(host='0.0.0.0', port=3333, debug=True)