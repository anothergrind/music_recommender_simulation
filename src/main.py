"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from .recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs


PROFILES = [
    {
        "name": "High-Energy Pop",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False},
    },
    {
        "name": "Chill Lofi",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    },
    {
        "name": "Deep Intense Rock",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.95, "likes_acoustic": False},
    },
    {
        "name": "System Eval: Conflicting Acoustic EDM",
        "prefs": {"genre": "electronic", "mood": "energetic", "energy": 0.9, "likes_acoustic": True},
    },
    {
        "name": "System Eval: Boundary Extremist",
        "prefs": {"genre": "pop", "mood": "neutral", "energy": 0.5, "likes_acoustic": False},
    },
]


def print_recommendations(profile_name: str, user_prefs: dict, songs: list[dict]) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"\n=== {profile_name} ===")
    print(f"Profile: {user_prefs}")
    print("Top recommendations:\n")

    for idx, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        reasons = [part.strip() for part in explanation.split(";") if part.strip()]

        print(f"{idx}. {song['title']}")
        print(f"   Final score: {score:.2f}")
        print("   Reasons:")
        if reasons:
            for reason in reasons:
                print(f"   - {reason}")
        else:
            print("   - No specific reasons provided")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv") 

    for profile in PROFILES:
        print_recommendations(profile["name"], profile["prefs"], songs)


if __name__ == "__main__":
    main()
