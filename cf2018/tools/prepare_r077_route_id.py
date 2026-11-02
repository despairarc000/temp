"""R077: prepare a pinned, copy-only, *observe-only* CTDir route label.

Input: already prepared R073 SYN-difference directory and exact private
original libapollo.so. The R073 handler is reconstructed back to the known
R068 SHA before any modifications. No original binary is ever copied into the
output. The new handler emits a fixed route-equality label only; it cannot
send a second-service ACK.

Offline validation is separate from live owner opt-in.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R068_SHA = "7ab7ad90735201b6df96265c8dd379d08308690fb6956f3a46e4f793ba8c84d0"
GATE_SHA = "9f7ee1969541ca27a1da48a4f91d4edab89d726383c71513efbe6e357072a43e"

RECORD_R068 = "                        run.record('syn_security_context',cid,slot=slot,assessment=assessment)\n"
RECORD_R073 = (
    "                        from syn_difference_labels import diagnose\n"
    "                        run.record('syn_security_context',cid,slot=slot,assessment=assessment,**diagnose(raw_frame,original))\n"
)
REPORT_R068 = "class={e['assessment']}\")"
REPORT_R073 = "class={e['assessment']} reason={e['reason']} base_changed={e['base_changed']} syn_changed={e['syn_changed']}\")"
ACK_R068 = "__import__('os').environ.get('CF2018_SECOND_SERVICE_ACK') == 'YES'"
ACK_R073 = "if (assessment == 'MATCH_EXCEPT_ROUTE' and\n                            False):"
ACK_R068_CONTEXT = "if (assessment == 'MATCH_EXCEPT_ROUTE' and\n                            " + ACK_R068 + "):"
ORIGINAL_MAIN = "if __name__=='__main__':main()"

# Exactly the substitutions in prepare_syn_difference.py; inverse restores
# the original SHA-pinned one-ACK handler without ever running that handler.
INVERSE_R073 = (
    (RECORD_R073, RECORD_R068),
    (ACK_R073, ACK_R068_CONTEXT),
    (REPORT_R073, REPORT_R068),
    ("CF2018_SYN_DIFFERENCE_Result.txt", "CF2018_SECOND_SERVICE_ACK_Result.txt"),
    ("cf2018_syn_difference_runs", "cf2018_second_service_ack_runs"),
    ("CF2018 SYN difference diagnostic; second-service ACK disabled",
     "CF2018 second-service one-ACK experiment; not an authenticated session"),
)

R077_RECORD = (
    "                        from syn_difference_labels import diagnose\n"
    "                        from r076_private_route_equality import classify_transient_frame\n"
    "                        run.record('syn_security_context',cid,slot=slot,assessment=assessment,"
    "route_label=classify_transient_frame(raw_frame,_R077_ORIGINAL_ROUTE),"
    "**diagnose(raw_frame,original))\n"
)
R077_REPORT = (
    "class={e['assessment']} reason={e['reason']} base_changed={e['base_changed']} "
    "syn_changed={e['syn_changed']} route_label={e['route_label']}\")"
)
R077_MAIN = """_R077_ORIGINAL_ROUTE = None
if __name__=='__main__':
    try:
        from r076_private_route_equality import _original_route_name
        _R077_ORIGINAL_ROUTE = _original_route_name(
            __import__('os').environ['CF18_APOLLO_LIBRARY'])
    except (OSError, ValueError, KeyError, TypeError):
        print('R077 preflight REFUSED: exact original Apollo required')
        raise SystemExit(2)
    main()"""

MODULES = (
    "r057_original_address_callers.py",
    "r058_name_service_wiring.py",
    "r075_directory_connector_discriminator.py",
    "r076_private_route_equality.py",
)


def _only(text, before, after):
    if text.count(before) != 1:
        raise ValueError("original source anchor absent or duplicated")
    return text.replace(before, after, 1)


def original_r068_sha_verified(r073):
    original = r073
    for before, after in INVERSE_R073:
        original = _only(original, before, after)
    if hashlib.sha256(original.encode()).hexdigest() != R068_SHA:
        raise ValueError("R073 not derived from exact pinned R068 handler")
    return True


def patch_handler(r073):
    original_r068_sha_verified(r073)
    text = _only(r073, RECORD_R073, R077_RECORD)
    text = _only(text, REPORT_R073, R077_REPORT)
    text = _only(text, "CF2018_SYN_DIFFERENCE_Result.txt",
                 "CF2018_R077_ROUTE_ID_Result.txt")
    text = _only(text, "cf2018_syn_difference_runs", "cf2018_r077_route_id_runs")
    text = _only(text, "CF2018 SYN difference diagnostic; second-service ACK disabled",
                 "CF2018 R077 original route equality only; second-service ACK disabled")
    text = _only(text, ORIGINAL_MAIN, R077_MAIN)
    if ACK_R073 not in text or ACK_R068 in text or "second_service_probe=True" not in text:
        raise ValueError("original ACK guard altered")
    # Source differs solely in the above observational substitutions.
    restored = text
    substitutions = (
        (R077_MAIN, ORIGINAL_MAIN),
        ("CF2018 R077 original route equality only; second-service ACK disabled",
         "CF2018 SYN difference diagnostic; second-service ACK disabled"),
        ("cf2018_r077_route_id_runs", "cf2018_syn_difference_runs"),
        ("CF2018_R077_ROUTE_ID_Result.txt", "CF2018_SYN_DIFFERENCE_Result.txt"),
        (R077_REPORT, REPORT_R073),
        (R077_RECORD, RECORD_R073),
    )
    for newer, older in substitutions:
        restored = _only(restored, newer, older)
    if restored != r073:
        raise ValueError("non-observational change to R073 handler")
    compile(text, "routed_probe_r037.py", "exec")
    return text


def prepare(source, output, original_lib, module_root=ROOT):
    source, output = Path(source).resolve(), Path(output).resolve()
    original_lib = Path(original_lib).resolve()
    if source == output or output.exists() or source in output.parents:
        raise ValueError("fresh output outside source required")
    if not source.is_dir() or any(p.is_symlink() for p in source.rglob("*")):
        raise ValueError("exact source directory required, no symlinks")
    from sys import path
    module_dir = Path(module_root) / "experiments"
    # All modules are owned by this repository. Import must be from an
    # explicit verified local module folder, never download at runtime.
    from importlib.util import spec_from_file_location, module_from_spec
    # Require original private binary at preparation; never copy it.
    import sys
    previous = list(sys.path)
    try:
        sys.path.insert(0, str(module_dir))
        from r076_private_route_equality import _original_route_name
        if len(_original_route_name(original_lib)) != 10:
            raise ValueError("original library route shape mismatch")
    finally:
        sys.path[:] = previous

    handler = (source / "routed_probe_r037.py").read_text()
    patched = patch_handler(handler)
    if hashlib.sha256((source / "second_service_syn_gate.py").read_bytes()).hexdigest() != GATE_SHA:
        raise ValueError("R073 security-context parser changed")
    original_helper = (source / "syn_difference_labels.py").read_text()
    # Validate the exact R073 helper from the repo source, not an arbitrary
    # replacement with the same API name.
    from importlib.util import spec_from_file_location
    spec = spec_from_file_location("r077_expected_helper", Path(module_root)/"tools"/"prepare_syn_difference.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    import inspect
    if original_helper != inspect.getsource(module.diagnose):
        raise ValueError("R073 difference-label helper modified")
    for name in MODULES:
        p = module_dir / name
        if not p.is_file() or p.is_symlink():
            raise ValueError("original-check module missing or symlinked")
    # No private original Apollo/route string is persisted.
    shutil.copytree(source, output, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (output/"routed_probe_r037.py").write_text(patched)
    for name in MODULES:
        shutil.copyfile(module_dir/name, output/name)
    # Only shell's explicit live command may launch the listener; this
    # preparer creates no sockets, processes or env variables.
    return {"prepared": True, "source_r068_pinned": True,
            "original_apollo_verified": True, "second_service_ack_disabled": True,
            "original_lib_copied": False, "listener_started": False,
            "output": str(output)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, help="existing R073 prepared directory")
    p.add_argument("--output", required=True, help="new and absent directory")
    p.add_argument("--original-lib", required=True,
                   help="private exact original Apollo on this device; not copied")
    a = p.parse_args()
    try:
        result = prepare(a.source, a.output, a.original_lib)
    except (OSError, ValueError, TypeError, ImportError) as exc:
        print(json.dumps({"prepared": False, "reason": "UNPINNED_OR_MISSING_SOURCE",
                          "listener_started": False}))
        raise SystemExit(2) from None
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
