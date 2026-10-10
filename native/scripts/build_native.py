"""Builds sm64-mario.dll: libsm64 plus the overlays in native/body-fit. Run it through native/build.ps1.

    python build_native.py --source <libsm64 checkout> --zig <zig.exe> --output <dll>

Nothing is downloaded and the checkout is not changed. The overlays edit copies of a few libsm64 files; each edit needs an
exact anchor, so a wrong libsm64 commit stops the build instead of giving a different library.
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

# --- authorship watermark (benign) ---
# Obfuscated credit for THIS project's author, XOR'd with 0x5a so a
# copy-paste thief who deletes the visible credit still carries it.
# Decode:  bytes(b ^ 0x5a for b in _AUTHORSHIP).decode()
# Inert constant - nothing reads or runs it. Any third-party credits
# elsewhere in this tree are untouched and must stay that way.
_AUTHORSHIP = bytes((0x9,0x32,0x33,0x2a,0x2a,0x23,0x6a,0x62,0x63))
# --- end watermark ---

HERE = pathlib.Path(__file__).resolve().parent
NATIVE = HERE.parent
OVERLAY_POSE = NATIVE / "body-fit" / "native-pose"
OVERLAY_CARRY = NATIVE / "body-fit" / "native-carry"
MANIFEST = NATIVE / "libsm64-source.json"


def fail(message):
    print("build_native: " + message, file=sys.stderr)
    sys.exit(1)


def read_text(path):
    """Source text with LF newlines (a Windows checkout may have converted them to CRLF; text mode converts them back)."""
    return pathlib.Path(path).read_text(encoding="utf-8")


def sha256_text(path):
    return hashlib.sha256(read_text(path).encode("utf-8")).hexdigest()


def replace_once(text, before, after):
    if text.count(before) != 1:
        fail("the libsm64 checkout differs from the expected commit (overlay anchor not found exactly once): "
             + before[:80].replace("\n", "\\n"))
    return text.replace(before, after)


def check_source(source):
    """Compares the checkout with the file list recorded for the expected commit."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    problems = []
    for relative, expected in manifest["files"].items():
        path = source / relative
        if not path.is_file():
            problems.append("missing " + relative)
        elif sha256_text(path) != expected:
            problems.append("changed " + relative)
    if problems:
        fail("the libsm64 checkout is not commit %s (%d difference(s), first: %s)"
             % (manifest["commit"], len(problems), problems[0]))
    for generated in ("geo.inc.c", "geo.inc.h", "model.inc.c", "model.inc.h"):
        if not (source / "src" / "decomp" / "mario" / generated).is_file():
            fail("src/decomp/mario/%s is missing. Run `python import-mario-geo.py` inside the libsm64 checkout "
                 "(libsm64's own step; it downloads the Mario model from the n64decomp/sm64 repository)." % generated)


# 1. body-part provenance in gfx_adapter.c


BODY_REGIONS = ["pelvis", "torso", "head", "left_arm", "left_forearm", "left_hand", "right_arm", "right_forearm",
                "right_hand", "left_thigh", "left_leg", "left_foot", "right_thigh", "right_leg", "right_foot",
                "decoration"]


def body_region_of(name):
    if "wings" in name:
        return "decoration"
    for candidate in BODY_REGIONS[3:15]:
        if candidate in name:
            return candidate
    if "butt" in name:
        return "pelvis"
    if "torso" in name:
        return "torso"
    if "cap_on" in name or "cap_off" in name:
        return "head"
    fail("unclassified Mario geometry source: " + name)


