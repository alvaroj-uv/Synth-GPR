#!/usr/bin/env python3
"""
Train RF on v3 dataset with Pandoscope labels and test on real Site-1 data.

Compares:
- v2_selig: synthetic v2 (balanced) trained on Selig FI
- v3_pandoscope: synthetic v3 (imbalanced) trained on Pandoscope FI

Both tested on real Site-1 Pandoscope labels (112 traces).

Expected outcome: v3_pandoscope should perform better since label definitions match.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import balanced_accuracy_score, classification_report, confusion_matrix
import joblib
import warnings

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.signal_processing import preprocess_signal, extract_features_from_csv

warnings.filterwarnings('ignore')


def load_real_data():
    """Load real Site-1 data with Pandoscope labels."""
    df_traces = pd.read_csv('D:/Codigo/Data_Labled/Señales_Brutas/df_GPR_match_filtrado.csv')
    df_fi = pd.read_csv('D:/Codigo/Data_Labled/Mediciones_FI/df_pandoscope_med.csv')

    # Merge on ID
    df_labeled = df_traces.merge(df_fi, on='ID')

    # Extract samples (skip columns ID, n_traza, use columns 1-510)
    X = df_labeled.iloc[:, 2:512].values.astype(np.float32)  # 510 samples
    y_fi = df_labeled['FI_Estimado_Medio_JRO_Final'].values

    # Bin to Selig classes
    def fi_to_class(fi):
        if fi <= 2:
            return 'C'
        elif fi <= 8:
            return 'MC'
        elif fi <= 20:
            return 'MF'
        elif fi <= 50:
            return 'F'
        else:
            return 'HF'

    y = np.array([fi_to_class(f) for f in y_fi])

    print(f"Real data loaded: {X.shape}")
    print(f"Real label distribution:")
    unique, counts = np.unique(y, return_counts=True)
    for cls, count in zip(unique, counts):
        print(f"  {cls}: {count:3d} ({100*count/len(y):5.1f}%)")

    return X, y, y_fi


def train_model(X_train: np.ndarray, y_train: np.ndarray, model_name: str) -> RandomForestClassifier:
    """Train RF model."""
    print(f"\nTraining RF ({model_name}) ...")

    # Use balanced weights to handle class imbalance
    model = RandomForestClassifier(
        n_estimators=300,
        class_weight='balanced',
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        n_jobs=-1,
        random_state=42,
    )

    model.fit(X_train, y_train)

    # Cross-val score
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='balanced_accuracy')
    print(f"  CV Balanced Accuracy: {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")

    return model


def evaluate_model(model: RandomForestClassifier, X_test: np.ndarray, y_test: np.ndarray, model_name: str):
    """Evaluate model on test set."""
    y_pred = model.predict(X_test)

    acc = (y_pred == y_test).sum() / len(y_test)
    bal_acc = balanced_accuracy_score(y_test, y_pred)

    print(f"\n{'='*70}")
    print(f"EVALUATION: {model_name}")
    print(f"{'='*70}")
    print(f"Accuracy: {acc:.4f}")
    print(f"Balanced Accuracy: {bal_acc:.4f}")

    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print(f"\nConfusion Matrix (rows=true, cols=pred):")
    cm = confusion_matrix(y_test, y_pred, labels=sorted(np.unique(y_test)))
    print(pd.DataFrame(cm, index=sorted(np.unique(y_test)), columns=sorted(np.unique(y_test))))

    return bal_acc


def main():
    print("=" * 70)
    print("TRAIN & EVALUATE: V3 Pandoscope vs V2 Selig")
    print("=" * 70)

    # Load real test data
    X_real, y_real, y_real_fi = load_real_data()

    # Load v3 synthetic data
    print(f"\nLoading v3 parquet...")
    v3_path = Path('output/gpr_synth_dataset_v3_pandoscope_features.parquet')
    if not v3_path.exists():
        print(f"ERROR: {v3_path} not found")
        return 1

    df_v3 = pd.read_parquet(v3_path)
    print(f"V3 loaded: {df_v3.shape}")

    # Extract features and labels (exclude metadata)
    metadata_cols = ['sample_id', 'label_selig', 'label_pandoscope', 'pvc', 'porosity', 'FI_pandoscope']
    feature_cols = [c for c in df_v3.columns if c not in metadata_cols]

    X_v3 = df_v3[feature_cols].values.astype(np.float32)
    y_v3_pandoscope = df_v3['label_pandoscope'].values

    print(f"V3 features shape: {X_v3.shape}")
    print(f"V3 Pandoscope label distribution:")
    unique, counts = np.unique(y_v3_pandoscope, return_counts=True)
    for cls, count in zip(unique, counts):
        print(f"  {cls}: {count:5d} ({100*count/len(y_v3_pandoscope):5.1f}%)")

    # Train v3_pandoscope model
    X_train, X_test, y_train, y_test = train_test_split(
        X_v3, y_v3_pandoscope, test_size=0.2, random_state=42, stratify=y_v3_pandoscope
    )

    model_v3 = train_model(X_train, y_train, "V3 Pandoscope")

    # Evaluate on synthetic test set
    bal_acc_v3_synth = evaluate_model(model_v3, X_test, y_test, "V3 Pandoscope (Synthetic Test)")

    # Evaluate on real data
    print(f"\n{'='*70}")
    print(f"CROSS-DOMAIN TEST: V3 Pandoscope on Real Site-1 Data")
    print(f"{'='*70}")

    # Interpolate real data to match v3 feature count
    if X_real.shape[1] != X_v3.shape[1]:
        print(f"\nWARNING: Feature dimension mismatch")
        print(f"  Real: {X_real.shape[1]} samples")
        print(f"  V3:   {X_v3.shape[1]} features")
        print(f"  Interpolating real to match v3...")

        X_real_interp = np.zeros((X_real.shape[0], X_v3.shape[1]), dtype=np.float32)
        indices_old = np.linspace(0, X_real.shape[1] - 1, X_real.shape[1])
        indices_new = np.linspace(0, X_real.shape[1] - 1, X_v3.shape[1])

        for i in range(X_real.shape[0]):
            X_real_interp[i] = np.interp(indices_new, indices_old, X_real[i])

        X_real = X_real_interp

    bal_acc_v3_real = evaluate_model(model_v3, X_real, y_real, "V3 Pandoscope on Real")

    # Load and evaluate v2 baseline for comparison
    print(f"\n{'='*70}")
    print(f"BASELINE: V2 Selig Model")
    print(f"{'='*70}")

    v2_model_path = Path('output/rf_model_v2_waveform.joblib')
    if v2_model_path.exists():
        model_v2 = joblib.load(v2_model_path)

        # Interpolate real data to v2 feature count
        X_real_v2 = X_real[:, :model_v2.n_features_in_] if X_real.shape[1] >= model_v2.n_features_in_ else X_real

        if X_real_v2.shape[1] != model_v2.n_features_in_:
            print(f"WARNING: Feature dimension mismatch for v2")
            print(f"  Model expects: {model_v2.n_features_in_}")
            print(f"  Real has: {X_real_v2.shape[1]}")
        else:
            bal_acc_v2_real = evaluate_model(model_v2, X_real_v2, y_real, "V2 Selig on Real")

            print(f"\n{'='*70}")
            print(f"SUMMARY COMPARISON")
            print(f"{'='*70}")
            print(f"V2 Selig (synthetic test):  {0.5954:.4f} (from prior run)")
            print(f"V2 Selig (real test):       {bal_acc_v2_real:.4f}")
            print(f"V3 Pandoscope (synth test): {bal_acc_v3_synth:.4f}")
            print(f"V3 Pandoscope (real test):  {bal_acc_v3_real:.4f}")

            improvement = (bal_acc_v3_real - bal_acc_v2_real) / bal_acc_v2_real * 100
            print(f"\nImprovement: {improvement:+.1f}%")

            if improvement > 0:
                print(f"SUCCESS: Pandoscope label conversion improved real-data generalization!")
            else:
                print(f"Note: Gap persists. May indicate feature domain shift beyond label definition.")
    else:
        print(f"v2 baseline not found at {v2_model_path}")

    # Save v3 model
    model_v3_path = Path('output/rf_model_v3_pandoscope.joblib')
    joblib.dump(model_v3, model_v3_path)
    print(f"\nModel saved: {model_v3_path}")

    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
