; Page scrolling preserves logical world state. The camera never moves actors.
camera_manual:
    ld a,(password_mode)
    or a
    ret nz
    ld a,(help_mode)
    or a
    ret nz
    ld a,(map_mode)
    or a
    ret nz
    ld a,(state)
    cp 1
    jr nz,camera_manual_ready
    ld a,1
    ld (paused),a
    ld a,7
    call status_line
camera_manual_ready:
    ld a,(camera_x)
    ld b,a
    ld a,(camera_y)
    ld c,a
    ld a,(params+445)
    cp 16
    jr nz,camera_cycle_row
    ld a,b
    xor 8
    ld b,a
    jp nz,camera_set_xy
camera_cycle_row:
    ld a,(params+235)
    cp 7
    jp c,camera_set_xy
    ld a,c
    xor 6
    ld c,a
    jp camera_set_xy
camera_follow_toggle:
    xor a
    ld (camera_manual_mode),a
    ld a,(help_mode)
    or a
    ret nz
    ld a,(follow_actor)
    xor 1
    ld (follow_actor),a
    jp camera_follow_force
camera_selection:
    ld a,(selected)
    add a,a
    ld e,a
    ld d,0
    ld hl,params+19
    add hl,de
    ld b,(hl)
    inc hl
    ld c,(hl)
    jp camera_position
camera_follow:
    ld a,(camera_manual_mode)
    or a
    ret nz
    ld a,(state)
    cp 1
    ret nz
    ld a,(paused)
    or a
    ret nz
camera_follow_force:
    ld ix,cat_actor
    ld a,(follow_actor)
    or a
    jr z,camera_follow_chosen
    ld ix,rabbit_actor
camera_follow_chosen:
    ld a,(ix+6)
    or a
    jr z,camera_follow_position
    ; Follow the remaining friend automatically after one reaches home.
    ld a,(follow_actor)
    xor 1
    ld (follow_actor),a
    ld ix,rabbit_actor
    or a
    jr nz,camera_follow_position
    ld ix,cat_actor
camera_follow_position:
    ld b,(ix+0)
    ld c,(ix+1)
camera_position:
    ld a,b
    and 8
    ld b,a
    ld a,c
    cp 6
    ld c,0
    jr c,camera_set_xy
    ld c,6
camera_set_xy:
    ld a,(camera_x)
    cp b
    jr nz,camera_changed
    ld a,(camera_y)
    cp c
    ret z
camera_changed:
    ld a,b
    ld (camera_x),a
    ld a,c
    ld (camera_y),a
    call restore_board
    call terrain_changed
    ld a,(status_id)
    jp status_line

toggle_map:
    ld a,(help_mode)
    or a
    call nz,toggle_help
    ld a,(map_mode)
    xor 1
    ld (map_mode),a
    jr z,map_close
    call restore_board
    ld a,0Ah
    ld e,8
    jp reg_write
map_close:
    call restore_board
    ld a,08h
    ld e,8
    call reg_write
    call terrain_changed
    ld a,(status_id)
    jp status_line
camera_x: db 0
camera_y: db 0
follow_actor: db 0
map_mode: db 0

; During execution, cursor arrows browse without resetting either actor.
camera_cursor:
    ld a,(keys8)
    and 0F0h
    ret z
    ld a,1
    ld (camera_manual_mode),a
    ld a,(camera_x)
    ld b,a
    ld a,(camera_y)
    ld c,a
    ld a,(keys8)
    bit 4,a
    jr z,camera_not_left
    ld b,0
camera_not_left:
    bit 7,a
    jr z,camera_not_right
    ld a,(params+445)
    cp 16
    jr nz,camera_not_right
    ld b,8
camera_not_right:
    ld a,(keys8)
    bit 5,a
    jr z,camera_not_up
    ld c,0
camera_not_up:
    bit 6,a
    jp z,camera_set_xy
    ld a,(params+235)
    cp 7
    jp c,camera_set_xy
    ld c,6
    jp camera_set_xy
camera_manual_mode: db 0
