# Playtify 🎵  
A playlist management web application where users can create playlists, add their favorite songs, preview the sound of the song, and interact with others by liking playlists. Playtify aims to mimic the core functionalities of music platforms, enabling seamless organization and display of songs and playlists. Users can view other user's profile to see the list of their playlist and the songs they have under their radar, user can also keep tracks of other user's playlists through the like.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Schema](#project-schema)
- [Technologies Used](#technologies-used)
- [Credits](#credits)

---

## Overview  
Playtify is built with Flask as the backend framework, leveraging Jinja templates for rendering dynamic HTML content. The app is designed for users to:
- Create and manage playlists.
- Sample/preview artist's song.
- Add and remove songs to/from playlists.
- Mark songs as favorites.
- Like other users' playlists.
- View user-specific statistics and details.

The app uses a relational database structure to manage songs, playlists, users, and their interactions effectively.

---

## Features

### Core Features:
1. **User Management**  
   - Each user can have their own profile and playlists.
   - Users can add favorite songs to their personal collection.

2. **Playlists Management**  
   - Users can create, edit, and delete playlists.
   - Songs can be added or removed from playlists.

3. **Songs Management**  
   - Add details such as song title, artist, duration, and popularity.

4. **Like Playlists**  
   - Users can like other playlists for easy discovery.

5. **Dynamic Content Rendering**  
   - Jinja templates dynamically display playlists, songs, and user interactions.

---

## Project Schema

Below is the database schema that models the relationships between users, playlists, songs, and their associations.

### Tables:
- **Users**  
   Stores user information and associations.  
   | Column       | Type        | Description           |
   | ------------ | ----------- | --------------------- |
   | id           | int         | Primary key           |
   | Name         | string      | User's name           |
   | email        | string      | User's email          |
   | password     | string      | Hashed password       |
   | image_url    | string      | Profile picture       |
   | fav_songs    | int         | Reference to songs    |
   | playlists    | int         | Reference to playlists|
   | likes        | int         | User likes for playlists|

- **Songs**  
   Stores song data.  
   | Column       | Type        | Description           |
   | ------------ | ----------- | --------------------- |
   | id           | int         | Primary key           |
   | user_id      | int         | Foreign key to Users  |
   | title        | string(100) | Song title            |
   | artist       | string(100) | Artist's name         |
   | duration     | string      | Duration of the song  |
   | popularity   | string      | Popularity score      |

- **Playlists**  
   Contains playlist metadata.  
   | Column       | Type        | Description           |
   | ------------ | ----------- | --------------------- |
   | id           | int         | Primary key           |
   | user_id      | int         | Foreign key to Users  |
   | name         | string      | Playlist name         |
   | description  | string      | Playlist description  |
   | pl_img       | string      | Playlist image URL    |
   | songs        | int         | Reference to songs    |

- **Playlist_Songs**  
   Junction table for many-to-many relationships between playlists and songs.  
   | Column       | Type        | Description           |
   | ------------ | ----------- | --------------------- |
   | id           | int         | Primary key           |
   | playlist_id  | int         | Foreign key to Playlists |
   | song_id      | int         | Foreign key to Songs  |
   | user_id      | int         | Foreign key to Users  |

- **Likes**  
   Tracks user likes on playlists.  
   | Column       | Type        | Description           |
   | ------------ | ----------- | --------------------- |
   | id           | int         | Primary key           |
   | user_id      | int         | Foreign key to Users  |
   | playlist_id  | int         | Foreign key to Playlists|

- **User_Songs**  
   Junction table for user favorites and songs.  
   | Column       | Type        | Description           |
   | ------------ | ----------- | --------------------- |
   | id           | int         | Primary key           |
   | user_id      | int         | Foreign key to Users  |
   | song_id      | int         | Foreign key to Songs  |

---

## Technologies Used

- **Backend**: Python, Flask  
- **Frontend**: HTML, CSS, Bootstrap, Jinja2  
- **Database**: SQL (Relational Database)  
- **JavaScript**: jQuery for interactivity  

- **Tools**:  
   - SQLAlchemy for ORM  
   - Flask Forms for handling form data  
---

## Future Enhancements
- Integrate real song streaming functionality.
- Add user authentication (sign up, login, and logout).
- Allow playlist collaboration between multiple users.
- Implement API integration for real-time song data.

---

## Credits  
Developed by: [corjim]  
