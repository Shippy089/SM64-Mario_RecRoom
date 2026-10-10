/* Mario carry proxies. Included only in the separate body-carry libsm64 overlay, after pose_api.c.inc.

   Scope: feed caller-declared grabbable proxies into SM64's ORIGINAL object-interaction path. Nothing here
   decides a grab, a hold, a throw or a drop. SM64 decides all of it:
     - collision: detect_object_hitbox_overlap (upstream sm64 decomp src/game/object_collision.c), Mario as the
       player-list object exactly as check_player_object_collision/check_collision_in_list order it;
     - interaction: interact_grabbable (upstream src/game/interaction.c) restored in the overlay interaction.c,
       which feeds able_to_grab_object (local interaction.c:375) and mario_check_object_grab (local :406);
     - pick up / hold / throw / drop: the unmodified local mario_actions_*.c (act_picking_up :180,
       act_hold_* , act_throwing :257, act_air_throw, check_common_hold_idle_cancels Z -> drop) and
       mario_grab_used_object / mario_drop_held_object / mario_throw_held_object (local interaction.c:276-320);
     - hand anchor: marioBodyState->heldObjLastPosition (HOLP) written by geo_switch_mario_hand_grab_pos
       (local mario_misc.c:551) through the overlay rendering_graph_node.c (see there).
   With no proxy ever offered to an actor, actor->carry stays NULL and none of this code runs. */
#include "decomp/include/object_fields.h"
#include "decomp/game/interaction.h"

#define BODY_CARRY_SLOTS 8
/* Proxies are plain light grabbables (oInteractionSubtype 0, like a bob-omb without its kick subtype); flags must be 0. */

enum BodyCarryPhase { CARRY_NONE=0, CARRY_PICKING_UP=1, CARRY_HOLDING=2, CARRY_THROWING=3, CARRY_PLACING_DOWN=4 };
enum BodyCarryEvent {
    CARRY_EVENT_GRABBED=1u<<0,        /* heldObj became this proxy (mario_grab_used_object) */
    CARRY_EVENT_THROWN=1u<<1,         /* mario_throw_held_object released it */
    CARRY_EVENT_DROPPED=1u<<2,        /* mario_drop_held_object released it (Z, hurt, death, wall, placing down ...) */
    CARRY_EVENT_RELEASED_OTHER=1u<<3, /* heldObj cleared by a path that is neither of the above */
    CARRY_EVENT_KICKED=1u<<4,         /* interact_grabbable -> attack_object on a KICKABLE proxy */
    CARRY_EVENT_RELEASE_OUTSIDE_TICK=1u<<5 /* the release happened in an export between ticks (e.g. take_damage) */
};
enum { CARRY_RELEASE_DROP=1, CARRY_RELEASE_THROW=2 };

struct BodyCarry;
struct BodyCarryProxy {
    struct Object obj;          /* must stay first: SM64 only ever sees &proxy->obj */
    struct BodyCarry *owner;
    uint32_t key;
    uint8_t used, offered;
};
struct BodyCarry {
    struct BodyCarryProxy slots[BODY_CARRY_SLOTS];
    struct Object *heldBefore;
    uint32_t pendingReleaseKind, pendingReleaseKey, pendingReleaseAction, pendingOutsideTick;
    float pendingReleasePos[3];
    int32_t pendingReleaseYaw;
    uint8_t inTick;
    struct BodyCarryState *last;
};
struct BodyCarryState {
    uint32_t schemaVersion;
    int32_t actorId;
    uint64_t generation;
    uint64_t completedTick;
    uint32_t phase;
    uint32_t heldKey;            /* proxy in m->heldObj, 0 if none */
    uint32_t pickingUpKey;       /* proxy in m->usedObj while ACT_PICKING_UP has not grabbed yet */
    uint32_t events;
    uint32_t releaseKey;
    uint32_t releaseKind;        /* CARRY_RELEASE_DROP / CARRY_RELEASE_THROW / 0 */
    uint32_t releaseAction;      /* m->action at the moment the decomp released it */
    uint32_t action;             /* m->action after the tick */
    int32_t releaseYaw;          /* oMoveAngleYaw written by the decomp (= faceAngle[1]) */
    float releasePosition[3];    /* oPosX/Y/Z written by mario_drop_held_object / mario_throw_held_object */
    float holp[3];               /* marioBodyState->heldObjLastPosition */
    float marioVelocity[3];
    float forwardVelocity;
    int32_t faceYaw;             /* m->faceAngle[1] */
    uint32_t grabPos;            /* marioBodyState->grabPos */
    uint32_t kickedKey;
    uint32_t offeredCount;
    uint32_t collidedCount;      /* marioObj->numCollidedObjs from the overlap pass */
};

