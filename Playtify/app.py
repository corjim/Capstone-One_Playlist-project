import os
from requests import get
from flask import Flask, render_template, request, json, flash, redirect, session, g, url_for,abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models import db, connect_db, User, Playlist, Song ,UserSongs, PlaylistSong, Likes
from forms import AddUserForm, LoginForm, CreatePlaylistForm, NewSongForPlaylistForm

from helper_function import fetch_album_tracks, fetch_artist_albums, fetch_artist_info, fetch_artist_top_tracks
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///playtify'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "No secret is actually a secret")


connect_db(app)

CURR_USER_KEY = "curr_user" 

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
 
@app.route('/signup', methods=['GET','POST'])
def signup():
    ''' Handles user sign up'''

    form = AddUserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""
    
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        flash('You have logged out successfully', 'success')

    return redirect('/login')

##########################
#  Users routes 
##################################################

@app.route('/users')
def show_all_user():
    """Page with listing of users."""
    
    if not g.user:
        flash('You must be logged in to seach user. Please sign-up or log in', 'info')
        return render_template('home-anon.html')

    search = request.args.get('p')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()
    return render_template('users/index.html', user=users)

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)
    playlists = (Playlist
                .query
                .filter(Playlist.user_id == user_id)
                .order_by(Playlist.name.desc())
                .limit(10)
                .all())
    
    userId = g.user.id
    songs = Song.query.filter_by(user_id=userId).all()
    
    # Get all the user's favorite songs to display
    fav_songs = user.fav_songs if user else []

    return render_template('users/show.html', user=user, playlists=playlists,songs=songs, fav_songs=fav_songs)

#  User's Likes Route
@app.route('/users/<int:user_id>/likes', methods=["GET"])
def show_liked_playlist(user_id):
    """ show all the playlist liked a user"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("users"))

    user = User.query.get_or_404(user_id)
    likes = user.likes

    return render_template('users/likes.html', user=user, likes=likes)

@app.route('/playlists/<int:playlist_id>/like', methods=["POST"])
def like_playlist(playlist_id):
    """Toggle a liked playlist for the currently-logged-in user."""

    if not g.user:
        flash("Not Allowed", "danger")
        return redirect(url_for("homepage"))

    try:
        liked_playlist = Playlist.query.get_or_404(playlist_id)

        if liked_playlist.user_id == g.user.id:
            flash("You cannot like your own playlist.", "warning")
            return abort(403)

        # Toggle the liked playlist
        if liked_playlist in g.user.likes:
            g.user.likes = [like for like in g.user.likes if like != liked_playlist]
            flash("Playlist unliked.", "info")
        else:
            g.user.likes.append(liked_playlist)
            flash("Playlist liked!", "success")

        # Attempt to commit changes
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback changes if any error occurs
        flash("An error occurred while updating likes. Please try again.", "danger")
        print(f"Database Error: {e}")  # Log error for debugging

    except Exception as e:
        flash("Something went wrong. Please try again.", "danger")
        print(f"Unexpected Error: {e}")  # Log unexpected errors

    return redirect(url_for("homepage"))

@app.route("/users/delete", methods=["POST"])
def delete_user():
    """ Deletes user from the database"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("homepage"))
    
    do_logout()
    db.session.delete(g.user)
    db.session.commit()

    flash("Account delete: Successful", "success")
    return redirect(url_for("signup"))
   

# ########################################
#   artist and their albums
##################################################

