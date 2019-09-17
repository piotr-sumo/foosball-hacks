import random
import os

SCORES_DIR = "./voices"


class ScoreSounds:
    def play_game_start(self):
        variant_count = 1
        random_variant = random.randrange(0, variant_count)
        self.play_file(f"{SCORES_DIR}/voice_gamestarted"
                       + f".{random_variant}.wav")

    def play_score(self, red_score, blue_score):
        variant_count = 3 if red_score != blue_score else 2
        random_variant = random.randrange(0, variant_count)
        self.play_file(f"{SCORES_DIR}/voice"
                       + f"{red_score}.{blue_score}.{random_variant}.wav")

    def play_game_end(self, red_score, blue_score):
        variant_count = 1
        random_variant = random.randrange(0, variant_count)
        self.play_file(f"{SCORES_DIR}/voice_gameended."
                       + f"{red_score}.{blue_score}.{random_variant}.wav")

    def play_file(self, filename):
        os.system(f"omxplayer -o local {filename} >/dev/null")


if __name__ == "__main__":
    scores = ScoreSounds()
    scores.play_game_start()
    scores.play_score(3, 8)
    scores.play_game_end(9, 6)