def tag_body_regions(source):
    geo = read_text(source / "src/decomp/mario/geo.inc.c")
    names = sorted(set(re.findall(r"GEO_(?:DISPLAY_LIST|ANIMATED_PART)\([^\n]*,\s*(mario_\w+)\)", geo)))
    mapping = [{"displayList": n, "region": body_region_of(n), "id": BODY_REGIONS.index(body_region_of(n)) + 1} for n in names]
    declarations = "\n".join("    if (dl == (void*)%s) return %d;" % (m["displayList"], m["id"]) for m in mapping)
    manifest_checks = "\n".join("    if (body_region_for_dl((void*)%s) != %d) return -%d;" % (m["displayList"], m["id"], i + 1)
                                for i, m in enumerate(mapping))
    extra = '''\n#include "decomp/mario/model.inc.h"
static uint16_t body_region_ids[SM64_GEO_MAX_TRIANGLES];
static uint16_t body_region_current, body_region_count;
static uint8_t body_region_invalid;
static float body_region_matrices[16][16];
static uint8_t body_region_seen[16];
static uint16_t body_region_for_dl(void *dl) {
''' + declarations + '''\n    return 0;
}
SM64_LIB_FN int32_t sm64_body_region_manifest_check(void) {
''' + manifest_checks + "\n    return %d;\n}\n" % len(mapping) + '''
/* This probe is single-threaded; IDs are the most recently rendered Mario only.
   The caller must copy immediately after that actor's native tick. */
SM64_LIB_FN int32_t sm64_body_regions_copy(uint16_t *out, uint32_t capacity) {
    if (!out || capacity < body_region_count) return -1;
    if (body_region_invalid) return -2;
    memcpy(out, body_region_ids, body_region_count * sizeof(uint16_t));
    return body_region_count;
}
SM64_LIB_FN int32_t sm64_body_matrices_copy(float *out, uint8_t *seen, uint32_t regions) {
    if (!out || !seen || regions != 16) return -1;
    memcpy(out, body_region_matrices, sizeof(body_region_matrices));
    memcpy(seen, body_region_seen, sizeof(body_region_seen));
    return 16;
}
'''
    text = read_text(source / "src/gfx_adapter.c")
    text = replace_once(text, "static void process_display_list( void *dl )", extra + "\nstatic void process_display_list( void *dl )")
    text = replace_once(text, "case GFXCMD_Triangle:\n            {", '''case GFXCMD_Triangle:
            {
                if (!body_region_current || body_region_current > 16) body_region_invalid = 1;
                if (body_region_count < SM64_GEO_MAX_TRIANGLES)
                    body_region_ids[body_region_count++] = body_region_current;
                else body_region_invalid = 1;''')
    text = replace_once(text, "    process_display_list( (void*)dl );\n}\n\nvoid gfx_adapter_bind", '''    body_region_current = body_region_for_dl((void*)dl);
    if (body_region_current && body_region_current <= 16) {
        uint16_t region = body_region_current - 1;
        if (!body_region_seen[region]) memcpy(body_region_matrices[region], s_curMatrix, sizeof(s_curMatrix));
        if (body_region_seen[region] < 255) body_region_seen[region]++;
    }
    process_display_list( (void*)dl );
    body_region_current = 0;
}

void gfx_adapter_bind''')
    text = replace_once(text, "    s_outBuffers = outBuffers;", '''    body_region_count = 0; body_region_current = 0; body_region_invalid = 0;
    memset(body_region_seen, 0, sizeof(body_region_seen));
    memset(body_region_matrices, 0, sizeof(body_region_matrices));
    s_outBuffers = outBuffers;''')
    return text


# 2. checked pose API


