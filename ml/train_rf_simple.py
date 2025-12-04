import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder

def train_model(data_path='features_dataset.csv'):
    print(f"Loading data from {data_path}...")
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: File {data_path} not found.")
        return

    print(f"Dataset shape: {df.shape}")
    
    # 1. Preprocessing
    # Drop non-feature columns
    # Metadata columns from read_gprmax_hdf5.py
    metadata_cols = ['gprMax', 'Title', 'Iterations', 'nx_ny_nz', 'dx_dy_dz', 'dt', 'srcsteps', 'rxsteps', 'nsrc', 'nrx']
    cols_to_drop = ['Filename', 'Signal'] + metadata_cols
    
    # Filter out columns that actually exist in the dataframe
    cols_to_drop = [col for col in cols_to_drop if col in df.columns]
    
    X = df.drop(columns=cols_to_drop + ['Label'])
    y = df['Label']
    
    print(f"Features: {X.shape[1]}")
    print(f"Target classes: {y.unique()}")
    
    # Handle missing values (if any)
    if X.isnull().sum().sum() > 0:
        print("Warning: Missing values found. Imputing with 0.")
        X = X.fillna(0)
        
    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    print(f"Encoded classes: {dict(zip(le.classes_, le.transform(le.classes_)))}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
    
    print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
    
    # 2. Train Random Forest
    print("Training Random Forest Classifier...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    # 3. Evaluation
    print("Evaluating model...")
    y_pred = rf.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {acc:.4f}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=le.classes_, yticklabels=le.classes_)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    print("Confusion matrix saved to 'confusion_matrix.png'")
    
    # Feature Importance
    importances = rf.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    print("\nTop 20 Feature Importances:")
    top_n = 20
    for f in range(top_n):
        print(f"{f+1}. {X.columns[indices[f]]} ({importances[indices[f]]:.4f})")
        
    # Plot Feature Importance
    plt.figure(figsize=(12, 6))
    plt.title("Feature Importances (Top 20)")
    plt.bar(range(top_n), importances[indices[:top_n]], align="center")
    plt.xticks(range(top_n), X.columns[indices[:top_n]], rotation=90)
    plt.xlim([-1, top_n])
    plt.tight_layout()
    plt.savefig('feature_importance.png')
    print("Feature importance plot saved to 'feature_importance.png'")

if __name__ == "__main__":
    train_model()
