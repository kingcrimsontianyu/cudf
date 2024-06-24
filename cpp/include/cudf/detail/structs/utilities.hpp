/*
 * Copyright (c) 2020-2024, NVIDIA CORPORATION.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#pragma once

#include <cudf/structs/structs_column_view.hpp>
#include <cudf/table/table_view.hpp>
#include <cudf/types.hpp>
#include <cudf/utilities/default_stream.hpp>
#include <cudf/utilities/span.hpp>

#include <rmm/cuda_stream_view.hpp>
#include <rmm/device_buffer.hpp>
#include <rmm/resource_ref.hpp>

#include <utility>

namespace cudf::structs::detail {

enum class column_nullability {
  MATCH_INCOMING,  ///< generate a null column if the incoming column has nulls
  FORCE            ///< always generate a null column
};

/**
 * @brief The struct to hold temporary data that is not directly used but needs to be kept alive to
 * support the output generated by `superimpose_nulls(column_view)` and
 * `superimpose_nulls(table_view)`.
 */
struct temporary_nullable_data {
  /**
   * @brief Store the newly generated null masks (if any).
   */
  std::vector<rmm::device_buffer> new_null_masks;

  /**
   * @brief Store the newly generated columns with new null masks (if any).
   */
  std::vector<std::unique_ptr<column>> new_columns;

  /**
   * @brief Take over the content of another instance and append it into the internal data.
   *
   * @param other The other instance to take over its content
   */
  void emplace_back(temporary_nullable_data&& other);
};

/**
 * @brief Flatten the children of the input columns into a vector where the i'th element
 * is a vector of column_views representing the i'th child from each input column_view.
 *
 * @code{.pseudo}
 * s1 = [ col0 : {0, 1}
 *        col1 : {2, 3, 4, 5, 6}
 *        col2 : {"abc", "def", "ghi"} ]
 *
 * s2 = [ col0 : {7, 8}
 *        col1 : {-4, -5, -6}
 *        col2 : {"uvw", "xyz"} ]
 *
 * e = extract_ordered_struct_children({s1, s2})
 *
 * e is now [ {{0, 1}, {7, 8}}
 *            {{2, 3, 4, 5, 6}, {-4, -5, -6}}
 *            {{"abc", "def", "ghi"}, {"uvw", "xyz"} ]
 * @endcode
 *
 * @param columns Vector of structs columns to extract from.
 * @return New column with concatenated results.
 */
std::vector<std::vector<column_view>> extract_ordered_struct_children(
  host_span<column_view const> struct_cols, rmm::cuda_stream_view stream);

/**
 * @brief Check whether the specified column is of type LIST, or any LISTs in its descendent
 * columns.
 * @param col column to check for lists.
 * @return true if the column or any of it's children is a list, false otherwise.
 */
bool is_or_has_nested_lists(cudf::column_view const& col);

/**
 * @brief Result of `flatten_nested_columns()`, where all `STRUCT` columns are replaced with
 * their non-nested member columns, and `BOOL8` columns for their null masks.
 *
 * `flatten_nested_columns()` produces a "flattened" table_view with all `STRUCT` columns
 * replaced with their child column_views, preceded by their null masks.
 * All newly allocated columns and device_buffers that back the returned table_view
 * are also encapsulated in `flatten_result`.
 *
 * Objects of `flatten_result` need to kept alive while its table_view is accessed.
 */
class flattened_table {
 public:
  /**
   * @brief Constructor, to be used from `flatten_nested_columns()`.
   *
   * @param flattened_columns_ table_view resulting from `flatten_nested_columns()`
   * @param orders_ Per-column ordering of the table_view
   * @param null_orders_ Per-column null_order of the table_view
   * @param columns_ Newly allocated columns to back the table_view
   * @param nullable_data_ Newly generated temporary data that needs to be kept alive
   */
  flattened_table(table_view flattened_columns_,
                  std::vector<order> const& orders_,
                  std::vector<null_order> const& null_orders_,
                  std::vector<std::unique_ptr<column>>&& columns_,
                  temporary_nullable_data&& nullable_data_)
    : _flattened_columns{std::move(flattened_columns_)},
      _orders{orders_},
      _null_orders{null_orders_},
      _columns{std::move(columns_)},
      _nullable_data{std::move(nullable_data_)}
  {
  }

  flattened_table() = default;

  /**
   * @brief Getter for the flattened columns, as a `table_view`.
   */
  [[nodiscard]] table_view flattened_columns() const { return _flattened_columns; }

  /**
   * @brief Getter for the cudf::order of the table_view's columns.
   */
  [[nodiscard]] std::vector<order> orders() const { return _orders; }

  /**
   * @brief Getter for the cudf::null_order of the table_view's columns.
   */
  [[nodiscard]] std::vector<null_order> null_orders() const { return _null_orders; }

  /**
   * @brief Conversion to `table_view`, to fetch flattened columns.
   */
  operator table_view() const { return flattened_columns(); }