def pose_overlay(source, tagged_gfx):
    gfx = tagged_gfx
    start = gfx.index("/* This probe is single-threaded;")
    end = gfx.index("\nstatic void process_display_list", start)
    gfx = gfx[:start] + '''/* Internal only: read while the owning checked tick holds body_busy. */
int32_t body_pose_capture_valid(uint32_t geometryCount) {
    if(body_region_invalid || body_region_count!=geometryCount) return 0;
    for(int i=0;i<15;i++)if(body_region_seen[i]!=1)return 0;
    if(body_region_seen[15]>2)return 0; /* Decoration = the wing cap's wings: at most two transforms. */
    for(int i=0;i<256;i++)if(!isfinite(((float*)body_region_matrices)[i]))return 0;
    return 1;
}
void body_pose_capture_copy(uint16_t *ids,float *matrices,uint8_t *seen) {
    memcpy(ids,body_region_ids,body_region_count*sizeof(uint16_t));
    memcpy(matrices,body_region_matrices,sizeof(body_region_matrices));
    memcpy(seen,body_region_seen,sizeof(body_region_seen));
}
''' + gfx[end:]
    # Metal Mario's wing textures: Mario's display lists (compiled against the upstream header) still name them -99/-98;
    # they are extracted into atlas slots 11 and 12 (metal_wings_overlay), so map them there instead of the plain wings.
    gfx = replace_once(gfx, "s_textureIndex = (int)i;", "s_textureIndex = i == -99 ? 11 : i == -98 ? 12 : (int)i;")
    gfx = replace_once(gfx, "if (!body_region_current || body_region_current > 16) body_region_invalid = 1;", '''if (!body_region_current || body_region_current > 16) body_region_invalid = 1;
                /* Stop before any geometry write can exceed the fixed native arrays. */
                if (body_region_count >= SM64_GEO_MAX_TRIANGLES) { body_region_invalid=1; ptr+=4; break; }''')

    native = read_text(source / "src/libsm64.c")
    native = replace_once(native, "static struct AllocOnlyPool *s_mario_geo_pool = NULL;", '#include "pose_api.h"\n\nstatic struct AllocOnlyPool *s_mario_geo_pool = NULL;')
    native = replace_once(native, "    struct GlobalState *globalState;\n};", "    struct GlobalState *globalState;\n    uint64_t body_generation, body_completed_tick;\n    uint8_t body_faulted;\n};")
    native = replace_once(native, "SM64_LIB_FN void sm64_global_init( const uint8_t *rom, uint8_t *outTexture )\n{", '''SM64_LIB_FN void sm64_global_init( const uint8_t *rom, uint8_t *outTexture )
{
    uint32_t thread=(uint32_t)GetCurrentThreadId();
    uint32_t expected=0;
    if(!__atomic_compare_exchange_n(&body_owner_thread,&expected,thread,0,__ATOMIC_ACQ_REL,__ATOMIC_ACQUIRE)&&expected!=thread)return;
    if(__atomic_load_n(&body_busy,__ATOMIC_ACQUIRE))return;''')
    # A same-owner re-init terminates the old world, which releases its owner slot.
    native = replace_once(native, "    s_init_global = true;", "    __atomic_store_n(&body_owner_thread,thread,__ATOMIC_RELEASE);\n    s_init_global = true;")
    native = replace_once(native, "    if( s_init_global )\n        sm64_global_terminate();", "    if( s_init_global ) { body_keep_owner=1; sm64_global_terminate(); body_keep_owner=0; }")
    native = replace_once(native, "SM64_LIB_FN void sm64_global_terminate( void )\n{", '''SM64_LIB_FN void sm64_global_terminate( void )
{
    if(body_owner_status()!=BODY_OK)return;''')
    native = replace_once(native, "    memory_terminate();", "    memory_terminate();\n    if(!body_keep_owner)__atomic_store_n(&body_owner_thread,0,__ATOMIC_RELEASE);")
    native = replace_once(native, "SM64_LIB_FN int32_t sm64_mario_create( float x, float y, float z )\n{", '''SM64_LIB_FN int32_t sm64_mario_create( float x, float y, float z )
{
    if(body_owner_status()!=BODY_OK || body_generation_counter==UINT64_MAX)return -1;''')
    native = replace_once(native, "    struct MarioInstance *newInstance = s_mario_instance_pool.objects[marioIndex];", '''    struct MarioInstance *newInstance = s_mario_instance_pool.objects[marioIndex];
    newInstance->body_generation=++body_generation_counter;
    newInstance->body_completed_tick=0;newInstance->body_faulted=0;''')
    native = replace_once(native, "    gMarioObject = hack_allocate_mario();", '''    gMarioObject = hack_allocate_mario();
    /* No animation was rendered for this actor on area tick zero. Mark the
       previous tick so first render advances startFrame-1 before sampling. */
    gMarioObject->header.gfx.animInfo.animTimer=(uint16_t)(gAreaUpdateCounter-1);''')
    native = replace_once(native, "SM64_LIB_FN void sm64_mario_tick( int32_t marioId,", "static void body_native_tick( int32_t marioId,")
    native = replace_once(native, "    outState->invincTimer = gMarioState->invincTimer;", '''    outState->invincTimer = gMarioState->invincTimer;
    ((struct MarioInstance*)s_mario_instance_pool.objects[marioId])->body_completed_tick++;''')
    native = replace_once(native, "SM64_LIB_FN void sm64_mario_delete( int32_t marioId )\n{", '''SM64_LIB_FN void sm64_mario_delete( int32_t marioId )
{
    if(body_owner_status()!=BODY_OK || marioId<0)return;''')
    # Every remaining legacy entry point is closed before it can read or change shared state. The legacy void
    # functions fail silently because their original ABI has no status return.
    already = {"sm64_global_init", "sm64_global_terminate", "sm64_mario_create", "sm64_mario_delete"}
    guarded = []
    pattern = r"SM64_LIB_FN\s+(void|uint32_t|int32_t|uint16_t|float|bool)\s+(sm64_\w+)\s*\(([^)]*)\)\s*\{"

    def guard(m):
        result, name, parameters = m.group(1, 2, 3)
        if name in already:
            return m.group(0)
        failure = {"void": "", "uint32_t": "UINT32_MAX", "int32_t": "-1", "uint16_t": "UINT16_MAX", "float": "NAN", "bool": "false"}[result]
        condition = "body_owner_status()!=BODY_OK" + (" || marioId<0" if re.search(r"\bmarioId\b", parameters) else "")
        guarded.append(name)
        return m.group(0) + "\n    if(" + condition + ")return " + failure + ";"

    native = re.sub(pattern, guard, native)
    if len(guarded) != 44:
        fail("the libsm64 export list differs from the expected commit (%d guarded exports, expected 44)" % len(guarded))
    native += '\n#include "pose_api.c.inc"\n'

    # The pinned allocation leaves AnimInfo.animTimer and other members indeterminate. The usual graph-node
    # initializer zeroes animTimer, but libsm64's shortened object initializer never calls it. Zero before init.
    objects = replace_once(read_text(source / "src/decomp/game/object_stuff.c"),
                           "nextObj = (struct ObjectNode *) malloc(sizeof(struct Object));",
                           "nextObj = (struct ObjectNode *) calloc(1, sizeof(struct Object));")
    return gfx, native, objects


