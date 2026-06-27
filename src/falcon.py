#  /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
#  \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\
#      / FBK / PY MODULE ADV-SIGNATURE / / PYQT5 APP /

import sys
import os
import json
import math
import hashlib
import base64
import time
import gzip
import shutil
import tempfile
import copy
import builtins
import numpy as np
import networkx as nx
import scipy.stats
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from PyQt5 import QtWidgets, QtCore, QtGui
import tokenize, io, ast, token as tokenmod
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

PY_KEYWORDS: frozenset = frozenset({
    "def", "class", "return", "if", "elif", "else", "for", "while",
    "try", "except", "finally", "with", "as", "import", "from", "pass",
    "break", "continue", "raise", "yield", "del", "global", "nonlocal",
    "assert", "async", "await", "lambda", "in", "not", "and", "or",
    "is", "True", "False", "None", "match", "case", "type",})
_BUILTIN_NAMES: frozenset = frozenset(dir(builtins))

DARK_QSS = """
QWidget { background:#0e0e0e; color:#E2E2E2; font-family:'Segoe UI',sans-serif;}
QLineEdit, QTextEdit, QPlainTextEdit {
  background:#131313; border:1px solid #252525; border-radius:5px; padding:5px;}
QPushButton {
  background:#161616; border:1px solid #2c2c2c; border-radius:7px; padding:7px 11px;}
QPushButton:hover { background:#202020;}
QPushButton:pressed { background:#282828;}
QPushButton:disabled { color:#444; border-color:#1a1a1a;}
QLabel { color:#E2E2E2;}
QGroupBox { border:1px solid #252525; border-radius:9px; margin-top:10px;}
QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 6px; color:#aaa; }
QProgressBar { border:1px solid #252525; border-radius:5px; background:#131313; text-align:center;}
QProgressBar::chunk { background:#4C78A8; border-radius:4px;}
QTableWidget { background:#131313; border:1px solid #252525; gridline-color:#1e1e1e;}
QHeaderView::section { background:#111; padding:5px; border:1px solid #252525;}
QComboBox { background:#131313; border:1px solid #252525; border-radius:5px; padding:4px;}
QComboBox::drop-down { border:none;}
QListWidget { background:#131313; border:1px solid #252525;}
QTabWidget::pane { border:1px solid #252525;}
QTabBar::tab { background:#161616; border:1px solid #252525; padding:5px 12px;
                   border-top-left-radius:5px; border-top-right-radius:5px;}
QTabBar::tab:selected { background:#1e1e1e;}
QScrollBar:vertical { background:#0e0e0e; width:8px;}
QScrollBar::handle:vertical { background:#2a2a2a; border-radius:4px;}"""

def sha256_bytes(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def merkle_root(hex_hashes: List[str]) -> str:
    if not hex_hashes:
        return sha256_hex(b"")
    layer = [bytes.fromhex(h) for h in hex_hashes]
    while len(layer) > 1:
        if len(layer) % 2 == 1: layer.append(layer[-1])
        layer = [sha256_bytes(layer[i] + layer[i + 1]) for i in range(0, len(layer), 2)]
    return layer[0].hex()

def literal_bucket(lit: str) -> str:
    if lit is None:
        return "<none>"
    s = lit.strip()
    if not s:
        return "<empty>"
    try:
        ast.literal_eval(s)
        if s[0].isdigit() or (len(s) > 1 and s[0] in "+-" and s[1].isdigit()):
            return "<num>"
    except Exception:
        pass
    if re_bytes(s):
        return "<bytes>"
    if re_str(s):
        return "<str>"
    return "<lit>"

def re_bytes(s: str) -> bool:
    return s[:2].lower() in ("b'", 'b"', "rb", "br") or s[:3].lower() in ("b'''", 'b"""')

def re_str(s: str) -> bool:
    prefixes = ("'", '"', "f'", 'f"', "r'", 'r"', "u'", 'u"', "f'''", 'f"""', "'''", '"""')
    return any(s.startswith(p) for p in prefixes)

class AlphaRenameCanonicalizer(ast.NodeTransformer):

    def __init__(self):
        super().__init__()
        self._scope_stack: List[Dict[str, str]] = []; self._cnt_stack: List[int] = []

    def _enter(self):
        self._scope_stack.append({}); self._cnt_stack.append(0)

    def _exit(self):
        self._scope_stack.pop(); self._cnt_stack.pop()

    def _canon(self, name: str) -> str:
        for scope in reversed(self._scope_stack):
            if name in scope:
                return scope[name]
        if not self._scope_stack: self._enter()
        scope = self._scope_stack[-1]; cnt = self._cnt_stack[-1]
        self._cnt_stack[-1] += 1; canon = f"v{cnt}"; scope[name] = canon
        return canon

    def _rename_args(self, args: ast.arguments):
        for a in args.posonlyargs + args.args + args.kwonlyargs:
            a.arg = self._canon(a.arg)
        if args.vararg: args.vararg.arg = self._canon(args.vararg.arg)
        if args.kwarg: args.kwarg.arg = self._canon(args.kwarg.arg)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._enter(); self._rename_args(node.args)
        self.generic_visit(node); self._exit()
        return node

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self._enter(); self.generic_visit(node); self._exit()
        return node

    def visit_Lambda(self, node: ast.Lambda):
        self._enter(); self._rename_args(node.args); self.generic_visit(node); self._exit()
        return node

    def visit_Name(self, node: ast.Name):
        if node.id in PY_KEYWORDS or node.id in _BUILTIN_NAMES:
            return node
        node.id = self._canon(node.id)
        return node

def ast_to_canonical_tokens(tree: ast.AST) -> List[str]:
    d = ast.dump(tree, include_attributes=False)
    out, cur = [], []
    for ch in d:
        if ch in "(),[]{}":
            if cur:
                out.append("".join(cur)); cur = []
            out.append(ch)
        elif ch.isspace():
            continue
        else: cur.append(ch)
    if cur: out.append("".join(cur))
    return out

def normalize_source(src: str) -> Tuple[str, List[str], ast.AST]:
    try:
        raw_tree = ast.parse(src); can = AlphaRenameCanonicalizer()
        tree = can.visit(raw_tree); ast.fix_missing_locations(tree)
        tokens = ast_to_canonical_tokens(tree)
        seed = sha256_hex(canonical_json({"ast": ast.dump(tree, include_attributes=False)}))
        return seed, tokens, tree
    except Exception:
        try:
            toks_raw = []
            g = tokenize.generate_tokens(io.StringIO(src).readline)
            for tok in g:
                tn = tokenmod.tok_name.get(tok.type, "?")
                if tn in ("ENCODING", "NL", "NEWLINE", "INDENT", "DEDENT", "COMMENT", "ENDMARKER"):
                    continue
                val = tok.string
                if tn == "STRING": val = "<str>"
                elif tn == "NUMBER": val = "<num>"
                toks_raw.append(val)
            seed = sha256_hex(canonical_json({"fb": toks_raw[:2000]}))
            dummy = ast.parse("")
            return seed, toks_raw, dummy
        except Exception:
            seed = sha256_hex(src.encode())
            return seed, list(src.split()), ast.parse("")

def extract_basic_blocks(tree: ast.AST) -> List[Dict]:
    blocks = []; block_id = 0

    def process_body(stmts: List[ast.stmt], kind: str, parent_name: str = ""):
        nonlocal block_id
        if not stmts:
            return
        try:
            mod = ast.Module(body=list(stmts), type_ignores=[])
            can = AlphaRenameCanonicalizer(); mod2 = can.visit(mod)
            ast.fix_missing_locations(mod2); toks = ast_to_canonical_tokens(mod2)
        except Exception:
            toks = []
        sha = sha256_hex(canonical_json({"block": toks}))
        lineno = getattr(stmts[0], "lineno", 0) if stmts else 0
        blocks.append({"block_id": block_id, "kind": kind, "parent": parent_name, "sha": sha, "tokens": toks[:400], "lineno": lineno, "stmt_count": len(stmts),})
        block_id += 1

    class Visitor(ast.NodeVisitor):
        def visit_Module(self, node):
            process_body(node.body, "module"); self.generic_visit(node)

        def visit_FunctionDef(self, node):
            process_body(node.body, "funcbody", node.name)
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                    if hasattr(child, "body") and child.body:
                        process_body(child.body, f"branch:{type(child).__name__}", node.name)
                    if hasattr(child, "orelse") and child.orelse:
                        process_body(child.orelse, f"else:{type(child).__name__}", node.name)
                elif isinstance(child, ast.Try):
                    process_body(child.body, "try_body", node.name)
                    process_body(child.finalbody if hasattr(child, "finalbody") else [], "finally", node.name)
                    for handler in child.handlers: process_body(handler.body, "except", node.name)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            self.visit_FunctionDef(node)

        def visit_ClassDef(self, node):
            process_body(node.body, "classbody", node.name); self.generic_visit(node)

    try:
        Visitor().visit(tree)
    except Exception:
        pass
    return blocks

def build_ast_graph(node: ast.AST) -> nx.DiGraph:
    G = nx.DiGraph()

    def add(n, parent=None):
        nid = id(n); tp = type(n).__name__
        if isinstance(n, ast.Constant): label = f"Const:{type(n.value).__name__}"
        elif isinstance(n, (ast.Name, ast.arg)): label = "VarRef"
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)): label = "FuncDef"
        elif isinstance(n, ast.ClassDef): label = "ClassDef"
        elif isinstance(n, ast.Attribute): label = "Attr"
        else: label = tp
        G.add_node(nid, label=label)
        if parent is not None: G.add_edge(parent, nid)
        for child in ast.iter_child_nodes(n): add(child, nid)
    add(node)
    return G

