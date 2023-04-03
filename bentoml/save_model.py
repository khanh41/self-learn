"""Learn bentoml."""
import bentoml

from sklearn import svm, datasets

iris_ds = datasets.load_iris()

X, y = iris_ds.data, iris_ds.target

clf = svm.SVC()
clf.fit(X, y)

saved_model = bentoml.sklearn.save_model("iris_clf", clf)
print(saved_model)
