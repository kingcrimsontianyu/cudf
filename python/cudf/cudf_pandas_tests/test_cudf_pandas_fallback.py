# SPDX-FileCopyrightText: Copyright (c) 2024, NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest

from cudf.pandas import LOADED

if not LOADED:
    raise ImportError("These tests must be run with cudf.pandas loaded")

import pandas as xpd
import pandas._testing as tm

pd = xpd._fsproxy_slow

pytestmark = pytest.mark.filterwarnings(
    "error::UserWarning:.*Falling back to the slow path.*"
)


@pytest.fixture
def dataframe():
    pdf = pd.DataFrame({"a": [1, 1, 1, 2, 3], "b": [1, 2, 3, 4, 5]})
    df = xpd.DataFrame(pdf)
    return (pdf, df)


@pytest.fixture
def series(dataframe):
    pdf, df = dataframe
    return (pdf["a"], df["a"])


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
    tm.assert_series_equal(res, expect)


@pytest.mark.xfail(reason="Fallback expected")
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
def test_fallback_in_reduction_ops(op):
    s = pd.Series(range(2), dtype=object)
    xs = pd.Series(range(2), dtype=object)
    res = getattr(xs, op)
    expect = getattr(s, op)
    tm.assert_series_equal(res, expect)
