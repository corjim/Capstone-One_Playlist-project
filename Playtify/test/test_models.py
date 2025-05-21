import unittest
from app import app
from models import db, User, Playlist, Song, PlaylistSong, UserSongs, Likes
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class ModelTestCase(unittest.TestCase):
    """Test models for Playtify."""

    @classmethod
    def setUpClass(cls):
        """Setup the test database once before running tests."""
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///playtify_test"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['TESTING'] = True

        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Drop tables after all tests are done."""
        with app.app_context():
            db.drop_all()

    def setUp(self):
        """Create test data before each test."""
        with app.app_context():
            User.query.delete()
            Playlist.query.delete()
            Song.query.delete()
            PlaylistSong.query.delete()
            UserSongs.query.delete()
            Likes.query.delete()
            db.session.commit()

            self.user = User.signup(
                username="testuser",
                email="test@example.com",
                password="password",
                image_url=None
            )
            db.session.commit()

            self.playlist = Playlist(
                name="Test Playlist",
                description="A test playlist",
                user_id=self.user.id
            )
            db.session.add(self.playlist)
            db.session.commit()

            self.song = Song(
                title="Test Song",
                artist="Test Artist",
                duration="3:30",
                popularity="90",
                track_id="123456",
                user_id=self.user.id
            )
            db.session.add(self.song)
            db.session.commit()

            self.playlist_song = PlaylistSong(
                playlist_id=self.playlist.id,
                song_id=self.song.id,
                user_id=self.user.id
            )
            db.session.add(self.playlist_song)
            db.session.commit()

    def test_user_signup(self):
        """Test user signup and password hashing."""
        with app.app_context():
            user = User.signup(
                username="newuser",
                email="newuser@example.com",
                password="newpassword",
                image_url=None
            )
            db.session.commit()
            
            self.assertIsNotNone(user.id)
            self.assertNotEqual(user.password, "newpassword")  # Ensure password is hashed

    def test_user_authenticate(self):
        """Test authentication of user."""
        with app.app_context():
            user = User.authenticate("testuser", "password")
            self.assertIsNotNone(user)

            wrong_user = User.authenticate("testuser", "wrongpassword")
            self.assertFalse(wrong_user)

    def test_playlist_creation(self):
        """Test playlist creation and linking with user."""
        with app.app_context():
            playlist = Playlist.query.filter_by(name="Test Playlist").first()
            self.assertIsNotNone(playlist)
            self.assertEqual(playlist.user_id, self.user.id)

    def test_song_creation(self):
        """Test song creation and linking with user."""
        with app.app_context():
            song = Song.query.filter_by(title="Test Song").first()
            self.assertIsNotNone(song)
            self.assertEqual(song.artist, "Test Artist")

    def test_playlist_song_relationship(self):
        """Test that songs can be added to playlists."""
        with app.app_context():
            playlist_song = PlaylistSong.query.filter_by(playlist_id=self.playlist.id).first()
            self.assertIsNotNone(playlist_song)
            self.assertEqual(playlist_song.song_id, self.song.id)

    def test_likes_table(self):
        """Test that a user can like a playlist."""
        with app.app_context():
            like = Likes(user_id=self.user.id, playlist_id=self.playlist.id)
            db.session.add(like)
            db.session.commit()

            liked_playlist = Likes.query.filter_by(user_id=self.user.id).first()
            self.assertIsNotNone(liked_playlist)
            self.assertEqual(liked_playlist.playlist_id, self.playlist.id)


if __name__ == '__main__':
    unittest.main()
