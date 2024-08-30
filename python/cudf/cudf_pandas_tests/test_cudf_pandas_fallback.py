# SPDX-FileCopyrightText: Copyright (c) 2024, NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest

from cudf.pandas import LOADED

from .conftest import no_fallback

if not LOADED:
    raise ImportError("These tests must be run with cudf.pandas loaded")

import pandas as xpd

pd = xpd._fsproxy_slow


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
