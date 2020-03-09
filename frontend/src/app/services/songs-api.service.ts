import {Injectable} from '@angular/core';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {Observable} from 'rxjs/observable';
import 'rxjs/add/operator/catch';
import { throwError } from 'rxjs';
import {API_URL} from '../env';

@Injectable()
export class SongsApiService {

  constructor(private http: HttpClient) {
  }

  private static _handleError(err: HttpErrorResponse | any) {
    return Observable.throw(err.message || 'Error: Unable to complete request.');
  }

  getSongs(): Observable<any> {
    return this.http.get(`${API_URL}/get_songs`).catch(SongsApiService._handleError);
  }

  newSongs(): Observable<any> {
    return this.http.get(`${API_URL}/new_songs`).catch(SongsApiService._handleError);
  }

  getSong(filename: string) {
    return this.http.get(`${API_URL}/song/${encodeURIComponent(filename)}`).catch(SongsApiService._handleError);
  }

  getQueue() {
    return this.http.get(`${API_URL}/queue`).catch(SongsApiService._handleError);
  }

  addToQueue(song: string) {
    return this.http.post(`${API_URL}/queue`, {song: song}).catch(SongsApiService._handleError);
  }

  clearQueue() {
    return this.http.delete(`${API_URL}/queue`).catch(SongsApiService._handleError);
  }

  removeFromQueue(index: number) {
    return this.http.delete(`${API_URL}/queue/${index}`).catch(SongsApiService._handleError);
  }

  getReplayGain(filename: string) {
    return this.http.get(`${API_URL}/song${encodeURIComponent(filename)}/replaygain`).catch(SongsApiService._handleError);
  }

  updateElo(song_a: string, song_b: string, result: number) {
    return this.http.post(`${API_URL}/elo`, {a: song_a, b: song_b, result: result}).catch(SongsApiService._handleError);
  }

  getStats() {
    return this.http.get(`${API_URL}/stats`).catch(SongsApiService._handleError);
  }

  getTopSongs(n: number) {
    return this.http.get(`${API_URL}/top?n=${n}`).catch(SongsApiService._handleError);
  }

  getWorstSongs(n: number) {
    return this.http.get(`${API_URL}/worst?n=${n}`).catch(SongsApiService._handleError);
  }

  getRank(song: string) {
    return this.http.get(`${API_URL}/song${encodeURIComponent(song)}/rank`).catch(SongsApiService._handleError);
  }
}
