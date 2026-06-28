from __future__ import annotations
import argparse, json
from staqtapp_tds.admin.control import AdminControl
from staqtapp_tds.admin.panel import AdminPanelServer

def main(argv=None):
    p = argparse.ArgumentParser(prog="staqtapp-tds-admin")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    serve = sub.add_parser("serve-panel"); serve.add_argument("--host", default="127.0.0.1"); serve.add_argument("--port", type=int, default=8765)
    args = p.parse_args(argv)
    control = AdminControl()
    if args.cmd == "status":
        print(json.dumps(control.status(), indent=2))
    elif args.cmd == "serve-panel":
        AdminPanelServer(control, args.host, args.port).serve_forever()

if __name__ == "__main__":
    main()
