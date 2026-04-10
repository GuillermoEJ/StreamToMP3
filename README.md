# STREAMP3

![Version](https://img.shields.io/badge/version-1.2-blue)

A music player application with GUI that allows you to download songs from Spotify and YouTube, and play them locally.

## Features

- **Music Player**: Intuitive graphical interface to play MP3 files
- **Spotify Download**: Search and download songs from Spotify playlists
- **YouTube Download**: Download songs directly from YouTube URLs
- **Playlist Management**: Support for downloading complete Spotify playlists
- **Playback Controls**: Play, pause, next, previous, and volume control
- **Modern Interface**: Built with Tkinter

## Requirements

- Python 3.8 or higher
- FFmpeg installed on the system
- Spotify API credentials (free)

### Get Spotify Credentials

1. Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Sign in or create an account
3. Create a new application
4. Copy your `Client ID` and `Client Secret`

## Installation

### 1. Clone or download the repository
```bash
cd mp3_player
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**Windows (with Chocolatey):**
```bash
choco install ffmpeg
```

**Windows (manual download):**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Add FFmpeg to system environment variables

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

### 4. Configure Environment Variables

2. Create `.env` and add your Spotify credentials:
```env
SPOTIPY_CLIENT_ID='your_client_id_here'
SPOTIPY_CLIENT_SECRET='your_client_secret_here'
```

## Usage

### Main features:

- **Download Song**: Enter a song name or YouTube URL
- **Download Playlist**: Copy a Spotify playlist URL
- **Play**: Select a song from your local library
- **Controls**: Use buttons to control playback

## Dependencies

- `pygame` - Audio playback
- `spotipy` - Spotify API
- `yt-dlp` - YouTube download
- `python-dotenv` - Environment variable loader
- `FFmpeg` - Audio encoding

## Important Notes

- **Do not push `.env` to Git** - Contains sensitive credentials
- **FFmpeg is required** - MP3 download depends on it
- **Internet Connection** - Required to download from Spotify/YouTube
- Downloaded files are saved in the `downloads/` folder

## Troubleshooting

**Error: "Audio initialization failed"**
- Make sure pygame is correctly installed
- On some systems, it may be necessary to install audio dependencies from the operating system

**Error: "FFmpeg not found"**
- Verify that FFmpeg is installed and in the system PATH

**Spotify authentication error**
- Verify that your credentials in `.env` are correct
- Make sure there are no extra spaces

**Error downloading from YouTube**
- YouTube regularly changes its structure - yt-dlp is updated frequently
- Update yt-dlp: `pip install --upgrade yt-dlp`

## License

This project is open source.
