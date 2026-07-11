import numpy as np
import pytest

from supply_chain_resilience.distributions import DistType, Distribution, sample


@pytest.mark.parametrize("kind", list(DistType))
def test_all_distribution_families_are_bounded(kind):
    distribution = Distribution(
        kind=kind,
        minimum=0.0,
        maximum=0.8,
        mode=0.4,
        mean=-0.5 if kind == DistType.LOGNORMAL else 0.4,
    )
    values = sample(np.random.default_rng(7), 500, distribution)
    assert len(values) == 500
    assert np.isfinite(values).all()
    assert (values >= 0.0).all()
    assert (values <= 0.8).all()


def test_sampling_is_deterministic():
    distribution = Distribution(DistType.TRIANGULAR, 0.0, 0.7, mode=0.5)
    one = sample(np.random.default_rng(42), 100, distribution)
    two = sample(np.random.default_rng(42), 100, distribution)
    np.testing.assert_array_equal(one, two)


def test_distribution_rejects_invalid_bounds():
    with pytest.raises(ValueError):
        Distribution(minimum=0.5, maximum=0.5).validate()


def test_distribution_rejects_invalid_mode():
    with pytest.raises(ValueError):
        Distribution(minimum=0.0, maximum=0.5, mode=0.8).validate()


def test_sampling_rejects_non_positive_size():
    with pytest.raises(ValueError):
        sample(np.random.default_rng(0), 0, Distribution())