static const uint8_t body_carry_behavior_tag[4] = {'F','C','R','Y'};
static int body_carry_is_proxy_object(struct Object *o) {
    return o != NULL && o->behavior == (const BehaviorScript *)body_carry_behavior_tag;
}
/* Called from the overlay rendering_graph_node.c. */
int body_carry_is_proxy(struct Object *o) { return body_carry_is_proxy_object(o); }

/* Called from the overlay interaction.c immediately before the decomp writes m->heldObj = NULL in
   mario_drop_held_object / mario_throw_held_object, after it wrote the release pose. Observation only. */
void body_carry_note_release(struct MarioState *m, uint32_t kind) {
    struct Object *o = m->heldObj;
    if (!body_carry_is_proxy_object(o)) return;
    struct BodyCarryProxy *p = (struct BodyCarryProxy *)o;
    struct BodyCarry *c = p->owner;
    c->pendingReleaseKind = kind; c->pendingReleaseKey = p->key; c->pendingReleaseAction = m->action;
    c->pendingOutsideTick = !c->inTick;
    c->pendingReleasePos[0] = o->oPosX; c->pendingReleasePos[1] = o->oPosY; c->pendingReleasePos[2] = o->oPosZ;
    c->pendingReleaseYaw = o->oMoveAngleYaw;
}

/* Upstream sm64 decomp src/game/object_collision.c detect_object_hitbox_overlap, verbatim logic
   (including the missing return when out of radius, which the callers treat as false). */
static s32 body_carry_detect_object_hitbox_overlap(struct Object *a, struct Object *b) {
    f32 sp3C = a->oPosY - a->hitboxDownOffset;
    f32 sp38 = b->oPosY - b->hitboxDownOffset;
    f32 dx = a->oPosX - b->oPosX;
    f32 dz = a->oPosZ - b->oPosZ;
    f32 collisionRadius = a->hitboxRadius + b->hitboxRadius;
    f32 distance = sqrtf(dx * dx + dz * dz);
    if (collisionRadius > distance) {
        f32 sp20 = a->hitboxHeight + sp3C;
        f32 sp1C = b->hitboxHeight + sp38;
        if (sp3C > sp1C) return 0;
        if (sp20 < sp38) return 0;
        if (a->numCollidedObjs >= 4) return 0;
        if (b->numCollidedObjs >= 4) return 0;
        a->collidedObjs[a->numCollidedObjs] = b;
        b->collidedObjs[b->numCollidedObjs] = a;
        a->collidedObjInteractTypes |= b->oInteractType;
        b->collidedObjInteractTypes |= a->oInteractType;
        a->numCollidedObjs++;
        b->numCollidedObjs++;
        return 1;
    }
    return 0;
}

/* Runs inside body_native_tick after apply_mario_platform_displacement and before bhv_mario_update: the same
   place upstream update_objects runs detect_object_collisions (after apply_mario_platform_displacement, before
   update_non_terrain_objects updates Mario). Mario's oIntangibleTimer: bhvMario sets it to 0 in upstream
   behavior_data.c; libsm64 never runs that script (its allocate_object leaves -1), so Mario is treated as the
   tangible player object here, without writing the field. */
static void body_carry_pre_tick(struct MarioInstance *actor) {
    struct BodyCarry *c = actor->carry;
    if (!c) return;
    struct Object *mo = gMarioState->marioObj;
    c->inTick = 1;
    /* clear_object_collision equivalent for the objects this overlay owns. */
    mo->numCollidedObjs = 0; mo->collidedObjInteractTypes = 0;
    for (int i = 0; i < BODY_CARRY_SLOTS; i++) {
        struct Object *o = &c->slots[i].obj;
        if (!c->slots[i].used) continue;
        o->numCollidedObjs = 0; o->collidedObjInteractTypes = 0;
        /* Objects clear their own interact status in their behaviour each frame. */
        o->oInteractStatus = 0;
    }
    for (int i = 0; i < BODY_CARRY_SLOTS; i++) {
        struct BodyCarryProxy *p = &c->slots[i];
        /* A held object is intangible in SM64 (obj_set_held_state -> cur_obj_become_intangible). */
        if (!p->used || !p->offered || &p->obj == gMarioState->heldObj || p->obj.oIntangibleTimer != 0) continue;
        body_carry_detect_object_hitbox_overlap(mo, &p->obj);
    }
    c->heldBefore = gMarioState->heldObj;
}

static uint32_t body_carry_key(struct Object *o) {
    return body_carry_is_proxy_object(o) ? ((struct BodyCarryProxy *)o)->key : 0;
}

