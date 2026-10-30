# DLL startup investigation acceptance

Base main6a0ecc16877adbdc4eed03cefebb5b4144f7bd6f. Direct user-authorized
offline integrity/loader investigation, separate from paused session workers.
Preserve re-signed-only works / edited DLL exits as historical phone observations.
Do not assume integrity enforcement or modify/repack/install originals.

Before implementation: verify original APK/DLL/library hashes and ISA; determine
whether the stored assembly is actually an ordinary managed PE image; trace the
loader/read/validation path before managed C# attribution. Record earliest observed
format/branch divergence, not an invented phone termination cause.

Acceptance: bounded original-native trace with exact source pins/addresses and
explicit substitutions where emulated. Negative controls must independently
distinguish malformed image, changed envelope/transform, decoded image validity,
loader error and a deliberate exit predicate. No proprietary output/raw native
dump, decrypted DLL, keys or APKs in public repository. Any local derived analysis
stays private; no automatic phone/device/network run. If historical edited files
or logs are absent, identify that precise causal limit and continue independent
loader analysis. Do not promise safe modification from host parsing alone.