@app.route("/search")
def search_artist():
    # Ensure user is authenticated
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # Retrieve artist name or return error
    artist_name = request.args.get('artist')
    if not artist_name:
        flash("Access unauthorized: Please log in to add songs.", "danger")
        return redirect("/")

    try:
        # Get token and headers
        token = User.get_token()
        headers = User.get_auth_header(token)

        # Fetch artist information
        artist_info = fetch_artist_info(artist_name, headers)
        if not artist_info:
            return {"error": f"No artist found for {artist_name}"}

        artist_id = artist_info['id']

        # Fetch albums and tracks
        albums_info = fetch_artist_albums(artist_id, headers)
        if not albums_info:
            return {"error": f"No album found for artist {artist_name}"}

        top_tracks = fetch_artist_top_tracks(artist_id, headers)
        if not top_tracks:
            return {"error": f"No tracks found for artist {artist_name}"}

        # Build response
        response = {
            "artist": {
                "id": artist_id,
                "name": artist_info['name'],
                "images": artist_info.get('images', [])[0],
                "followers": artist_info['followers'].get('total'),
                "genres": artist_info.get('genres', []),
                "popularity": artist_info.get('popularity'),
                "url_link": artist_info.get('uri'),
            },
            "track": {"name": top_tracks},
            "album": {"info": albums_info},
        }

        return response

    except Exception as e:
        # Log error (optional) and return a generic error response
        return {"error": f"An error occurred: {str(e)}"}


# Get artist top tracks
@app.route('/artist_top_tracks')
def artist_top_tracks():
    
    if not g.user:
        flash("Access unauthorized please log in get artists.", "danger")
        return redirect("/")

    artist_data = search_artist()

    artist = artist_data.get('artist')
    tracks  = artist_data.get('track')
    albums_result = artist_data.get("album")
    albums = albums_result["info"]

    return render_template('artists/tracks.html', artist=artist, tracks=tracks, albums=albums, user=g.user)

# Adds artist's top tracks to user's favorite songs
@app.route('/add_playlist_songs', methods=["POST"])
def add_song():
    '''Add tracks to user's song list and stay on the same page.'''

    if not g.user:
        flash("Access unauthorized: Please log in to add songs.", "danger")
        return redirect("/")

    user = g.user

    try:
        # Extract track and artist details from form request
        track_name = request.form.get('track_name')
        artist_name = request.form.get('artist_name')
        track_duration = request.form.get('track_duration')
        track_popularity = request.form.get('track_popularity')
        track_id = request.form.get("track_id")

        if not track_name or not artist_name:
            flash("Invalid song details provided.", "danger")
            return redirect(request.referrer or "/")  # Stay on the same page

        # Check if the song already exists in the database
        existing_song = Song.query.filter_by(
            title=track_name,
            artist=artist_name
        ).first()

        if not existing_song:
            # Create a new song if it doesn't already exist
            song = Song(
                title=track_name,
                artist=artist_name,
                duration=track_duration,
                popularity=track_popularity,
                user_id=user.id,
                track_id=track_id
            )
            db.session.add(song)
        else:
            song = existing_song

        # Commit changes to the database
        db.session.commit()

        flash(f"'{track_name}' by {artist_name} has been added to your favorites.", "success")

    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback database changes on error
        flash("An error occurred while adding the song. Please try again.", "danger")
        print(f"Database Error: {e}")  # Log error for debugging

    except Exception as e:
        flash("Something went wrong. Please try again.", "danger")
        print(f"Unexpected Error: {e}")  # Log unexpected errors

    return redirect(request.referrer or "/")


# Displays artist album details
@app.route("/show_album_tracks/<album_id>")
def show_album_tracks(album_id):
    '''Route to review artist's album track'''
   
    if not g.user:
        flash("Access unauthorized please log in get an album details.", "danger")
        return redirect(url_for("homepage"))

    albums_url =  f"https://api.spotify.com/v1/albums/{album_id}"
    token = User.get_token()
    headers = User.get_auth_header(token)
    albums_params = {'market': 'US'}

    albums_result = get(albums_url, headers=headers, params=albums_params)

    if albums_result.status_code != 200:
        flash("Failed to fetch album details from Spotify.", "danger")
        return redirect("/")

    albums_json = json.loads(albums_result.content)

    if albums_json is None:
        return flash("No albums found or an error occurred.", "info")
        
    #  Process album and review details
    album_name = albums_json.get('name')
    release_date = albums_json.get("release_date")
    total_tracks = albums_json.get("total_tracks")
    album_artists = albums_json.get('artists')[0]["name"]
    album_url = albums_json.get('images')[0]['url']
    tracks_info = [track for track in albums_json.get('tracks', {}).get('items', [])]
    album_id = album_id

    albums_info = []
    albums_info = {
        'name': album_name,
        'image': album_url,
        'release_date': release_date,
        'total_tracks': total_tracks,
        "artists" : album_artists,
        'tracks': tracks_info,
        'id' : album_id
        }
    return render_template("albums/tracks.html", album=albums_info, user=g.user)

