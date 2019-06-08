import { Component, OnInit, ViewChild } from '@angular/core';
import { SongsApiService } from './services/songs-api.service';
import { API_URL } from './env';
import { Meta } from '@angular/platform-browser'; 

@Component({
	selector: 'app-root',
	templateUrl: './app.component.html',
	styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
	title = 'frontend';
	songs: any;
	playing_song: any;
	songURL: string;
	songTestURL: string;
	player: HTMLAudioElement;
	testplayer: HTMLAudioElement;
	testSource: MediaElementAudioSourceNode;
	audioSource: MediaElementAudioSourceNode;
	gain: GainNode;
	audioCtx = new AudioContext();
	queue: any;
	notStarted = true;
	replaygain = -8;
	volume = -2;
	scaledVolume = 1;
	testing = false;
	// @ViewChild('HTMLAudioElement', {static: true}) testplayer: HTMLAudioElement;

	constructor(private songsApi: SongsApiService, private meta: Meta) {
		meta.addTag({name: 'media-controllable'});
	}

	ngOnInit() {
		this.songsApi.getSongs().subscribe(res => {
			this.songs = res;
			console.log(res);
			document.addEventListener("MediaPlayPause", () => {
				console.log('playpause')
				if (this.player.paused) {
					this.player.play();
				} else {
					this.player.pause();
				}
			});
			console.log('done');
		},
		console.error
		);
		console.log(window.navigator);
		this.getQueue();
	}


	pickSong(song, random) {
		if (this.testing) {
			this.songTestURL = API_URL + '/song' + encodeURIComponent(this.songs[song].filename);
			this.songsApi.getReplayGain(this.songs[song].filename).subscribe(res => {
				console.log(res);
				this.replaygain = res['replaygain'];
			this.adjustVolume();
		});
			console.log(this.songTestURL);
		} else {
			this.songsApi.getStats().subscribe(res => {
				console.log(res);
			});
			this.songsApi.addToQueue(this.songs[song]).subscribe(res => {
				this.queue = res;
			});
			if (!random) {
				this.songsApi.updateElo(this.songs['a']['filename'], this.songs['b']['filename'], (song == 'a') ? 1 : 0).subscribe(res => {
				console.log(res);
			});
			}		
			// this.play(this.songs[song]);

			this.getNewSongs();
		}
	}

	adjustVolume() {
		this.scaledVolume = Math.pow(10, (this.replaygain + this.volume) / 10);
	}

	play(song) {
		this.songsApi.getReplayGain(song.filename).subscribe(res => {
			console.log(res);
			this.replaygain = res['replaygain'];
			this.adjustVolume();
		});
		this.songURL = API_URL + '/song' + encodeURIComponent(song.filename);
	}

	getNewSongs() {
		this.songsApi.newSongs().subscribe(res => {
			this.songs = res;
			console.log(res);
		},
		console.error
		);
	}

	getQueue() {
		this.songsApi.getQueue().subscribe(res => {
			this.queue = res;
		});
	}

	togglePlay() {
		if (this.notStarted) {
			this.notStarted = false;
			this.play(this.queue[0]);
			this.player = <HTMLAudioElement>document.getElementById('player');
			this.player.crossOrigin = 'anonymous';
			this.audioCtx = new(AudioContext)();
			this.audioSource = this.audioCtx.createMediaElementSource(this.player);
			
			this.gain = this.audioCtx.createGain()
			this.gain.gain.value = 1;
			this.gain.channelCount = 1;
			this.gain.channelCountMode = "explicit";
			this.gain.channelInterpretation = "speakers";
			this.audioSource.connect(this.gain);
			
			this.gain.connect(this.audioCtx.destination);
		}
	}

	clearQueue() {
		this.songsApi.clearQueue().subscribe(res => {
			this.queue = res;
		});
		this.songURL = '';
	}

	advanceQueue() {
		this.songsApi.removeFromQueue(0).subscribe(res => {
			this.queue = res;
			if (this.queue.length > 0) {
				this.play(this.queue[0]);
			}
		});
		
	}

	randomSong() {
		this.songsApi.updateElo(this.songs['a']['filename'], this.songs['b']['filename'], 0.5).subscribe(res => {
			console.log(res);
		})
		if (this.songs) {
			let rand = Math.floor((Math.random() * 2));
			if (rand == 0) {
				this.pickSong('a', true);
			} else {
				this.pickSong('b', true);
			}
		}
	}

	test() {
		this.testing = !this.testing;
		this.songTestURL = '';
		//TODO: also set up the other audio source here if we haven't already
		if (this.testing) {
			window.setTimeout(() => {
				this.testplayer = <HTMLAudioElement>document.getElementById('testplayer');
				this.testplayer.crossOrigin = 'anonymous';
				this.testSource = this.audioCtx.createMediaElementSource(this.testplayer);
				this.testSource.connect(this.gain);
			}, 0);
		}
	}

}