def wl_hash(node: ast.AST, iterations: int = 4) -> str:
    try:
        G = build_ast_graph(node)
        if len(G) == 0:
            return sha256_hex(b"empty")
        return nx.weisfeiler_lehman_graph_hash(G, node_attr="label", iterations=iterations)
    except Exception:
        return sha256_hex(ast.dump(node, include_attributes=False).encode())

def wl_subtree_fingerprints(tree: ast.AST, limit: int = 400) -> List[Dict]:
    fps = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fps.append({"kind": "func", "name": n.name, "wl_hash": wl_hash(n), "lineno": getattr(n, "lineno", 0),})
        elif isinstance(n, ast.ClassDef):
            fps.append({"kind": "class", "name": n.name, "wl_hash": wl_hash(n), "lineno": getattr(n, "lineno", 0),})
    fps.append({"kind": "module", "name": "__module__", "wl_hash": wl_hash(tree), "lineno": 0})
    return fps[:limit]

_MINHASH_N = 128

def _minhash_coeff():
    rng = np.random.RandomState(0xDEADBEEF)
    a = rng.randint(1, 2**31, size=_MINHASH_N, dtype=np.int64)
    b = rng.randint(0, 2**31, size=_MINHASH_N, dtype=np.int64)
    return a, b

_MH_A, _MH_B = _minhash_coeff()
_MH_P = (1 << 31) - 1

def minhash_sig(shingles: List[str]) -> np.ndarray:
    if not shingles:
        return np.full(_MINHASH_N, _MH_P, dtype=np.int64)
    sig = np.full(_MINHASH_N, _MH_P, dtype=np.int64)
    for s in shingles:
        h = int(hashlib.md5(s.encode(), usedforsecurity=False).hexdigest(), 16) % _MH_P
        vals = (_MH_A * h + _MH_B) % _MH_P; sig = np.minimum(sig, vals)
    return sig

def minhash_jaccard(s1: np.ndarray, s2: np.ndarray) -> float:
    return float(np.sum(s1 == s2)) / _MINHASH_N

def token_shingles(tokens: List[str], k: int = 5) -> List[str]:
    if len(tokens) < k: tokens = tokens + ["<pad>"] * (k - len(tokens))
    return [" ".join(tokens[i: i + k]) for i in range(len(tokens) - k + 1)]

def sw_align(a: List[str], b: List[str],match: float = 1.0, mismatch: float = -0.2, gap: float = -0.3) -> Tuple[float, Tuple[int, int, int, int]]:
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return 0.0, (0, 0, 0, 0)
    b_arr = np.array(b)
    dp_prev = np.zeros(m + 1, dtype=np.float32)
    dp_curr = np.zeros(m + 1, dtype=np.float32)
    ptr_mat = np.zeros((n + 1, m + 1), dtype=np.uint8)
    score_mat = np.zeros((n + 1, m + 1), dtype=np.float32)
    best = 0.0; best_i, best_j = 0, 0
    for i in range(1, n + 1):
        dp_curr[:] = 0.0
        match_row = np.where(b_arr == a[i - 1], match, mismatch)
        for j in range(1, m + 1):
            diag = dp_prev[j - 1] + match_row[j - 1]; up = dp_prev[j] + gap
            left = dp_curr[j - 1] + gap; val = max(0.0, float(diag), float(up), float(left))
            dp_curr[j] = val; score_mat[i, j] = val
            if val > best:
                best = val; best_i = i; best_j = j
            if val == 0.0: ptr_mat[i, j] = 0
            elif val == diag: ptr_mat[i, j] = 1
            elif val == up: ptr_mat[i, j] = 2
            else: ptr_mat[i, j] = 3
        dp_prev, dp_curr = dp_curr, dp_prev
    i2, j2 = best_i, best_j
    a_end, b_end = i2, j2
    while i2 > 0 and j2 > 0 and score_mat[i2, j2] > 0:
        p = ptr_mat[i2, j2]
        if p == 1: i2 -= 1; j2 -= 1
        elif p == 2: i2 -= 1
        elif p == 3: j2 -= 1
        else:
            break
    a_start, b_start = i2, j2
    span_len = 0.5 * (abs(a_end - a_start) + abs(b_end - b_start))
    norm = min(1.0, best / max(1.0, span_len))
    return norm, (a_start, a_end, b_start, b_end)

@dataclass
class ModuleEvidence:
    file_sha256: str
    norm_seed: str
    tokens: List[str]
    func_blocks: List[Dict]
    basic_blocks: List[Dict]
    stmt_fingerprints: List[Dict]
    wl_fingerprints: List[Dict]
    minhash_sigs: Dict[int, Any]
    merkle_leaf_hashes: List[str]