@app.route('/add_album_tracks', methods=["POST"])
def add_album_tracks():
    '''Adds songs to the user's song list.'''

    if not g.user:
        flash("Access unauthorized: Please log in to manage songs.", "danger")
        return redirect("/")

    user = g.user

    try:

        # Extract track and artist details from the form
        track_name = request.form.get('track_name')
        artist_name = request.form.get('artist_name')
        track_duration = request.form.get('track_duration')
        track_popularity = request.form.get('track_popularity')
        album_id = request.form.get('album_id')
        track_id = request.form.get('track_id')
    
        if not track_name or not artist_name:
            flash("Invalid song details provided.", "danger")
            return redirect("/")

        # Check if the song exists in the Song table
        song = Song.query.filter_by(title=track_name, artist=artist_name).first()

        if not song:
            # If the song doesn't exist, create a new one
            song = Song(
                title=track_name,
                artist=artist_name,
                duration=track_duration,
                popularity=track_popularity,
                user_id=user.id,
                track_id = track_id
            )
            db.session.add(song)
            db.session.commit()

            flash(f"'{track_name}' by {artist_name} has been added to your songs list.", "success")
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback database changes on error
        flash("An error occurred while adding the song. Please try again.", "danger")
        print(f"Database Error: {e}")  # Log error for debugging

    except Exception as e:
        flash("Something went wrong. Please try again.", "danger")
        print(f"Unexpected Error: {e}")  # Log unexpected errors

    return redirect(f'show_album_tracks/{album_id}')  

##################################################
#            Playlists routes
##################################################

# Create playlist
@app.route('/playlists')
def show_playlists():
    ''' Return a list of playlist for user'''

    if not g.user:
        flash("Access unauthorized: Please log in to view playlist.", "danger")
        return redirect("/")
    
    playlists = Playlist.query.filter_by(user_id=g.user.id).all()

    return render_template('/playlist/playlists.html', playlists=playlists)

# View individual playlist
@app.route('/playlists/<int:playlist_id>')
def show_playlist_details(playlist_id):
    """Show details of a playlist"""

    if not g.user:
        flash("Access unauthorized: Please log in.", "danger")
        return redirect("/")

    playlist = Playlist.query.get_or_404(playlist_id)

    if not playlist: 
        return flash (f'Playlist not found', "info") 

    return render_template('/playlist/playlist.html',playlist=playlist)

@app.route("/create_playtifylist", methods=["GET", "POST"])
def add_playlist():
    """ Handle create-playlist form """
    if not g.user:
        flash("Access unauthorized: Only users are allowed to create a playtifylist.", "danger")
        return redirect("/")
    
    try:

        form = CreatePlaylistForm()
        userId = g.user.id

        if form.validate_on_submit():
            #  Extract values from form
            name = form.name.data
            description = form.description.data
        
            playlist = Playlist(name=name, description=description,user_id = userId)

            db.session.add(playlist)
            db.session.commit()

            flash("Playtifylist Created!!", "success")
            
            return redirect('/playlists')
        
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback database changes on error
        flash("An error occurred while creating your playlist. Please try again.", "danger")
        print(f"Database Error: {e}")  # Log error for debugging

    except Exception as e:
        flash("Something went wrong. Please try again.", "danger")
        print(f"Unexpected Error: {e}")  # Log unexpected errors
    else:
        return render_template('/playlist/addplaylist.html', form=form)

