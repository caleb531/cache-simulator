#!/usr/bin/env python3

import copy

from cachesimulator.cache import Cache


def reset_state():
    cache = Cache(
        {
            "010": [
                {"tag": "1000"},
                {"tag": "1100"},
                {"tag": "1101"},
                {"tag": "1110"},
            ]
        }
    )
    recently_used_addrs = [("100", "1100"), ("010", "1101"), ("010", "1110")]
    new_entry = {"tag": "1111"}
    return cache, recently_used_addrs, new_entry


def test_empty_set():
    """set_block should add new block if index set is empty"""
    cache, _, new_entry = reset_state()
    cache["010"][:] = []
    cache.recently_used_addrs = []
    cache.set_block(
        replacement_policy="lru",
        num_blocks_per_set=4,
        addr_index="010",
        new_entry=new_entry,
    )
    assert cache == {"010": [{"tag": "1111"}]}


def test_lru_replacement():
    """set_block should perform LRU replacement as needed"""
    cache, recently_used_addrs, new_entry = reset_state()
    cache.recently_used_addrs = recently_used_addrs
    cache.set_block(
        replacement_policy="lru",
        num_blocks_per_set=4,
        addr_index="010",
        new_entry=new_entry,
    )
    assert cache == {
        "010": [
            {"tag": "1000"},
            {"tag": "1100"},
            {"tag": "1111"},
            {"tag": "1110"},
        ]
    }


def test_mru_replacement():
    """set_block should optionally perform MRU replacement as needed"""
    cache, recently_used_addrs, new_entry = reset_state()
    cache.recently_used_addrs = recently_used_addrs
    cache.set_block(
        replacement_policy="mru",
        num_blocks_per_set=4,
        addr_index="010",
        new_entry=new_entry,
    )
    assert cache == {
        "010": [
            {"tag": "1000"},
            {"tag": "1100"},
            {"tag": "1101"},
            {"tag": "1111"},
        ]
    }


def test_no_replacement():
    """set_block should not perform replacement if there are no recents"""
    cache, _, new_entry = reset_state()
    original_cache = copy.deepcopy(cache)
    cache.recently_used_addrs = []
    cache.set_block(
        replacement_policy="lru",
        num_blocks_per_set=4,
        addr_index="010",
        new_entry=new_entry,
    )
    assert cache is not original_cache
    assert cache == original_cache
