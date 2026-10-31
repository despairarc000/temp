"""Build only an original-code patch kit; never include the private source ZIP."""
from pathlib import Path
import argparse
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'apply_v381.py': 'experiments/v381_termux_patch.py',
    'routed_body_diagnostic.py': 'experiments/routed_body_diagnostic.py',
    'V38_SOURCE_PINS.json': 'coordination/V38_SOURCE_PINS.json',
    'README.txt': 'coordination/V381_TERMUX_STEPS.txt',
}


def build(output):
    output = Path(output)
    if output.exists():
        raise ValueError('new kit output required')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for name, source in FILES.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 31, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, (ROOT / source).read_bytes())
    return {'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'entries': list(FILES), 'private_files_included': False}


if __name__ == '__main__':
    import json
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True)
    print(json.dumps(build(p.parse_args().output), sort_keys=True))
