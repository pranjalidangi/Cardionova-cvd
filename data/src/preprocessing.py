"""
Cardionova - FraminghamPreProcessor
Production-grade preprocessing for Framingham Heart Study dataset.

Aligns with project objectives:
- Clean and preprocess Framingham-style CVD data.
- Engineer clinically meaningful features (hypertension, pack-years, etc.).
- Save artifacts for deployment in FastAPI backend.
"""

import os
from typing import Tuple, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler


class FraminghamPreProcessor:
    """
    End-to-end preprocessing for Framingham CVD dataset.

    Responsibilities:
      1. Load and validate data.
      2. Impute missing numeric values using KNN (clinical-friendly).
      3. Engineer extra clinical features.
      4. Split into train/test with stratification (for class imbalance).
      5. Scale features with RobustScaler and save scaler + imputer.
    """

    TARGET_COL = "TenYearCHD"

    # All features we want after engineering
    FEATURE_COLS = [
        "male", "age", "education", "currentSmoker", "cigsPerDay",
        "BPMeds", "prevalentStroke", "prevalentHyp", "diabetes",
        "totChol", "sysBP", "diaBP", "BMI", "heartRate", "glucose",
        # engineered
        "hypertension_stage", "pack_years", "pulse_pressure",
        "cholesterol_risk", "age_group", "bmi_category",
    ]

    def __init__(
        self,
        n_neighbors: int = 5,
        test_size: float = 0.2,
        random_state: int = 42,
        scaler_path: str = "models/scaler.pkl",
    ):
        self.n_neighbors = n_neighbors
        self.test_size = test_size
        self.random_state = random_state
        self.scaler_path = scaler_path

        self.imputer = KNNImputer(n_neighbors=self.n_neighbors)
        self.scaler = RobustScaler()
        self.feature_names: Optional[list] = None
        self._is_fitted = False

    # ---------------------------------------------------------
    # Step 1: Load data and basic sanity checks
    # ---------------------------------------------------------
    def load(self, path: str) -> pd.DataFrame:
        """
        Reads CSV and prints basic stats so you understand dataset shape.
        """
        df = pd.read_csv(path)

        if self.TARGET_COL not in df.columns:
            raise ValueError(f"Target column '{self.TARGET_COL}' not found in dataset.")

        print(f"[LOAD] Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"[LOAD] CVD prevalence: {df[self.TARGET_COL].mean():.2%}")
        print("[LOAD] Missing values per column (only non-zero):")
        mv = df.isnull().sum()
        print(mv[mv > 0])

        return df

    # ---------------------------------------------------------
    # Step 2: KNN Imputation
    # ---------------------------------------------------------
    def impute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fills missing numeric values using KNNImputer.

        Idea:
          - For each row with missing glucose, look at similar patients
            (age, BP, cholesterol, etc.) and average their values.
          - This is more clinically reasonable than just mean/median.
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        df_imputed = df.copy()
        df_imputed[numeric_cols] = self.imputer.fit_transform(df_imputed[numeric_cols])

        print(f"[IMPUTE] Total missing values after KNN: {df_imputed.isnull().sum().sum()}")
        return df_imputed

    # ---------------------------------------------------------
    # Step 3: Clinical Feature Engineering
    # ---------------------------------------------------------
    @staticmethod
    def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds clinically meaningful features on top of raw columns:

          - hypertension_stage: BP categories (JNC-like)
          - pack_years: smoking intensity × duration proxy
          - pulse_pressure: sysBP - diaBP (arterial stiffness)
          - cholesterol_risk: categorical cholesterol tiers
          - age_group: age bands
          - bmi_category: WHO BMI categories

        These help ML models learn clinically relevant patterns that
        the raw numbers alone may not capture clearly.
        """
        df = df.copy()

        # Hypertension stage based on systolic BP
        df["hypertension_stage"] = 0  # normal
        df.loc[df["sysBP"] >= 120, "hypertension_stage"] = 1   # elevated
        df.loc[df["sysBP"] >= 130, "hypertension_stage"] = 2   # stage 1
        df.loc[df["sysBP"] >= 140, "hypertension_stage"] = 3   # stage 2
        df.loc[df["sysBP"] >= 180, "hypertension_stage"] = 4   # crisis

        # Pack-years: (cigarettes per day / 20) * age
        df["pack_years"] = (df["cigsPerDay"] / 20.0) * df["age"]

        # Pulse pressure: sysBP - diaBP
        df["pulse_pressure"] = df["sysBP"] - df["diaBP"]

        # Cholesterol risk tiers (0=optimal, 1=borderline, 2=high)
        df["cholesterol_risk"] = pd.cut(
            df["totChol"],
            bins=[0, 200, 239, 1000],
            labels=[0, 1, 2],
            include_lowest=True,
        ).astype(int)

        # Age groups (rough decades)
        df["age_group"] = pd.cut(
            df["age"],
            bins=[0, 40, 50, 60, 70, 120],
            labels=[0, 1, 2, 3, 4],
            include_lowest=True,
        ).astype(int)

        # BMI categories (WHO)
        df["bmi_category"] = pd.cut(
            df["BMI"],
            bins=[0, 18.5, 25, 30, 100],
            labels=[0, 1, 2, 3],
            include_lowest=True,
        ).astype(int)

        print(f"[FEATS] Added engineered features. New shape: {df.shape}")
        return df

    # ---------------------------------------------------------
    # Step 4: Train/test split + scaling
    # ---------------------------------------------------------
    def split_and_scale(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Splits into train/test and scales numeric features.

        Why stratify?
          - Your dataset is imbalanced (~15% positives). We want the
            train and test splits to preserve that proportion.

        Why RobustScaler?
          - Many clinical values have outliers (e.g., very high BP).
          - RobustScaler uses median and IQR, less sensitive than mean.
        """
        # Make sure all desired features exist
        available = [col for col in self.FEATURE_COLS if col in df.columns]
        self.feature_names = available

        X = df[available].values
        y = df[self.TARGET_COL].values

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y,
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        self._is_fitted = True

        print(f"[SPLIT] Train: {X_train_scaled.shape}, Test: {X_test_scaled.shape}")
        print(f"[SPLIT] Train CVD rate: {y_train.mean():.2%}, Test CVD rate: {y_test.mean():.2%}")
        return X_train_scaled, X_test_scaled, y_train, y_test

    # ---------------------------------------------------------
    # Step 5: Save / load scaler & imputer
    # ---------------------------------------------------------
    def save_scaler(self) -> None:
        """
        Saves scaler, imputer, and feature list to a single .pkl file
        so the FastAPI backend can reuse identical preprocessing.
        """
        if not self._is_fitted:
            raise RuntimeError("Call split_and_scale() before saving scaler.")

        os.makedirs(os.path.dirname(self.scaler_path), exist_ok=True)

        joblib.dump(
            {
                "scaler": self.scaler,
                "imputer": self.imputer,
                "feature_names": self.feature_names,
            },
            self.scaler_path,
        )
        print(f"[SAVE] Scaler + imputer saved to: {self.scaler_path}")

    @classmethod
    def load_scaler(cls, path: str):
        """
        Loads scaler, imputer and feature names from disk.
        """
        artifacts = joblib.load(path)
        print(f"[LOAD] Loaded preprocessing artifacts from: {path}")
        return artifacts

    # ---------------------------------------------------------
    # Convenience: one-shot pipeline
    # ---------------------------------------------------------
    def fit_transform(self, csv_path: str):
        """
        Runs the full pipeline in one call:
          load → impute → engineer_features → split_and_scale → save_scaler
        """
        df = self.load(csv_path)
        df = self.impute(df)
        df = self.engineer_features(df)
        X_train, X_test, y_train, y_test = self.split_and_scale(df)
        self.save_scaler()
        return X_train, X_test, y_train, y_test, df
