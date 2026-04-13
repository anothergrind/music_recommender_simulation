import csv

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 0
    release_year: int = 2024
    mood_tags: str = ""
    instrumentalness: float = 0.0
    speechiness: float = 0.0


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


MODE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "genre_first": {
        "genre": 3.0,
        "mood": 1.8,
        "energy": 1.6,
        "acoustic": 1.0,
    },
    "mood_first": {
        "genre": 1.2,
        "mood": 3.6,
        "energy": 1.3,
        "acoustic": 1.0,
    },
    "energy_focused": {
        "genre": 0.8,
        "mood": 1.0,
        "energy": 4.0,
        "acoustic": 0.8,
    },
}


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(
        self,
        user: UserProfile,
        k: int = 5,
        mode: str = "genre_first",
        artist_penalty: float = 0.0,
        genre_penalty: float = 0.0,
    ) -> List[Song]:
        """Return the top-k Song objects ranked by profile match score."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        song_dicts = [_song_to_dict(song) for song in self.songs]
        ranked = recommend_songs(
            user_prefs,
            song_dicts,
            k=k,
            mode=mode,
            artist_penalty=artist_penalty,
            genre_penalty=genre_penalty,
        )
        id_to_song = {song.id: song for song in self.songs}
        ordered_ids = [rec[0]["id"] for rec in ranked]
        return [id_to_song[song_id] for song_id in ordered_ids if song_id in id_to_song]

    def explain_recommendation(self, user: UserProfile, song: Song, mode: str = "genre_first") -> str:
        """Return a readable explanation of why a song matches the user."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        _, reasons = score_song(user_prefs, _song_to_dict(song), mode=mode)
        return "; ".join(reasons) if reasons else "This song is a reasonable match for the profile."


