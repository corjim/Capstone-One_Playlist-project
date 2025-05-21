from flask import flash, redirect, request, g
from requests import get
import json


def fetch_artist_info(artist_name, headers):
    """Fetch basic artist information from API."""
    url = "https://api.spotify.com/v1/search"
    query_params = {'q': artist_name, 'type': 'artist', 'limit': 1}
    result = get(url, headers=headers, params=query_params)
    artist_items = json.loads(result.content).get('artists', {}).get('items', [])
    return artist_items[0] if artist_items else None


def fetch_artist_albums(artist_id, headers):
    """Fetch artist albums and their details."""
    album_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    album_params = {'market': 'US', 'limit': 10}
    album_result = get(album_url, headers=headers, params=album_params)
    albums_json = json.loads(album_result.content).get('items', [])

    albums_info = []
    for album in albums_json:
        album_details = {
            'album_name': album.get('name'),
            'id': album.get('id'),
            'image': album.get('images', [{}])[0].get('url'),
            'release_date': album.get('release_date'),
            'total_tracks': album.get('total_tracks'),
            'album_url' :album.get('images')[0]['url'],
            'tracks': fetch_album_tracks(album.get('id'), headers),
        }
        albums_info.append(album_details)
    return albums_info


def fetch_album_tracks(album_id, headers):
    """Fetch tracks for a specific album."""
    tracks_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    tracks_result = get(tracks_url, headers=headers)
    tracks_json = json.loads(tracks_result.content).get('items', [])
    return [track.get('name') for track in tracks_json]


def fetch_artist_top_tracks(artist_id, headers):
    """Fetch top tracks of an artist."""
    tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    tracks_params = {'market': 'US'}
    tracks_result = get(tracks_url, headers=headers, params=tracks_params)
    tracks_json = json.loads(tracks_result.content).get('tracks', [])

    track_details = []
    for track in tracks_json:
         track_info = {
                "id": track.get("id"),
                "name": track.get("name"),
                "popularity": track.get("popularity"),
                "duration_ms": track.get("duration_ms"),
                "preview_url": track.get("preview_url"),  # Optional: Add preview URL if needed
                "artists": [artist.get("name") for artist in track.get("artists", [])]  # Artist names
            }
         
         track_details.append(track_info)
    
    return track_details