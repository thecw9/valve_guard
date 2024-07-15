import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.utils import check_array
from sklearn.utils.validation import check_is_fitted


def are_all_elements_same(X):
    return np.all(X == X[0])


class GMM1D:
    CLASSES = {
        "normal": 0,
        "anomaly": 1,
    }

    def __init__(self, n_components) -> None:
        self.n_components = n_components
        self.data_is_fixed = False

    def fit(self, X):
        """
        Fit the model with X.

        Parameters
        ----------
        X : array-like of shape (n_samples, 1)
        """
        check_array(X)
        self.X = X

        # check data is fixed
        if np.all(X == X[0]):
            self.data_is_fixed = True
            self.detector_ = GaussianMixture(n_components=1)
            self.threshold_ = 0.1
            self.probs_density_curve_x_ = np.linspace(
                np.min(X) - 1, np.max(X) + 1, 101
            ).reshape(-1, 1)
            self.train_samples_probs_ = self.predict_proba(X)
            return self

        self.probs_density_curve_x_ = np.linspace(
            np.min(X) - (np.max(X) - np.min(X)) / 2,
            np.max(X) + (np.max(X) - np.min(X)) / 2,
            100,
        ).reshape(-1, 1)

        self.detector_ = GaussianMixture(n_components=self.n_components)
        self.detector_.fit(X)

        self.train_samples_probs_ = self.predict_proba(X)
        self.threshold_ = np.min(self.train_samples_probs_)

        return self

    def predict_proba(self, X):
        if self.data_is_fixed:
            return np.where(X == self.X[0], 1, 0)

        # check data is fixed
        check_is_fitted(self, ["X", "detector_"])
        check_array(X)
        return np.exp(self.detector_.score_samples(X))

    def predict(self, X):
        check_is_fitted(self, ["X", "detector_"])
        check_array(X)
        probs = self.predict_proba(X)
        return np.where(
            probs < self.threshold_, self.CLASSES["anomaly"], self.CLASSES["normal"]
        )

    def _prob_density_curve(self):
        check_is_fitted(self, ["X", "detector_"])
        probs = self.predict_proba(self.probs_density_curve_x_)
        probs_density_curve = np.column_stack((self.probs_density_curve_x_, probs))
        # down threshold of value to 0.1
        return probs_density_curve

    def _get_threshold(self, probs_density_curve):
        threshold_up = 0
        threshold_down = 0
        for data in probs_density_curve:
            if data[1] > 0.1:
                threshold_down = data[0]
                break

        for data in probs_density_curve[::-1]:
            if data[1] > 0.1:
                threshold_up = data[0]
                break

        return threshold_down, threshold_up

    def describe(self):
        check_is_fitted(self, ["X", "detector_"])
        return {
            "X_train": np.squeeze(self.X).tolist(),
            "probs_density": self._prob_density_curve().tolist(),
            "X": np.squeeze(self.probs_density_curve_x_).tolist(),
            # "probs_density": {
            #     "X": np.squeeze(self.probs_density_curve_x_).tolist(),
            #     "probs": np.squeeze(
            #         self.predict_proba(self.probs_density_curve_x_)
            #     ).tolist(),
            # },
            "train_samples_probs": np.squeeze(self.train_samples_probs_).tolist(),
            "n_components": self.n_components,
            "threshold": self.threshold_,
            "threshold_down": self._get_threshold(self._prob_density_curve())[0],
            "threshold_up": self._get_threshold(self._prob_density_curve())[1],
        }


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    random_data = np.random.normal(0, 1, 1000).reshape(-1, 1)
    gmm = GMM1D(n_components=2).fit(random_data)
    fixed_data = np.zeros((1000, 1))
    gmm = GMM1D(n_components=2).fit(fixed_data)

    desc = gmm.describe()
    print(desc)
    # print(gmm._prob_density_curve())

    # plot desc["X"]
    plt.scatter(desc["X"], np.zeros_like(desc["X"]), alpha=0.5)

    # plot probs_density_curve
    # plt.plot(
    #     desc["probs_density"]["X"],
    #     desc["probs_density"]["probs"],
    #     color="red",
    #     label="probs_density_curve",
    # )
    plt.plot(
        gmm._prob_density_curve()[:, 0],
        gmm._prob_density_curve()[:, 1],
    )

    # plot threshold
    plt.axhline(desc["threshold"], color="green", label="threshold")

    plt.show()
