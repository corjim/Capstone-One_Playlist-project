import unittest
from unittest.mock import patch
from helper_function import fetch_artist_info, fetch_artist_albums, fetch_album_tracks, fetch_artist_top_tracks

class TestSpotifyAPIIntegration(unittest.TestCase):
    def setUp(self):
        """Set up common headers and data for tests."""
        self.headers = {"Authorization": "Bearer mock_access_token"}
        self.artist_name = "Coldplay"
        self.artist_id = "mock_artist_id"
        self.album_id = "mock_album_id"
        self.mock_album_tracks = ["Track 1", "Track 2"]
        self.mock_artist_top_tracks = [
            {
                "id": "track1_id",
                "name": "Top Track 1",
                "popularity": 90,
                "duration_ms": 200000,
                "preview_url": "mock_preview_url_1",
                "artists": ["Artist 1"]
            },
            {
                "id": "track2_id",
                "name": "Top Track 2",
                "popularity": 85,
                "duration_ms": 180000,
                "preview_url": "mock_preview_url_2",
                "artists": ["Artist 1", "Artist 2"]
            },
        ]

    @patch("your_module.get")
    def test_fetch_artist_info(self, mock_get):
        """Test fetching artist info."""
        mock_response = {
            "artists": {
                "items": [{"id": "mock_artist_id", "name": "Coldplay"}]
            }
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = lambda: mock_response

        artist_info = fetch_artist_info(self.artist_name, self.headers)
        self.assertIsNotNone(artist_info)
        self.assertEqual(artist_info['name'], "Coldplay")
        self.assertEqual(artist_info['id'], "mock_artist_id")

    @patch("your_module.get")
    @patch("your_module.fetch_album_tracks")
    def test_fetch_artist_albums(self, mock_fetch_album_tracks, mock_get):
        """Test fetching artist albums."""
        mock_fetch_album_tracks.return_value = self.mock_album_tracks
        mock_response = {
            "items": [
                {
                    "id": "mock_album_id",
                    "name": "Mock Album",
                    "images": [{"url": "mock_album_url"}],
                    "release_date": "2024-12-01",
                    "total_tracks": 12,
                }
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = lambda: mock_response

        albums = fetch_artist_albums(self.artist_id, self.headers)
        self.assertEqual(len(albums), 1)
        self.assertEqual(albums[0]['album_name'], "Mock Album")
        self.assertEqual(albums[0]['id'], "mock_album_id")
        self.assertEqual(albums[0]['image'], "mock_album_url")
        self.assertEqual(albums[0]['release_date'], "2024-12-01")
        self.assertEqual(albums[0]['tracks'], self.mock_album_tracks)

    @patch("your_module.get")
    def test_fetch_album_tracks(self, mock_get):
        """Test fetching album tracks."""
        mock_response = {
            "items": [
                {"name": "Track 1"},
                {"name": "Track 2"}
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = lambda: mock_response

        tracks = fetch_album_tracks(self.album_id, self.headers)
        self.assertEqual(tracks, ["Track 1", "Track 2"])

    @patch("your_module.get")
    def test_fetch_artist_top_tracks(self, mock_get):
        """Test fetching artist's top tracks."""
        mock_response = {"tracks": self.mock_artist_top_tracks}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = lambda: mock_response

        top_tracks = fetch_artist_top_tracks(self.artist_id, self.headers)
        self.assertEqual(len(top_tracks), 2)
        self.assertEqual(top_tracks[0]['name'], "Top Track 1")
        self.assertEqual(top_tracks[1]['popularity'], 85)
        self.assertEqual(top_tracks[0]['artists'], ["Artist 1"])
        self.assertEqual(top_tracks[1]['duration_ms'], 180000)


# MORE ROUTES AND DB TEST COMING!!
if __name__ == "__main__":
    unittest.main()
