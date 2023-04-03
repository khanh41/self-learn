"""Create inference services to expose models as APIs ⚙️."""
import bentoml
import numpy as np
from bentoml.io import NumpyNdarray, Text

iris_clf_runner = bentoml.sklearn.get("iris_clf:latest").to_runner()
google_summarizer_runner = bentoml.transformers.get("google_summarizer:latest").to_runner()

svc = bentoml.Service("iris_classifier", runners=[iris_clf_runner, google_summarizer_runner])


@svc.api(input=NumpyNdarray(), output=NumpyNdarray())
def classify(input_series: np.ndarray) -> np.ndarray:
    result = iris_clf_runner.predict.run(input_series)
    return result


@svc.api(input=Text(), output=Text())
def text_summary(input_paragraph: str) -> str:
    result = google_summarizer_runner.run(input_paragraph)
    return result[0]["summary_text"]
