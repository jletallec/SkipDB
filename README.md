# SkipDB

**SkipDB** is a web dashboard to visualize and browse the [Stremio Skip Button](https://github.com/shugi12345/stremio-skip-button) data for TV shows in Stremio Enhanced.

This project allows you to:
- See which series and episodes have skip data available
- View skip timecodes for each episode
- Filter and search for series in the **Stremio Skip Button** database
- Track progress of skip coverage

## Features

- Fast search and filtering of series
- Progress bars for skip coverage
- Multilingual support (English & French)

## Usage

1. **Get a TMDB API key:**  
Create a (free) account on [The Movie Database](https://www.themoviedb.org/) and generate an API key from your account settings.

2. **Set your TMDB API key as an environment variable:**  
   On macOS/Linux:
   ```bash
   export TMDB_API_KEY=your_tmdb_api_key_here
   ```
   On Windows (cmd):
   ```cmd
   set TMDB_API_KEY=your_tmdb_api_key_here
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the app:**
   ```bash
   python src/app.py
   ```
5. **Open your browser:**
Go to http://127.0.0.1:5000

## About
This project is a companion viewer for the [Stremio Skip Button](https://github.com/shugi12345/stremio-skip-button) project, which brings community-powered "Skip Intro" and "Skip Recap" features to Stremio.