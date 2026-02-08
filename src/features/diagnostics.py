import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_procession.processing import DataProcessor
from data_procession.data_loader import DataLoader
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import norm

# Use absolute path relative to script location
file = str(Path(__file__).parent.parent.parent / "data" / "UCI_Credit_Card.csv")

loader = DataLoader(file)
df = loader.clean_data()
print(df.head())
print(df.columns)

# Correlation of features

def correlation_heatmap(df):
    """Plot a heatmap of feature correlations"""
    plt.figure(figsize=(12, 10))
    corr = df.corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm")
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.savefig("artifacts/correlation_heatmap.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Correlation heatmap saved")

continuous_cols = [col for col in df.columns if df[col].nunique() > 10 and df[col].dtype in [np.int64, np.float64]]

# Check Gaussian Curve 
def plot_gaussian_curve(df, column):
    """Plot the distribution of a numeric column with a Gaussian curve"""
    mean = df[column].mean()
    std = df[column].std()
    
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x=column, bins=30, stat="density", kde=True)

    x = np.linspace(df[column].min(), df[column].max(), 300)
    y = norm.pdf(x, mean, std)
    plt.plot(x, y, linewidth=2.5, color='red', label='Gaussian')
    plt.title(f"Gaussian Check for {column}", fontsize=12, fontweight='bold')
    plt.xlabel(column, fontsize=11)
    plt.ylabel("Density", fontsize=11)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"artifacts/gaussian_check_{column}.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Gaussian plot saved for {column}")

def box_plot_outliers(df, column):
    """Create a box plot to identify outliers in a column"""
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, y=column, palette='Set2')
    plt.title(f"Box Plot for {column}", fontsize=12, fontweight='bold')
    plt.ylabel(column, fontsize=11)
    plt.tight_layout()
    plt.savefig(f"artifacts/box_plot_{column}.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Box plot saved for {column}")

# Generate plots for all continuous columns
correlation_heatmap(df)

print(f"\nGenerating diagnostic plots for {len(continuous_cols)} continuous columns...")
for col in continuous_cols:
    plot_gaussian_curve(df, col)
    box_plot_outliers(df, col)
print("✓ All plots generated successfully!")