static void body_carry_post_tick(int32_t id, struct MarioInstance *actor) {
    struct BodyCarry *c = actor->carry;
    if (!c) return;
    struct MarioState *m = gMarioState;
    struct BodyCarryState s;
    memset(&s, 0, sizeof s);
    s.schemaVersion = 1; s.actorId = id; s.generation = actor->body_generation; s.completedTick = actor->body_completed_tick;
    s.action = m->action;
    s.heldKey = body_carry_key(m->heldObj);
    if (m->heldObj == NULL && m->action == ACT_PICKING_UP) s.pickingUpKey = body_carry_key(m->usedObj);
    if (s.pickingUpKey) s.phase = CARRY_PICKING_UP;
    else if (s.heldKey) {
        if (m->action == ACT_PICKING_UP || m->action == ACT_DIVE_PICKING_UP) s.phase = CARRY_PICKING_UP;
        else if (m->action & ACT_FLAG_THROWING) s.phase = CARRY_THROWING;
        else if (m->action == ACT_PLACING_DOWN) s.phase = CARRY_PLACING_DOWN;
        else s.phase = CARRY_HOLDING;
    }
    if (s.heldKey && c->heldBefore != m->heldObj) s.events |= CARRY_EVENT_GRABBED;
    if (c->pendingReleaseKind) {
        s.events |= c->pendingReleaseKind == CARRY_RELEASE_THROW ? CARRY_EVENT_THROWN : CARRY_EVENT_DROPPED;
        if (c->pendingOutsideTick) s.events |= CARRY_EVENT_RELEASE_OUTSIDE_TICK;
        s.releaseKey = c->pendingReleaseKey; s.releaseKind = c->pendingReleaseKind; s.releaseAction = c->pendingReleaseAction;
        s.releaseYaw = c->pendingReleaseYaw;
        memcpy(s.releasePosition, c->pendingReleasePos, sizeof s.releasePosition);
    } else if (body_carry_is_proxy_object(c->heldBefore) && m->heldObj != c->heldBefore) {
        s.events |= CARRY_EVENT_RELEASED_OTHER; s.releaseKey = body_carry_key(c->heldBefore);
    }
    for (int i = 0; i < BODY_CARRY_SLOTS; i++) {
        struct BodyCarryProxy *p = &c->slots[i];
        if (p->used && (p->obj.oInteractStatus & INT_STATUS_WAS_ATTACKED)) { s.events |= CARRY_EVENT_KICKED; s.kickedKey = p->key; }
        if (p->offered) s.offeredCount++;
        p->offered = 0; /* offers are per tick */
    }
    s.collidedCount = (uint32_t)m->marioObj->numCollidedObjs;
    vec3f_copy(s.holp, m->marioBodyState->heldObjLastPosition);
    vec3f_copy(s.marioVelocity, m->vel);
    s.forwardVelocity = m->forwardVel; s.faceYaw = m->faceAngle[1]; s.grabPos = m->marioBodyState->grabPos;
    *c->last = s;
    c->pendingReleaseKind = 0; c->pendingOutsideTick = 0; c->inTick = 0;
}

static void body_carry_free(struct MarioInstance *actor) {
    if (!actor->carry) return;
    free(actor->carry->last); free(actor->carry); actor->carry = NULL;
}

static int body_carry_bind(int32_t id, uint64_t generation, struct MarioInstance **out) {
    int32_t status = body_owner_status(); if (status) return status;
    struct MarioInstance *actor = body_actor(id); if (!actor) return BODY_BAD_ACTOR;
    if (!generation || generation != actor->body_generation) return BODY_BAD_GENERATION;
    if (actor->body_faulted) return BODY_ACTOR_FAULTED;
    global_state_bind(actor->globalState);
    *out = actor; return BODY_OK;
}

/* Declare one nearby carriable for the NEXT tick (offers are cleared after every tick). SM64 alone decides
   whether Mario touches, faces, grabs, holds, throws or drops it. key != 0 is the caller's stable id.
   Units and axes are SM64 world units in the same frame as sm64_body_tick_copy positions. */
