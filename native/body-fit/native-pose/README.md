# Actor-bound pose export

This is an isolated source overlay for the pinned libsm64 build. It is not installed in Rec Room. The deployed Mario DLL and component remain unchanged.

`sm64_body_tick_copy` advances one real native actor once, then copies its state, triangle geometry, anatomical triangle IDs and joint matrices into caller-owned buffers before returning. There is no public function that accepts the global last-rendered pose. The former unqualified region/matrix copy exports are absent.

## Identity and order

Create an actor with `sm64_body_actor_create`. Its stamp contains a native actor ID, nonzero generation and completed tick 0. This initial stamp is metadata only; it contains no geometry or invented initial state. Request tick 1 to obtain the first actual pose.

Every checked step supplies that exact ID/generation and `expectedNextTick = completedTick + 1`. Duplicate, skipped or old tick numbers fail before physics. Legacy `sm64_mario_tick` calls advance the same per-actor counter, so an older checked request cannot repeat a step unnoticed.

The generation counter survives actor deletion, ID recycling and global terminate/re-initialize within the loaded module. Overflow rejects creation. A generation is scoped to one loaded module lifetime; unloading and loading a DLL requires a new host session identity. Actor ticks are independent. A future multi-player host must coordinate its own complete world-tick batch rather than treating these per-actor counters as a world clock.

## Ownership

The first global initialization acquires one Windows thread ID. Every original exported entry point is guarded, including state setters, collision queries, surface mutation, callback registration and audio. A wrong-thread call cannot bind shared native state. Original void exports retain their ABI and silently return when rejected; the new functions return explicit status codes.

The checked tick holds a busy gate while running native code and copying outputs. Registered debug/sound callbacks cause checked creation and stepping to fail before native work. This prevents callback re-entry during a checked operation. The API assumes valid caller allocations and exclusive ownership of the supplied buffers for the duration of the call, as any pointer-based C API must. It does not defend against arbitrary writes into library memory or another thread modifying caller buffers.

Analog stick validation allows a squared length up to `1 + 2 × FLT_EPSILON` so a valid unit vector rounded to binary32, such as `(0.6f, 0.8f)`, is accepted. The original input floats are passed unchanged. This small input-number allowance is unrelated to geometry tolerances or body padding.

“Atomic” means one coherent pose is returned by the owner-thread call. It is not a hardware-atomic multi-buffer publication to concurrent readers. A host must publish an immutable owned snapshot only after success.

## Buffers and failures

The checked API requires the complete pinned capacities: 1,024 triangles; 9,216 floats each for positions, normals and colors; 6,144 UV floats; 1,024 region IDs; 256 matrix floats; and 16 matrix-presence bytes. It validates capacities, non-null pointers, pointer-range overflow and overlap among all arrays, state, stamp, input and descriptor before stepping. Output arrays may not alias one another or the input/descriptor.

On success, only the actual triangle portion is copied. Matrices/presence bytes have fixed sizes. All 15 anatomical regions must appear once with one finite transform each; every emitted triangle must have a known anatomical ID. Geometry overflow is stopped before a native buffer write. The wing cap's wings are the one decoration admitted: triangles tagged region 16 with at most two transforms (`sm64_body_pose_abi(8)` returns 1 in a native that does this). Missing geometry or ambiguous repeated body-region transforms are rejected.

| Status | Meaning | Tick/output effect |
|---|---|---|
| 0 | Success | Native tick completed; coherent outputs copied |
| -1 to -9 | No world, wrong thread, busy, bad actor/generation/tick/argument, short buffer or registered callback | No tick and no output writes |
| -10 | Actor already faulted | No further tick or output writes |
| -11 | Generation or tick overflow | No tick/creation or output writes |
| -12 | Native step finished but pose validation failed | Outputs unchanged; actor becomes faulted and must be deleted |

Do not retry a `-12` request. Its native physics step already happened. Other actors remain available. Pose counts and the stamp are published only after all post-step validation succeeds.

## Reproduction and evidence

Built by `native/build.ps1` (`scripts/build_native.py`), which applies this overlay to a copy of the libsm64 sources together with the gfx, silent-audio and carry overlays, and compiles one `sm64-mario.dll`. The checkout is compared with the recorded file hashes (`native/libsm64-source.json`) first, and every overlay edit has an exact anchor, so a different libsm64 commit stops the build instead of producing a different library.

The ROM-backed fixture is `tests/body-pose/probe.py --reviewed-body-pose`. It requires matching Defender receipts before loading native files, uses a Windows read lock on each DLL and restricts native dependency resolution to its directory and System32. It compares every named native state field and every returned position, normal, color and UV byte to the original reviewed DLL over the original 673 action frames after the same 30-tick warmup per scenario. The report records any warmup differences separately; initial allocation/animation state is not covered by that baseline claim. C struct padding is not a state field and is recorded separately if its bytes differ.

This is a prerequisite for later same-actor body geometry queries. It does not provide continuous pose collision, pre-step head/torso growth admission, a body-fitted live hitbox or any quest result.

## Fresh-object initialization fix

The first comparison also exposed a pinned upstream initialization defect. `object_stuff.c::try_allocate_object` allocates `Object` with `malloc`. Its shortened `geo_obj_init` sets only part of `AnimInfo`; it never initializes `animTimer`. The normal graph-node initializer sets that timer to zero. On the first rendered tick, `geo_update_animation_frame` compares it to the zero area counter, so the first animation frame and mesh can depend on old allocation contents.

The isolated overlay changes that single allocation to `calloc(1, sizeof(struct Object))` before the existing initializer. These are fresh objects, so no previous values are intended to survive. This also initializes the remaining object members before their existing explicit defaults are applied.

Zeroing alone is insufficient: libsm64 begins rendering at area counter zero, and animation setup selects `startFrame - 1`. A zero timer would incorrectly mark this first frame as already advanced. `retrieve_animation_index` accepts that negative frame and can read before an animation values array. Actor creation therefore marks `animTimer` as the previous area tick, so the first actual render advances to frame zero before sampling. The original source and deployed DLL are unchanged.

The pre-fix report is preserved as `artifacts/body-pose-before-object-init-tests.json`; its three observed first-tick differences are recorded, not counted as successful baseline comparisons. The fixed candidate additionally checks 16 real first poses across ID reuse and global re-initialization, including the copied anatomical tags and matrices. The original 673 post-warmup frame comparison remains required. The justified first-tick behavior change is separate from that compatibility claim.
