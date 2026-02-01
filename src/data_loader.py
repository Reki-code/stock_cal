import pandas as pd

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_ibkr_records(self):
        """Loads IBKR trading records from a CSV file"""
        try:
            data = pd.read_csv(self.file_path)
            return data
        except Exception as e:
            print(f"Error loading file: {e}")
            return None