SM64_LIB_FN int32_t sm64_carry_offer(int32_t id, uint64_t generation, uint32_t key, float x, float y, float z,
    float radius, float height, float downOffset, uint32_t flags) {
    struct MarioInstance *actor; int32_t status = body_carry_bind(id, generation, &actor); if (status) return status;
    if (!key || !isfinite(x) || !isfinite(y) || !isfinite(z) || fabsf(x) > 32767 || fabsf(y) > 32767 || fabsf(z) > 32767
        || !isfinite(radius) || !(radius > 0) || radius > 1000 || !isfinite(height) || !(height > 0) || height > 2000
        || !isfinite(downOffset) || downOffset < 0 || downOffset > height || flags != 0)
        return BODY_BAD_ARGUMENT;
    if (!actor->carry) {
        struct BodyCarry *c = calloc(1, sizeof *c);
        struct BodyCarryState *last = calloc(1, sizeof *last);
        if (!c || !last) { free(c); free(last); return BODY_OVERFLOW; }
        c->last = last; actor->carry = c;
    }
    struct BodyCarry *c = actor->carry;
    struct MarioState *m = gMarioState;
    struct BodyCarryProxy *p = NULL;
    for (int i = 0; i < BODY_CARRY_SLOTS && !p; i++) if (c->slots[i].used && c->slots[i].key == key) p = &c->slots[i];
    if (p && p->offered) return BODY_BAD_ARGUMENT; /* one offer per key per tick */
    if (!p) for (int i = 0; i < BODY_CARRY_SLOTS && !p; i++) {
        struct Object *o = &c->slots[i].obj;
        /* Never recycle storage SM64 still points at (held, used or interact object). */
        if (c->slots[i].offered || o == m->heldObj || o == m->usedObj || o == m->interactObj) continue;
        p = &c->slots[i];
        memset(p, 0, sizeof *p);
        p->owner = c; p->key = key; p->used = 1;
        p->obj.behavior = (const BehaviorScript *)body_carry_behavior_tag;
        p->obj.activeFlags = ACTIVE_FLAG_ACTIVE;
        vec3f_set(p->obj.header.gfx.scale, 1.0f, 1.0f, 1.0f); /* geo_obj_init default; sharedChild stays NULL */
    }
    if (!p) return BODY_OVERFLOW;
    p->offered = 1;
    if (&p->obj == m->heldObj) return BODY_OK; /* SM64 owns a held object's pose; the offer only keeps it listed */
    p->obj.oPosX = x; p->obj.oPosY = y; p->obj.oPosZ = z;
    p->obj.hitboxRadius = radius; p->obj.hitboxHeight = height; p->obj.hitboxDownOffset = downOffset;
    p->obj.hurtboxRadius = 0.0f; p->obj.hurtboxHeight = 0.0f;
    p->obj.oInteractType = INTERACT_GRABBABLE;
    p->obj.oInteractionSubtype = flags;
    p->obj.oIntangibleTimer = 0;
    return BODY_OK;
}

/* Last post-tick report for this actor (all zero before the first offer). */
SM64_LIB_FN int32_t sm64_carry_state(int32_t id, uint64_t generation, struct BodyCarryState *out) {
    struct MarioInstance *actor; int32_t status = body_carry_bind(id, generation, &actor); if (status) return status;
    if (!out) return BODY_BAD_ARGUMENT;
    if (!actor->carry) { memset(out, 0, sizeof *out); out->schemaVersion = 1; out->actorId = id; out->generation = generation;
        out->completedTick = actor->body_completed_tick; return BODY_OK; }
    *out = *actor->carry->last; return BODY_OK;
}

/* Raise the ORIGINAL external drop request for the next tick: marioObj->oInteractStatus |= INT_STATUS_MARIO_DROP_OBJECT,
   the flag upstream objects set on Mario. Only act_hold_idle / act_hold_walking / act_hold_jump / act_hold_freefall
   (local mario_actions_*.c) consume it; execute_mario_action clears it at the end of every tick (local mario.c:1786),
   so callers re-assert it each tick until a release event arrives. */
SM64_LIB_FN int32_t sm64_carry_request_drop(int32_t id, uint64_t generation) {
    struct MarioInstance *actor; int32_t status = body_carry_bind(id, generation, &actor); if (status) return status;
    if (!actor->carry || !body_carry_is_proxy_object(gMarioState->heldObj)) return BODY_BAD_ARGUMENT;
    gMarioState->marioObj->oInteractStatus |= INT_STATUS_MARIO_DROP_OBJECT;
    return BODY_OK;
}

SM64_LIB_FN uint32_t sm64_carry_abi(uint32_t item) {
    switch (item) {
        case 0: return sizeof(struct BodyCarryState);
        case 1: return offsetof(struct BodyCarryState, completedTick);
        case 2: return offsetof(struct BodyCarryState, phase);
        case 3: return offsetof(struct BodyCarryState, releasePosition);
        case 4: return offsetof(struct BodyCarryState, holp);
        case 5: return offsetof(struct BodyCarryState, collidedCount);
        case 6: return BODY_CARRY_SLOTS;
        case 7: return 1; /* schema */
        default: return UINT32_MAX;
    }
}
