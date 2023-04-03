import bentoml
from transformers import pipeline

summarizer = pipeline("summarization", model="google/pegasus-cnn_dailymail")
bentoml.transformers.save_model(name="google_summarizer", pipeline=summarizer)
