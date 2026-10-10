; A configured chip must not conceal a mechanically important floor.
socket_badge_type:
    push bc
    push de
    push hl
    ld a,(render_index)
    add a,a
    ld e,a
    ld d,0
    ld hl,params+19
    add hl,de
    ld b,(hl)
    inc hl
    ld a,(hl)
    call row_to_index
    add a,b
    ld e,a
    ld hl,params+43
    add hl,de
    ld a,(hl)
    cp 1
    jr z,socket_badge_store
    cp 2
    jr z,socket_badge_store
    cp 6
    jr z,socket_badge_store
    cp 9
    jr z,socket_badge_store
    cp 14
    jr z,socket_badge_store
    cp 18
    jr z,socket_badge_store
    cp 19
    jr z,socket_badge_store
    cp 32
    jr z,socket_badge_store
    cp 35
    jr z,socket_badge_store
    cp 39
    jr z,socket_badge_store
    cp 40
    jr z,socket_badge_store
    xor a
socket_badge_store:
    ld (socket_badge),a
    pop hl
    pop de
    pop bc
    ret
draw_socket_badge:
    ld a,(socket_badge)
    or a
    ret z
    ld l,a
    ld h,0
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ld de,06000h
    add hl,de
    ld a,SPECIAL_BADGE_BANK
    call music_map_bank
    ld a,(patch_y)
    add a,20
    ld (patch_y),a
    ld a,14
    ld (patch_bytes),a
    ld a,8
    ld (patch_rows),a
    jp patch_blit
socket_badge: db 0

; Independent SWAP circuit: gate bit 3. Existing OPEN/FLIP are unchanged.
check_swap_gate:
    ld a,(next_code)
    cp 43
    jr z,twin_pressure_gate
    cp 41
    jr z,empty_pressure_gate
    cp 33
    jr z,swap_gate_one
    cp 34
    jr z,swap_gate_two
    or a
    ret
swap_gate_one:
    ld a,(gate)
    bit 3,a
    jr z,swap_blocked
    or a
    ret
swap_gate_two:
    ld a,(gate)
    bit 3,a
    jr nz,swap_blocked
    or a
    ret
swap_blocked:
    scf
    ret
twin_pressure_gate:
    ld a,(support_count)
    cp 2
    ret
empty_pressure_gate:
    ld a,(pressure)
    or a
    jr nz,swap_blocked
    ret
swap_floor:
    call target_index
    ld hl,params+43
    add hl,de
    ld a,(hl)
    cp 39
    jr nz,swap_repeatable
    ld (hl),40
    jr swap_activate
swap_repeatable:
    cp 32
    ret nz
swap_activate:
    ld a,(gate)
    xor 8
    ld (gate),a
    jp terrain_changed
fragile_depart:
    ld a,(ix+1)
    call row_to_index
    add a,(ix+0)
    ld e,a
    ld d,0
    ld hl,params+43
    add hl,de
    ld a,(hl)
    cp 35
    ret nz
    ld (hl),2
    jp terrain_changed
advanced_tile:
    cp 43
    jr z,draw_twin_pressure_gate
    cp 41
    jr z,draw_empty_pressure_gate
    cp 32
    jr z,draw_swap
    cp 33
    jr z,draw_swap_one
    cp 34
    jr z,draw_swap_two
    jp terrain_bank_default
draw_twin_pressure_gate:
    ld a,(support_count)
    cp 2
    jr nc,draw_twin_open
    or a
    jp z,terrain_bank_default
    ld b,45
    jp terrain_bank_default
draw_twin_open:
    ld b,44
    jp terrain_bank_default
draw_empty_pressure_gate:
    ld a,(pressure)
    or a
    jp nz,terrain_bank_default
    ld b,42
    jp terrain_bank_default
draw_swap:
    ld a,(gate)
    bit 3,a
    jp z,terrain_bank_default
    ld b,36
    jp terrain_bank_default
draw_swap_one:
    ld a,(gate)
    bit 3,a
    jp z,terrain_bank_default
    ld b,37
    jp terrain_bank_default
draw_swap_two:
    ld a,(gate)
    bit 3,a
    jp nz,terrain_bank_default
    ld b,38
    jp terrain_bank_default
