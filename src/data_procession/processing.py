"Data processing module for cleaning and transforming credit scoring data"
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_procession.data_loader import DataLoader
import numpy as np
from sklearn.preprocessing import StandardScaler, PowerTransformer, QuantileTransformer
from sklearn.model_selection import train_test_split
from scipy import stats

file = str(Path(__file__).parent.parent.parent / "data" / "UCI_Credit_Card.csv")

loader = DataLoader(file)
loader.load_data()
df = loader.clean_data()
#print(loader.data_informer())

columns = [col for col in df.columns if df[col].nunique() > 10 and col != 'ID']

class DataProcessor:
    def __init__(self, columns, scaler_type='power'):
        """
        Initialize DataProcessor.
        
        Args:
            columns: Columns to scale
            scaler_type: 'power' (PowerTransformer), 'quantile' (QuantileTransformer), 
                        'standard' (StandardScaler), or 'outlier_removal' (remove outliers first)
        """
        self.columns = columns
        self.scaler_type = scaler_type
        
        if scaler_type == 'power':
            self.scaler = PowerTransformer(method='yeo-johnson')
        elif scaler_type == 'quantile':
            self.scaler = QuantileTransformer(output_distribution='normal', random_state=42)
        elif scaler_type == 'standard':
            self.scaler = StandardScaler()
        else:
            self.scaler = StandardScaler()
    
    def remove_outliers_iqr(self, X, multiplier=3):
        """Remove extreme outliers using IQR method"""
        X_clean = X.copy()
        for col in self.columns:
            Q1 = X_clean[col].quantile(0.25)
            Q3 = X_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR
            X_clean[col] = X_clean[col].clip(lower_bound, upper_bound)
        return X_clean
    
    def split_data(self, df, target_col, test_size=0.2, random_state=42):
        X = df.drop(columns=[target_col])
        y = df[target_col]

        X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                             test_size=test_size,
                                                             random_state=random_state)
        
        return X_train, X_test, y_train, y_test
    
    def scale_data(self, X_train, X_test):
        X_train_scaled = X_train.copy()
        X_test_scaled = X_test.copy()

        # Remove extreme outliers if specified
        if self.scaler_type == 'outlier_removal':
            X_train_scaled = self.remove_outliers_iqr(X_train_scaled, multiplier=3)
            X_test_scaled = self.remove_outliers_iqr(X_test_scaled, multiplier=3)
            # Then apply standard scaling
            self.scaler = StandardScaler()
        
        X_train_scaled[self.columns] = self.scaler.fit_transform(X_train_scaled[self.columns])
        X_test_scaled[self.columns] = self.scaler.transform(X_test_scaled[self.columns])
        return X_train_scaled, X_test_scaled



if __name__ == '__main__':
    # Try different scaling methods
    print("="*60)
    print("Testing different scaling methods:")
    print("="*60)
    
    scalers = ['power', 'quantile', 'outlier_removal', 'standard']
    
    for scaler_type in scalers:
        print(f"\n--- {scaler_type.upper()} Scaler ---")
        processor = DataProcessor(columns, scaler_type=scaler_type)
        X_train, X_test, y_train, y_test = processor.split_data(df, target_col='default.payment.next.month')
        X_train_scaled, X_test_scaled = processor.scale_data(X_train, X_test)
        
        print(f"Training data shape: {X_train_scaled.shape}")
        print(f"Testing data shape: {X_test_scaled.shape}")
        print(f"Train mean: {X_train_scaled[columns].mean().mean():.6f}")
        print(f"Train std: {X_train_scaled[columns].std().mean():.6f}")
        print(f"Train min: {X_train_scaled[columns].min().min():.6f}")
        print(f"Train max: {X_train_scaled[columns].max().max():.6f}")
    
    print("\n" + "="*60)
    print("Recommendation: Use 'power' or 'quantile' for highly skewed data")
    print("="*60)

