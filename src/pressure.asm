; Pressure is sampled once per logical tick, before either actor moves.
pressure: db 0
box_old_code: db 0
support_count: db 0
update_pressure:
    ld hl,params+43
    ld b,192
    ld c,0
pressure_boxes:
    ld a,(hl)
    cp 19
    jr nz,pressure_next_box
    inc c
pressure_next_box:
    inc hl
    djnz pressure_boxes
    ld ix,cat_actor
    call actor_on_plate
    jr z,pressure_rabbit
    inc c
pressure_rabbit:
    ld ix,rabbit_actor
    call actor_on_plate
    jr z,pressure_total
    inc c
pressure_total:
    ld a,c
    cp 2
    jr c,pressure_count_ready
    ld c,2
pressure_count_ready:
    ld a,(support_count)
    ld b,a
    ld a,c
    ld (support_count),a
    or a
    jr z,pressure_bool_ready
    ld a,1
pressure_bool_ready:
    ld d,a
    ld a,(pressure)
    cp d
    ld a,d
    ld (pressure),a
    jp nz,terrain_changed
    ld a,b
    cp c
    ret z
    jp terrain_changed
actor_on_plate:
    ld a,(ix+6)
    or a
    jr nz,not_on_plate
    ld a,(ix+1)
    call row_to_index
    add a,(ix+0)
    ld e,a
    ld d,0
    ld hl,params+43
    add hl,de
    ld a,(hl)
    cp 18
    jr z,on_plate
    cp 30
    jr z,on_plate
not_on_plate:
    xor a
    ret
on_plate:
    ld a,1
    or a
    ret
fixed_floor:
    call target_index
    ld hl,params+43
    add hl,de
    ld a,(hl)
    cp 18
    jp z,terrain_changed
    cp 30
    jr nz,fixed_not_plate
    call terrain_changed
    jr fixed_east
fixed_not_plate:
    cp 28
    jr z,fixed_south
    cp 30
    jr z,fixed_east
    cp 31
    jr z,fixed_east
    sub 23
    cp 4
    ret nc
    ld (ix+4),a
    ret
fixed_south:
    ld a,2
    ld (ix+4),a
    ret
fixed_east:
    ld a,1
    ld (ix+4),a
    ret
pressure_tile:
    cp 32
    jp nc,advanced_tile
    cp 18
    jr z,draw_plate
    cp 20
    jr z,draw_pressure_gate
    cp 28
    jr z,draw_blue_south
    cp 30
    jr z,draw_east_plate
    jp terrain_bank_default
draw_plate:
    call displayed_plate_pressed
    or a
    jp z,terrain_bank_default
    ld b,21
    jp terrain_bank_default
draw_pressure_gate:
    ld a,(pressure)
    or a
    jp z,terrain_bank_default
    ld b,22
    jp terrain_bank_default
draw_blue_south:
    ld a,(gate)
    bit 1,a
    jp z,terrain_bank_default
    ld b,25
    jp terrain_bank_default
draw_east_plate:
    call displayed_plate_pressed
    or a
    jp z,terrain_bank_default
    ld b,29
    jp terrain_bank_default
displayed_plate_pressed:
    push bc
    push ix
    ld ix,cat_actor
    call displayed_actor_matches
    jr nz,displayed_plate_done
    ld ix,rabbit_actor
    call displayed_actor_matches
displayed_plate_done:
    pop ix
    pop bc
    ret
displayed_actor_matches:
    ld a,(ix+6)
    or a
    jr nz,displayed_actor_absent
    ld a,(ix+1)
    call row_to_index
    add a,(ix+0)
    ld c,a
    ld a,(terrain_index)
    cp c
    jr nz,displayed_actor_absent
    ld a,1
    or a
    ret
displayed_actor_absent:
    xor a
    ret

; Rendering only: an admitted actor keeps its gate visually open until departure.
; Never changes terrain codes, pressure, phase or admission checks.
gate_visual_tile:
    push bc
    push de
    push hl
    push ix
    ld b,a
    call gate_visual_is_gate
    jr nz,gate_visual_original
    ld ix,cat_actor
    call gate_visual_actor
    jr nz,gate_visual_open
    ld ix,rabbit_actor
    call gate_visual_actor
    jr z,gate_visual_original
gate_visual_open:
    ld a,b
    cp 20
    ld a,22
    jr z,gate_visual_return
    ld a,b
    cp 33
    ld a,37
    jr z,gate_visual_return
    ld a,b
    cp 34
    ld a,38
    jr z,gate_visual_return
    ld a,b
    inc a
    jr gate_visual_return
gate_visual_original:
    ld a,b
gate_visual_return:
    cp 44
    jr nz,gate_visual_pop
    ld a,(support_count)
    cp 2
    ld a,44
    jr nc,gate_visual_pop
    ld a,(support_count)
    add a,46
gate_visual_pop:
    pop ix
    pop hl
    pop de
    pop bc
    ret
gate_visual_is_gate:
    cp 20
    ret z
    cp 33
    ret z
    cp 34
    ret z
    cp 41
    ret z
    cp 43
    ret
gate_visual_actor:
    ld a,(ix+6)
    or a
    jr nz,gate_visual_absent
    ld a,(ix+1)
    call row_to_index
    add a,(ix+0)
    ld c,a
    ld a,(terrain_index)
    cp c
    jr z,gate_visual_present
    ld a,(ix+5)
    or a
    jr z,gate_visual_absent
    ld a,(ix+10)
    call row_to_index
    add a,(ix+9)
    ld c,a
    ld a,(terrain_index)
    cp c
    jr z,gate_visual_present
gate_visual_absent:
    xor a
    ret
gate_visual_present:
    ld a,1
    or a
    ret
gate_visual_depart:
    ld a,(ix+1)
    call row_to_index
    add a,(ix+0)
    ld e,a
    ld d,0
    ld hl,params+43
    add hl,de
    ld a,(hl)
    call gate_visual_is_gate
    ret nz
    jp terrain_changed
