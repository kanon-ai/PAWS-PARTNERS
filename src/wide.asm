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
    call terrain_changed
    jp map_render
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

; Planning controls share parts and selection with the normal view.
map_keys:
    ld a,(state)
    cp 5
    jr z,map_stuck_keys
    ld a,(keys7)
    bit 2,a
    jr z,map_not_escape
    ld a,(state)
    or a
    jp z,toggle_map
    jp edit_mode
map_not_escape:
    ld a,(keys7)
    bit 7,a
    jr z,map_edit_keys
    ld a,(state)
    cp 1
    jp z,toggle_pause
    cp 3
    jp z,next_stage
    cp 4
    jp z,replay
    or a
    jp z,start_run
    ret
map_stuck_keys:
    ld a,(keys7)
    bit 7,a
    jp nz,edit_mode
    bit 2,a
    jp nz,password_open
    ret
map_edit_keys:
    ld a,(state)
    or a
    ret nz
    ld a,(keys8)
    or a
    ret z
    jp edit_keys
map_draw:
    xor a
    ld (render_index),a
map_draw_loop:
    ld a,(render_index)
    add a,a
    ld e,a
    ld d,0
    ld hl,params+19
    add hl,de
    ld a,(hl)
    call map_times14
    ld b,a
    ld a,(params+445)
    cp 16
    ld a,16
    jr z,map_left_ready
    ld a,72
map_left_ready:
    add a,b
    ld (patch_x),a
    inc hl
    ld a,(hl)
    call map_times14
    add a,22
    ld (patch_y),a
    ld a,(render_index)
    ld e,a
    ld hl,parts
    add hl,de
    ld c,(hl)
    ld a,(state)
    or a
    jr nz,map_no_selection
    ld a,(selected)
    cp e
    jr nz,map_no_selection
    ld a,c
    add a,8
    ld c,a
map_no_selection:
    ld hl,params+428
    add hl,de
    ld a,(hl)
    add a,a
    add a,a
    add a,a
    add a,a
    add a,c
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
    ld a,MAP_TILE_BANK
    call music_map_bank
    ld a,7
    ld (patch_bytes),a
    ld a,14
    ld (patch_rows),a
    call patch_blit
    call socket_badge_type
    ld a,(socket_badge)
    or a
    jr z,map_next_socket
    ld l,a
    ld h,0
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ld de,06000h
    add hl,de
    ld a,MAP_TILE_BANK+1
    call music_map_bank
    ld a,(patch_y)
    add a,10
    ld (patch_y),a
    ld a,4
    ld (patch_rows),a
    call patch_blit
map_next_socket:
    ld hl,render_index
    inc (hl)
    ld a,(params+5)
    cp (hl)
    jp nz,map_draw_loop
    ld a,(state)
    or a
    jp nz,map_run_label
    call part_pointer
    ld a,(hl)
    add a,a
    ld e,a
    ld d,0
    ld hl,map_label_table
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ex de,hl
    ld de,06580h
    jp password_text
map_times14:
    push bc
    ld b,a
    add a,a
    add a,a
    add a,a
    sub b
    add a,a
    pop bc
    ret
map_label_table:
    dw map_empty,map_right,map_left,map_wait2,map_wait4,map_wait6,map_wait8
map_empty: db "EMPTY       ENTER GO  F5 BACK   ",0
map_right: db "TURN RIGHT  ENTER GO  F5 BACK   ",0
map_left: db "TURN LEFT   ENTER GO  F5 BACK   ",0
map_wait2: db "WAIT 2      ENTER GO  F5 BACK   ",0
map_wait4: db "WAIT 4      ENTER GO  F5 BACK   ",0
map_wait6: db "WAIT 6      ENTER GO  F5 BACK   ",0
map_wait8: db "WAIT 8      ENTER GO  F5 BACK   ",0

; The overview is a camera, not a separate simulation. It uses run_tick,
; terrain visual resolution and the normal sprite animation poses.
map_render:
    ld a,(dirty)
    or a
    call nz,map_refresh
    ld hl,satbuf
    ld ix,cat_actor
    xor a
    call draw_actor
    ld ix,rabbit_actor
    ld a,128
    call draw_actor
    jp render_sat
map_refresh:
    ld a,(terrain_refresh)
    or a
    call nz,refresh_terrain
    call map_draw
    call refresh_popup
    xor a
    ld (dirty),a
    ret
map_status:
    ld (status_id),a
    ld a,1
    ld (dirty),a
    ret
