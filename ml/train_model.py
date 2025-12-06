import pandas as pd
import numpy as np
import argparse
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer

def load_data(filepath):
    """
    Load dataset from CSV.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    df = pd.read_csv(filepath)
    print(f"Loaded dataset with shape: {df.shape}")
    return df

def preprocess_data(df, target_col='Label'):
    """
    Preprocess data:
    - Separate features and target.
    - Drop non-feature columns (Filename, Signal, etc.).
    - Handle missing values.
    - Encode target labels.
    """
    # unexpected columns to drop
    drop_cols = ['Filename', 'Signal', 'Time', 'FI_percent', 'pvc', 'basename'] 
    
    # Also drop any other derived columns that map directly to target if known
    # e.g. if target is FI_class, FI_percent is leakage.
    
    # Drop columns that are in drop_cols and exist in df
    cols_to_drop = [c for c in drop_cols if c in df.columns]
    df_clean = df.drop(columns=cols_to_drop)

    # Identify non-numeric columns that are not the target
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    
    # Features are numeric columns
    feature_cols = [c for c in numeric_cols if c != target_col]
    
    X = df[feature_cols]
    y = df[target_col]
    
    # Impute missing values
    imputer = SimpleImputer(strategy='mean')
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
    
    # Encode target
    le = LabelEncoder()
    y_encoded = le.fit_transform(y.astype(str))
    
    print(f"Features used: {len(feature_cols)}")
    print(f"Target classes: {le.classes_}")
    
    return X_imputed, y_encoded, le, feature_cols

def train_model(X, y):
    """
    Train Random Forest Classifier with Cross-Validation.
    """
    # Initialize RF
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    
    # 5-fold Stratified CV
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X, y, cv=cv, scoring='accuracy')
    
    print(f"Cross-Validation Accuracy: {scores.mean():.4f} (+/- {scores.std()*2:.4f})")
    
    # Train on full provided set (for evaluation split or final model)
    clf.fit(X, y)
    
    return clf

def evaluate_model(clf, X_test, y_test, le, output_dir, prefix="model"):
    """
    Evaluate model and save visual reports.
    """
    y_pred = clf.predict(X_test)
    
    # Accuracy
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Set Accuracy: {acc:.4f}")
    
    # Classification Report
    report = classification_report(y_test, y_pred, target_names=le.classes_)
    print("\nClassification Report:\n")
    print(report)
    
    # Save Report
    with open(os.path.join(output_dir, f"{prefix}_report.txt"), "w") as f:
        f.write(f"Test Set Accuracy: {acc:.4f}\n\n")
        f.write(report)
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=le.classes_, yticklabels=le.classes_)
    plt.title(f'Confusion Matrix - {prefix}')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{prefix}_confusion_matrix.png"))
    plt.close()

def plot_feature_importance(clf, feature_names, output_dir, prefix="model", top_n=20):
    """
    Plot Top N Feature Importances.
    """
    importances = clf.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    top_indices = indices[:top_n]
    
    plt.figure(figsize=(12, 8))
    plt.title(f"Top {top_n} Feature Importances - {prefix}")
    plt.bar(range(top_n), importances[top_indices], align="center")
    plt.xticks(range(top_n), [feature_names[i] for i in top_indices], rotation=90)
    plt.xlim([-1, top_n])
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{prefix}_feature_importance.png"))
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Train ML model for GPR classification.")
    parser.add_argument("--input", type=str, required=True, help="Path to features CSV")
    parser.add_argument("--output_dir", type=str, default="ml_output", help="Directory to save results")
    parser.add_argument("--target", type=str, default="Label", help="Target column name (e.g., Label or FI_class_legacy)")
    parser.add_argument("--metadata", type=str, help="Path to metadata CSV (optional, for connecting extra labels)")
    
    args = parser.parse_args()
    
    # Create output dir
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        
    # Load Features
    df = load_data(args.input)
    
    # Load Metadata and Merge if provided
    if args.metadata:
        if not os.path.exists(args.metadata):
             print(f"Warning: Metadata file not found: {args.metadata}")
        else:
             print(f"Loading metadata from {args.metadata}...")
             meta_df = pd.read_csv(args.metadata)
             
             # Create common joining column (basename)
             # Features: 'Filename' e.g. s_0000.out
             # Metadata: 'filename' e.g. s_0000.in
             
             df['basename'] = df['Filename'].apply(lambda x: os.path.splitext(x)[0])
             meta_df['basename'] = meta_df['filename'].apply(lambda x: os.path.splitext(x)[0])
             
             # Drop filename from metadata to avoid collision/duplication if not needed, 
             # but keep target columns like FI_class, FI_class_legacy
             cols_to_use = meta_df.columns.difference(df.columns)
             # Ensure we keep basename for join
             if 'basename' not in cols_to_use:
                  cols_to_use = cols_to_use.union(['basename'])

             # Merge
             df = pd.merge(df, meta_df[cols_to_use], on='basename', how='left')
             print(f"Merged metadata. New shape: {df.shape}")
    
    # Check if target exists
    if args.target not in df.columns:
        # Fallback/Check for common names
        print(f"Warning: Target '{args.target}' not found in DataFrame.")
        if 'Label' in df.columns:
            print(f"Using 'Label' instead.")
            target_col = 'Label'
        elif 'FI_class' in df.columns: # Sometimes Label might be named differently
             print(f"Using 'FI_class' instead.")
             target_col = 'FI_class'
        else:
             raise ValueError(f"Target column '{args.target}' not found in dataset columns: {df.columns}")
    else:
        target_col = args.target
        
    print(f"Training on target: {target_col}")

    # Preprocess
    # Pass target_col to preprocess to ensure it's separated from features
    X, y, le, feature_cols = preprocess_data(df, target_col=target_col)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train
    print("Training Random Forest...")
    clf = train_model(X_train, y_train)
    
    # Evaluate
    print("Evaluating...")
    evaluate_model(clf, X_test, y_test, le, args.output_dir, prefix=target_col)
    
    # Feature Importance
    plot_feature_importance(clf, feature_cols, args.output_dir, prefix=target_col)
    
    print(f"Done. Results saved to {args.output_dir}")

if __name__ == "__main__":
    main()