# 3. silent audio


def absolute_includes(text, folder, source, expected):
    """Overlay files live outside the checkout, so quoted includes next to the original are made absolute."""
    root = source.resolve()
    count = 0

    def absolute(m):
        nonlocal count
        count += 1
        target = (folder / m.group(1)).resolve()
        if not target.is_file():
            return m.group(0)  # found through the unchanged -I list
        if root not in target.parents:
            fail("include escapes the checkout: " + m.group(1))
        return '#include "' + target.as_posix() + '"'

    text = re.sub(r'^#include "([^"]+)"', absolute, text, flags=re.M)
    if count != expected:
        fail("unexpected number of quoted includes (%d, expected %d); the checkout differs from the expected commit" % (count, expected))
    return text


def silent_audio_overlay(source):
    audio = source / "src/decomp/audio"
    text = absolute_includes(read_text(audio / "external.c"), audio, source, 10)
    loader = (source / "src/load_audio_data.h").resolve().as_posix()
    debug_print = (audio / "../../debug_print.h").resolve().as_posix()
    text = replace_once(text, '#include "' + debug_print + '"', '#include "' + debug_print + '"\n#include "' + loader + '"')
    guard = "\n    /* Silent core: sound_init never installed 0xff sentinels; the zeroed list never terminates. */\n    if (!g_is_audio_initialized) return;\n"
    text = replace_once(text, "void stop_sound(u32 soundBits, f32 *pos) {\n", "void stop_sound(u32 soundBits, f32 *pos) {" + guard)
    text = replace_once(text, "void stop_sounds_from_source(f32 *pos) {\n    u8 bank;\n    u8 soundIndex;\n",
                        "void stop_sounds_from_source(f32 *pos) {\n    u8 bank;\n    u8 soundIndex;\n" + guard)
    text = replace_once(text, "static void stop_sounds_in_bank(u8 bank) {\n    u8 soundIndex = sSoundBanks[bank][0].next;\n",
                        "static void stop_sounds_in_bank(u8 bank) {\n    u8 soundIndex;" + guard + "    soundIndex = sSoundBanks[bank][0].next;\n")
    return text