#  Add songs to playtifylist
@app.route("/playlists/<int:playlist_id>/add-song", methods=["GET", "POST"])
def add_song_to_playlist(playlist_id):
    """Add a playlist and redirect to list."""

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/")
    
    try:

        user_id = g.user.id

        playlist = Playlist.query.get_or_404(playlist_id)
        form = NewSongForPlaylistForm()

        curr_on_playlist = [song.id for song in playlist.songs]
        form.song.choices = [
        (song.id, song.title + f' by ' + song.artist) for song in db.session.query(Song.id, Song.title, Song.artist)
        .filter(Song.id.notin_(curr_on_playlist))
        .all()]      

        if form.validate_on_submit():

            playlist_song = PlaylistSong(user_id=user_id,song_id=form.song.data, playlist_id=playlist_id)

            db.session.add(playlist_song)
            db.session.commit()

            return redirect(f"/playlists/{playlist_id}")
        
    except SQLAlchemyError as e:
        db.session.rollback() 
        flash("An error occurred while adding the song. Please try again.", "danger")
        print(f"Database Error: {e}") 
    except Exception as e:
        flash("Something went wrong. Please try again.", "danger")
        print(f"Unexpected Error: {e}") 

    return render_template("/playlist/song_feed_playlist.html", playlist=playlist, form=form)

# Delete  Platifylist
@app.route("/playlists/<int:playlist_id>/delete", methods=["POST"])
def delete_playtifylist(playlist_id):
    """ Delete Playtifylist"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("homepage"))
    
    try:
    
        p_l = Playlist.query.get_or_404(playlist_id)

        # Check for right ownership of playlist
        if p_l.user_id != g.user.id:
            flash('Access unathorized: Stop!!', "danger" )

            return redirect(url_for("homepage"))

        db.session.delete(p_l)
        db.session.commit()
        
        flash(f"{p_l.name} successfully deleted", "info")
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback database changes on error
        flash("An error occurred deleting playlist. Please try again.", "danger")
        print(f"Database Error: {e}")  # Log error for debugging

    except Exception as e:
        flash("Something went wrong. Please try again.", "danger")
        print(f"Unexpected Error: {e}")  # Log unexpected errors

    return redirect(url_for("playlists"))

# PLAYLIST ITEMS (To delete and play playlist songs)
@app.route("/remove_from_playlist/<int:playlist_id>/<int:song_id>", methods=["POST"])
def remove_song_from_playlist(playlist_id, song_id):
    """ Removes song from a playlist"""

    if not g.user:
        flash("Access unauthorized. Please log in to remove songs from a playlist.", "danger")
        return redirect('/')

    # Get the playlist and song
    playlist = Playlist.query.get_or_404(playlist_id)
    song = Song.query.get_or_404(song_id)

    # Check the current user owns the playlist
    if playlist.user_id != g.user.id:
        flash("You do not have permission to modify this playlist.", "danger")
        return redirect(url_for('playlists'))

    # Check if the song is in the playlist
    if song in playlist.songs:
        playlist.songs.remove(song)
        db.session.commit()
        flash(f"'{song.title}' has been removed from the playlist '{playlist.name}'.", "success")
    else:
        flash(f"The song '{song.title}' is not in the playlist '{playlist.name}'.", "warning")

    return redirect(f"/playlists/{playlist_id}")


##################################################
#            Song routes
##################################################

@app.route("/songs")
def show_all_songs():
    """Show all songs in users profile."""

    if not g.user:
        flash("Access unauthorized: Please log in to view songs.", "danger")
        return redirect(url_for("homepage"))

    user = g.user
    songs = Song.query.filter_by(user_id=g.user.id).all()
    
    # Get all the user's favorite songs to display
    fav_songs = user.fav_songs if user else []
    
    return render_template("/users/songs.html", songs=songs, user=user, fav_songs=fav_songs)

@app.route("/songs/<int:song_id>")
def show_song(song_id):
    """return a specific song"""

    if not g.user:
        flash("Access unauthorized: Please log in to view song's details.", "danger")
        return redirect(url_for("homepage"))

    song = Song.query.get(song_id)

    if not song:
        return flash(f'Song not found', "warning")

    return render_template('/users/song.html', song=song)

@app.route('/add_to_favorites/<int:song_id>', methods=['POST'])
def add_to_favorites(song_id):
    """Add a song to the user's favorites."""

    if not g.user:
        flash("Access unauthorized: Please log in to add songs to favorites.", "danger")
        return redirect("/")
    
    try:

        user = g.user
        song = Song.query.get_or_404(song_id)

        # Check if the song is already in the user's favorites
        if song in user.fav_songs:
            flash("This song is already in your favorites.", "info")
        else:
            user.fav_songs.append(song)
            db.session.commit()
            flash(f"'{song.title}' by {song.artist} added to your favorites!", "success")
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback database changes on error
        flash("An error occurred while adding the song to the list. Please try again.", "danger")
        print(f"Database Error: {e}")  # Log error for debugging

    except Exception as e:
        flash("Something went wrong. Please try again.", "danger")
        print(f"Unexpected Error: {e}")  # Log unexpected errors

    return redirect(request.referrer or url_for("homepage"))

