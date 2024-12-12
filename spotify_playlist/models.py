from flask_sqlalchemy import SQLAlchemy
from requests import post, get
import os
import base64
from dotenv import load_dotenv
from flask import Flask, render_template, request, json
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
load_dotenv()


db = SQLAlchemy()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
playlist_img = "/static/images.playtify-logo.jpg"

def connect_db(app):
    """Connect to database."""
    with app.app_context():
        db.app = app
        db.init_app(app)


class PlaylistSong(db.Model):
    """Mapping of a playlist to a song."""

    __tablename__ = 'playlists_songs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)

    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Playlist(db.Model):
    """Playlist table"""
    
    __tablename__ = "playlists"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    user_id = db.Column(db.Integer,db.ForeignKey('users.id', ondelete='cascade'))
    
    name = db.Column(db.String(20),  nullable=False)

    description = db.Column(db.String(100), nullable=False)

    pl_img = db.Column(db.Text,nullable=True, default=playlist_img)

    songs = db.relationship("Song", secondary="playlists_songs", backref="playlists")

    def __repr__(self):
        """show info about post"""
        p = self 
        return f'Playlists id = {p.id}, Name: {p.name}, Description = {p.description}'
    


class User(db.Model):
    ''' User table'''

    __tablename__ = 'users'
    id = db.Column(
        db.Integer,
        primary_key=True,unique=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )
    
    def __repr__(self):
        """show info about post"""
        p = self 
        return f'Username = {p.username}, email = {p.email}'   

    fav_songs = db.relationship(
        'Song',
        secondary='user_songs',
        backref=db.backref('favorited_by', lazy='dynamic')  # Gives Song a 'favorited_by' attribute
    )


    playlists = db.relationship(
        'Playlist',
        secondary='playlists_songs',
        primaryjoin='User.id == PlaylistSong.user_id',
        secondaryjoin='Playlist.id == PlaylistSong.playlist_id',
        backref=db.backref('users', lazy='dynamic'),
        overlaps="songs,playlists"
    )

    likes = db.relationship(
        'Playlist',
        secondary="likes")

    @staticmethod
    def get_token():
        auth_string = client_id + ":" + client_secret
    

        auth_bytes = auth_string.encode("utf-8")

        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = " https://accounts.spotify.com/api/token"

        headers = {
        "Authorization" : "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded" 
        }
        data = {"grant_type": "client_credentials"}

        result = post(url, headers=headers, data= data)

        json_result = json.loads(result.content)
    
        token = json_result['access_token']
        return token

    @staticmethod
    def get_auth_header(token):
        '''returns header's authorization'''

        return {
        "Authorization" : "Bearer " + token
        }

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):


        """Find user with `username` and `password`."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                
                return user

        return False
    

class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    title = db.Column(db.String(100), nullable=False)

    artist = db.Column(db.String(100), nullable=False)

    duration = db.Column(db.String, nullable=True)

    popularity = db.Column(db.String, nullable=True)

    track_id = db.Column(db.String, nullable=False)


    def __repr__(self):
        """show info about post"""
        p = self 
        return f'<Title = {p.title}, artist = {p.artist}'
    
class UserSongs(db.Model):

    __tablename__ = 'user_songs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    

class Likes(db.Model):
    
    """Mapping user likes to playlist."""

    __tablename__ = 'likes' 

    id = db.Column(
        db.Integer,
        primary_key=True,unique=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    playlist_id = db.Column(
        db.Integer,
        db.ForeignKey('playlists.id', ondelete='cascade'),
        unique=True
    )