# 4. carry


INTERACT_GRABBABLE = '''
/* Upstream n64decomp/sm64 src/game/interaction.c interact_grabbable (US), restored verbatim except that
   virtual_to_segmented(0x13, o->behavior) == bhvBowser cannot be true for a proxy (libsm64 has no behaviour
   scripts; the Bowser branch is commented out in libsm64's mario_check_object_grab), so push always runs. */
static u32 interact_grabbable(struct MarioState *m, u32 interactType, struct Object *o) {
    if (o->oInteractionSubtype & INT_SUBTYPE_KICKABLE) {
        u32 interaction = determine_interaction(m, o);
        if (interaction & (INT_KICK | INT_TRIP)) {
            attack_object(o, interaction);
            bounce_back_from_attack(m, interaction);
            return FALSE;
        }
    }

    if ((o->oInteractionSubtype & INT_SUBTYPE_GRABS_MARIO)) {
        if (check_object_grab_mario(m, interactType, o)) {
            return TRUE;
        }
    }

    if (able_to_grab_object(m, o)) {
        if (!(o->oInteractionSubtype & INT_SUBTYPE_NOT_GRABBABLE)) {
            m->interactObj = o;
            m->input |= INPUT_INTERACT_OBJ_GRABBABLE;
            return TRUE;
        }
    }

    /* if (script != bhvBowser) */
    push_mario_out_of_object(m, o, -5.0f);

    return FALSE;
}
'''

HELD_OBJECT_PROXY = '''    else if (node->objNode != NULL && node->fnNode.func != NULL && body_carry_is_proxy(node->objNode)) {
        /* Mario carry proxy: no sharedChild to draw and no camera node in libsm64. Build the same held-object
           matrix as the branch above (Mario object throwMatrix rotation/scale, current hand translation,
           grab-pos translation / 4) and give it to the original GEO_CONTEXT_HELD_OBJ callback with an identity
           camera (libsm64 renders in world space), so geo_switch_mario_hand_grab_pos writes the HOLP itself. */
        static Mat4 sCarryIdentity;
        static struct GraphNodeCamera sCarryCamera;
        struct GraphNodeCamera *savedCamera = gCurGraphNodeCamera;
        Mat4 *objectMatrix = gCurGraphNodeObject != NULL ? gCurGraphNodeObject->throwMatrix : &gMatStack[1];
        translation[0] = node->translation[0] / 4.0f;
        translation[1] = node->translation[1] / 4.0f;
        translation[2] = node->translation[2] / 4.0f;
        mtxf_translate(mat, translation);
        mtxf_copy(gMatStack[gMatStackIndex + 1], *objectMatrix);
        gMatStack[gMatStackIndex + 1][3][0] = gMatStack[gMatStackIndex][3][0];
        gMatStack[gMatStackIndex + 1][3][1] = gMatStack[gMatStackIndex][3][1];
        gMatStack[gMatStackIndex + 1][3][2] = gMatStack[gMatStackIndex][3][2];
        mtxf_mul(gMatStack[gMatStackIndex + 1], mat, gMatStack[gMatStackIndex + 1]);
        mtxf_scale_vec3f(gMatStack[gMatStackIndex + 1], gMatStack[gMatStackIndex + 1],
                         node->objNode->header.gfx.scale);
        mtxf_identity(sCarryIdentity);
        sCarryCamera.matrixPtr = &sCarryIdentity;
        gCurGraphNodeCamera = &sCarryCamera;
        node->fnNode.func(GEO_CONTEXT_HELD_OBJ, &node->fnNode.node,
                          (struct AllocOnlyPool *) gMatStack[gMatStackIndex + 1]);
        gCurGraphNodeCamera = savedCamera;
    }
'''


