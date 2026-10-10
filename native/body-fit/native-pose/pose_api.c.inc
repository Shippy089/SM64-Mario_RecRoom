/* Included only in the separate libsm64 source overlay after native functions. */
static float body_positions[SM64_GEO_MAX_TRIANGLES*9];
static float body_normals[SM64_GEO_MAX_TRIANGLES*9];
static float body_colors[SM64_GEO_MAX_TRIANGLES*9];
static float body_uvs[SM64_GEO_MAX_TRIANGLES*6];

static int32_t body_owner_status(void) {
    uint32_t owner=__atomic_load_n(&body_owner_thread,__ATOMIC_ACQUIRE);
    if (!owner) return BODY_NO_WORLD;
    if (owner != (uint32_t)GetCurrentThreadId()) return BODY_WRONG_THREAD;
    if (!s_init_global) return BODY_NO_WORLD;
    if (__atomic_load_n(&body_busy,__ATOMIC_ACQUIRE)) return BODY_BUSY;
    return BODY_OK;
}
static struct MarioInstance *body_actor(int32_t id) {
    if (id < 0 || id >= s_mario_instance_pool.size || !s_mario_instance_pool.objects[id]) return NULL;
    return s_mario_instance_pool.objects[id];
}
static struct BodyPoseStamp body_stamp(int32_t id, struct MarioInstance *actor, uint32_t triangles) {
    struct BodyPoseStamp stamp = {1,id,actor->body_generation,actor->body_completed_tick,triangles,0,0,0};
    if (triangles) { stamp.matrixCount=16; stamp.matrixFloatCount=256; stamp.seenByteCount=16; }
    return stamp;
}
SM64_LIB_FN int32_t sm64_body_actor_stamp(int32_t id, struct BodyPoseStamp *out) {
    int32_t status=body_owner_status(); if(status) return status;
    if(!out) return BODY_BAD_ARGUMENT;
    struct MarioInstance *actor=body_actor(id); if(!actor) return BODY_BAD_ACTOR;
    if(actor->body_faulted) return BODY_ACTOR_FAULTED;
    /* Metadata only. It never exposes or validates global last-rendered arrays. */
    *out=body_stamp(id,actor,0); return BODY_OK;
}
SM64_LIB_FN int32_t sm64_body_actor_create(float x,float y,float z,struct BodyPoseStamp *out) {
    int32_t status=body_owner_status(); if(status) return status;
    if(!out || !isfinite(x)||!isfinite(y)||!isfinite(z)||fabsf(x)>32767||fabsf(y)>32767||fabsf(z)>32767) return BODY_BAD_ARGUMENT;
    if(g_debug_print_func || g_play_sound_func)return BODY_CALLBACKS;
    if(body_generation_counter==UINT64_MAX) return BODY_OVERFLOW;
    int32_t id=sm64_mario_create(x,y,z);if(id<0) return BODY_BAD_ACTOR;
    return sm64_body_actor_stamp(id,out);
}
SM64_LIB_FN int32_t sm64_body_actor_delete(int32_t id,uint64_t generation) {
    int32_t status=body_owner_status(); if(status) return status;
    struct MarioInstance *actor=body_actor(id);if(!actor)return BODY_BAD_ACTOR;
    if(!generation||generation!=actor->body_generation)return BODY_BAD_GENERATION;
    sm64_mario_delete(id);return BODY_OK;
}
/* Legacy calls remain available for baseline comparison and count as real ticks.
   During the atomic wrapper they cannot recursively advance another actor. */
