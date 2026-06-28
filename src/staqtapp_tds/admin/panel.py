from __future__ import annotations

import html
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from staqtapp_tds import __version__
from staqtapp_tds.admin.control import AdminControl

PANEL_REFRESH_SECONDS = 2.0

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Staqtapp-TDS VFS Admin Console</title>
<style>
:root {
  --bg: #050912;
  --panel: rgba(12, 20, 42, 0.88);
  --panel-2: rgba(17, 26, 55, 0.82);
  --line: rgba(125, 162, 255, 0.18);
  --text: #edf4ff;
  --muted: #9eafd3;
  --blue: #1268ff;
  --cyan: #00d7ff;
  --purple: #8e35ff;
  --orange: #ff7a18;
  --green: #33e68a;
  --warn: #ffb454;
  --shadow: 0 24px 80px rgba(0, 0, 0, .42);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  color: var(--text);
  font: 14px/1.5 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background:
    radial-gradient(circle at 18% 8%, rgba(18,104,255,.28), transparent 30%),
    radial-gradient(circle at 76% 10%, rgba(142,53,255,.22), transparent 32%),
    radial-gradient(circle at 16% 82%, rgba(255,122,24,.18), transparent 26%),
    linear-gradient(135deg, #04070e, #071126 48%, #080614);
}
a { color: inherit; }
.shell { display: grid; grid-template-columns: 272px 1fr; min-height: 100vh; }
.sidebar {
  border-right: 1px solid var(--line);
  background: rgba(5, 10, 22, .72);
  padding: 22px 18px;
  position: sticky;
  top: 0;
  height: 100vh;
}
.brand { display: flex; gap: 14px; align-items: center; margin-bottom: 28px; }
.logo {
  width: 64px; height: 64px; border-radius: 50%;
  display: grid; place-items: center;
  background:
    conic-gradient(from 220deg, var(--orange), var(--purple), var(--blue), var(--cyan), var(--orange));
  box-shadow: 0 0 34px rgba(18,104,255,.45), inset 0 0 22px rgba(255,255,255,.18);
}
.logo-inner {
  width: 50px; height: 50px; border-radius: 16px;
  background: linear-gradient(145deg, #0b5eff, #111a48 58%, #ff7a18);
  display: grid; place-items: center;
  font-weight: 900;
  letter-spacing: -.08em;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.24);
}
.brand h1 { font-size: 19px; line-height: 1; margin: 0; letter-spacing: .07em; }
.brand b { color: var(--orange); }
.brand small { display: block; color: var(--muted); letter-spacing: .22em; margin-top: 7px; font-size: 11px; }
.nav { display: grid; gap: 8px; }
.nav div, .status-card, .card, .log, .actions { border: 1px solid var(--line); background: var(--panel); box-shadow: var(--shadow); }
.nav div {
  border-radius: 14px;
  padding: 13px 14px;
  color: #cfdaf5;
}
.nav div.active { background: linear-gradient(90deg, rgba(18,104,255,.48), rgba(142,53,255,.18)); color: white; border-color: rgba(18,104,255,.55); }
.status-card { margin-top: 24px; border-radius: 16px; padding: 16px; }
.status-card h3 { margin: 0 0 12px; font-size: 13px; letter-spacing: .08em; color: #d9e4ff; }
.status-row { display: flex; justify-content: space-between; gap: 10px; color: var(--muted); margin: 8px 0; }
.main { padding: 22px 28px 32px; }
.topbar {
  display: flex; align-items: center; justify-content: space-between; gap: 18px;
  padding-bottom: 22px; border-bottom: 1px solid var(--line); margin-bottom: 24px;
}
.topbar h2 { margin: 0; font-size: 24px; letter-spacing: .08em; }
.topbar p { margin: 3px 0 0; color: var(--muted); }
.pills { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.pill { border: 1px solid var(--line); background: rgba(11, 18, 38, .78); border-radius: 999px; padding: 9px 13px; color: #cdd9f7; }
.pill strong { color: var(--green); }
.grid { display: grid; grid-template-columns: repeat(4, minmax(160px, 1fr)); gap: 16px; }
.card { border-radius: 18px; padding: 19px; min-height: 118px; }
.card h3, .log h3, .actions h3 { margin: 0 0 12px; font-size: 13px; color: #b7c8ee; letter-spacing: .08em; text-transform: uppercase; }
.metric { font-size: 25px; font-weight: 800; letter-spacing: .02em; }
.sub { color: var(--muted); margin-top: 5px; }
.glow-blue { box-shadow: 0 0 0 1px rgba(18,104,255,.18), 0 18px 60px rgba(18,104,255,.10); }
.glow-purple { box-shadow: 0 0 0 1px rgba(142,53,255,.18), 0 18px 60px rgba(142,53,255,.10); }
.glow-orange { box-shadow: 0 0 0 1px rgba(255,122,24,.18), 0 18px 60px rgba(255,122,24,.10); }
.arch { margin-top: 16px; display: grid; grid-template-columns: 1.1fr .9fr; gap: 16px; }
.diagram { padding: 20px; border-radius: 18px; border: 1px solid var(--line); background: var(--panel); box-shadow: var(--shadow); }
.diagram-flow { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 12px; }
.node { padding: 14px; border-radius: 16px; background: linear-gradient(180deg, rgba(18,104,255,.18), rgba(142,53,255,.11)); border: 1px solid rgba(125,162,255,.18); }
.node em { display:block; color: var(--green); font-style: normal; font-size: 12px; margin-top: 6px; }
.lower { margin-top: 16px; display: grid; grid-template-columns: 1fr 270px; gap: 16px; }
.log, .actions { border-radius: 18px; padding: 18px; }
pre {
  white-space: pre-wrap;
  margin: 0;
  overflow: auto;
  max-height: 290px;
  color: #dce6ff;
  font: 12.5px/1.55 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
button, input, select {
  border-radius: 12px;
  border: 1px solid rgba(125,162,255,.24);
  background: rgba(8, 14, 32, .92);
  color: var(--text);
  padding: 10px 12px;
}
button { cursor: pointer; width: 100%; margin-top: 9px; font-weight: 700; }
button.primary { background: linear-gradient(90deg, var(--blue), var(--purple)); border-color: rgba(255,255,255,.18); }
button.orange { background: linear-gradient(90deg, rgba(255,122,24,.92), rgba(142,53,255,.78)); }
form { display: grid; gap: 8px; }
label { color: var(--muted); display: grid; gap: 4px; }
.dot { display:inline-block; width:9px; height:9px; border-radius:50%; background: var(--green); box-shadow: 0 0 15px var(--green); margin-right: 7px; }
.footer { margin-top: 18px; color: var(--muted); font-size: 12px; }
@media (max-width: 980px) { .shell { grid-template-columns: 1fr; } .sidebar { position: relative; height: auto; } .grid, .arch, .lower, .diagram-flow { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<div class="shell">
  <aside class="sidebar">
    <div class="brand"><div class="logo"><div class="logo-inner">&lt;/&gt;</div></div><div><h1>STAQTAPP-TDS <b>VFS</b></h1><small>VIRTUAL FILE SYSTEM</small></div></div>
    <nav class="nav">
      <div class="active">Dashboard</div><div>Configurations</div><div>Entries</div><div>Audit Log</div><div>Metrics</div><div>System Health</div><div>Security</div><div>Diagnostics</div>
    </nav>
    <section class="status-card"><h3>TDS Status</h3><div class="status-row"><span><span class="dot"></span>State</span><b id="side-health">HEALTHY</b></div><div class="status-row"><span>Version</span><b>v{version}</b></div><div class="status-row"><span>Network</span><b>local-only</b></div><div class="status-row"><span>Refresh</span><b>{refresh}s</b></div></section>
    <div class="footer">Browser console is a local observer/control shell. The hot TDS path receives immutable config only.</div>
  </aside>
  <main class="main">
    <header class="topbar"><div><h2>DASHBOARD</h2><p>Snapshot-driven control plane for Staqtapp-TDS Virtual File System.</p></div><div class="pills"><div class="pill">SYSTEM HEALTH: <strong id="health-pill">HEALTHY</strong></div><div class="pill">ACTIVE CONFIG: <strong id="active-pill">loading</strong></div><div class="pill">WORKLOAD: <strong id="workload-pill">idle</strong></div></div></header>
    <section class="grid">
      <article class="card glow-blue"><h3>Active Config</h3><div class="metric" id="active-config">loading</div><div class="sub" id="active-gen">Generation —</div></article>
      <article class="card glow-purple"><h3>Candidate Config</h3><div class="metric" id="candidate-config">none</div><div class="sub">Staged beside active; never in-place.</div></article>
      <article class="card glow-orange"><h3>Audit Events</h3><div class="metric" id="audit-count">0</div><div class="sub">stage / promote / rollback</div></article>
      <article class="card"><h3>Interference Budget</h3><div class="metric">&lt;1%</div><div class="sub">cached snapshots only</div></article>
    </section>
    <section class="grid" style="margin-top:16px">
      <article class="card glow-blue"><h3>Reads/sec</h3><div class="metric" id="reads-sec">0</div><div class="sub" id="lookup-latency">avg lookup — ms</div></article>
      <article class="card glow-purple"><h3>Writes/sec</h3><div class="metric" id="writes-sec">0</div><div class="sub" id="write-latency">avg write — ms</div></article>
      <article class="card glow-orange"><h3>Compression</h3><div class="metric" id="compression-ratio">1.0x</div><div class="sub" id="chunk-count">chunks 0</div></article>
      <article class="card"><h3>Index Pressure</h3><div class="metric" id="index-pressure">OK</div><div class="sub" id="index-detail">probe stats pending</div></article>
    </section>
    <section class="arch">
      <div class="diagram"><h3>LIVE ARCHITECTURE</h3><div class="diagram-flow"><div class="node">Admin Panel<em>observer</em></div><div class="node">Telemetry Cache<em>snapshot</em></div><div class="node">RuntimeConfig<em>immutable</em></div><div class="node">TDS Core<em>hot path isolated</em></div><div class="node">Swiss Index<em id="swiss-state">healthy</em></div><div class="node">Radix Router<em id="radix-state">healthy</em></div><div class="node">Chunk Manager<em id="chunk-state">observed</em></div><div class="node">Persistence<em>manual checks</em></div></div></div>
      <div class="diagram"><h3>SAFE POLLING MODEL</h3><p class="sub">The browser polls <code>/status.json</code> every {refresh}s. Deep diagnostics and benchmarks are manual actions only, so radix/Swiss-table operations are not scanned repeatedly.</p></div>
    </section>
    <section class="lower">
      <section class="log"><h3>Status Snapshot</h3><pre id="status">{status}</pre></section>
      <aside class="actions"><h3>Quick Actions</h3><form method="post" action="/stage"><label>Chunk bytes<input name="chunk_bytes" value="65536"></label><label>Compression<select name="compression"><option>zlib</option><option>lz4</option><option>zstd</option></select></label><label><input type="checkbox" name="compression_enabled"> Compression enabled</label><button class="primary">Stage next generation</button></form><form method="post" action="/promote"><button class="primary">Promote staged RC</button></form><form method="post" action="/rollback"><button class="orange">Rollback active RC</button></form></aside>
    </section>
  </main>
</div>
<script>
async function refreshStatus() {
  try {
    const res = await fetch('/status.json', {cache: 'no-store'});
    const data = await res.json();
    document.getElementById('status').textContent = JSON.stringify(data, null, 2);
    const active = data.active || {};
    const cand = data.candidate || null;
    document.getElementById('active-config').textContent = active.config_id || 'unknown';
    document.getElementById('active-pill').textContent = active.config_id || 'unknown';
    document.getElementById('active-gen').textContent = 'Generation ' + (active.generation || '—');
    document.getElementById('candidate-config').textContent = cand ? cand.config_id : 'none';
    document.getElementById('audit-count').textContent = data.audit_count || 0;
    document.getElementById('health-pill').textContent = data.system_health || 'HEALTHY';
    document.getElementById('side-health').textContent = data.system_health || 'HEALTHY';
    const obs = data.observation || {};
    const perf = obs.performance || {};
    const storage = obs.storage || {};
    const behavior = obs.behavior || {};
    const indexes = obs.indexes || {};
    const swiss = indexes.swiss || {};
    const radix = indexes.radix || {};
    document.getElementById('workload-pill').textContent = behavior.workload_mode || 'idle';
    document.getElementById('reads-sec').textContent = perf.reads_per_sec ?? 0;
    document.getElementById('writes-sec').textContent = perf.writes_per_sec ?? 0;
    document.getElementById('lookup-latency').textContent = 'avg lookup ' + (perf.avg_lookup_ms ?? '—') + ' ms';
    document.getElementById('write-latency').textContent = 'avg write ' + (perf.avg_write_ms ?? '—') + ' ms';
    document.getElementById('compression-ratio').textContent = (behavior.compression_ratio ?? 1.0) + 'x';
    document.getElementById('chunk-count').textContent = 'chunks ' + (storage.chunks_created ?? 0);
    const maxProbe = swiss.max_probe ?? 0;
    const avgProbe = swiss.average_probe ?? 0;
    document.getElementById('index-pressure').textContent = maxProbe >= 16 || avgProbe >= 3 ? 'WATCH' : 'OK';
    document.getElementById('index-detail').textContent = 'avg probe ' + avgProbe + ', max ' + maxProbe;
    document.getElementById('swiss-state').textContent = (swiss.entries ?? 0) + ' entries';
    document.getElementById('radix-state').textContent = (radix.nodes ?? 0) + ' nodes';
    document.getElementById('chunk-state').textContent = (storage.chunks_created ?? 0) + ' chunks';
  } catch (err) {
    document.getElementById('health-pill').textContent = 'PANEL ERROR';
  }
}
setInterval(refreshStatus, {refresh_ms});
refreshStatus();
</script>
</body>
</html>"""


class AdminPanelServer:
    """Optional localhost browser panel.

    The panel deliberately reads the AdminControl snapshot instead of walking TDS
    structures. Expensive diagnostics should be explicit admin actions, never
    dashboard refresh work.
    """

    def __init__(self, control: AdminControl | None = None, host: str = "127.0.0.1", port: int = 8765):
        self.control = control or AdminControl()
        self.host = host
        self.port = port

    def _status_snapshot(self) -> dict[str, object]:
        snap = self.control.status()
        snap["system_health"] = "HEALTHY"
        snap["panel"] = {
            "mode": "local-only",
            "refresh_seconds": PANEL_REFRESH_SECONDS,
            "snapshot_only": True,
            "deep_diagnostics_manual_only": True,
        }
        snap["server_time"] = time.time()
        return snap

    def make_handler(self):
        outer = self
        control = self.control

        class Handler(BaseHTTPRequestHandler):
            def _send(self, code: int, body: str, ctype: str = "text/html"):
                data = body.encode("utf-8")
                self.send_response(code)
                self.send_header("content-type", ctype)
                self.send_header("content-length", str(len(data)))
                self.send_header("cache-control", "no-store")
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                if self.path == "/status.json":
                    self._send(200, json.dumps(outer._status_snapshot(), indent=2), "application/json")
                    return
                status = html.escape(json.dumps(outer._status_snapshot(), indent=2))
                body = (
                    HTML.replace("{status}", status)
                    .replace("{version}", html.escape(str(__version__)))
                    .replace("{refresh}", f"{PANEL_REFRESH_SECONDS:.0f}")
                    .replace("{refresh_ms}", str(int(PANEL_REFRESH_SECONDS * 1000)))
                )
                self._send(200, body)

            def do_POST(self):
                length = int(self.headers.get("content-length", "0"))
                raw = self.rfile.read(length).decode("utf-8")
                form = parse_qs(raw)
                try:
                    if self.path == "/stage":
                        active = control.registry.active()
                        cand = active.next_generation(
                            chunk_bytes=int(form.get("chunk_bytes", [active.chunk_bytes])[0]),
                            compression=str(form.get("compression", [active.compression])[0]),
                            compression_enabled="compression_enabled" in form,
                            admin_panel_enabled=True,
                            network_mode="local-only",
                        )
                        control.stage_config(cand, control.auth.issue("stage"))
                    elif self.path == "/promote":
                        control.promote_config(control.auth.issue("promote"))
                    elif self.path == "/rollback":
                        control.rollback_config(control.auth.issue("rollback"))
                    else:
                        self._send(404, "not found", "text/plain")
                        return
                    self.send_response(303)
                    self.send_header("location", "/")
                    self.end_headers()
                except Exception as exc:
                    self._send(400, html.escape(str(exc)), "text/plain")

            def log_message(self, fmt, *args):
                return

        return Handler

    def serve_forever(self):
        server = ThreadingHTTPServer((self.host, self.port), self.make_handler())
        print(f"Staqtapp-TDS admin panel: http://{self.host}:{self.port}")
        server.serve_forever()
