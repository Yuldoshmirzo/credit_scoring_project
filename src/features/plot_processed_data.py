"""
Plot diagnostics for processed data from data_procession module
"""
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_procession.processing import DataProcessor
from data_procession.data_loader import DataLoader
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from scipy.stats import norm

# Load and prepare data
file = str(Path(__file__).parent.parent.parent / "data" / "UCI_Credit_Card.csv")

loader = DataLoader(file)
loader.load_data()
df = loader.clean_data()

# Get columns (same logic as in processing.py)
columns = [col for col in df.columns if df[col].nunique() > 10 and col != 'ID']

# Split and scale data using DataProcessor
processor = DataProcessor(columns, scaler_type='power')   
X_train, X_test, y_train, y_test = processor.split_data(df, target_col='default.payment.next.month')
X_train_scaled, X_test_scaled = processor.scale_data(X_train, X_test)

# Combine scaled data for plotting
df_scaled = pd.concat([X_train_scaled, X_test_scaled], ignore_index=True)

print("Data loaded and processed successfully")
print(f"Processed data shape: {df_scaled.shape}")


# ========== Plotting Functions ==========

def correlation_heatmap(df):
    """Plot a heatmap of feature correlations"""
    plt.figure(figsize=(12, 10))
    corr = df.corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm")
    plt.title("Feature Correlation Heatmap (Original Data)")
    plt.tight_layout()
    
    artifacts_path = Path(__file__).parent.parent.parent / "artifacts" / "after_processing"
    artifacts_path.mkdir(parents=True, exist_ok=True)
    plt.savefig(artifacts_path / "correlation_heatmap_scaled.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Correlation heatmap saved")


def plot_gaussian_curve(df, column):
    """Plot the distribution of a numeric column with a Gaussian curve"""
    mean = df[column].mean()
    std = df[column].std()
    
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x=column, bins=30, stat="density", kde=True)

    x = np.linspace(df[column].min(), df[column].max(), 300)
    y = norm.pdf(x, mean, std)
    plt.plot(x, y, linewidth=2.5, color='red', label='Gaussian')
    plt.title(f"Gaussian Check for {column} (Original Data)", fontsize=12, fontweight='bold')
    plt.xlabel(column, fontsize=11)
    plt.ylabel("Density", fontsize=11)
    plt.legend()
    plt.tight_layout()
    
    artifacts_path = Path(__file__).parent.parent.parent / "artifacts" / "after_processing"
    artifacts_path.mkdir(parents=True, exist_ok=True)
    plt.savefig(artifacts_path / f"gaussian_check_{column}_original.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Gaussian plot saved for {column}")


def box_plot_outliers(df, column):
    """Create a box plot to identify outliers in a column"""
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, y=column, palette='Set2')
    plt.title(f"Box Plot for {column} (Original Data)", fontsize=12, fontweight='bold')
    plt.ylabel(column, fontsize=11)
    plt.tight_layout()
    
    artifacts_path = Path(__file__).parent.parent.parent / "artifacts" / "after_processing"
    artifacts_path.mkdir(parents=True, exist_ok=True)
    plt.savefig(artifacts_path / f"box_plot_{column}_original.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Box plot saved for {column}")


    
correlation_heatmap(df_scaled)

print(f"\nGenerating diagnostic plots for {len(columns)} continuous columns...")
for col in columns:
    plot_gaussian_curve(df_scaled, col)
    box_plot_outliers(df_scaled, col)
print("✓ All plots generated successfully!")