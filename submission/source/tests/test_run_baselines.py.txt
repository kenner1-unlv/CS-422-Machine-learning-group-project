import unittest
import numpy as np
from scripts.run_baselines import make_pipeline, metrics


class BaselineTests(unittest.TestCase):
    def test_scaler_stays_fitted_to_training_after_predictions(self):
        train = np.array([[0., 5.], [2., 5.], [4., 5.]])
        for model, alpha in [('linear', None), ('ridge', 1.)]:
            pipeline = make_pipeline(model, alpha).fit(train, np.array([1., 3., 5.]))
            before = pipeline['scale'].mean_.copy()
            pipeline.predict(np.array([[1000., 5.], [2000., 5.]]))
            np.testing.assert_array_equal(pipeline['scale'].mean_, before)
            np.testing.assert_allclose(before, [2., 5.])
            self.assertEqual(pipeline['scale'].n_samples_seen_, 3)

    def test_metrics_keep_yield_units(self):
        result = metrics(np.array([10., 20.]), np.array([12., 16.]))
        self.assertEqual(result['mae'], 3.)
        self.assertAlmostEqual(result['rmse'], np.sqrt(10))
