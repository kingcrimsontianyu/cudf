# SPDX-FileCopyrightText: Copyright (c) 2024, NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import warnings

import pytest

from cudf.pandas import LOADED

if not LOADED:
    raise ImportError("These tests must be run with cudf.pandas loaded")

import pandas as xpd

pd = xpd._fsproxy_slow


def no_fallback(fallback=False):
    def decorator(func):
        @pytest.mark.usefixtures("recwarn")
        def wrapper(*args, **kwargs):
            with pytest.MonkeyPatch().context() as mp:
                mp.setenv("CUDF_PANDAS_WARN_ON_FALLBACK", "True")
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    result = func(*args, **kwargs)
                    fallback_warnings = any(
                        issubclass(warn.category, UserWarning)
                        and "Falling back to the slow path."
                        in str(warn.message)
                        for warn in w
                    )
                    if fallback:
                        assert (
                            fallback_warnings
                        ), "Expected fallback, but no fallback occured."
                    else:
                        assert (
                            not fallback_warnings
                        ), "Expected no fallback, but fallback occured"
                    return result

        return wrapper

    return decorator


@pytest.fixture
def dataframe():
    pdf = pd.DataFrame({"a": [1, 1, 1, 2, 3], "b": [1, 2, 3, 4, 5]})
    df = xpd.DataFrame(pdf)
    return (pdf, df)


@pytest.fixture
def series(dataframe):
    pdf, df = dataframe
    return (pdf["a"], df["a"])


@no_fallback
@pytest.mark.parametrize(
    "op",
    [
        "sum",
        "min",
        "max",
        "mean",
        "std",
        "var",
        "prod",
        "median",
    ],
)
def test_no_fallback_in_reduction_ops(series, op):
    s, xs = series
    res = getattr(xs, op)
    expect = getattr(s, op)
    assert res == expect
