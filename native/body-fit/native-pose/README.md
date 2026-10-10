# Actor-bound pose export

This is a separate source overlay (a set of edits applied on top of the libsm64 code) for the pinned libsm64 build. It isn't
installed in Rec Room. The Mario DLL that ships, and the component that uses it, stay as they are.

`sm64_body_tick_copy` moves one real native actor forward by one tick. Then it copies the actor's state, triangle geometry,
anatomical triangle IDs and joint matrices into buffers that the caller owns, and returns. No public function takes the global
last-rendered pose. The old region and matrix copy exports that had no actor attached are gone.

## Identity and order

Create an actor with `sm64_body_actor_create`. Its stamp holds a native actor ID, a generation number that isn't zero, and a
completed tick of 0. This first stamp is only a label. It has no geometry and no made-up starting state. Ask for tick 1 to get
the first real pose.

Every checked step gives that exact ID and generation, plus `expectedNextTick = completedTick + 1`. A repeated, skipped or old tick
number fails before any physics runs. Older `sm64_mario_tick` calls move the same per-actor counter forward. So an older checked
request can't repeat a step without being noticed.

The generation counter survives actor deletion, ID reuse, and a global terminate followed by re-initialize, inside the loaded
module. If it overflows, creating an actor is refused. A generation only applies to one loaded module's lifetime. If you unload
and load the DLL again, you need a new host session identity. Actor ticks are independent of each other. A future multi-player
host would have to run its own full world-tick batch. It shouldn't treat these per-actor counters as a world clock.

## Ownership

The first global initialization records one Windows thread ID. Every original exported entry point checks it. That covers state
setters, collision queries, surface changes, callback registration and audio. A call from the wrong thread can't touch the shared
native state. The original void exports keep their ABI (the binary interface callers rely on). When one is rejected, it quietly
returns. The new functions return explicit status codes instead.

While a checked tick runs native code and copies outputs, it holds a busy gate. If debug or sound callbacks are registered,
checked creation and stepping fail before any native work starts. This stops a callback from re-entering during a checked
operation. The API assumes the caller's allocations are valid and that the caller has exclusive use of the buffers it passed in
for the length of the call. Any C API that takes pointers has to assume that. The API doesn't protect against arbitrary writes
into library memory, or against another thread changing the caller's buffers.

The check on the analog stick allows a squared length up to `1 + 2 × FLT_EPSILON`. That way a valid unit vector rounded to
binary32, such as `(0.6f, 0.8f)`, is accepted. The original input floats are passed on unchanged. This small allowance for input
numbers has nothing to do with the geometry tolerances or the body padding.

“Atomic” means the owner-thread call returns one consistent pose. It does not mean a hardware-atomic update of several buffers
for readers on other threads. A host should only publish an immutable snapshot that it owns, and only after the call succeeds.

## Buffers and failures

The checked API needs the full pinned capacities: 1,024 triangles; 9,216 floats each for positions, normals and colors; 6,144 UV
floats; 1,024 region IDs; 256 matrix floats; and 16 matrix-presence bytes. Before stepping, it checks the capacities, that no
pointer is null, that no pointer range overflows, and that no arrays overlap among all the arrays, the state, the stamp, the
input and the descriptor. Output arrays may not alias each other, the input or the descriptor.

On success, only the part of the buffers that holds real triangles is copied. The matrices and presence bytes have fixed sizes.
All 15 anatomical regions must appear once, each with one finite transform. Every triangle that is emitted must have a known
anatomical ID. If geometry would overflow, the call stops before it writes to the native buffer. The wing cap's wings are the one
extra piece allowed: triangles tagged region 16, with at most two transforms (`sm64_body_pose_abi(8)` returns 1 in a native
library that does this). Missing geometry, or repeated body-region transforms that can't be told apart, are rejected.

| Status | Meaning | Effect on the tick and outputs |
|---|---|---|
| 0 | Success | The native tick finished and a consistent output was copied |
| -1 to -9 | No world, wrong thread, busy, bad actor/generation/tick/argument, short buffer or registered callback | No tick and no output writes |
| -10 | The actor already faulted | No further tick or output writes |
| -11 | Generation or tick overflow | No tick or creation, and no output writes |
| -12 | The native step finished but the pose check failed | Outputs unchanged. The actor becomes faulted and must be deleted |

Don't retry a `-12` request. Its native physics step already happened. Other actors stay usable. The pose counts and the stamp
are only updated after all the checks that run after the step succeed.

## Reproduction and evidence

`native/build.ps1` (`scripts/build_native.py`) builds it. It applies this overlay to a copy of the libsm64 sources, together with
the gfx, silent-audio and carry overlays, and compiles one `sm64-mario.dll`. First it compares the checkout with the recorded
file hashes (`native/libsm64-source.json`). Every overlay edit has an exact anchor. So a different libsm64 commit stops the build
instead of producing a different library.

The test that uses the ROM is `tests/body-pose/probe.py --reviewed-body-pose`. It needs matching Defender receipts before it loads
any native files. It takes a Windows read lock on each DLL and limits native dependency lookup to its own directory and System32.
It compares every named native state field, and every returned position, normal, color and UV byte, to the original reviewed DLL.
It does this over the original 673 action frames, after the same 30-tick warmup for each scenario. The report lists any warmup
differences separately. The starting allocation and animation state is not covered by that baseline claim. C struct padding isn't
a state field. If its bytes differ, that is recorded separately.

This is a first step toward later same-actor body geometry queries. It does not give you continuous pose collision, a check on
head and torso growth before each step, a live hitbox fitted to the body, or any quest result.

## Fresh-object initialization fix

The first comparison also turned up a bug in the pinned upstream code. `object_stuff.c::try_allocate_object` allocates `Object`
with `malloc`. Its shortened `geo_obj_init` sets only part of `AnimInfo`, and it never sets `animTimer`. The normal graph-node
initializer sets that timer to zero. On the first rendered tick, `geo_update_animation_frame` compares the timer to the zero
area counter. So the first animation frame and mesh can depend on whatever the memory held before.

The isolated overlay changes that one allocation to `calloc(1, sizeof(struct Object))`, before the existing initializer runs.
These are fresh objects, so no earlier values are meant to survive. This also clears the other object members before their
existing explicit defaults are applied.

Zeroing alone isn't enough, though. libsm64 starts rendering at area counter zero, and animation setup picks `startFrame - 1`. A zero
timer would wrongly mark this first frame as already advanced. `retrieve_animation_index` accepts that negative frame and can read
before an animation values array. So actor creation sets `animTimer` to the previous area tick. That way the first real render
moves to frame zero before it samples. The original source and the shipped DLL are unchanged.

The report from before the fix is kept as `artifacts/body-pose-before-object-init-tests.json`. Its three first-tick differences
are written down, not counted as successful baseline comparisons. The fixed version also checks 16 real first poses across ID
reuse and global re-initialization. That includes the copied anatomical tags and matrices. The original 673-frame comparison
after warmup is still required. The first-tick behavior change is justified, and it is separate from that compatibility claim.
