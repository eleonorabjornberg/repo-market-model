#!/usr/bin/env python3
"""One-off migration (#866): split the single-file research log into `docs/research/log/` and check the round trip.

Writes `_header.md` and one file per entry, in the log's own order under a `0001-` prefix, and exits 1 unless
`assemble` gives back the original `docs/research/log.md` byte for byte. Run once, at the migration commit; the
log is then generated (`python3 scripts/check_research_log.py assemble`) and this script has nothing left to do.

    python3 scripts/split_research_log_866.py
"""
import importlib.util
import sys
from pathlib import Path

_path = Path(__file__).with_name("check_research_log.py")
_spec = importlib.util.spec_from_file_location("check_research_log", _path)
crl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(crl)


def main():
    if crl.LOG_DIR.exists():
        sys.stderr.write("%s exists: the log is already split\n" % crl.LOG_DIR)
        return 1
    original = crl.LOG.read_text(encoding="utf-8")
    header, files = crl.split_log(original)
    if crl.assemble(header, dict(files)) != original:
        sys.stderr.write("the split does not assemble back to log.md; nothing written\n")
        return 1
    crl.LOG_DIR.mkdir(parents=True)
    (crl.LOG_DIR / crl.HEADER_NAME).write_text(header, encoding="utf-8")
    for name, text in files:
        (crl.LOG_DIR / name).write_text(text, encoding="utf-8")
    print("wrote %s and %d entry files; log.md assembles back byte-identical" % (crl.HEADER_NAME, len(files)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
