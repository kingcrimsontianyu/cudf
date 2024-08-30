# SPDX-FileCopyrightText: Copyright (c) 2024, NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import warnings

import pytest


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
