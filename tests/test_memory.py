"""Tests for ShortTermMemory and LongTermMemory."""
from __future__ import annotations

import pytest

from src.memory.short_term import ShortTermMemory
from src.memory.long_term import LongTermMemory


@pytest.mark.asyncio
async def test_short_term_store_retrieve():
    mem = ShortTermMemory()
    await mem.store("key1", {"val": 1})
    result = await mem.retrieve("key1")
    assert result == {"val": 1}


@pytest.mark.asyncio
async def test_short_term_eviction():
    mem = ShortTermMemory(max_size=2)
    await mem.store("a", 1)
    await mem.store("b", 2)
    await mem.store("c", 3)  # Should evict "a"
    assert await mem.retrieve("a") is None
    assert await mem.retrieve("c") == 3


@pytest.mark.asyncio
async def test_short_term_delete():
    mem = ShortTermMemory()
    await mem.store("x", 99)
    await mem.delete("x")
    assert await mem.exists("x") is False


@pytest.mark.asyncio
async def test_short_term_clear():
    mem = ShortTermMemory()
    await mem.store("a", 1)
    await mem.store("b", 2)
    await mem.clear()
    assert await mem.exists("a") is False


@pytest.mark.asyncio
async def test_long_term_store_retrieve(tmp_path):
    path = str(tmp_path / "lt.json")
    mem = LongTermMemory(storage_path=path)
    await mem.store("greeting", "hello")
    result = await mem.retrieve("greeting")
    assert result == "hello"


@pytest.mark.asyncio
async def test_long_term_delete(tmp_path):
    path = str(tmp_path / "lt.json")
    mem = LongTermMemory(storage_path=path)
    await mem.store("k", "v")
    await mem.delete("k")
    assert await mem.exists("k") is False


@pytest.mark.asyncio
async def test_long_term_clear(tmp_path):
    path = str(tmp_path / "lt.json")
    mem = LongTermMemory(storage_path=path)
    await mem.store("a", 1)
    await mem.clear()
    assert await mem.exists("a") is False