@app.route('/remove_from_favorite/<int:song_id>', methods=['POST'])
def remove_from_favorite(song_id):
    """Remove a song from user's favorite's song list."""
    if not g.user:
        flash("Access unauthorized: Please log in to manage favorite list.", "danger")
        return redirect(url_for("homepage"))
    
    try:
    
        user = g.user
        song = Song.query.get_or_404(song_id)

        # Check if the song exists in the lists
        if song not in user.fav_songs:
            flash("Song is not in the favorite list.", "info")
        else:
            user.fav_songs.remove(song)
            db.session.commit()
            flash(f"'{song.title}' by {song.artist} removed from the list", "success")

    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback database changes on error
        flash("An error occurred while adding the song. Please try again.", "danger")
        print(f"Database Error: {e}")

    except Exception as e:
        flash("Something went wrong. Please try again.", "danger")
        print(f"Unexpected Error: {e}")  

    return redirect("/songs")
    
@app.route("/remove_song/<int:song_id>",methods=['POST'])
def delete_song(song_id):
    """Delete song from Song list"""

    if not g.user:
       return flash("Access unauthorized: Please log in to remove song", "info")
    
    try:
    
        song = Song.query.get_or_404(song_id)

        # Delete the song from the database
        db.session.delete(song)
        db.session.commit()
        flash(f"'{song.title}' by {song.artist} has been removed from the list.", "success")

        return redirect("/songs")
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback database changes on error
        flash("An error occurred while deleting the song. Please try again.", "danger")
        print(f"Database Error: {e}")  # Log error for debugging

    except Exception as e:
        flash("Something went wrong. Please try again.", "danger")
        print(f"Unexpected Error: {e}")  # Log unexpected errors

@app.route('/')
def homepage():
    
    if g.user:
       id = g.user.id
       
       songs = Song.query.filter_by(user_id=g.user.id).all()
       playlists = Playlist.query.filter_by(user_id=id).all()

       return render_template('home.html',songs=songs,user=g.user, playlists=playlists)
    
    else:
        return render_template('home-anon.html')


#  Time Conversion for the song duration.
@app.template_filter('convert_duration')
def convert_duration_filter(ms):
        
    return  convert_duration(int(ms))

def convert_duration(ms): 
    seconds, ms = divmod(ms, 1000) 
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60) 
    days, hours = divmod(hours, 24) 
    parts = [] 
    if days > 0: 
        parts.append(f"{days}d") 
    if hours > 0: 
        parts.append(f"{hours}h") 
    if minutes > 0: 
        parts.append(f"{minutes}m") 
    if seconds > 0:
        if ms > 500:
            seconds += 1 
        parts.append(f"{seconds}s") 
    return " ".join(parts)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port= 8080, debug=True)