SM64_LIB_FN void sm64_mario_tick(int32_t id,const struct SM64MarioInputs *inputs,
    struct SM64MarioState *state,struct SM64MarioGeometryBuffers *geometry) {
    if(body_owner_status()!=BODY_OK || !inputs || !state || !geometry)return;
    struct MarioInstance *actor=body_actor(id);
    if(!actor || actor->body_faulted || actor->body_completed_tick==UINT64_MAX)return;
    if(!__sync_bool_compare_and_swap(&body_busy,0,1))return;
    body_native_tick(id,inputs,state,geometry);
    __sync_lock_release(&body_busy);
}
struct BodyRange {uintptr_t start,end;};
static int body_range(struct BodyRange *range,const void *pointer,size_t bytes) {
    uintptr_t start=(uintptr_t)pointer;
    if(!start || bytes>UINTPTR_MAX-start)return 0;
    range->start=start;range->end=start+bytes;return 1;
}
static int body_finite(const float *values,uint32_t count) {
    for(uint32_t i=0;i<count;i++)if(!isfinite(values[i]))return 0;
    return 1;
}
SM64_LIB_FN int32_t sm64_body_tick_copy(int32_t id,uint64_t generation,uint64_t expectedNextTick,
    const struct SM64MarioInputs *input,const struct BodyPoseBuffers *output,
    struct SM64MarioState *outState,struct BodyPoseStamp *outStamp) {
    int32_t status=body_owner_status();if(status)return status;
    struct MarioInstance *actor=body_actor(id);if(!actor)return BODY_BAD_ACTOR;
    if(!generation || generation!=actor->body_generation)return BODY_BAD_GENERATION;
    if(actor->body_faulted)return BODY_ACTOR_FAULTED;
    if(actor->body_completed_tick==UINT64_MAX)return BODY_OVERFLOW;
    if(!expectedNextTick || expectedNextTick!=actor->body_completed_tick+1)return BODY_BAD_TICK;
    if(!input || !output || !outState || !outStamp)return BODY_BAD_ARGUMENT;
    if(g_debug_print_func || g_play_sound_func)return BODY_CALLBACKS;
    /* Copy caller descriptors before running native code; outputs may not alias. */
    const struct SM64MarioInputs in=*input;const struct BodyPoseBuffers out=*output;
    if(!isfinite(in.camLookX)||!isfinite(in.camLookZ)||!isfinite(in.stickX)||!isfinite(in.stickY)
       ||fabsf(in.camLookX)>1||fabsf(in.camLookZ)>1||(in.camLookX==0&&in.camLookZ==0)
       ||(double)in.stickX*in.stickX+(double)in.stickY*in.stickY>1.0+2.0*FLT_EPSILON
       ||in.buttonA>1||in.buttonB>1||in.buttonZ>1||out.reserved)return BODY_BAD_ARGUMENT;
    if(out.positionFloats<SM64_GEO_MAX_TRIANGLES*9 || out.normalFloats<SM64_GEO_MAX_TRIANGLES*9
       ||out.colorFloats<SM64_GEO_MAX_TRIANGLES*9 ||out.uvFloats<SM64_GEO_MAX_TRIANGLES*6
       ||out.regionIdsCapacity<SM64_GEO_MAX_TRIANGLES ||out.matrixFloats<256 ||out.seenBytes<16)return BODY_SHORT_BUFFER;
    struct BodyRange ranges[11];
    const void *pointers[11]={out.positions,out.normals,out.colors,out.uvs,out.regionIds,out.matrices,out.seen,outState,outStamp,input,output};
    const size_t sizes[11]={sizeof(body_positions),sizeof(body_normals),sizeof(body_colors),sizeof(body_uvs),SM64_GEO_MAX_TRIANGLES*sizeof(uint16_t),256*sizeof(float),16,sizeof(*outState),sizeof(*outStamp),sizeof(*input),sizeof(*output)};
    for(int i=0;i<11;i++) {
        if(!body_range(&ranges[i],pointers[i],sizes[i]))return BODY_BAD_ARGUMENT;
        for(int j=0;j<i;j++)if(ranges[i].start<ranges[j].end&&ranges[j].start<ranges[i].end)return BODY_BAD_ARGUMENT;
    }
    if(!__sync_bool_compare_and_swap(&body_busy,0,1))return BODY_BUSY;
    struct SM64MarioState state={0};
    struct SM64MarioGeometryBuffers geometry={body_positions,body_normals,body_colors,body_uvs,0};
    body_native_tick(id,&in,&state,&geometry);
    uint32_t triangles=geometry.numTrianglesUsed;
    if(actor->body_completed_tick!=expectedNextTick || !triangles || triangles>SM64_GEO_MAX_TRIANGLES
       ||!body_pose_capture_valid(triangles)
       ||!body_finite(state.position,3)||!body_finite(state.velocity,3)||!isfinite(state.faceAngle)||!isfinite(state.forwardVelocity)
       ||!body_finite(body_positions,triangles*9)||!body_finite(body_normals,triangles*9)
       ||!body_finite(body_colors,triangles*9)||!body_finite(body_uvs,triangles*6)) {
        actor->body_faulted=1;__sync_lock_release(&body_busy);return BODY_POSTSTEP_INVALID;
    }
    memcpy(out.positions,body_positions,triangles*9*sizeof(float));memcpy(out.normals,body_normals,triangles*9*sizeof(float));
    memcpy(out.colors,body_colors,triangles*9*sizeof(float));memcpy(out.uvs,body_uvs,triangles*6*sizeof(float));
    body_pose_capture_copy(out.regionIds,out.matrices,out.seen);
    *outState=state;*outStamp=body_stamp(id,actor,triangles);
    __sync_lock_release(&body_busy);return BODY_OK;
}
SM64_LIB_FN uint32_t sm64_body_pose_abi(uint32_t item) {
    switch(item) {
        case 0:return sizeof(struct BodyPoseStamp);case 1:return sizeof(struct BodyPoseBuffers);
        case 2:return offsetof(struct BodyPoseStamp,generation);case 3:return offsetof(struct BodyPoseStamp,completedTick);
        case 4:return offsetof(struct BodyPoseStamp,triangleCount);case 5:return offsetof(struct BodyPoseBuffers,positionFloats);
        case 6:return offsetof(struct BodyPoseBuffers,reserved);case 7:return sizeof(struct SM64MarioState);
        case 8:return 1; /* wing decoration triangles (region 16, up to two transforms) are admitted */
        case 9:return 13; /* texture atlas slots: 13 = Metal Mario's wing textures extracted (832x64); older builds 11 (704x64) */
        default:return UINT32_MAX;
    }
}
#if BODY_POSE_TESTING
/* Separate test DLL only: mutate metadata, never fabricate state or geometry.
   Tests set a counter to its limit and assert rejection before another tick. */
SM64_LIB_FN int32_t sm64_body_test_counter(int32_t id,uint64_t generation,uint64_t completedTick) {
    int32_t status=body_owner_status();if(status)return status;
    struct MarioInstance *actor=body_actor(id);if(!actor)return BODY_BAD_ACTOR;
    if(generation!=actor->body_generation)return BODY_BAD_GENERATION;
    actor->body_completed_tick=completedTick;return BODY_OK;
}
SM64_LIB_FN int32_t sm64_body_test_generation_limit(void) {
    int32_t status=body_owner_status();if(status)return status;
    body_generation_counter=UINT64_MAX;return BODY_OK;
}
#endif
