import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.utils import check_array
from sklearn.utils.validation import check_is_fitted

from .base import BaseDiagnosisModel


class GMM(BaseDiagnosisModel):
    CLASSES = {
        "normal": 0,
        "anomaly": 1,
    }

    def __init__(self, n_components) -> None:
        self.n_components = n_components

    def fit(self, X):
        """
        Fit the model with X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
        """
        check_array(X)
        self.X = X

        self.detector_ = GaussianMixture(n_components=self.n_components)
        self.detector_.fit(X)

        self.train_samples_probs_ = np.exp(self.detector_.score_samples(X))
        self.threshold_ = np.min(self.train_samples_probs_)

        return self

    def predict_proba(self, X):
        check_is_fitted(self, ["X", "detector_", "threshold_"])
        check_array(X)
        return np.exp(self.detector_.score_samples(X))

    def predict(self, X):
        check_is_fitted(self, ["X", "detector_", "threshold_"])
        check_array(X)
        probs = self.predict_proba(X)
        return np.where(
            probs < self.threshold_, self.CLASSES["anomaly"], self.CLASSES["normal"]
        )

    def describe(self):
        check_is_fitted(self, ["X", "detector_", "threshold_"])
        return {
            "X": self.X,
            "threshold": self.threshold_,
        }


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    np.random.seed(0)
    X = np.random.randn(100, 1)
    X = np.concatenate([X, np.random.randn(100, 1) + 10])
    X = np.concatenate([X, np.random.randn(100, 1) + 20])

    model = GMM(n_components=3)
    model.fit(X)

    plt.hist(X, bins=20)
    plt.show()

    plt.hist(model.train_samples_probs_, bins=20)
    plt.show()

    print(model.describe())
