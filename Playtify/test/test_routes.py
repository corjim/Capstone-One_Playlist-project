import unittest
from app import app
from models import db, User, Playlist, Song, PlaylistSong, Likes
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class RoutesTestCase(unittest.TestCase):
    """Test routes for Playtify."""

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
            Likes.query.delete()
            db.session.commit()

            # Create test user
            hashed_pwd = bcrypt.generate_password_hash("password").decode('UTF-8')
            self.user = User(
                username="testuser",
                email="test@example.com",
                password=hashed_pwd
            )
            db.session.add(self.user)
            db.session.commit()

            self.client = app.test_client()

    def test_homepage(self):
        """Test that the homepage loads successfully."""
        with self.client:
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Welcome to Playtify", response.data)

    def test_user_signup(self):
        """Test user signup route."""
        with self.client:
            response = self.client.post("/signup", data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpassword"
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Account created", response.data)

    def test_user_login(self):
        """Test user login route."""
        with self.client:
            response = self.client.post("/login", data={
                "username": "testuser",
                "password": "password"
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Welcome back", response.data)

    def test_create_playlist(self):
        """Test creating a playlist."""
        with self.client:
            self.client.post("/login", data={"username": "testuser", "password": "password"}, follow_redirects=True)

            response = self.client.post("/playlists/new", data={
                "name": "Test Playlist",
                "description": "This is a test playlist"
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Playlist created", response.data)

    def test_get_playlists(self):
        """Test getting a list of playlists."""
        with app.app_context():
            playlist = Playlist(name="Sample Playlist", description="A test playlist", user_id=self.user.id)
            db.session.add(playlist)
            db.session.commit()

        with self.client:
            response = self.client.get("/playlists")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Sample Playlist", response.data)

    def test_get_songs(self):
        """Test retrieving songs."""
        with app.app_context():
            song = Song(title="Test Song", artist="Test Artist", user_id=self.user.id, track_id="123")
            db.session.add(song)
            db.session.commit()

        with self.client:
            response = self.client.get("/songs")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Test Song", response.data)

    def test_add_song_to_playlist(self):
        """Test adding a song to a playlist."""
        with app.app_context():
            playlist = Playlist(name="Test Playlist", description="A test playlist", user_id=self.user.id)
            db.session.add(playlist)
            db.session.commit()

            song = Song(title="New Song", artist="Artist", user_id=self.user.id, track_id="456")
            db.session.add(song)
            db.session.commit()

        with self.client:
            response = self.client.post(f"/playlists/{playlist.id}/add", data={
                "song_id": song.id
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Song added to playlist", response.data)

    def test_like_playlist(self):
        """Test liking a playlist."""
        with app.app_context():
            playlist = Playlist(name="Likeable Playlist", description="A test playlist", user_id=self.user.id)
            db.session.add(playlist)
            db.session.commit()

        with self.client:
            response = self.client.post(f"/playlists/{playlist.id}/like", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Playlist liked", response.data)

    def test_remove_playlist(self):
        """Test deleting a playlist."""
        with app.app_context():
            playlist = Playlist(name="Removable Playlist", description="A test playlist", user_id=self.user.id)
            db.session.add(playlist)
            db.session.commit()

        with self.client:
            response = self.client.post(f"/playlists/{playlist.id}/delete", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Playlist deleted", response.data)

    def test_logout(self):
        """Test user logout."""
        with self.client:
            response = self.client.get("/logout", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Successfully logged out", response.data)

if __name__ == '__main__':
    unittest.main()
