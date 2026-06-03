#!/usr/bin/env python3
"""
Domain-shift probe: is the 80k phantom-trained RF robust to the rock z-fix?

The 0.7083 baseline was trained on PHANTOM traces (rocks dropped). This asks: if
we feed that same model the SAME 50 samples but with rocks now present (and with
heterogeneous fouling), do its predictions hold or fall apart?

  - If predictions barely change -> the phantom bug barely affects the classifier;
    the 0.7083 baseline is largely salvageable.
  - If predictions flip / accuracy drops on rock traces -> the model learned
    phantom-specific artifacts; the baseline is invalid and the full re-run matters.

Uses the SAME feature pipeline as the 80k parquet (build_parquet._process) so the
feature vectors align with the trained model.

    python scripts/main/phantom_domain_shift.py --model output/rf_model_waveform_only.joblib
"""
import sys, argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.main.build_parquet import _process
from sklearn.metrics import balanced_accuracy_score, accuracy_score

SUBSET_DIR = Path(r"D:\gprMax\user_models\phantom_recovery_s1")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=Path,
                    default=ROOT / "output" / "rf_model_waveform_only.joblib")
    args = ap.parse_args()

    import joblib
    bundle = joblib.load(args.model)
    model = bundle.get("model") if isinstance(bundle, dict) else bundle

    # Derive feature columns the SAME way training did (exclude metadata),
    # from the training parquet — guarantees identical column order.
    from scripts.main.train_rf_waveform_only import METADATA_FIELDS
    pq = pd.read_parquet(ROOT / "output" / "dataset_80k_features.parquet")
    exclude = {"sample_id", "source", "label"} | METADATA_FIELDS
    feat_cols = [c for c in pq.columns if c not in exclude]
    print(f"Model expects {len(feat_cols)} features\n")

    man = pd.read_csv(SUBSET_DIR / "manifest.csv")

    def feats_for(stem):
        p = SUBSET_DIR / f"{stem}.out"
        if not p.exists():
            return None
        row = _process(p)
        if row is None:
            return None
        return row

    # Build per-arm feature frames aligned to model columns
    arms = ["phantom", "rock", "rockhetero"]
    records = {a: [] for a in arms}
    labels = {a: [] for a in arms}
    for _, r in man.iterrows():
        a = r["arm"]
        if a not in arms:
            continue
        row = feats_for(r["stem"])
        if row is None:
            continue
        records[a].append(row)
        labels[a].append(r["label"])

    # Only samples present in ALL arms (for a fair paired comparison)
    common = set(man[man.arm == "rockhetero"].sample_id)

    print("Per-arm balanced accuracy of the PHANTOM-trained model:")
    preds = {}
    for a in arms:
        if not records[a]:
            continue
        X = pd.DataFrame(records[a]).reindex(columns=feat_cols).fillna(0.0).values.astype("float32")
        y = np.array(labels[a])
        p = model.predict(X)
        preds[a] = (y, p)
        bal = balanced_accuracy_score(y, p)
        acc = accuracy_score(y, p)
        print(f"  {a:<11} n={len(y):<3} balanced_acc={bal:.3f}  acc={acc:.3f}")

    # Prediction flips phantom -> rock (paired, same sample order)
    print("\nPrediction stability (paired phantom vs rock, same samples):")
    mp = man[man.arm == "phantom"].set_index("sample_id")["stem"].to_dict()
    mr = man[man.arm == "rock"].set_index("sample_id")["stem"].to_dict()
    flips = same = 0
    for sid in sorted(set(mp) & set(mr)):
        fp, fr = feats_for(mp[sid]), feats_for(mr[sid])
        if fp is None or fr is None:
            continue
        Xp = pd.DataFrame([fp]).reindex(columns=feat_cols).fillna(0.0).values.astype("float32")
        Xr = pd.DataFrame([fr]).reindex(columns=feat_cols).fillna(0.0).values.astype("float32")
        pp, pr = model.predict(Xp)[0], model.predict(Xr)[0]
        if pp == pr:
            same += 1
        else:
            flips += 1
    tot = same + flips
    if tot:
        print(f"  phantom->rock: {flips}/{tot} predictions FLIPPED ({flips/tot*100:.0f}%)")
        print("  (high flip rate => phantom-trained model is fragile to the bug fix)")


if __name__ == "__main__":
    main()
