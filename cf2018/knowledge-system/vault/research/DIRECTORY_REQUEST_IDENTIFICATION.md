# R094 — Directory application traffic observed; operation still unidentified

2026-11-02. Owner DIRECTORY_STAGE report SHA256 `8ca511b14fbf77f6c36ad020bfb97fca30b33bf955d152ce6325e87064320809`. No private report or payload published.

## PHONE_OBSERVED

Slot1 discovery path wrote169-byte address reply. Slot2 exact CTDir SYN route with unit5 change received63-byte ACK, emitted0x2001, then received existing54-byte synthetic auth and91-byte synthetic Bingo. A third client frame was observed: **0x4013/kind5,171 bytes total,92-byte body**. Status DIRECTORY_ROUTED_FRAME_OBSERVED. Header length79 is subtraction, not independent operation identification. Probe intentionally closed without replying to this application frame; slots3/4 were withheld by the one-shot budget. This is actual application traffic after directory transport staging. It does not prove real account authentication, directory RPC method, directory response acceptance, lobby or bots.

## CONFIRMED_NATIVE_STATIC and bounded original-writer execution

Rehashed original5,243,704-byte ARM/Thumb Apollo SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`. Sender PC-relative literals resolve to DirService:get_server_dirtree_all (33 bytes; send0x36af9c), DirService:get_server_dirtree_by_id (35B;0x36b3dc), and DirService:get_server_by_ids (28B;0x36b824). Route literal is DirService. Pointer-args writers0x369c18/0x369e50/0x36a0d4 emit respectively [(1,I64),(2,STRING),(3,I64)], [(1,I64),(2,STRING),(3,I32),(4,I64)], [(1,I64),(2,STRING),(3,I32),(4,I32),(5,I64)]. These are direct argument structs, not AddressService's nested request struct.

New native_directory_writer_controls.py executes actual binary message header0x39c3bc and these args writers with original protocol vtable addresspoint0x4f4768. Preconstructed synthetic C++ string storage; bounded synthetic memory output sink is the only substituted call. Header and args execute in fresh emulator contexts with state transfer. A four-byte synthetic TGCP sequence prefix is added separately; complete sender/MsgBuffer/transport execution is NOT claimed.

**All three methods fit92 bytes.** Actual legacy64 writers need synthetic string lengths12/3/3; strict64 writers need9/0/0. Six native cases PASS and parse to their distinct expected method/argument labels. Thus92B cannot identify a method, version, account or string contents; no production value inferred. This explicitly rejects unsupported size-based identification.

## Bounded identification copy

Single-file prepare_directory_identify.py SHA-pins preceding stage handler `87a988a98ab56fb6d789a6faabc0ed8b26b685b06d4c3ea55542a94d27a46cb6` and original gate helper, copies to a new folder and keeps all original stages, exact-route/unit/security gates and one-shot budget. New CF2018_DIRECTORY_IDENTIFY=YES opt-in. No new reply, directory response or broad packet capture is added.

Before identifying, it requires complete bounded routed header/body accounting, clear cipher flag, compression=no, route byte-equal to privately loaded original CTDir route, and body TGCP prefix equal to independent header sequence. Exact allowlisted qualified method, CALL1, eight-byte RPC sequence, exact ordered argument types, bounded string and terminal STOP/no trailing bytes are checked. Output contains only fixed method/encoding/reason labels. Numeric sequence/arguments, strings and raw bytes are neither returned nor recorded. RPC sequence64 is not TGCP sequence32. Unexpected method/route/encoding is explicitly unknown, not auto-accepted.

11 parser/frame/native test methods PASS, including malformed field/string/type/bounds, sequence/route/compression/encryption controls, privacy and all six original-writer92-byte cases. Six prepared-copy lifecycle methods PASS, including a complete synthetic method label exported by actual observer without any application reply. Original113 baseline tests PASS. Default public run skips private native/parser-module cases. Both knowledge doctors checked after adding links; no new remote CI claim.

**NEXT owner test:** same directory-stage sequence once, now report fixed request label in Android Download/CF2018_DIRECTORY_IDENTIFY_Result.txt. If NOT_IDENTIFIED/NOT_COMPARABLE, fixed reason discriminates route, cipher/compression, sequence or schema mismatch. Do not send a guessed DirTreeResult before exact phone method and pending response correlation are established. Last real phone result remains the171-byte application frame, not decoded method/login.