def build_module_evidence(py_path: str, limit_funcs: int = 120) -> ModuleEvidence:
    src = open(py_path, "r", encoding="utf-8", errors="replace").read()
    file_sha = sha256_hex(src.encode("utf-8"))
    norm_seed, norm_tokens, canon_tree = normalize_source(src)
    try:
        raw_tree = ast.parse(src)
    except Exception:
        raw_tree = ast.Module(body=[], type_ignores=[])
    basic_blocks = extract_basic_blocks(raw_tree)
    wl_fps = wl_subtree_fingerprints(raw_tree)
    func_blocks: List[Dict] = []
    func_nodes = [n for n in ast.walk(raw_tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    func_nodes = func_nodes[:limit_funcs]
    for fi, fn in enumerate(func_nodes):
        try:
            w = ast.Module(body=[fn], type_ignores=[]); can = AlphaRenameCanonicalizer()
            w2 = can.visit(w); ast.fix_missing_locations(w2); toks = ast_to_canonical_tokens(w2)
            sha = sha256_hex(canonical_json({"func": fn.name, "toks": toks}))
            func_blocks.append({"func_idx": fi, "name": fn.name, "sha": sha, "tokens": toks[:3000],})
        except Exception:
            continue
    stmt_nodes: List[ast.stmt] = []
    for n in ast.walk(raw_tree):
        if (isinstance(n, ast.stmt) and not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))): stmt_nodes.append(n)
    stmt_nodes = stmt_nodes[:6000]; stmt_fps: List[Dict] = []; leaf_hashes: List[str] = []
    for idx, s in enumerate(stmt_nodes):
        try:
            mod = ast.Module(body=[s], type_ignores=[]); can2 = AlphaRenameCanonicalizer(); mod2 = can2.visit(mod)
            ast.fix_missing_locations(mod2); toks = ast_to_canonical_tokens(mod2)
        except Exception:
            toks = []
        sha = sha256_hex(canonical_json({"stmt": toks}))
        stmt_fps.append({"stmt_idx": idx, "sha": sha, "tokens": toks[:2000]})
        leaf_hashes.append(sha)
    minhash_sigs: Dict[int, np.ndarray] = {}
    for blk in basic_blocks:
        sh = token_shingles(blk["tokens"], k=5); minhash_sigs[blk["block_id"]] = minhash_sig(sh)
        sha = blk["sha"]; leaf_hashes.append(sha)
    for fp in wl_fps: leaf_hashes.append(sha256_hex(fp["wl_hash"].encode()))
    for fb in func_blocks: leaf_hashes.append(fb["sha"])
    return ModuleEvidence(file_sha256=file_sha, norm_seed=norm_seed, tokens=norm_tokens, func_blocks=func_blocks, basic_blocks=basic_blocks, stmt_fingerprints=stmt_fps, wl_fingerprints=wl_fps, minhash_sigs=minhash_sigs, merkle_leaf_hashes=leaf_hashes,)

@dataclass
class SpanMatch:
    a_start: int
    a_end: int
    b_start: int
    b_end: int
    similarity: float
    method: str
    evidence_hash: str
    consensus_count: int = 1

def _wl_consensus(a_fps: List[Dict], b_fps: List[Dict]) -> List[Tuple[str, str, str, str]]:
    b_by_hash: Dict[str, List[Dict]] = {}
    for fp in b_fps: b_by_hash.setdefault(fp["wl_hash"], []).append(fp)
    matches = []
    for afp in a_fps:
        for bfp in b_by_hash.get(afp["wl_hash"], []): matches.append((afp["name"], bfp["name"], afp["kind"], afp["wl_hash"]))
    return matches

def compare_modules(a_ev: ModuleEvidence, b_ev: ModuleEvidence, k_shingle: int = 5, max_candidates: int = 60, consensus_threshold: int = 2) -> Tuple[Dict, List[str]]:
    wl_matches = _wl_consensus(a_ev.wl_fingerprints, b_ev.wl_fingerprints)
    wl_match_names_b = {m[1] for m in wl_matches}
    b_ids = list(a_ev.minhash_sigs.keys())
    a_blocks_map = {blk["block_id"]: blk for blk in a_ev.basic_blocks}
    b_blocks_map = {blk["block_id"]: blk for blk in b_ev.basic_blocks}
    a_sigs = {bid: a_ev.minhash_sigs[bid] for bid in a_ev.minhash_sigs}
    b_sigs = {bid: b_ev.minhash_sigs[bid] for bid in b_ev.minhash_sigs}
    candidates: List[Tuple[float, int, int]] = []
    b_sig_arr = np.stack(list(b_sigs.values()), axis=0) if b_sigs else np.zeros((0, _MINHASH_N), dtype=np.int64)
    b_sig_ids = list(b_sigs.keys())
    for a_bid, a_sig in a_sigs.items():
        if b_sig_arr.shape[0] == 0:
            break
        scores = np.sum(b_sig_arr == a_sig[None, :], axis=1) / _MINHASH_N
        top_k = min(4, len(scores)); top_idx = np.argsort(scores)[-top_k:][::-1]
        for idx in top_idx:
            s = float(scores[idx])
            if s > 0.05: candidates.append((s, a_bid, b_sig_ids[idx]))
    candidates.sort(reverse=True); candidates = candidates[:max_candidates]
    func_scores: List[float] = []; span_matches: List[SpanMatch] = []
    a_funcs = {fb["name"]: fb for fb in a_ev.func_blocks}; b_funcs = {fb["name"]: fb for fb in b_ev.func_blocks}
    for fname in set(a_funcs) & set(b_funcs):
        at = a_funcs[fname]["tokens"]; bt = b_funcs[fname]["tokens"]
        score, (as_, ae, bs, be) = sw_align(at, bt)
        func_scores.append(score)
        ev = {"method": "func_sw", "func": fname, "as": as_, "ae": ae, "bs": bs, "be": be, "score": score}
        eh = sha256_hex(canonical_json(ev))
        wl_agree = fname in {m[0] for m in wl_matches} or fname in wl_match_names_b
        cc = 2 if wl_agree else 1
        span_matches.append(SpanMatch(as_, ae, bs, be, score, "func_sw", eh, cc))
    for a_name, b_name, kind, _wh in wl_matches:
        if a_name in a_funcs and b_name in b_funcs and a_name != b_name:
            at = a_funcs[a_name]["tokens"]; bt = b_funcs[b_name]["tokens"]
            score, (as_, ae, bs, be) = sw_align(at, bt)
            func_scores.append(score)
            ev = {"method": "wl_func_sw", "a_func": a_name, "b_func": b_name, "as": as_, "ae": ae, "bs": bs, "be": be, "score": score}
            eh = sha256_hex(canonical_json(ev))
            span_matches.append(SpanMatch(as_, ae, bs, be, score, "wl_func_sw", eh, 2))
    for mh_score, a_bid, b_bid in candidates[:30]:
        ab = a_blocks_map.get(a_bid); bb = b_blocks_map.get(b_bid)
        if ab is None or bb is None:
            continue
        score, (as_, ae, bs, be) = sw_align(ab["tokens"], bb["tokens"])
        func_scores.append(score)
        ev = {"method": "block_sw", "a_bid": a_bid, "b_bid": b_bid, "as": as_, "ae": ae, "bs": bs, "be": be, "score": score}
        eh = sha256_hex(canonical_json(ev))
        span_matches.append(SpanMatch(as_, ae, bs, be, score, "block_sw", eh, 1))
    span_matches.sort(key=lambda x: x.similarity, reverse=True)
    for i, sm in enumerate(span_matches):
        if sm.similarity < 0.15:
            continue
        for j in range(i + 1, len(span_matches)):
            other = span_matches[j]
            if other.method == sm.method:
                continue
            a_overlap = min(sm.a_end, other.a_end) - max(sm.a_start, other.a_start)
            b_overlap = min(sm.b_end, other.b_end) - max(sm.b_start, other.b_start)
            if a_overlap > 0 and b_overlap > 0:
                span_matches[i] = SpanMatch(sm.a_start, sm.a_end, sm.b_start, sm.b_end, sm.similarity, sm.method, sm.evidence_hash, sm.consensus_count + 1)
                break
    confirmed = [s for s in span_matches if s.consensus_count >= consensus_threshold or s.similarity > 0.7]
    all_spans = span_matches
    if func_scores:
        arr = np.array(func_scores, dtype=np.float32); max_sim = float(arr.max())
        mean_sim = float(arr.mean())
        hist, _ = np.histogram(arr, bins=10, range=(0, 1), density=True)
        p = hist / (hist.sum() + 1e-12); entropy = float(-(p * np.log2(p + 1e-12)).sum())
        temperature = float(1.0 - entropy / math.log2(len(hist) + 1e-12))
    else: max_sim = mean_sim = temperature = 0.0
    wl_summary = [{"a_name": m[0], "b_name": m[1], "kind": m[2], "wl_hash": m[3]} for m in wl_matches[:30]]
    evidence = {"module_a": {"file_sha256": a_ev.file_sha256, "norm_seed": a_ev.norm_seed},
                "module_b": {"file_sha256": b_ev.file_sha256, "norm_seed": b_ev.norm_seed},
                "scores": {"max_similarity": max_sim,
                           "mean_similarity": mean_sim,
                           "temperature": temperature,
                           "matched_span_count": len(confirmed),
                           "all_candidate_count": len(all_spans),
                           "wl_exact_matches": len(wl_matches),
                           "consensus_threshold": consensus_threshold,},
                "wl_matches": wl_summary,
                "top_spans": [{"a_span_start": s.a_start, "a_span_end": s.a_end,
                               "b_span_start": s.b_start, "b_span_end": s.b_end,
                               "similarity": s.similarity,
                               "method": s.method,
                               "consensus_count": s.consensus_count,
                               "evidence_hash": s.evidence_hash,} for s in confirmed[:30]],}
    leaf_hashes = [s.evidence_hash for s in confirmed[:30]]
    return evidence, leaf_hashes

