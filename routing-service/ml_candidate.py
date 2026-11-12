from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
import joblib


class MLCandidate:
    def __init__(self):
        self.vectorizer = FeatureUnion([
            (
                "word",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1, 2),
                    min_df=2
                )
            ),
            (
                "character",
                TfidfVectorizer(
                    analyzer="char_wb",
                    lowercase=True,
                    ngram_range=(3, 5),
                    min_df=2
                )
            )
        ])

        self.model = LogisticRegression(
            class_weight="balanced",
            random_state=42
        )

    def clean_text(self, body):
        return " ".join(body.split())

    def fit(self, bodies, departments):
        cleaned_bodies = [self.clean_text(body) for body in bodies]
        features = self.vectorizer.fit_transform(cleaned_bodies)
        self.model.fit(features, departments)

    def predict(self, body):
        cleaned_body = self.clean_text(body)
        features = self.vectorizer.transform([cleaned_body])

        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]

        return {
            "recommended_department": str(prediction),
            "class_scores": {
                department: round(float(score), 4)
                for department, score in zip(
                    self.model.classes_, probabilities
                )
            }
        }

    def save(self, path):
        joblib.dump(self, path)

    @classmethod
    def load(cls, path):
        return joblib.load(path)
