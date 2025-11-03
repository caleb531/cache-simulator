#!/usr/bin/env python3

from cachesimulator.table import Table


def test_init_default():
    """
    should initialize table with required parameters and default values
    """
    table = Table(num_cols=5, width=78)
    assert table.num_cols == 5
    assert table.width == 78
    assert table.alignment == "left"
    assert table.title is None
    assert table.header == []
    assert table.rows == []


def test_init_optional():
    """should initialize table with optional parameters if supplied"""
    table = Table(num_cols=5, width=78, alignment="right", title="Cache")
    assert table.num_cols == 5
    assert table.width == 78
    assert table.alignment == "right"
    assert table.title == "Cache"


def test_get_separator():
    """should return the correct ASCII separator string"""
    table = Table(num_cols=5, width=78)
    assert table.get_separator() == "-" * 78


def test_str_title():
    """should correctly display title"""
    table = Table(num_cols=5, width=12, title="Cache")
    expected_text = "".join(("Cache".center(12), "\n", ("-" * 12)))
    assert expected_text in str(table)


def test_str_no_title():
    """should not display title if not originally supplied"""
    table = Table(num_cols=5, width=12)
    assert str(table).strip() == ""


def _assert_table_alignment(alignment, just):
    table_width = 16
    num_cols = 2
    col_width = table_width // num_cols
    table = Table(num_cols=num_cols, width=table_width, alignment=alignment)
    table.header = ["First", "Last"]
    table.rows.append(["Bob", "Smith"])
    table.rows.append(["John", "Earl"])
    assert str(table) == "{}{}\n{}\n{}{}\n{}{}".format(
        just("First", col_width),
        just("Last", col_width),
        "-" * table_width,
        just("Bob", col_width),
        just("Smith", col_width),
        just("John", col_width),
        just("Earl", col_width),
    )


def test_str_align_left():
    """should correctly display table when left-aligned"""
    _assert_table_alignment(alignment="left", just=str.ljust)


def test_str_align_center():
    """should correctly display table when center-aligned"""
    _assert_table_alignment(alignment="center", just=str.center)


def test_str_align_right():
    """should correctly display table when right-aligned"""
    _assert_table_alignment(alignment="right", just=str.rjust)