def _song_to_dict(song: Song) -> Dict:
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "genre": song.genre,
        "mood": song.mood,
        "energy": song.energy,
        "tempo_bpm": song.tempo_bpm,
        "valence": song.valence,
        "danceability": song.danceability,
        "acousticness": song.acousticness,
        "popularity": song.popularity,
        "release_year": song.release_year,
        "mood_tags": song.mood_tags,
        "instrumentalness": song.instrumentalness,
        "speechiness": song.speechiness,
    }


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of dictionaries."""
    songs: List[Dict] = []

    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if not row:
                continue

            song = {
                "id": int(row["id"].strip()),
                "title": row["title"].strip(),
                "artist": row["artist"].strip(),
                "genre": row["genre"].strip(),
                "mood": row["mood"].strip(),
                "energy": float(row["energy"].strip()),
                "tempo_bpm": float(row["tempo_bpm"].strip()),
                "valence": float(row["valence"].strip()),
                "danceability": float(row["danceability"].strip()),
                "acousticness": float(row["acousticness"].strip()),
                "popularity": int((row.get("popularity") or "0").strip()),
                "release_year": int((row.get("release_year") or "2024").strip()),
                "mood_tags": (row.get("mood_tags") or "").strip(),
                "instrumentalness": float((row.get("instrumentalness") or "0.0").strip()),
                "speechiness": float((row.get("speechiness") or "0.0").strip()),
            }
            songs.append(song)

    return songs


def _advanced_feature_scores(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Compute math-based points for new advanced features."""
    score = 0.0
    reasons: List[str] = []

    preferred_decade = user_prefs.get("preferred_decade")
    if preferred_decade is not None:
        song_release_year = int(song.get("release_year", 2024))
        decade = (song_release_year // 10) * 10
        if decade == int(preferred_decade):
            score += 1.2
            reasons.append("decade match (+1.2)")

    target_popularity = user_prefs.get("target_popularity")
    if target_popularity is not None:
        pop_points = max(0.0, 1.5 - abs(float(song.get("popularity", 50)) - float(target_popularity)) / 30.0)
        if pop_points > 0:
            score += pop_points
            reasons.append(f"popularity closeness (+{pop_points:.2f})")

    preferred_mood_tags = user_prefs.get("preferred_mood_tags", [])
    if isinstance(preferred_mood_tags, list) and preferred_mood_tags:
        song_mood_tags = {
            tag.strip().lower()
            for tag in str(song.get("mood_tags", "")).split("|")
            if tag.strip()
        }
        desired_tags = {str(tag).strip().lower() for tag in preferred_mood_tags if str(tag).strip()}
        overlap_count = len(song_mood_tags & desired_tags)
        if overlap_count > 0:
            overlap_points = overlap_count * 0.6
            score += overlap_points
            reasons.append(f"mood tag overlap (+{overlap_points:.1f})")

    target_instrumentalness = user_prefs.get("target_instrumentalness")
    if target_instrumentalness is not None:
        instr_points = max(
            0.0,
            1.2 - abs(float(song.get("instrumentalness", 0.0)) - float(target_instrumentalness)) * 2.0,
        )
        if instr_points > 0:
            score += instr_points
            reasons.append(f"instrumentalness closeness (+{instr_points:.2f})")

    target_speechiness = user_prefs.get("target_speechiness")
    if target_speechiness is not None:
        speech_points = max(
            0.0,
            1.0 - abs(float(song.get("speechiness", 0.0)) - float(target_speechiness)) * 2.5,
        )
        if speech_points > 0:
            score += speech_points
            reasons.append(f"speechiness closeness (+{speech_points:.2f})")

    return score, reasons


def score_song(user_prefs: Dict, song: Dict, mode: str = "genre_first") -> Tuple[float, List[str]]:
    """Compute a weighted score and explanation reasons for one song."""
    selected_mode = mode if mode in MODE_WEIGHTS else "genre_first"
    weights = MODE_WEIGHTS[selected_mode]

    score = 0.0
    reasons: List[str] = [f"mode: {selected_mode}"]

    user_genre = str(user_prefs.get("genre", "")).strip().lower()
    user_mood = str(user_prefs.get("mood", "")).strip().lower()
    user_energy = float(user_prefs.get("energy", 0.0))
    likes_acoustic = bool(user_prefs.get("likes_acoustic", False))

    song_genre = str(song.get("genre", "")).strip().lower()
    song_mood = str(song.get("mood", "")).strip().lower()
    song_energy = float(song.get("energy", 0.0))
    song_acousticness = float(song.get("acousticness", 0.0))

    if user_genre and song_genre == user_genre:
        points = weights["genre"]
        score += points
        reasons.append(f"genre match (+{points:.1f})")

    if user_mood and song_mood == user_mood:
        points = weights["mood"]
        score += points
        reasons.append(f"mood match (+{points:.1f})")

    energy_gap = abs(song_energy - user_energy)
    energy_points = max(0.0, 2.0 - (energy_gap * 4.0)) * weights["energy"]
    if energy_points > 0:
        score += energy_points
        reasons.append(f"energy closeness (+{energy_points:.1f})")

    if likes_acoustic:
        acoustic_points = song_acousticness * 1.5 * weights["acoustic"]
        score += acoustic_points
        reasons.append(f"acoustic preference (+{acoustic_points:.1f})")
    else:
        acoustic_points = (1.0 - song_acousticness) * 0.5 * weights["acoustic"]
        score += acoustic_points
        reasons.append(f"lower acousticness preferred (+{acoustic_points:.1f})")

    advanced_points, advanced_reasons = _advanced_feature_scores(user_prefs, song)
    score += advanced_points
    reasons.extend(advanced_reasons)

    return score, reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "genre_first",
    artist_penalty: float = 0.0,
    genre_penalty: float = 0.0,
) -> List[Tuple[Dict, float, str]]:
    """Rank songs by score and return top-k with optional diversity penalties."""
    pool: List[Dict] = []
    for song in songs:
        base_score, reasons = score_song(user_prefs, song, mode=mode)
        pool.append({
            "song": song,
            "base_score": base_score,
            "reasons": reasons,
        })

    selected: List[Tuple[Dict, float, str]] = []
    selected_artist_counts: Dict[str, int] = {}
    selected_genre_counts: Dict[str, int] = {}

    while pool and len(selected) < k:
        best_idx = 0
        best_adjusted_score = float("-inf")
        best_penalty = 0.0

        for idx, candidate in enumerate(pool):
            song = candidate["song"]
            artist = str(song.get("artist", "")).strip().lower()
            genre = str(song.get("genre", "")).strip().lower()

            penalty = (
                selected_artist_counts.get(artist, 0) * artist_penalty
                + selected_genre_counts.get(genre, 0) * genre_penalty
            )
            adjusted_score = float(candidate["base_score"]) - penalty

            if adjusted_score > best_adjusted_score:
                best_adjusted_score = adjusted_score
                best_idx = idx
                best_penalty = penalty

        chosen = pool.pop(best_idx)
        chosen_song = chosen["song"]
        chosen_reasons = list(chosen["reasons"])

        if best_penalty > 0:
            chosen_reasons.append(f"diversity penalty (-{best_penalty:.2f})")

        artist_key = str(chosen_song.get("artist", "")).strip().lower()
        genre_key = str(chosen_song.get("genre", "")).strip().lower()
        selected_artist_counts[artist_key] = selected_artist_counts.get(artist_key, 0) + 1
        selected_genre_counts[genre_key] = selected_genre_counts.get(genre_key, 0) + 1

        explanation = "; ".join(chosen_reasons) if chosen_reasons else "No strong feature matches"
        selected.append((chosen_song, best_adjusted_score, explanation))

    return selected
