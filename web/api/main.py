from fastapi import FastAPI, UploadFile
import pandas as pd
from hashprep.analyzer import DatasetAnalyzer

app = FastAPI()

@app.post("/analyze/")
async def analyze_dataset(file: UploadFile):
    df = pd.read_csv(file.file)
    analyzer = DatasetAnalyzer(df)
    return analyzer.analyze()
