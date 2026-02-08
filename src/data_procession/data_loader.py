"data loading module will be implemted with cleaning functions"

import pandas as pd
import numpy as np

class DataLoader:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = None

    def load_data(self) -> pd.DataFrame:
        """Load the credit scorind datset from data folder"""
        self.data = pd.read_csv(self.filepath)
        return self.data
    
    def clean_data(self) -> pd.DataFrame:
        """Clean the dataset by handling missing values and duplicates"""
        
        data = self.data.copy()
        
        # Drop duplicates
        initial_rows = len(data)
        data = data.drop_duplicates()
        removed_rows = initial_rows - len(data)
        if removed_rows > 0:
            print(f"✓ Removed {removed_rows} duplicate rows")
        
        # Identify binary and numeric columns
        binary_cols = [col for col in data.columns if data[col].nunique() == 2]
        numeric_cols = [col for col in data.columns 
                        if data[col].dtype in [np.int64, np.float64] and col not in binary_cols]
        
        # Fill missing values in binary columns with mode
        for col in binary_cols:
            missing_count = data[col].isnull().sum()
            if missing_count > 0:
                mode_val = data[col].mode()
                if len(mode_val) > 0:
                    data[col] = data[col].fillna(mode_val[0])
                    print(f"✓ Filled {missing_count} missing values in '{col}' with mode: {mode_val[0]}")
        
        # Fill missing values in numeric columns with median
        for col in numeric_cols:
            missing_count = data[col].isnull().sum()
            if missing_count > 0:
                median_val = data[col].median()
                data[col] = data[col].fillna(median_val)
                print(f"✓ Filled {missing_count} missing values in '{col}' with median: {median_val:.2f}")
        
        print(f"✓ Data cleaning complete. Final shape: {data.shape}")
        return data
    
    def data_informer(self) -> None:
        """Print basic information about the dataset"""
        print("Shape of the dataset:", self.data.shape)
        print("Data Info:")
        print(self.data.info())
        print("\nMissing Values:")
        print(self.data.isnull().sum())
        print("\nStatistical Summary:")
        print(self.data.describe())

if __name__ == "__main__":
    df_loader = DataLoader("../../data/UCI_Credit_Card.csv")
    df = df_loader.load_data()
    print("Initial Data Info:")
    df_loader.data_informer()

    df_cleaned = df_loader.clean_data()
    print("\nCleaned Data Info:")
    df_loader.data_informer()
    