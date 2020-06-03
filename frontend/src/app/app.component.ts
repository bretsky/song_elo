import { Component, OnInit, ViewChild, AfterViewInit, ChangeDetectorRef, Injectable, NgZone } from '@angular/core';
import { SongsApiService } from './services/songs-api.service';
import { API_URL } from './env';
import { Meta } from '@angular/platform-browser';
import WaveSurfer from 'wavesurfer.js';
import CursorPlugin from 'wavesurfer.js/dist/plugin/wavesurfer.cursor.min.js';
import { MatSnackBar, MatSnackBarRef, SimpleSnackBar, MatSnackBarConfig } from '@angular/material/snack-bar';


@Component({
	selector: 'app-root',
	templateUrl: './app.component.html',
	styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, AfterViewInit {
	title = 'frontend';
	songs: any;
	playing_song: any;
	songURL: string;
	songTestURL: string;
	testplayer: HTMLAudioElement;
	testSource: MediaElementAudioSourceNode;
	audioSource: MediaElementAudioSourceNode;
	gain: GainNode;
	testGain: GainNode;
	audioCtx = new AudioContext();
	queue: any;
	notStarted = true;
	volume = -2;
	scaledVolume = 1;
	testing = false;
	wavesurfer: WaveSurfer;
	seeking = false;
	topSongs: any;
	worstSongs: any;
	snackbarConfig: MatSnackBarConfig;

	constructor(private songsApi: SongsApiService, private meta: Meta, private cd: ChangeDetectorRef, private snackbar: MatSnackBar, private zone: NgZone) {
		meta.addTag({name: 'media-controllable'});
	}

	ngOnInit() {
		this.songsApi.getSongs().subscribe(res => {
			this.songs = res;
			document.addEventListener("MediaPlayPause", () => {
				this.wavesurfer.playPause();
			});
		},
		console.error
		);
		this.snackbarConfig = new MatSnackBarConfig();
	    this.snackbarConfig.panelClass = ['background-red'];
	    this.snackbarConfig.verticalPosition = 'bottom';
	    this.snackbarConfig.horizontalPosition = 'center';
	    this.snackbarConfig.duration = 5000;

		this.getQueue();
		this.songsApi.getTopSongs(50).subscribe(res => {
			this.topSongs = res;
		});
		this.songsApi.getWorstSongs(50).subscribe(res => {
			this.worstSongs = res;
		});
	}

	ngAfterViewInit() {
		requestAnimationFrame(() => {
			this.wavesurfer = WaveSurfer.create({
				container: '#waveform',
				waveColor: '#14868f',
				progressColor: '#143a3d',
				barWidth: 2,
				barGap: 2,
				cursorColor: '#ffffff',
				cursorWidth: 0,
				height: 64,
				normalize: true,
				responsive: true,
				plugins: [
					CursorPlugin.create({
		            showTime: true,
		            opacity: 1,
		            hideOnBlur: true,
		            deferInit: true,
		            width: 2,
		            customShowTimeStyle: {
		                'background-color': '#000',
		                color: '#fff',
		                padding: '2px',
		                'font-size': '12px',
		                'position': 'absolute',
		                'bottom': '0px',
		                'font-family': '"Roboto Condensed", sans-serif'
		            },
		            customStyle: {
		            	'height': '64px',
		            }
		        })
				]
			});
			this.wavesurfer.on('ready', () => {
				this.wavesurfer.play();
				this.cd.detectChanges();
				this.wavesurfer.cursor.init();
				this.wavesurfer.cursor.hideCursor();
				this.wavesurfer.cursor.formatTime = function (time) {
				    return [
				        Math.floor((time % 3600) / 60), // minutes
				        ('00' + Math.floor(time % 60)).slice(-2) // seconds
				    ].join(':');
				};
			});
			this.wavesurfer.on('finish', () => {
				this.advanceQueue();
			});
		});
	}

	seek(event) {
		if (!this.seeking && this.wavesurfer.cursor.cursor) {
			this.wavesurfer.cursor.hideCursor();
		}
	}

	startSeek(event) {
		if (this.wavesurfer.cursor.cursor) {
			this.seeking = true;
			this.wavesurfer.cursor.showCursor()
		}
	}

	unSeek(event) {
		if (this.wavesurfer.cursor.cursor) {
			this.seeking = false;
			this.wavesurfer.cursor.hideCursor()
		}
	}

	pickSong(song, random) {
		
	    
		if (this.testing) {
			this.songTestURL = API_URL + '/song' + encodeURIComponent(this.songs[song].filename);
			// this.songsApi.getReplayGain(this.songs[song].filename).subscribe(res => {
			// 	console.log(res);
			// 	this.replaygain = res['replaygain'];
			this.adjustVolume();
		// 		
			console.log(this.songTestURL);
		} else {
			this.songsApi.getStats().subscribe(res => {
				console.log(res);
			});
			this.songsApi.addToQueue(this.songs[song]).subscribe(res => {
				this.queue = res;
			});
			this.songsApi.getTopSongs(50).subscribe(res => {
				this.topSongs = res;
			});
			this.songsApi.getWorstSongs(50).subscribe(res => {
				this.worstSongs = res;
			});
			
			if (!random) {
				var rankA, rankB, newRankA, newRankB;
				this.songsApi.getRank(this.songs['a']['filename']).subscribe(res => {
					rankA = res;
				});
				this.songsApi.getRank(this.songs['b']['filename']).subscribe(res => {
					rankB = res;
				});
				var songA = this.songs['a']['filename'];
				var songB = this.songs['b']['filename'];
				this.songsApi.updateElo(this.songs['a']['filename'], this.songs['b']['filename'], (song == 'a') ? 1 : 0).subscribe(res => {
					console.log(res);
					this.songsApi.getRank(songA).subscribe(res => {
						newRankA = res;
						console.log(songA + ': ' + (rankA + 1) + ' -> ' + (newRankA + 1))
						if (Math.min(rankA, newRankA) < 50) {
							this.zone.run(() => {
						    	this.snackbar.open(songA + ': ' + (rankA + 1) + ' -> ' + (newRankA + 1), 'x', this.snackbarConfig);
						    });
						}
					});
					this.songsApi.getRank(songB).subscribe(res => {
						newRankB = res;
						console.log(songB + ': ' + (rankB + 1) + ' -> ' + (newRankB + 1))
						if (Math.min(rankB, newRankB) < 50) {
							this.zone.run(() => {
						    	this.snackbar.open(songB + ': ' + (rankB + 1) + ' -> ' + (newRankB + 1), 'x', this.snackbarConfig);
						    });
						}
					});
				});
			}		
			// this.play(this.songs[song]);

			this.getNewSongs();
		}
	}

	adjustVolume() {
		this.scaledVolume = Math.pow(10, (this.volume) / 10);
		console.log(this.gain.gain.value)
		this.gain.gain.value = this.scaledVolume;
		console.log(this.gain.gain.value)
	}

	play(song) {
		// this.songsApi.getReplayGain(song.filename).subscribe(res => {
		// 	console.log(res);
		// 	this.replaygain = res['replaygain'];
		// this.adjustVolume();
		// });
		this.songURL = API_URL + '/song' + encodeURIComponent(song.filename);
		this.wavesurfer.load(this.songURL);
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
			this.cd.detectChanges()
		});
	}

	togglePlay() {
		if (this.notStarted) {
			this.notStarted = false;
			this.play(this.queue[0]);
			this.gain = this.wavesurfer.backend.ac.createGain();
			this.gain.gain.value = this.scaledVolume;
			this.gain.channelCount = 1;
			this.gain.channelCountMode = "explicit";
			this.gain.channelInterpretation = "speakers";
			this.wavesurfer.backend.setFilter(this.gain);
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
			this.cd.detectChanges()
			if (this.queue.length > 0) {
				this.play(this.queue[0]);
			}
		});
		
	}

	randomSong() {
		var rankA, rankB, newRankA, newRankB;
		this.songsApi.getRank(this.songs['a']['filename']).subscribe(res => {
			rankA = res;
		});
		this.songsApi.getRank(this.songs['b']['filename']).subscribe(res => {
			rankB = res;
		});
		var songA = this.songs['a']['filename'];
		var songB = this.songs['b']['filename'];
		this.songsApi.updateElo(this.songs['a']['filename'], this.songs['b']['filename'], 0.5).subscribe(res => {
			console.log(res);
			this.songsApi.getRank(songA).subscribe(res => {
				newRankA = res;
				console.log(songA + ': ' + (rankA + 1) + ' -> ' + (newRankA + 1))
				if (Math.min(rankA, newRankA) < 50) {
					this.zone.run(() => {
				    	this.snackbar.open(songA + ': ' + (rankA + 1) + ' -> ' + (newRankA + 1), 'x', this.snackbarConfig);
				    });
				}
			});
			this.songsApi.getRank(songB).subscribe(res => {
				newRankB = res;
				console.log(songB + ': ' + (rankB + 1) + ' -> ' + (newRankB + 1))
				if (Math.min(rankB, newRankB) < 50) {
					this.zone.run(() => {
				    	this.snackbar.open(songB + ': ' + (rankB + 1) + ' -> ' + (newRankB + 1), 'x', this.snackbarConfig);
				    });
				}
			});
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
		//TODO: separate replaygain for test and main player
		if (this.testing) {
			window.setTimeout(() => {
				this.testplayer = <HTMLAudioElement>document.getElementById('testplayer');
				this.audioCtx = new AudioContext();
				this.testplayer.crossOrigin = 'anonymous';
				this.testSource = this.audioCtx.createMediaElementSource(this.testplayer);
				this.testGain = this.audioCtx.createGain();
				this.testGain.gain.value = 1;
				this.testGain.channelCount = 1;
				this.testGain.channelCountMode = "explicit";
				this.testGain.channelInterpretation = "speakers";
				this.testSource.connect(this.testGain);
				this.testGain.connect(this.audioCtx.destination);
				console.log(this.audioCtx);
			}, 0);
		}
	}

}
