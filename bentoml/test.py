import bentoml.transformers

model = bentoml.transformers.load_model("google_summarizer:h7qziawduskfznbo")
print(model.predict("Model deployment is one of the last and most important stages in the machine learning life cycle: only by putting a machine learning model into a production environment and making predictions for end applications, the full potential of ML can be realized."))