def render_ogr(scores: Dict, wl_matches: List[Dict], out_png: str):
    fig = plt.figure(figsize=(9.0, 5.2), dpi=160, facecolor="#0d0d0d")
    gs = GridSpec(2, 3, figure=fig, hspace=0.55, wspace=0.45)
    dark = "#0d0d0d"; fg = "#E2E2E2"
    acc  = ["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756", "#72B7B2"]

    def styled(ax, title):
        ax.set_facecolor(dark); ax.set_title(title, color=fg, fontsize=8.5, pad=6)
        ax.tick_params(colors=fg, labelsize=7); ax.spines[:].set_color("#2a2a2a")
        ax.grid(axis="y", color="#2a2a2a", linewidth=0.7, alpha=0.8)

    ax1 = fig.add_subplot(gs[0, 0]); labels1 = ["MaxSim", "MeanSim", "Temp"]
    vals1   = [scores["max_similarity"], scores["mean_similarity"], scores["temperature"]]
    bars = ax1.bar(labels1, vals1, color=acc[:3], alpha=0.92); ax1.set_ylim(0, 1.1)
    for b in bars:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width() / 2, h + 0.03, f"{h:.2f}", ha="center", va="bottom", color=fg, fontsize=7.5)
    styled(ax1, "Similarity Metrics"); ax2 = fig.add_subplot(gs[0, 1]); sc = scores
    keys2 = ["Confirmed\nSpans", "All\nCandidates", "WL\nExact"]
    vals2 = [sc["matched_span_count"], sc["all_candidate_count"], sc["wl_exact_matches"]]
    bars2 = ax2.bar(keys2, vals2, color=acc[1:4], alpha=0.92)
    for b in bars2:
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width() / 2, h + 0.3, str(int(h)), ha="center", va="bottom", color=fg, fontsize=7.5)
    styled(ax2, "Span Counts")
    ax3 = fig.add_subplot(gs[0, 2], polar=True); ax3.set_facecolor(dark)
    cats  = ["MaxSim", "MeanSim", "Temp", "WL%", "Consensus%"]; n_cat = len(cats)
    angles = np.linspace(0, 2 * np.pi, n_cat, endpoint=False).tolist(); angles += angles[:1]
    wl_pct = min(1.0, sc["wl_exact_matches"] / max(1, sc["all_candidate_count"]))
    cons_pct = min(1.0, sc["matched_span_count"] / max(1, sc["all_candidate_count"]))
    radar_vals = [sc["max_similarity"], sc["mean_similarity"], sc["temperature"], wl_pct, cons_pct]
    radar_vals += radar_vals[:1]
    ax3.plot(angles, radar_vals, color=acc[0], linewidth=1.5)
    ax3.fill(angles, radar_vals, color=acc[0], alpha=0.22)
    ax3.set_xticks(angles[:-1])
    ax3.set_xticklabels(cats, color=fg, fontsize=6.5)
    ax3.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax3.set_yticklabels(["0.25", "0.5", "0.75", "1.0"], color="#888", fontsize=6)
    ax3.tick_params(colors=fg)
    ax3.set_title("Signature Radar", color=fg, fontsize=8.5, pad=12)
    ax3.spines["polar"].set_color("#2a2a2a")
    ax4 = fig.add_subplot(gs[1, 0])
    kind_counts: Dict[str, int] = {}
    for m in wl_matches: kind_counts[m.get("kind", "?")] = kind_counts.get(m.get("kind", "?"), 0) + 1
    if kind_counts:
        kk = list(kind_counts.keys()); kv = list(kind_counts.values())
        ax4.bar(kk, kv, color=acc[4], alpha=0.92)
        for xi, (k, v) in enumerate(zip(kk, kv)): ax4.text(xi, v + 0.1, str(v), ha="center", color=fg, fontsize=7)
    else: ax4.text(0.5, 0.5, "No WL matches", ha="center", va="center", color="#888", transform=ax4.transAxes)
    styled(ax4, "WL Match Kinds"); ax5 = fig.add_subplot(gs[1, 1])
    x = np.linspace(0, 1, 100)
    mu, sigma = scores["mean_similarity"], max(0.05, scores["temperature"] * 0.2 + 0.05)
    y = np.exp(-0.5 * ((x - mu) / sigma) ** 2)
    ax5.fill_between(x, y, color=acc[2], alpha=0.5)
    ax5.axvline(scores["max_similarity"], color=acc[0], linewidth=1.2, linestyle="--")
    ax5.set_xlim(0, 1); ax5.set_ylim(0, 1.1)
    styled(ax5, "Score Distribution (est.)")
    ax6 = fig.add_subplot(gs[1, 2])
    consensus_ratio = cons_pct
    theta = np.linspace(np.pi, 0, 300)
    ax6.plot(np.cos(theta), np.sin(theta), color="#333", linewidth=4, solid_capstyle="round")
    filled = int(consensus_ratio * 300)
    needle_color = acc[1] if consensus_ratio < 0.4 else (acc[2] if consensus_ratio < 0.75 else acc[4])
    ax6.plot(np.cos(theta[:filled]), np.sin(theta[:filled]), color=needle_color, linewidth=4, solid_capstyle="round")
    ax6.set_xlim(-1.2, 1.2); ax6.set_ylim(-0.2, 1.2)
    ax6.set_aspect("equal"); ax6.axis("off"); ax6.set_facecolor(dark)
    ax6.text(0, -0.1, f"Consensus\n{consensus_ratio:.0%}", ha="center", color=fg, fontsize=8, fontweight="bold")
    ax6.set_title("Consensus Gauge", color=fg, fontsize=8.5, pad=6)
    fig.patch.set_facecolor(dark); fig.savefig(out_png, bbox_inches="tight", facecolor=dark); plt.close(fig)