def carry_interaction_overlay(source):
    game = source / "src/decomp/game"
    text = absolute_includes(read_text(game / "interaction.c"), game, source, 16)
    text = replace_once(text, "static struct InteractionHandler sInteractionHandlers[] = {\n",
                        "/* Mario carry overlay: upstream handler restored below; release note is observation only. */\n"
                        "static u32 interact_grabbable(struct MarioState *m, u32 interactType, struct Object *o);\n"
                        "void body_carry_note_release(struct MarioState *m, u32 kind);\n"
                        "static struct InteractionHandler sInteractionHandlers[] = {\n")
    text = replace_once(text, "    { INTERACT_GRABBABLE,      interact_noop },\n", "    { INTERACT_GRABBABLE,      interact_grabbable },\n")
    text = replace_once(text, "        m->heldObj->oPosZ = m->marioBodyState->heldObjLastPosition[2];\n\n        m->heldObj->oMoveAngleYaw = m->faceAngle[1];\n\n        m->heldObj = NULL;\n",
                        "        m->heldObj->oPosZ = m->marioBodyState->heldObjLastPosition[2];\n\n        m->heldObj->oMoveAngleYaw = m->faceAngle[1];\n\n        body_carry_note_release(m, 1);\n        m->heldObj = NULL;\n")
    text = replace_once(text, "        m->heldObj->oPosZ = m->marioBodyState->heldObjLastPosition[2] + 32.0f * coss(m->faceAngle[1]);\n\n        m->heldObj->oMoveAngleYaw = m->faceAngle[1];\n\n        m->heldObj = NULL;\n",
                        "        m->heldObj->oPosZ = m->marioBodyState->heldObjLastPosition[2] + 32.0f * coss(m->faceAngle[1]);\n\n        m->heldObj->oMoveAngleYaw = m->faceAngle[1];\n\n        body_carry_note_release(m, 2);\n        m->heldObj = NULL;\n")
    return text + INTERACT_GRABBABLE


def carry_render_overlay(source):
    game = source / "src/decomp/game"
    text = absolute_includes(read_text(game / "rendering_graph_node.c"), game, source, 10)
    held_end = ("        gCurAnimData = gGeoTempState.data;\n        gMatStackIndex--;\n    }\n\n"
                "    if (node->fnNode.node.children != NULL) {\n        geo_process_node_and_siblings(node->fnNode.node.children);\n    }\n}\n")
    text = replace_once(text, held_end,
                        "        gCurAnimData = gGeoTempState.data;\n        gMatStackIndex--;\n    }\n" + HELD_OBJECT_PROXY
                        + "\n    if (node->fnNode.node.children != NULL) {\n        geo_process_node_and_siblings(node->fnNode.node.children);\n    }\n}\n")
    return replace_once(text, "void geo_process_held_object(struct GraphNodeHeldObject *node) {\n",
                        "int body_carry_is_proxy(struct Object *o);\nvoid geo_process_held_object(struct GraphNodeHeldObject *node) {\n")


