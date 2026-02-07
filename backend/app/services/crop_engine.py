"""
CropEngine — KNN-based Crop Recommendation Service

Uses the Kaggle Crop Recommendation Dataset to predict the best crop
based on soil nutrients (N, P, K), weather conditions (temperature,
humidity, rainfall), and soil pH.

Algorithm: K-Nearest Neighbours (Euclidean distance) on normalised features.
Returns top-3 crop predictions with confidence scores.
"""

import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger("orbital.crop_engine")

# ── Dataset path ──────────────────────────────────────────────────
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
_CSV_PATH = _DATA_DIR / "crop_recommendation.csv"


class CropEngine:
    """Singleton-style crop prediction engine backed by Kaggle dataset."""

    FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

    def __init__(self) -> None:
        self._df: pd.DataFrame | None = None
        self._feature_matrix: np.ndarray | None = None
        self._labels: np.ndarray | None = None
        self._means: np.ndarray | None = None
        self._stds: np.ndarray | None = None
        self._load()

    # ── Loading & Normalisation ───────────────────────────────────

    def _load(self) -> None:
        csv = os.environ.get("CROP_CSV_PATH", str(_CSV_PATH))
        try:
            self._df = pd.read_csv(csv)
            logger.info("Loaded crop dataset: %d rows from %s", len(self._df), csv)

            raw = self._df[self.FEATURES].values.astype(np.float64)
            self._means = raw.mean(axis=0)
            self._stds = raw.std(axis=0)
            # Avoid division by zero
            self._stds[self._stds == 0] = 1.0
            self._feature_matrix = (raw - self._means) / self._stds
            self._labels = self._df["label"].values
        except Exception as exc:
            logger.error("Failed to load crop dataset: %s", exc)
            self._df = None

    # ── Prediction ────────────────────────────────────────────────

    def predict(
        self,
        n: float,
        p: float,
        k: float,
        temperature: float,
        humidity: float,
        ph: float,
        rainfall: float,
        top_k: int = 3,
    ) -> list[dict]:
        """
        Predict best crops for given conditions using KNN.

        Returns a list of dicts:
            [{"crop": "rice", "confidence": 0.92}, ...]
        """
        if self._feature_matrix is None or self._labels is None:
            logger.warning("CropEngine not loaded — returning fallback")
            return [{"crop": "wheat", "confidence": 0.5}]

        # Normalise the input query using training stats
        query = np.array(
            [n, p, k, temperature, humidity, ph, rainfall], dtype=np.float64
        )
        query_norm = (query - self._means) / self._stds

        # Euclidean distances to every row in the dataset
        distances = np.linalg.norm(self._feature_matrix - query_norm, axis=1)

        # Get K nearest neighbours
        k_neighbours = min(top_k * 4, len(distances))  # over-sample then aggregate
        nearest_idx = np.argsort(distances)[:k_neighbours]
        nearest_labels = self._labels[nearest_idx]
        nearest_dists = distances[nearest_idx]

        # Aggregate: count occurrences weighted by inverse distance
        crop_scores: dict[str, float] = {}
        for label, dist in zip(nearest_labels, nearest_dists):
            weight = 1.0 / (dist + 1e-6)
            crop_scores[label] = crop_scores.get(label, 0.0) + weight

        # Sort by score, take top_k
        sorted_crops = sorted(crop_scores.items(), key=lambda x: x[1], reverse=True)
        total = sum(s for _, s in sorted_crops)

        results = []
        for crop, score in sorted_crops[:top_k]:
            confidence = round(float(min(score / total, 1.0)), 2)
            results.append({"crop": str(crop), "confidence": confidence})

        logger.info(
            "CropEngine prediction: N=%s P=%s K=%s → %s",
            n,
            p,
            k,
            ", ".join(f"{r['crop']}({r['confidence']})" for r in results),
        )
        return results

    # ── Utility ───────────────────────────────────────────────────

    @property
    def is_loaded(self) -> bool:
        return self._df is not None

    @property
    def crop_labels(self) -> list[str]:
        if self._df is None:
            return []
        return sorted(self._df["label"].unique().tolist())


# ── Module-level singleton ────────────────────────────────────────
crop_engine = CropEngine()
