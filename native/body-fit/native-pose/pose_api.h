#ifndef MARIO_BODY_POSE_API_H
#define MARIO_BODY_POSE_API_H
#include <stdint.h>
#include <stddef.h>
#include <float.h>

/* Isolated Windows x64 probe. Every library operation belongs to one OS thread. */
__declspec(dllimport) unsigned long __stdcall GetCurrentThreadId(void);
static uint32_t body_owner_thread;
static volatile int32_t body_busy;
static int body_keep_owner;
/* Never reset while the module remains loaded, including global terminate/init. */
static uint64_t body_generation_counter;

enum BodyPoseStatus {
    BODY_OK=0, BODY_NO_WORLD=-1, BODY_WRONG_THREAD=-2, BODY_BUSY=-3,
    BODY_BAD_ACTOR=-4, BODY_BAD_GENERATION=-5, BODY_BAD_TICK=-6,
    BODY_BAD_ARGUMENT=-7, BODY_SHORT_BUFFER=-8, BODY_CALLBACKS=-9,
    BODY_ACTOR_FAULTED=-10, BODY_OVERFLOW=-11, BODY_POSTSTEP_INVALID=-12
};
struct BodyPoseStamp {
    uint32_t schemaVersion;
    int32_t actorId;
    uint64_t generation;
    uint64_t completedTick;
    uint32_t triangleCount;
    uint32_t matrixCount;
    uint32_t matrixFloatCount;
    uint32_t seenByteCount;
};
struct BodyPoseBuffers {
    float *positions, *normals, *colors, *uvs;
    uint16_t *regionIds;
    float *matrices;
    uint8_t *seen;
    uint32_t positionFloats, normalFloats, colorFloats, uvFloats;
    uint32_t regionIdsCapacity, matrixFloats, seenBytes, reserved;
};
int32_t body_pose_capture_valid(uint32_t geometryCount);
void body_pose_capture_copy(uint16_t *ids, float *matrices, uint8_t *seen);
static int32_t body_owner_status(void);
#endif