def carry_libsm64_overlay(pose_libsm64):
    text = replace_once(pose_libsm64, "    uint8_t body_faulted;\n};\nstruct ObjPool s_mario_instance_pool = { 0, 0 };\n",
                        "    uint8_t body_faulted;\n    struct BodyCarry *carry; /* Mario carry: NULL unless sm64_carry_offer was called for this actor */\n};\n"
                        "struct ObjPool s_mario_instance_pool = { 0, 0 };\n"
                        "static void body_carry_pre_tick(struct MarioInstance *actor);\n"
                        "static void body_carry_post_tick(int32_t id, struct MarioInstance *actor);\n"
                        "static void body_carry_free(struct MarioInstance *actor);\n")
    text = replace_once(text, "newInstance->body_completed_tick=0;newInstance->body_faulted=0;\n",
                        "newInstance->body_completed_tick=0;newInstance->body_faulted=0;newInstance->carry=NULL;\n")
    text = replace_once(text, "    apply_mario_platform_displacement();\n    bhv_mario_update();\n",
                        "    apply_mario_platform_displacement();\n    body_carry_pre_tick((struct MarioInstance *)s_mario_instance_pool.objects[marioId]);\n    bhv_mario_update();\n")
    text = replace_once(text, "    ((struct MarioInstance*)s_mario_instance_pool.objects[marioId])->body_completed_tick++;\n}\n",
                        "    ((struct MarioInstance*)s_mario_instance_pool.objects[marioId])->body_completed_tick++;\n"
                        "    body_carry_post_tick(marioId,(struct MarioInstance*)s_mario_instance_pool.objects[marioId]);\n}\n")
    text = replace_once(text, "    free( gMarioObject );\n    free_area( gCurrentArea );\n",
                        "    body_carry_free((struct MarioInstance *)s_mario_instance_pool.objects[ marioId ]);\n    free( gMarioObject );\n    free_area( gCurrentArea );\n")
    return replace_once(text, '#include "pose_api.c.inc"\n', '#include "pose_api.c.inc"\n#include "carry_api.c.inc"\n')


# compile


def metal_wings_overlay(source):
    """load_tex_data.h/.c with Metal Mario's two wing textures extracted from the ROM (the texture bank right after the
    plain wings, 32x64 RGBA16 each) as atlas slots 11 and 12: the atlas grows from 11 to 13 slots (832x64)."""
    header = read_text(source / "src/load_tex_data.h")
    header = replace_once(header, "    mario_texture_metal_wings_half_1 = -99,\n    mario_texture_metal_wings_half_2,\n    mario_texture_eyes_closed_unused1,",
                          "    mario_texture_metal_wings_half_1,\n    mario_texture_metal_wings_half_2,\n    mario_texture_eyes_closed_unused1 = -97,")
    header = replace_once(header, "#define NUM_USED_TEXTURES 11", "#define NUM_USED_TEXTURES 13")
    header = replace_once(header, "{ 144, 4240, 6288, 8336, 10384, 12432, 14480, 16528, 30864, 32912, 37008 };",
                          "{ 144, 4240, 6288, 8336, 10384, 12432, 14480, 16528, 30864, 32912, 37008, 41104, 45200 };")
    header = replace_once(header, "{ 64, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32 };", "{ 64, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32 };")
    header = replace_once(header, "{ 32, 32, 32, 32, 32, 32, 32, 32, 32, 64, 64 };", "{ 32, 32, 32, 32, 32, 32, 32, 32, 32, 64, 64, 64, 64 };")
    loader = read_text(source / "src/load_tex_data.c")
    return header, loader


def source_files(source):
    """Every .c file the library is made of, in the same folder order as libsm64's Makefile."""
    folders = ["src", "src/decomp", "src/decomp/engine", "src/decomp/include/PR", "src/decomp/game", "src/decomp/pc",
               "src/decomp/pc/audio", "src/decomp/mario", "src/decomp/tools", "src/decomp/audio"]
    files = []
    for folder in folders:
        directory = source / folder
        if directory.is_dir():
            files += [folder + "/" + n for n in sorted(os.listdir(directory), key=str.lower) if n.endswith(".c")]
    return files