 private:
  table_view _flattened_columns;
  std::vector<order> _orders;
  std::vector<null_order> _null_orders;
  std::vector<std::unique_ptr<column>> _columns;
  temporary_nullable_data _nullable_data;
};

/**
 * @brief Flatten table with struct columns to table with constituent columns of struct columns.
 *
 * If a table does not have struct columns, same input arguments are returned.
 *
 * @param input input table to be flattened
 * @param column_order column order for input table
 * @param null_precedence null order for input table
 * @param nullability force output to have nullability columns even if input columns are all valid
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate new device memory
 * @return A pointer of type `flattened_table` containing flattened columns, flattened column
 *         orders, flattened null precedence, alongside the supporting columns and device_buffers
 *         for the flattened table.
 */
[[nodiscard]] std::unique_ptr<cudf::structs::detail::flattened_table> flatten_nested_columns(
  table_view const& input,
  std::vector<cudf::order> const& column_order,
  std::vector<cudf::null_order> const& null_precedence,
  cudf::structs::detail::column_nullability nullability,
  rmm::cuda_stream_view stream,
  rmm::device_async_resource_ref mr);

/**
 * @brief Superimpose nulls from a given null mask into the input column, using bitwise AND.
 *
 * This function will recurse through all struct descendants. It is expected that the size of
 * the given null mask in bits is the same as size of the input column.
 *
 * Any null strings/lists in the input (if any) will also be sanitized to make sure nulls in the
 * output always have their sizes equal to 0.
 *
 * @param null_mask Null mask to be applied to the input column
 * @param null_count Null count in the given null mask
 * @param input Column to apply the null mask to
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate new device memory
 * @return A new column with potentially new null mask
 */
[[nodiscard]] std::unique_ptr<cudf::column> superimpose_nulls(bitmask_type const* null_mask,
                                                              cudf::size_type null_count,
                                                              std::unique_ptr<cudf::column>&& input,
                                                              rmm::cuda_stream_view stream,
                                                              rmm::device_async_resource_ref mr);

/**
 * @brief Push down nulls from the given input column into its children columns, using bitwise AND.
 *
 * This function constructs a new column_view instance equivalent to the input column_view,
 * with possibly new child column_view, all with possibly new null mask reflecting null rows from
 * the parent column:
 * 1. If the specified column is not STRUCT, the column_view is returned unmodified, with no
 *    temporary data allocated.
 * 2. If the column is STRUCT, the null masks of the parent and child are bitwise-ANDed, and a
 *    modified column_view is returned. This applies recursively.
 *
 * Any null strings/lists in the input (if any) will also be sanitized to make sure nulls in the
 * output always have their sizes equal to 0.
 *
 * @param input The input (possibly STRUCT) column whose nulls need to be pushed to its children
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate new device memory
 * @return A pair of:
 *         1. column_view with nulls pushed down to child columns, as appropriate.
 *         2. An instance of `temporary_nullable_data` holding the temporary data that needs
 *         to be kept alive.
 */
[[nodiscard]] std::pair<column_view, temporary_nullable_data> push_down_nulls(
  column_view const& input, rmm::cuda_stream_view stream, rmm::device_async_resource_ref mr);

/**
 * @brief Push down nulls from columns of the input table into their children columns, using
 * bitwise AND.
 *
 * This function constructs a new table_view containing new column_view instances equivalent to
 * the corresponding column_views in the input table. Each column_view might contain possibly new
 * child column_views, all with possibly new null mask reflecting null rows from the parent column:
 * 1. If the specified column is not STRUCT, the column_view is returned unmodified, with no
 *    temporary data allocated.
 * 2. If the column is STRUCT, the null masks of the parent and child are bitwise-ANDed, and a
 *    modified column_view is returned. This applies recursively.
 *
 * Any null strings/lists in the input (if any) will also be sanitized to make sure nulls in the
 * output always have their sizes equal to 0.
 *
 * @param input The table_view of (possibly STRUCT) columns whose nulls need to be pushed to their
 *        children
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate new device memory
 * @return A pair of:
 *         1. table_view of columns with nulls pushed down to child columns, as appropriate.
 *         2. An instance of `temporary_nullable_data` holding the temporary data that needs
 *         to be kept alive.
 */
[[nodiscard]] std::pair<table_view, temporary_nullable_data> push_down_nulls(
  table_view const& input, rmm::cuda_stream_view stream, rmm::device_async_resource_ref mr);

/**
 * @brief Checks if a column or any of its children is a struct column with structs that are null.
 *
 * This function searches for structs that are null -- differentiating between structs that are null
 * and structs containing null values. Null structs add a column to the result of the flatten column
 * utility and necessitates column_nullability::FORCE when flattening the column for comparison
 * operations.
 *
 * @param col Column to check for null structs
 * @return A boolean indicating if the column is or contains a struct column that contains a null
 * struct.
 */
bool contains_null_structs(column_view const& col);

}  // namespace cudf::structs::detail
