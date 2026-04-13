# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**RhythmFlow 0.0**

---

## 2. Goal / Task  

This model suggests songs from a small catalog.
It tries to match a user's genre, mood, energy, and acoustic preference.
It predicts which songs should be in the top 5 list.

---

## 3. Data Used  

The dataset has 18 songs in `data/songs.csv`.
Each song has genre, mood, energy, tempo, valence, danceability, and acousticness.
The user profile uses favorite genre, favorite mood, target energy, and likes acoustic.
The dataset is small, so it does not cover all music styles or all listener tastes.

---

## 4. Algorithm Summary  

The model gives points for genre match, mood match, and energy closeness.
It also gives points based on acoustic preference.
Songs with closer energy to the user get more points.
Then it sorts songs by total score and returns the top 5.
In my experiment, energy was weighted more and genre was weighted less.

---

## 5. Observed Behavior / Biases  

I saw an energy-driven filter bubble.
Songs with similar energy kept showing up, even when genre was different.
For example, "Gym Hero" appeared in many profiles because it is very high energy and low acoustic.
This can make results feel repetitive and less personal for some users.

---

## 6. Evaluation Process  

I tested five profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock, Conflicting Acoustic EDM, and Boundary Extremist.
I compared the top 5 songs for each profile and checked if they matched user intent.
I also ran a weight-shift experiment to see how rankings changed when energy mattered more than genre.
The biggest surprise was how often "Gym Hero" stayed near the top.

---

## 7. Intended Use and Non-Intended Use  

Intended use: classroom learning and simple recommender demos.
It is good for showing how scoring rules change results.
Non-intended use: real music apps, hiring, health, or any high-stakes decision.
It should not be used to judge people or make claims about personal identity.

---

## 8. Ideas for Improvement  

1. Add more rules so the top 5 are not all the same vibe.
2. Add more user inputs
3. Expand the dataset so more genres and moods are represented.

---

## 9. Personal Reflection  

My biggest learning moment was seeing how one weight change made the whole ranking feel different.
AI tools helped me move faster when creating test profiles, writing comparisons, and spotting possible bias patterns.
I still had to double-check AI suggestions by running `main.py` and reading the top results myself, because some suggestions sounded good but did not match the actual output.
I was surprised that a simple point system can still feel like a real recommender when the top songs line up with the user's vibe.
At the same time, it also showed me how easy it is for one song like "Gym Hero" to appear too often if one feature dominates.
If I extended this project, I would add a diversity rule, collect more songs, and let users tune how much genre, mood, and energy matter.