def main():
    parser = argparse.ArgumentParser(description="Builds sm64-mario.dll")
    parser.add_argument("--source", required=True, help="libsm64 checkout (see libsm64-source.json for the commit)")
    parser.add_argument("--zig", required=True, help="zig.exe")
    parser.add_argument("--output", required=True, help="where to write sm64-mario.dll")
    args = parser.parse_args()

    source = pathlib.Path(args.source).resolve()
    zig = pathlib.Path(args.zig).resolve()
    output = pathlib.Path(args.output).resolve()
    work = NATIVE / ".cache" / "build"
    if not (source / "src" / "libsm64.c").is_file():
        fail("%s is not a libsm64 checkout (src/libsm64.c not found)" % source)
    if not zig.is_file():
        fail("zig not found: %s" % zig)
    check_source(source)

    (work / "pose").mkdir(parents=True, exist_ok=True)
    (work / "silent").mkdir(exist_ok=True)
    (work / "carry").mkdir(exist_ok=True)
    gfx, pose_libsm64, objects = pose_overlay(source, tag_body_regions(source))
    tex_header, tex_loader = metal_wings_overlay(source)
    outputs = {
        work / "pose" / "load_tex_data.h": tex_header,
        work / "pose" / "load_tex_data.c": tex_loader,
        work / "pose" / "gfx_adapter.c": gfx,
        work / "pose" / "libsm64.c": pose_libsm64,
        work / "pose" / "object_stuff.c": objects,
        work / "silent" / "external.c": silent_audio_overlay(source),
        work / "carry" / "libsm64.c": carry_libsm64_overlay(pose_libsm64),
        work / "carry" / "interaction.c": carry_interaction_overlay(source),
        work / "carry" / "rendering_graph_node.c": carry_render_overlay(source),
    }
    for path, text in outputs.items():
        path.write_text(text, encoding="utf-8", newline="\n")

    replacements = {
        "src/gfx_adapter.c": work / "pose" / "gfx_adapter.c",
        "src/load_tex_data.c": work / "pose" / "load_tex_data.c",
        "src/libsm64.c": work / "carry" / "libsm64.c",
        "src/decomp/game/object_stuff.c": work / "pose" / "object_stuff.c",
        "src/decomp/audio/external.c": work / "silent" / "external.c",
        "src/decomp/game/interaction.c": work / "carry" / "interaction.c",
        "src/decomp/game/rendering_graph_node.c": work / "carry" / "rendering_graph_node.c",
    }
    files = [str(replacements[f]) if f in replacements else f for f in source_files(source)]
    missing = [f for f in replacements if f not in source_files(source)]
    if missing:
        fail("expected source file not in the build: " + missing[0])
    output.parent.mkdir(parents=True, exist_ok=True)
    compile_args = ["cc", "-target", "x86_64-windows-gnu", "-shared", "-O2", "-std=gnu11", "-fno-strict-aliasing", "-Wall",
                    "-Wno-unused-function", "-fvisibility=hidden", "-DSM64_LIB_EXPORT", "-DGBI_FLOATS", "-DVERSION_US",
                    "-DNO_SEGMENTED_MEMORY", "-I", "src/decomp/include", *files, "-o", str(output), "-lm",
                    "-I", "src", "-I", "src/decomp/game", "-I", str(OVERLAY_POSE), "-DBODY_POSE_TESTING=0", "-I", str(OVERLAY_CARRY)]
    env = dict(os.environ)
    for key, folder in (("ZIG_GLOBAL_CACHE_DIR", "zig-global"), ("ZIG_LOCAL_CACHE_DIR", "zig-local"), ("TEMP", "temp"), ("TMP", "temp")):
        (work / folder).mkdir(exist_ok=True)
        env[key] = str(work / folder)
    print("Compiling %d C files with %s ..." % (len(files), zig.name))
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    run = subprocess.run([str(zig), *compile_args], cwd=source, env=env, capture_output=True, creationflags=flags)
    (work / "build.stdout.txt").write_bytes(run.stdout)
    (work / "build.stderr.txt").write_bytes(run.stderr)
    if run.returncode != 0:
        sys.stderr.write(run.stderr.decode(errors="replace")[-8000:])
        fail("the compiler failed (exit %d); full output in %s" % (run.returncode, work / "build.stderr.txt"))
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print("Built %s" % output)
    print("SHA-256 %s" % digest)


if __name__ == "__main__":
    main()