map_run_label:
    ld hl,map_running
    ld a,(paused)
    or a
    jr z,map_run_label_state
    ld hl,map_paused
map_run_label_state:
    ld a,(state)
    cp 3
    jr c,map_run_label_write
    ld hl,map_result
    cp 5
    jr nz,map_run_label_write
    ld hl,map_stuck
map_run_label_write:
    ld de,06580h
    jp password_text
map_running: db "RUNNING  ENTER PAUSE  ESC RETRY ",0
map_paused: db "PAUSED   ENTER GO     ESC RETRY ",0
map_result: db "ENTER CONTINUE        ESC RETRY ",0
map_stuck: db "ENTER RETRY           ESC TITLE ",0

; Coordinates use 14-pixel world cells. BC = column,row.
map_patch_xy:
    ld a,b
    call map_times14
    ld b,a
    ld a,(params+445)
    cp 16
    ld a,16
    jr z,map_patch_left
    ld a,72
map_patch_left:
    add a,b
    ld (patch_x),a
    ld a,c
    call map_times14
    add a,22
    ld (patch_y),a
    ret
map_terrain_patch:
    call map_patch_xy
    ld a,(terrain_patch_bank)
    call music_map_bank
    ld a,(terrain_patch_hi)
    ld h,a
    ld l,0
    ; Same source pixels as overview's nearest-neighbour half-size assets.
    ; Pillow selects odd pixel centres for exact 2:1 downsampling.
    ld de,14
    add hl,de
    ld de,map_patch_pixels
    ld b,14
map_sample_row:
    push bc
    ld b,7
map_sample_pair:
    ld a,(hl)
    and 15
    rlca
    rlca
    rlca
    rlca
    ld c,a
    inc hl
    ld a,(hl)
    and 15
    or c
    ld (de),a
    inc de
    inc hl
    djnz map_sample_pair
    ld bc,14
    add hl,bc
    pop bc
    djnz map_sample_row
    ld hl,map_patch_pixels
    ld a,7
    ld (patch_bytes),a
    ld a,14
    ld (patch_rows),a
    call patch_blit
    jp terrain_draw_next
map_patch_pixels: defs 98

map_actor_position:
    push hl
    push de
    ld b,(ix+0)
    ld c,(ix+1)
    call map_patch_xy
    ld a,(patch_x)
    dec a
    ld b,a
    ld a,(patch_y)
    sub 2
    ld c,a
    ld a,(ix+5)
    or a
    jr z,map_actor_ground
    ld d,a
    ld a,(ix+8)
    or a
    ld a,14
    jr z,map_actor_distance
    ld a,28
map_actor_distance:
    sub d
    ld d,a
    ld a,(ix+4)
    or a
    jr z,map_actor_up
    cp 1
    jr z,map_actor_right
    cp 2
    jr z,map_actor_down
    ld a,b
    sub d
    ld b,a
    jr map_actor_ground
map_actor_right:
    ld a,b
    add a,d
    ld b,a
    jr map_actor_ground
map_actor_up:
    ld a,c
    sub d
    ld c,a
    jr map_actor_ground
map_actor_down:
    ld a,c
    add a,d
    ld c,a
map_actor_ground:
    ld a,(ix+8)
    or a
    jr z,map_actor_hop
    ld a,(ix+5)
    ld l,a
    ld h,0
    ld de,jump_heights
    add hl,de
    ld a,(hl)
    srl a
    ld d,a
    ld a,c
    sub d
    ld c,a
map_actor_hop:
    ld a,(state)
    cp 3
    jr nz,map_actor_arrived
    ld a,(tick)
    and 63
    srl a
    ld l,a
    ld h,0
    ld de,clear_hop_heights
    add hl,de
    ld a,(hl)
    srl a
    ld d,a
    ld a,c
    sub d
    ld c,a
    jr map_actor_clip
map_actor_arrived:
    ld a,(ix+6)
    or a
    jr z,map_actor_clip
    ld c,220
map_actor_clip:
    ld a,(state)
    cp 3
    jr c,map_actor_done
    ; Hide sprites under result windows, including the final celebration.
    ld a,b
    cp 192
    jr nc,map_actor_done
    cp 49
    jr c,map_actor_done
    ld a,c
    cp 152
    jr nc,map_actor_done
    cp 24
    jr c,map_actor_done
    ld c,220
map_actor_done:
    pop de
    pop hl
    jp actor_result_done