def load_or_create_ed25519_keys(private_path: str = "ed25519_private.pem", public_path: str  = "ed25519_public.pem") -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    if os.path.exists(private_path) and os.path.exists(public_path):
        try:
            priv_pem = open(private_path, "rb").read(); pub_pem = open(public_path,  "rb").read()
            priv = serialization.load_pem_private_key(priv_pem, password=None)
            pub = serialization.load_pem_public_key(pub_pem)
            return priv, pub
        except Exception:
            pass
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    open(private_path, "wb").write(priv.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    open(public_path, "wb").write(pub.public_bytes( serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    return priv, pub

def sign_ed25519(priv: Ed25519PrivateKey, blob: Dict) -> str:
    return base64.b64encode(priv.sign(canonical_json(blob))).decode("ascii")

def verify_ed25519(pub: Ed25519PublicKey, blob: Dict, sig_b64: str) -> bool:
    try:
        pub.verify(base64.b64decode(sig_b64), canonical_json(blob))
        return True
    except Exception:
        return False

class TinyMLP:
    IN_DIM = 16
    H1, H2, OUT_DIM = 32, 16, 8

    def __init__(self, seed: int = 42):
        rng = np.random.RandomState(seed); scale = 0.08
        self.W1 = (rng.randn(self.IN_DIM, self.H1) * scale).astype(np.float32)
        self.b1 = np.zeros(self.H1,  dtype=np.float32)
        self.W2 = (rng.randn(self.H1, self.H2) * scale).astype(np.float32)
        self.b2 = np.zeros(self.H2,  dtype=np.float32)
        self.W3 = (rng.randn(self.H2, self.OUT_DIM) * scale).astype(np.float32)
        self.b3 = np.zeros(self.OUT_DIM, dtype=np.float32)
        self.version = 0; self.update_history: List[Dict] = []

    @staticmethod
    def _relu(x):
        return np.maximum(0, x)
        
    @staticmethod
    def _sig(x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

    def forward(self, x: np.ndarray) -> np.ndarray:
        h1 = self._relu(x @ self.W1 + self.b1); h2 = self._relu(h1 @ self.W2 + self.b2)
        return self._sig(h2 @ self.W3 + self.b3)

    def update(self, features: List[float], lr: float = 0.008) -> np.ndarray:
        x  = np.array(features, dtype=np.float32)
        h1 = self._relu(x  @ self.W1 + self.b1)
        h2 = self._relu(h1 @ self.W2 + self.b2)
        out = self._sig(h2 @ self.W3 + self.b3)
        self.W1 += lr * 0.01 * np.outer(x,  h1); self.W1 *= 0.9999
        self.W2 += lr * 0.01 * np.outer(h1, h2); self.W2 *= 0.9999
        self.W3 += lr * 0.01 * np.outer(h2, out); self.W3 *= 0.9999
        self.version += 1; ts = int(time.time())
        self.update_history.append({"version": self.version, "ts": ts, "lr": lr, "norm": float(np.linalg.norm(out))})
        return out

    def to_dict(self) -> Dict:
        return {"version": self.version, "W1": self.W1.tolist(), "b1": self.b1.tolist(), "W2": self.W2.tolist(), "b2": self.b2.tolist(), "W3": self.W3.tolist(), "b3": self.b3.tolist(), "update_history": self.update_history[-50:]}

    @classmethod
    def from_dict(cls, d: Dict) -> "TinyMLP":
        m = cls.__new__(cls)
        m.W1 = np.array(d["W1"], dtype=np.float32)
        m.b1 = np.array(d["b1"], dtype=np.float32)
        m.W2 = np.array(d["W2"], dtype=np.float32)
        m.b2 = np.array(d["b2"], dtype=np.float32)
        m.W3 = np.array(d["W3"], dtype=np.float32)
        m.b3 = np.array(d["b3"], dtype=np.float32)
        m.version = d.get("version", 0)
        m.update_history = d.get("update_history", [])
        return m

class AeroEngine:

    def __init__(self):
        self.rho = 1.225
        self.mu = 1.81e-5
        self.c_L_max = 1.8
        self.c_D_base = 0.024
        self.AR_nom = 8.0
        self.version = 0
        self.update_log: List[Dict] = []

    def compute(self, max_sim: float, mean_sim: float, span_count: int, tok_len_mean: float, temperature: float) -> Dict:
        eps = 1e-9
        b = max(eps, max_sim * 100.0)
        V = max(eps, mean_sim * 50.0)
        c = max(eps, tok_len_mean / 10.0)
        k = max(eps, 1.0 - temperature)
        n = max(1, span_count)
        Re = self.rho * V * c / self.mu
        AR = b / c
        alpha = np.arctan(mean_sim)
        c_L = float(np.clip(2 * np.pi * np.sin(alpha) * (AR / (AR + 2)), 0, self.c_L_max))
        c_Di = c_L ** 2 / (np.pi * 0.85 * AR + eps)
        c_D = self.c_D_base + c_Di + k * 0.01
        LD = c_L / max(eps, c_D)
        q = 0.5 * self.rho * V ** 2
        c_p = float(1 - (V / max(eps, V + n)) ** 2)
        St = float((n * c) / max(eps, b))
        sig = np.array([float(np.tanh(Re / 1e6)), float(np.clip(AR / 20.0, 0, 1)), float(np.clip(c_L / self.c_L_max, 0, 1)), float(np.clip(c_D * 10, 0, 1)), float(np.clip(LD / 50.0, 0, 1)), float(np.clip(q / 5000, 0, 1)), float(np.clip(c_p, 0, 1)), float(np.clip(St * 2, 0, 1)),], dtype=np.float32)
        sig_hash = sha256_hex(sig.tobytes())
        return {"Re": float(Re), "AR": float(AR), "c_L": float(c_L), "c_D": float(c_D), "LD": float(LD), "q": float(q), "c_p": float(c_p), "St": float(St), "sig_vec": sig.tolist(), "sig_hash": sig_hash, "engine_version": self.version,}

    def apply_mlp_config(self, mlp_out: np.ndarray):
        o = np.clip(np.array(mlp_out, dtype=np.float32), 0, 1)
        self.rho = float(1.0 + o[0] * 0.5)
        self.c_L_max = float(1.5 + o[1] * 1.0)
        self.c_D_base = float(0.01 + o[2] * 0.04)
        self.AR_nom = float(4.0 + o[3] * 12.0)
        self.version += 1
        self.update_log.append({"version": self.version, "ts": int(time.time()), "mlp_out": o.tolist()})

    def to_dict(self) -> Dict:
        return {"version": self.version, "rho": self.rho, "mu": self.mu, "c_L_max": self.c_L_max, "c_D_base": self.c_D_base, "AR_nom": self.AR_nom, "update_log": self.update_log[-50:]}

    @classmethod
    def from_dict(cls, d: Dict) -> "AeroEngine":
        e = cls()
        e.version = d.get("version", 0)
        e.rho = d.get("rho", 1.225)
        e.mu = d.get("mu", 1.81e-5)
        e.c_L_max = d.get("c_L_max", 1.8)
        e.c_D_base = d.get("c_D_base", 0.024)
        e.AR_nom = d.get("AR_nom", 8.0)
        e.update_log = d.get("update_log", [])
        return e

CONFIG_DIR = "scanner_configs"
SNAPSHOT_DIR = "scanner_config_snapshots"
MLP_FILE = os.path.join(CONFIG_DIR, "mlp_config.json")
ENGINE_FILE = os.path.join(CONFIG_DIR, "aero_engine.json")
MANIFEST_FILE = os.path.join(CONFIG_DIR, "manifest.json")

def _ensure_dirs():
    os.makedirs(CONFIG_DIR, exist_ok=True); os.makedirs(SNAPSHOT_DIR, exist_ok=True)

def save_config_package(mlp: TinyMLP, engine: AeroEngine, label: str = "", module_sha: str = "", scan_ts: Optional[int] = None):
    _ensure_dirs(); ts = scan_ts or int(time.time()); label = label or f"snap_{ts}"
    json.dump(mlp.to_dict(), open(MLP_FILE, "w"), indent=2); json.dump(engine.to_dict(), open(ENGINE_FILE, "w"), indent=2)
    manifest = _load_manifest()
    snap_id = f"{ts}_{label}"; snap_name = f"{snap_id}.tar.gz"; snap_path = os.path.join(SNAPSHOT_DIR, snap_name)
    bundle = {"mlp": mlp.to_dict(), "engine": engine.to_dict(), "meta": {"label": label, "ts": ts, "module_sha": module_sha, "mlp_version": mlp.version, "engine_version": engine.version}}
    bundle_bytes = canonical_json(bundle)
    with gzip.open(snap_path, "wb") as gz: gz.write(bundle_bytes)
    manifest.append({"id": snap_id, "label": label, "ts": ts, "module_sha": module_sha, "file": snap_name, "mlp_v": mlp.version, "engine_v": engine.version})
    json.dump(manifest, open(MANIFEST_FILE, "w"), indent=2)
    return snap_id

def _load_manifest() -> List[Dict]:
    if os.path.exists(MANIFEST_FILE):
        try:
            return json.load(open(MANIFEST_FILE))
        except Exception:
            pass
    return []

def load_snapshot(snap_id: str) -> Tuple[TinyMLP, AeroEngine]:
    manifest = _load_manifest()
    for m in manifest:
        if m["id"] == snap_id:
            snap_path = os.path.join(SNAPSHOT_DIR, m["file"])
            with gzip.open(snap_path, "rb") as gz: bundle = json.loads(gz.read())
            return TinyMLP.from_dict(bundle["mlp"]), AeroEngine.from_dict(bundle["engine"])
    raise FileNotFoundError(f"Snapshot '{snap_id}' not found")

def load_current_config() -> Tuple[TinyMLP, AeroEngine]:
    _ensure_dirs()
    mlp = (TinyMLP.from_dict(json.load(open(MLP_FILE))) if os.path.exists(MLP_FILE) else TinyMLP())
    eng = (AeroEngine.from_dict(json.load(open(ENGINE_FILE))) if os.path.exists(ENGINE_FILE) else AeroEngine())
    return mlp, eng

def reset_config():
    for f in [MLP_FILE, ENGINE_FILE, MANIFEST_FILE]:
        if os.path.exists(f): os.remove(f)
    if os.path.exists(SNAPSHOT_DIR): shutil.rmtree(SNAPSHOT_DIR)
    _ensure_dirs()
    return TinyMLP(), AeroEngine()

def build_wl_feature_vector(a_ev: ModuleEvidence, b_ev: ModuleEvidence, scores: Dict) -> List[float]:
    a_wl = {fp["wl_hash"] for fp in a_ev.wl_fingerprints}
    b_wl = {fp["wl_hash"] for fp in b_ev.wl_fingerprints}
    wl_j = len(a_wl & b_wl) / max(1, len(a_wl | b_wl))
    top_spans = scores.get("top_spans", [])
    sims = [s["similarity"] for s in top_spans] or [0.0]
    cons = [s["consensus_count"] for s in top_spans] or [0]
    feat = [float(scores["max_similarity"]),
            float(scores["mean_similarity"]),
            float(scores["temperature"]),
            float(scores["matched_span_count"]) / 30.0,
            float(scores["wl_exact_matches"]) / 20.0,
            float(wl_j),
            float(np.max(sims)),
            float(np.mean(sims)),
            float(np.std(sims) if len(sims) > 1 else 0),
            float(np.mean(cons)) / 3.0,
            float(len(a_ev.func_blocks)) / 50.0,
            float(len(b_ev.func_blocks)) / 50.0,
            float(len(a_ev.basic_blocks)) / 100.0,
            float(len(b_ev.basic_blocks)) / 100.0,
            float(len(a_ev.tokens)) / 5000.0,
            float(len(b_ev.tokens)) / 5000.0,]
    return [min(1.0, max(0.0, f)) for f in feat]

class ScanMode:
    DYNAMIC = "dynamic"
    AI_ONLY = "ai_only"
    STATIC = "static"

class ScanWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(dict)
    error = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(str)

    def __init__(self, path_a: str, path_b: str, out_dir: str, mode: str = ScanMode.DYNAMIC, snap_id: Optional[str] = None):
        super().__init__()
        self.path_a = path_a
        self.path_b = path_b
        self.out_dir = out_dir
        self.mode = mode
        self.snap_id = snap_id

    def run(self):
        try:
            t0 = time.time()
            self.progress.emit("Building evidence for Module A…")
            a_ev = build_module_evidence(self.path_a)
            self.progress.emit("Building evidence for Module B…")
            b_ev = build_module_evidence(self.path_b)
            self.progress.emit("Comparing (WL + MinHash + SW alignment)…")
            evidence, leaf_hashes = compare_modules(a_ev, b_ev)
            self.progress.emit("Rendering OGR…")
            os.makedirs(self.out_dir, exist_ok=True)
            ogr_path = os.path.join(self.out_dir, "ogr.png")
            render_ogr(evidence["scores"], evidence.get("wl_matches", []), ogr_path)
            self.progress.emit("Loading config package…")
            if self.snap_id: mlp, engine = load_snapshot(self.snap_id)
            else: mlp, engine = load_current_config()
            feat = build_wl_feature_vector(a_ev, b_ev, evidence)
            sc = evidence["scores"]
            top_spans = evidence.get("top_spans", [])
            tok_len_mean = float(np.mean([abs(s["a_span_end"] - s["a_span_start"]) for s in top_spans]) if top_spans else 10.0)
            if self.mode != ScanMode.STATIC:
                self.progress.emit("Updating AI model weights…"); mlp_out = mlp.update(feat)
            else: mlp_out = mlp.forward(np.array(feat, dtype=np.float32))
            if self.mode == ScanMode.DYNAMIC:
                self.progress.emit("Reconfiguring aerodynamics engine…"); engine.apply_mlp_config(mlp_out)
            self.progress.emit("Computing aerodynamic signatures…")
            aero_result = engine.compute(sc["max_similarity"], sc["mean_similarity"], sc["matched_span_count"], tok_len_mean, sc["temperature"])
            self.progress.emit("Signing evidence…")
            priv, pub = load_or_create_ed25519_keys(os.path.join(self.out_dir, "ed25519_private.pem"), os.path.join(self.out_dir, "ed25519_public.pem"))
            merkle = merkle_root(leaf_hashes + [aero_result["sig_hash"]])
            t1 = time.time()
            blob: Dict = {"schema_version": 2,
                          "ogr_png": "ogr.png",
                          "timestamp_unix": int(time.time()),
                          "module_a_sha256": a_ev.file_sha256,
                          "module_b_sha256": b_ev.file_sha256,
                          "scores": sc,
                          "wl_matches": evidence.get("wl_matches", []),
                          "top_spans": evidence.get("top_spans", []),
                          "span_evidence_merkle_root": merkle,
                          "aero_signature": aero_result,
                          "mlp_version": mlp.version,
                          "engine_version": engine.version,
                          "scan_mode": self.mode,
                          "scanner_config": {"minhash_n": _MINHASH_N, "k_shingle": 5,
                                             "alignment": "smith-waterman-numpy",
                                             "wl_iterations": 4, "consensus_threshold": 2,}, "runtime_seconds": round(t1 - t0, 3),}
            sig_b64 = sign_ed25519(priv, blob); blob["ed25519_signature_b64"] = sig_b64; blob["signature_valid"] = verify_ed25519(pub, {k: v for k, v in blob.items() if k not in ("ed25519_signature_b64", "signature_valid")}, sig_b64)
            if self.mode != ScanMode.STATIC:
                snap_id = save_config_package(mlp, engine, label=f"scan_{int(t1)}", module_sha=b_ev.file_sha256, scan_ts=int(t1))
                blob["config_snap_id"] = snap_id
            else: blob["config_snap_id"] = None
            self.finished.emit(blob)
        except Exception as e:
            import traceback
            self.error.emit(f"{e}\n{traceback.format_exc()}")

class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(".FBK / PY MODULE ADV-SIGNATURE (WL • MinHash • SW • Aero)")
        self.resize(1280, 800)
        self.setStyleSheet(DARK_QSS)
        self.path_a = ""
        self.path_b = ""
        self.worker = None
        self.worker_thread = None
        self._build_ui()
        self._refresh_snapshot_list()

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setSpacing(6)
        hdr = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Py Module Originality Scanner")
        tf = QtGui.QFont()
        tf.setPointSize(13); tf.setBold(True)
        title.setFont(tf)
        subtitle = QtWidgets.QLabel("  WL · MinHash · Smith-Waterman · Aerodynamic Signatures")
        subtitle.setStyleSheet("color:#666;")
        hdr.addWidget(title)
        hdr.addWidget(subtitle)
        hdr.addStretch()
        root.addLayout(hdr)
        fg = QtWidgets.QGroupBox("Input Modules")
        fl = QtWidgets.QHBoxLayout(fg)
        self.le_a = QtWidgets.QLineEdit(); self.le_a.setPlaceholderText("Module A (.py)…")
        self.le_b = QtWidgets.QLineEdit(); self.le_b.setPlaceholderText("Module B (.py)…")
        btn_a = QtWidgets.QPushButton("Browse A")
        btn_b = QtWidgets.QPushButton("Browse B")
        btn_a.clicked.connect(lambda: self._browse("a"))
        btn_b.clicked.connect(lambda: self._browse("b"))
        fl.addWidget(QtWidgets.QLabel("A:")); fl.addWidget(self.le_a); fl.addWidget(btn_a)
        fl.addSpacing(12)
        fl.addWidget(QtWidgets.QLabel("B:")); fl.addWidget(self.le_b); fl.addWidget(btn_b)
        root.addWidget(fg)
        sg = QtWidgets.QGroupBox("Scan Controls")
        sl = QtWidgets.QHBoxLayout(sg)
        self.out_dir = QtWidgets.QLineEdit(os.path.abspath("./out"))
        self.out_dir.setReadOnly(True)
        btn_out = QtWidgets.QPushButton("Output Folder")
        btn_out.clicked.connect(self._choose_out)
        sl.addWidget(QtWidgets.QLabel("Output:")); sl.addWidget(self.out_dir); sl.addWidget(btn_out)
        sl.addSpacing(10)
        sl.addWidget(QtWidgets.QLabel("Aero/AI Mode:"))
        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(["Dynamic (AI+Engine evolve)", "AI Only", "Static (frozen)"])
        sl.addWidget(self.mode_combo)
        sl.addSpacing(6)
        self.btn_scan = QtWidgets.QPushButton("▶  Scan & Generate Signatures")
        self.btn_scan.setMinimumHeight(42)
        bold = QtGui.QFont(); bold.setBold(True)
        self.btn_scan.setFont(bold)
        self.btn_scan.clicked.connect(self._start_scan)
        sl.addWidget(self.btn_scan, 2)
        self.prog = QtWidgets.QProgressBar()
        self.prog.setRange(0, 0)
        self.prog.setVisible(False)
        self.prog.setMaximumWidth(160)
        sl.addWidget(self.prog)
        self.status_lbl = QtWidgets.QLabel("Ready.")
        self.status_lbl.setWordWrap(True)
        sl.addWidget(self.status_lbl, 3)
        root.addWidget(sg)
        self.tabs = QtWidgets.QTabWidget()
        root.addWidget(self.tabs, 1)
        tab1 = QtWidgets.QWidget()
        t1l = QtWidgets.QHBoxLayout(tab1)
        self.ogr_label = QtWidgets.QLabel("OGR will appear here.")
        self.ogr_label.setAlignment(QtCore.Qt.AlignCenter)
        self.ogr_label.setMinimumHeight(300)
        self.ogr_label.setStyleSheet("border:1px solid #222; border-radius:5px;")
        self.summary_txt = QtWidgets.QPlainTextEdit()
        self.summary_txt.setReadOnly(True)
        self.summary_txt.setFont(QtGui.QFont("Courier New", 8))
        t1l.addWidget(self.ogr_label, 3)
        t1l.addWidget(self.summary_txt, 2)
        self.tabs.addTab(tab1, "OGR & Summary")
        tab2 = QtWidgets.QWidget()
        t2l = QtWidgets.QVBoxLayout(tab2)
        self.span_table = QtWidgets.QTableWidget(0, 7)
        self.span_table.setHorizontalHeaderLabels(["#", "A span", "B span", "Similarity", "Consensus", "Method", "Evidence hash"])
        self.span_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        t2l.addWidget(self.span_table)
        self.tabs.addTab(tab2, "Matched Spans")
        tab3 = QtWidgets.QWidget()
        t3l = QtWidgets.QVBoxLayout(tab3)
        self.wl_table = QtWidgets.QTableWidget(0, 4)
        self.wl_table.setHorizontalHeaderLabels(["A Name", "B Name", "Kind", "WL Hash (prefix)"])
        self.wl_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        t3l.addWidget(self.wl_table)
        self.tabs.addTab(tab3, "WL Structural Matches")
        tab4 = QtWidgets.QWidget()
        t4l = QtWidgets.QVBoxLayout(tab4)
        self.aero_txt = QtWidgets.QPlainTextEdit()
        self.aero_txt.setReadOnly(True)
        self.aero_txt.setFont(QtGui.QFont("Courier New", 8))
        t4l.addWidget(self.aero_txt)
        self.tabs.addTab(tab4, "Aerodynamic Signatures")
        tab5 = QtWidgets.QWidget()
        t5l = QtWidgets.QVBoxLayout(tab5)
        snap_hdr = QtWidgets.QHBoxLayout()
        snap_hdr.addWidget(QtWidgets.QLabel("Saved Config Snapshots:"))
        snap_hdr.addStretch()
        self.btn_refresh_snaps = QtWidgets.QPushButton("Refresh")
        self.btn_refresh_snaps.clicked.connect(self._refresh_snapshot_list)
        self.btn_load_snap = QtWidgets.QPushButton("Load Selected")
        self.btn_load_snap.clicked.connect(self._load_selected_snapshot)
        self.btn_reset_all = QtWidgets.QPushButton("⚠ Reset All Configs")
        self.btn_reset_all.setStyleSheet("color:#E45756;")
        self.btn_reset_all.clicked.connect(self._reset_configs)
        snap_hdr.addWidget(self.btn_refresh_snaps)
        snap_hdr.addWidget(self.btn_load_snap)
        snap_hdr.addWidget(self.btn_reset_all)
        t5l.addLayout(snap_hdr)
        self.snap_list = QtWidgets.QListWidget()
        self.snap_list.setFont(QtGui.QFont("Courier New", 8))
        t5l.addWidget(self.snap_list)
        self.snap_detail = QtWidgets.QPlainTextEdit()
        self.snap_detail.setReadOnly(True)
        self.snap_detail.setFont(QtGui.QFont("Courier New", 8))
        self.snap_detail.setMaximumHeight(160)
        t5l.addWidget(self.snap_detail)
        self.tabs.addTab(tab5, "Config Snapshots")

    def _browse(self, which: str):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(self, f"Select Module {which.upper()}", "", "Python files (*.py)")
        if not p:
            return
        if which == "a": self.path_a = p; self.le_a.setText(p)
        else: self.path_b = p; self.le_b.setText(p)

    def _choose_out(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Output Folder", self.out_dir.text())
        if d: self.out_dir.setText(d)

    def _mode_str(self) -> str:
        i = self.mode_combo.currentIndex()
        return [ScanMode.DYNAMIC, ScanMode.AI_ONLY, ScanMode.STATIC][i]

    def _start_scan(self):
        if not self.path_a or not self.path_b:
            self.status_lbl.setText("Select both Module A and Module B first.")
            return
        self._clear_results(); self.btn_scan.setEnabled(False); self.prog.setVisible(True)
        snap_id = None; sel = self.snap_list.selectedItems()
        if sel: snap_id = sel[0].data(QtCore.Qt.UserRole)
        out_dir = self.out_dir.text().strip() or os.path.abspath("./out")
        self.worker = ScanWorker(self.path_a, self.path_b, out_dir, self._mode_str(), snap_id)
        self.worker_thread = QtCore.QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.progress.connect(self.status_lbl.setText)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(lambda: (self.btn_scan.setEnabled(True), self.prog.setVisible(False)))
        self.worker_thread.start()

    def _clear_results(self):
        self.span_table.setRowCount(0); self.wl_table.setRowCount(0); self.ogr_label.setText("Scanning…")
        self.summary_txt.setPlainText(""); self.aero_txt.setPlainText("")

    def _on_error(self, msg: str):
        self.status_lbl.setText("Error — see Summary tab")
        self.summary_txt.setPlainText("ERROR:\n" + msg)

    def _on_finished(self, blob: Dict):
        out_dir = self.out_dir.text().strip()
        ev_path = os.path.join(out_dir, "signed_evidence.json")
        with open(ev_path, "w") as f: json.dump(blob, f, indent=2)
        ogr_png = os.path.join(out_dir, "ogr.png")
        if os.path.exists(ogr_png):
            pix = QtGui.QPixmap(ogr_png)
            self.ogr_label.setPixmap(pix.scaled(self.ogr_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else: self.ogr_label.setText("OGR not found.")
        sc = blob["scores"]; aero = blob.get("aero_signature", {})
        self.summary_txt.setPlainText(
            f"Evidence saved: {ev_path}\n\n"
            f"Module A sha256 : {blob['module_a_sha256']}\n"
            f"Module B sha256 : {blob['module_b_sha256']}\n\n"
            f"── Similarity ─────────────────────\n"
            f"  Max sim       : {sc['max_similarity']:.4f}\n"
            f"  Mean sim      : {sc['mean_similarity']:.4f}\n"
            f"  Temperature   : {sc['temperature']:.4f}\n"
            f"  Confirmed spans: {sc['matched_span_count']}\n"
            f"  All candidates : {sc['all_candidate_count']}\n"
            f"  WL exact matches: {sc['wl_exact_matches']}\n\n"
            f"── Merkle / Crypto ─────────────────\n"
            f"  Merkle root   : {blob['span_evidence_merkle_root']}\n"
            f"  Sig valid     : {blob.get('signature_valid')}\n\n"
            f"── AI / Aero Config ────────────────\n"
            f"  MLP version   : {blob.get('mlp_version')}\n"
            f"  Engine version: {blob.get('engine_version')}\n"
            f"  Snap ID       : {blob.get('config_snap_id','—')}\n"
            f"  Mode          : {blob.get('scan_mode')}\n\n"
            f"  Runtime       : {blob.get('runtime_seconds')}s\n")
        top = blob.get("top_spans", []); self.span_table.setRowCount(len(top))
        for r, item in enumerate(top):
            a_sp = f"{item['a_span_start']}..{item['a_span_end']}"
            b_sp = f"{item['b_span_start']}..{item['b_span_end']}"
            self.span_table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(r + 1)))
            self.span_table.setItem(r, 1, QtWidgets.QTableWidgetItem(a_sp))
            self.span_table.setItem(r, 2, QtWidgets.QTableWidgetItem(b_sp))
            self.span_table.setItem(r, 3, QtWidgets.QTableWidgetItem(f"{item['similarity']:.3f}"))
            self.span_table.setItem(r, 4, QtWidgets.QTableWidgetItem(str(item.get("consensus_count", 1))))
            self.span_table.setItem(r, 5, QtWidgets.QTableWidgetItem(item["method"]))
            self.span_table.setItem(r, 6, QtWidgets.QTableWidgetItem(item["evidence_hash"][:20] + "…"))
            cc = item.get("consensus_count", 1)
            colour = "#1a2a1a" if cc >= 2 else "#0e0e0e"
            for col in range(7): self.span_table.item(r, col).setBackground(QtGui.QColor(colour))
        wl_m = blob.get("wl_matches", []); self.wl_table.setRowCount(len(wl_m))
        for r, m in enumerate(wl_m):
            self.wl_table.setItem(r, 0, QtWidgets.QTableWidgetItem(m.get("a_name", "")))
            self.wl_table.setItem(r, 1, QtWidgets.QTableWidgetItem(m.get("b_name", "")))
            self.wl_table.setItem(r, 2, QtWidgets.QTableWidgetItem(m.get("kind", "")))
            self.wl_table.setItem(r, 3, QtWidgets.QTableWidgetItem(m.get("wl_hash", "")[:20] + "…"))
        sv = aero.get("sig_vec", []); labels = ["Re", "AR", "CL", "CD", "L/D", "q", "Cp", "St"]
        lines = ["─── Aerodynamic Signature Vector ───", ""]
        for i, (lbl, v) in enumerate(zip(labels, sv)):
            bar = "█" * int(v * 30)
            lines.append(f"  {lbl:<4} {v:.4f}  {bar}")
        lines += [
            "", f"  Sig hash    : {aero.get('sig_hash','')[:32]}…",
            f"  Engine v    : {aero.get('engine_version','')}",
            "", "─── Raw Aero Params ─────────────────",
            f"  Re          : {aero.get('Re',0):.1f}",
            f"  AR          : {aero.get('AR',0):.2f}",
            f"  c_L         : {aero.get('c_L',0):.4f}",
            f"  c_D         : {aero.get('c_D',0):.5f}",
            f"  L/D ratio   : {aero.get('LD',0):.2f}",
            f"  q (dyn pres): {aero.get('q',0):.2f}",
            f"  Cp          : {aero.get('c_p',0):.4f}",
            f"  St          : {aero.get('St',0):.4f}",]
        self.aero_txt.setPlainText("\n".join(lines))
        self._refresh_snapshot_list()
        self.status_lbl.setText(f"Done in {blob.get('runtime_seconds')}s  •  "
                                f"max_sim={sc['max_similarity']:.3f}  •  "
                                f"WL matches={sc['wl_exact_matches']}")

    def _refresh_snapshot_list(self):
        manifest = _load_manifest(); self.snap_list.clear()
        for m in reversed(manifest):
            ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(m["ts"]))
            text = (f"[{ts_str}]  {m['label']}  "
                    f"mlp_v={m['mlp_v']}  eng_v={m['engine_v']}")
            item = QtWidgets.QListWidgetItem(text)
            item.setData(QtCore.Qt.UserRole, m["id"])
            self.snap_list.addItem(item)

    def _load_selected_snapshot(self):
        sel = self.snap_list.selectedItems()
        if not sel:
            self.snap_detail.setPlainText("No snapshot selected.")
            return
        snap_id = sel[0].data(QtCore.Qt.UserRole)
        try:
            mlp, eng = load_snapshot(snap_id)
            detail = (f"Loaded snapshot: {snap_id}\n"
                      f"MLP version    : {mlp.version}\n"
                      f"Engine version : {eng.version}\n"
                      f"Engine rho     : {eng.rho:.4f}\n"
                      f"Engine c_L_max : {eng.c_L_max:.4f}\n"
                      f"Engine AR_nom  : {eng.AR_nom:.4f}\n\n"
                      "This snapshot will be used as the starting config for the next scan.")
            self.snap_detail.setPlainText(detail)
        except Exception as e:
            self.snap_detail.setPlainText(f"Error loading snapshot: {e}")

    def _reset_configs(self):
        reply = QtWidgets.QMessageBox.question(self, "Confirm Reset", "Reset ALL config files and delete ALL snapshots?\nThis cannot be undone.", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            reset_config(); self._refresh_snapshot_list()
            self.snap_detail.setPlainText("All configs reset to factory defaults.")
            self.status_lbl.setText("Config reset done.")

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
