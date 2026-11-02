"""R077: prepare observer-only R076 comparison on a verified R073 copy.

Never launches listeners or modifies source; never enables an ACK. No private
Apollo or original packets are bundled. Runtime requires CF18_APOLLO_LIBRARY.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from prepare_syn_difference import prepare as prepare_r073

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_R068 = "7ab7ad90735201b6df96265c8dd379d08308690fb6956f3a46e4f793ba8c84d0"
GATE_SHA = "9f7ee1969541ca27a1da48a4f91d4edab89d726383c71513efbe6e357072a43e"
DEPENDENCIES = (
    "r057_original_address_callers.py",
    "r058_name_service_wiring.py",
    "r075_directory_connector_discriminator.py",
    "r076_private_route_equality.py",
)
REPORT_NAME = "CF2018_SYN_DIFFERENCE_Result.txt"
OUTPUT_NAME = "CF2018_CTDir_Route_Equality_Result.txt"

# Reconstruct the R068 source from R073's known narrowly-scoped substitutions.
# The reverse transform fails closed if any expected anchor is missing.
def verify_r073(text):
    old = "                        run.record('syn_security_context',cid,slot=slot,assessment=assessment)\n"
    new = ("                        from syn_difference_labels import diagnose\n"
           "                        run.record('syn_security_context',cid,slot=slot,assessment=assessment,**diagnose(raw_frame,original))\n")
    reverse = [
        (new, old),
        ("False", "__import__('os').environ.get('CF2018_SECOND_SERVICE_ACK') == 'YES'"),
        ("class={e['assessment']} reason={e['reason']} base_changed={e['base_changed']} syn_changed={e['syn_changed']}",
         "class={e['assessment']}"),
        (OUTPUT_NAME, OUTPUT_NAME),  # no-op reserved, not applied
        (REPORT_NAME, "CF2018_SECOND_SERVICE_ACK_Result.txt"),
        ("cf2018_syn_difference_runs", "cf2018_second_service_ack_runs"),
        ("CF2018 SYN difference diagnostic; second-service ACK disabled",
         "CF2018 second-service one-ACK experiment; not an authenticated session"),
    ]
    # The ACK guard is matched by *surrounding source*, never arbitrary False.
    guard = "if False:"
    original_guard = "if __import__('os').environ.get('CF2018_SECOND_SERVICE_ACK') == 'YES':"
    if text.count(guard) != 1:
        raise ValueError("R073 hard-disabled ACK guard not recognized")
    reconstructed = text.replace(guard, original_guard)
    for current, past in reverse:
        if current == "False" or current == OUTPUT_NAME:
            continue
        if reconstructed.count(current) != 1:
            raise ValueError("R073 expected source anchor missing or duplicated")
        reconstructed = reconstructed.replace(current, past)
    if hashlib.sha256(reconstructed.encode()).hexdigest() != EXPECTED_R068:
        raise ValueError("R073 does not reverse to pinned original R068")
    return True


def patch_handler(text):
    verify_r073(text)
    anchor = ("                        run.record('syn_security_context',cid,slot=slot,assessment=assessment,"
              "**diagnose(raw_frame,original))\n")
    injection = (
        "                        from r076_private_route_equality import classify_against_original\n"
        "                        from pathlib import Path as _RoutePath\n"
        "                        _route_source = __import__('os').environ.get('CF18_APOLLO_LIBRARY')\n"
        "                        route_label = (classify_against_original(raw_frame,_RoutePath(_route_source))\n"
        "                                       if _route_source else 'REFUSED')\n"
        "                        run.record('ctdir_route_equality',cid,slot=slot,label=route_label)\n"
    )
    report = ("            out.append(f\"SYN_CONTEXT slot={e['slot']} class={e['assessment']} reason={e['reason']} "
              "base_changed={e['base_changed']} syn_changed={e['syn_changed']}\")\n")
    report_add = (
        "    for e in ev:\n"
        "        if e['action'] == 'ctdir_route_equality':\n"
        "            out.append(f\"CTDIR_ROUTE slot={e['slot']} label={e['label']}\")\n"
    )
    old_header = "CF2018 SYN difference diagnostic; second-service ACK disabled"
    if any(text.count(k) != 1 for k in (anchor, report, old_header, REPORT_NAME)):
        raise ValueError("R073 report/handler anchors changed")
    out = text.replace(anchor, anchor + injection)
    out = out.replace(report, report + report_add)
    out = out.replace(old_header, "CF2018 CTDir route equality diagnostic; second-service ACK disabled")
    out = out.replace(REPORT_NAME, OUTPUT_NAME)
    if "if False:" not in out:
        raise ValueError("ACK disable guard missing")
    compile(out, "routed_probe_r037.py", "exec")
    return out


def prepare(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_dir() or output.exists() or source == output or source in output.parents:
        raise ValueError("source must exist; output must be a new directory elsewhere")
    if any(p.is_symlink() for p in source.rglob("*")):
        raise ValueError("symlinked original source refused")
    handler = source/"routed_probe_r037.py"
    content = handler.read_text()
    if hashlib.sha256((source/"second_service_syn_gate.py").read_bytes()).hexdigest() != GATE_SHA:
        raise ValueError("original strict SYN gate mismatch")
    patched = patch_handler(content)
    for name in DEPENDENCIES:
        if not (ROOT/"experiments"/name).is_file():
            raise ValueError("missing source dependency")
    shutil.copytree(source, output, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (output/"routed_probe_r037.py").write_text(patched)
    for name in DEPENDENCIES:
        shutil.copyfile(ROOT/"experiments"/name, output/name)
    return {"prepared": True, "ack_disabled": True, "listener_started": False,
            "private_original_embedded": False, "report_name": OUTPUT_NAME}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    print(json.dumps(prepare(args.source, args.output), sort_keys=True))
