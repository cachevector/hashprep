import pandas as pd
from hashprep.analyzer import DatasetAnalyzer

if __name__ == "__main__":
    df = pd.read_csv("datasets/train.csv")
    analyzer = DatasetAnalyzer(df)
    print(analyzer.analyze())
