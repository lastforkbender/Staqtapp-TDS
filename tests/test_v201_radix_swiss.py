from __future__ import annotations

import threading

import pytest

from staqtapp_tds import TDSFileSystem, TDSDirectory, ZoneCapability, RadixDirectoryRouter
from staqtapp_tds.index import EntryIndex


def test_radix_router_basic_prefixes_and_delete():
    r = RadixDirectoryRouter[int]()
    r.insert('alpha', 1)
    r.insert('alphabet', 2)
    r.insert('alpine', 3)
    r.insert('beta', 4)
    assert r.get('alpha') == 1
    assert r.get('alphabet') == 2
    assert r.get('alpine') == 3
    assert r.get('beta') == 4
    assert r.get('missing') is None
    assert sorted(r.keys()) == ['alpha', 'alphabet', 'alpine', 'beta']
    assert r.delete('alphabet') == 2
    assert r.get('alphabet') is None
    assert r.get('alpha') == 1


def test_filesystem_radix_resolve_and_capability():
    fs = TDSFileSystem()
    node = fs.makedirs('/models/language/tokenizers')
    node.write_text('notes.md', 'radix path works')
    assert fs.resolve('/models/language/tokenizers').read_text('notes.md') == 'radix path works'
    assert fs.resolve_radix('/models/language/tokenizers').read_text('notes.md') == 'radix path works'
    assert fs.root.capabilities.supports(ZoneCapability.RADIX_ROUTER)


def test_entryindex_native_or_fallback_swiss_stats():
    idx = EntryIndex(backend='auto')
    for i in range(500):
        idx.put(f'key_{i:04d}', {'i': i})
    for i in range(500):
        assert idx.get_handle(f'key_{i:04d}') > 0
        assert idx.get(f'key_{i:04d}') == {'i': i}
    stats = idx.stats()
    assert stats.size == 500
    # Native backend is optional, but when present it must advertise Swiss/GIL status.
    if 'native' in idx.backend_name:
        raw = idx._impl._index.stats()
        assert raw['gil_released_get_handle'] is True
        assert raw['swiss_control_bytes'] is True
        assert raw['probing'] == 'triangular'


def test_native_entryindex_concurrent_read_safety_if_available():
    try:
        idx = EntryIndex(backend='native')
    except RuntimeError:
        pytest.skip('native backend not built on this interpreter')
    for i in range(1000):
        idx.put(f'item_{i}', i)
    errors = []
    def worker(offset: int):
        try:
            for j in range(2500):
                k = f'item_{(j + offset) % 1000}'
                if idx.get_handle(k) < 0 or k not in idx:
                    errors.append(k)
        except Exception as exc:  # pragma: no cover
            errors.append(repr(exc))
    threads = [threading.Thread(target=worker, args=(n * 17,)) for n in range(8)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert errors == []


def test_radix_does_not_change_variable_and_text_semantics():
    fs = TDSFileSystem()
    d = fs.makedirs('/vars/session')
    assert d.addvar('my_var', {'a': 1}).ok
    assert not d.addvar('my_var', {'b': 2}).ok
    assert d.stalkvar('~my_var', {'b': 2}).ok
    assert d.loadvar('my_var_0001') == {'a': 1, 'b': 2}
    assert d.write_text('note.txt', 'hello').ok
    assert not d.write_text('note.txt', 'duplicate').ok
