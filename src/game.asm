    include "assets/layout.inc"
VDP equ 098h
    org 08000h
    jp entry
params equ 0E800h
parts equ 0E400h
satbuf equ 0E100h
entry:
    di
    call music_init
    ld hl,registers
    ld b,registers_end-registers
init_regs:
    ld e,(hl)
    inc hl
    ld a,(hl)
    inc hl
    call reg_write
    dec b
    djnz init_regs
    xor a
    ld e,16
    call reg_write
    ld hl,initial_palette
    ld bc,32*256+VDP+2
    call write_bytes
    xor a
    ld (stage),a
    ld (tick),a
    ld a,255
    ld (last8),a
    ld (last7),a
    ld (last6),a
    call load_stage
    call password_open
main_loop:
    call vblank
    ld a,(tick)
    inc a
    ld (tick),a
    call keyboard
    ld a,(password_mode)
    or a
    jp nz,presented
    ld a,(help_mode)
    or a
    jp nz,presented
    ld a,(state)
    cp 1
    call z,run_tick
    call render
presented:
    jp main_loop

load_stage:
    xor a
    ld (camera_x),a
    ld (camera_y),a
    ld (map_mode),a
    ld (follow_actor),a
    ld (camera_manual_mode),a
    ld e,1
    call reg_write
    ld a,(stage)
    ld e,a
    add a,a
    add a,e
    ld e,a
    ld d,0
    ld hl,level_table
    add hl,de
    ld a,(hl)
    ld (level_bank),a
    call music_map_bank
    inc hl
    ld e,(hl)
    inc hl
    ld d,(hl)
    ex de,hl
    ld (level_ptr),hl
    ld de,params
    ld bc,446
    ldir
    xor a
    ld hl,0
    call vram_address
    call upload_stage
    call load_sprite_data
    xor a
    ld (state),a
    call clear_parts
    xor a
    ld (selected),a
    call reset_ball
    call render
    ld a,043h
    ld e,1
    call reg_write
    ret

clear_parts:
    ld hl,parts
    ld b,12
    xor a
clear_loop:
    ld (hl),a
    inc hl
    djnz clear_loop
    jp edit_mode
reset_ball:
    ld a,(level_bank)
    call music_map_bank
    ld hl,(level_ptr)
    ld de,43
    add hl,de
    ld de,params+43
    ld bc,192
    ldir
    xor a
    ld (gate),a
    ld (pressure),a
    ld (paused),a
    ld (stuck_frames),a
    dec a
    ld (wait_last_cat),a
    ld (wait_last_rabbit),a
    xor a
    ld hl,cat_actor
    ld de,cat_actor+1
    ld (hl),a
    ld bc,31
    ldir
    ld ix,cat_actor
    ld hl,params
    call init_actor
    ld ix,rabbit_actor
    ld hl,params+440
    call init_actor
    call update_pressure
    call terrain_changed
    ret
init_actor:
    ld a,(hl)
    ld (ix+0),a
    call times28
    add a,14
    ld (ix+2),a
    inc hl
    ld a,(hl)
    ld (ix+1),a
    call times28
    add a,10
    ld (ix+3),a
    inc hl
    ld a,(hl)
    ld (ix+4),a
    ret
edit_mode:
    ld a,(state)
    cp 3
    call nc,restore_board
    xor a
    ld (state),a
    call reset_ball
    xor a
    jp status_line

keyboard:
    in a,(0AAh)
    and 0F0h
    or 8
    out (0AAh),a
    in a,(0A9h)
    ld c,a
    cpl
    ld b,a
    ld a,(last8)
    and b
    ld (keys8),a
    ld a,c
    ld (last8),a
    in a,(0AAh)
    and 0F0h
    or 7
    out (0AAh),a
    in a,(0A9h)
    ld c,a
    cpl
    ld b,a
    ld a,(last7)
    and b
    ld (keys7),a
    ld a,c
    ld (last7),a
    in a,(0AAh)
    and 0F0h
    or 6
    out (0AAh),a
    in a,(0A9h)
    ld c,a
    cpl
    ld b,a
    ld a,(last6)
    and b
    ld b,a
    ld a,c
    ld (last6),a
    ld a,(password_mode)
    or a
    jp nz,password_keys
    bit 7,b
    jp nz,camera_manual
    ld a,(keys7)
    bit 1,a
    jp nz,toggle_map
    ld a,(map_mode)
    or a
    jp nz,map_keys
    ld a,(keys7)
    bit 0,a
    jp nz,camera_follow_toggle
    bit 6,b
    jp nz,password_open
    bit 5,b
    jp nz,toggle_help
    ld a,(help_mode)
    or a
    jr z,normal_keys
    ld a,(keys7)
    bit 2,a
    jp nz,toggle_help
    ret
normal_keys:
    ld a,(state)
    cp 5
    jp z,stuck_keys
    ld a,(keys7)
    bit 2,a
    jp nz,edit_mode
    bit 7,a
    jr z,edit_keys
    ld a,(state)
    cp 1
    jp z,toggle_pause
    cp 3
    jr z,next_stage
    cp 4
    jr z,replay
    cp 2
    jp z,edit_mode
    or a
    jp z,start_run
edit_keys:
    ld a,(state)
    cp 1
    jp z,camera_cursor
    or a
    ret nz
    ld a,(keys8)
    bit 7,a
    call nz,select_next
    ld a,(keys8)
    bit 4,a
    call nz,select_prev
    ld a,(keys8)
    bit 0,a
    call nz,cycle_part
    ld a,(keys8)
    bit 5,a
    call nz,hint
    ld a,(keys8)
    bit 6,a
    jp nz,clear_parts
    ret
next_stage:
    ld a,(stage)
    inc a
    ld (stage),a
    jp load_stage
replay:
    xor a
    ld (stage),a
    jp load_stage
select_next:
    ld a,(selected)
    inc a
    ld b,a
    ld a,(params+5)
    cp b
    ld a,b
    jr nz,select_store
    xor a
select_store:
    ld (selected),a
    ld a,(map_mode)
    or a
    call z,camera_selection
    ld a,1
    ld (dirty),a
    xor a
    jp status_line
select_prev:
    ld a,(selected)
    or a
    jr nz,select_dec
    ld a,(params+5)
select_dec:
    dec a
    jr select_store
part_pointer:
    ld a,(selected)
    ld e,a
    ld d,0
    ld hl,parts
    add hl,de
    ret
cycle_part:
    call part_pointer
    ld c,(hl)
cycle_next:
    inc c
    ld a,c
    cp 7
    jr c,cycle_candidate
    ld c,0
    jr cycle_accept
cycle_candidate:
    ld b,c
    ld a,1
cycle_mask:
    add a,a
    djnz cycle_mask
    ld b,a
    ld a,(params+6)
    and b
    jr z,cycle_next
cycle_accept:
    ld (hl),c
    xor a
    jp status_line
hint:
    call part_pointer
    push hl
    ld hl,params+7
    add hl,de
    ld a,(hl)
    pop hl
    ld (hl),a
    ld a,6
    jp status_line

start_run:
    xor a
    ld (camera_manual_mode),a
    call reset_ball
    ld a,1
    ld (state),a
    ld a,120
    call sound_start
    ld a,1
    jp status_line
toggle_pause:
    ld a,(paused)
    xor 1
    ld (paused),a
    or a
    ld a,1
    jr z,pause_message
    ld a,7
pause_message:
    jp status_line
run_tick:
    ld a,(paused)
    or a
    ret nz
    call update_pressure
    xor a
    ld (who),a
    ld ix,cat_actor
    ld iy,rabbit_actor
    call actor_tick
    ld a,1
    ld (who),a
    ld ix,rabbit_actor
    ld iy,cat_actor
    call actor_tick
    ld a,(cat_actor+6)
    ld b,a
    ld a,(rabbit_actor+6)
    and b
    jp z,check_stuck
    ld a,(stage)
    cp LEVEL_COUNT-1
    ld a,3
    jr nz,duo_clear
    inc a
duo_clear:
    ld (state),a
    push af
    xor a
    ld (sound_time),a
    pop af
    jp status_line

; Actor fields: grid x/y, pixel x/y, direction, steps left,
; arrived, waiting, jumping, reserved destination x/y, unused.
actor_tick:
    ld a,(ix+6)
    or a
    ret nz
    ld a,(ix+11)
    or a
    jr z,actor_not_waiting
    dec (ix+11)
    ret
actor_not_waiting:
    ld a,(ix+5)
    or a
    jp nz,actor_move
    ld (ix+7),1
    ld (ix+8),0
    ld a,(ix+0)
    ld (next_x),a
    ld a,(ix+1)
    ld (next_y),a
    call advance_target
    call inspect_target
    ret c
    call occupied
    ret c
    ld a,(next_code)
    cp 2
    jr nz,check_crate
    ld a,(who)
    or a
    ret z
    call advance_target
    call inspect_target
    ret c
    call occupied
    ret c
    ld a,(next_code)
    cp 1
    ret z
    cp 19
    ret z
    cp 2
    ret z
    cp 5
    ret z
    cp 6
    ret z
    ld (ix+8),1
check_crate:
    ld a,(next_code)
    cp 1
    jr z,crate_found
    cp 19
    jr nz,check_barrier
crate_found:
    ld a,(who)
    or a
    ret nz
    call push_box
    ret c
check_barrier:
    ld a,(next_code)
    cp 5
    ret z
    cp 6
    ret z
    cp 3
    jr nz,check_blue_gate
    ld a,(gate)
    bit 0,a
    ret z
check_blue_gate:
    ld a,(next_code)
    cp 7
    jr z,blue_barrier
    cp 28
    jr nz,check_pressure_gate
blue_barrier:
    ld a,(gate)
    bit 1,a
    ret z
check_pressure_gate:
    call check_swap_gate
    ret c
    ld a,(next_code)
    cp 20
    jr nz,begin_walk
    ld a,(pressure)
    or a
    ret z
begin_walk:
    ld a,(next_x)
    ld (ix+9),a
    ld a,(next_y)
    ld (ix+10),a
    ld a,(ix+8)
    or a
    ld a,14
    jr z,walk_duration
    ld a,28
walk_duration:
    ld (ix+5),a
    ld (ix+7),0
actor_move:
    ld a,(ix+4)
    or a
    jr z,walk_up
    cp 1
    jr z,walk_right
    cp 2
    jr z,walk_down
    dec (ix+2)
    dec (ix+2)
    jr walked
walk_up:
    dec (ix+3)
    dec (ix+3)
    jr walked
walk_right:
    inc (ix+2)
    inc (ix+2)
    jr walked
walk_down:
    inc (ix+3)
    inc (ix+3)
walked:
    dec (ix+5)
    ret nz
    call gate_visual_depart
    call fragile_depart
    ld a,(ix+9)
    ld (ix+0),a
    ld (next_x),a
    ld a,(ix+10)
    ld (ix+1),a
    ld (next_y),a
    ld (ix+8),0
    call target_index
    ld hl,params+43
    add hl,de
    ld a,(hl)
    cp 4
    jr nz,land_blue
    ld a,(gate)
    or 1
    ld (gate),a
    call terrain_changed
land_blue:
    ld a,(hl)
    cp 8
    jr z,blue_landed
    cp 31
    jr nz,land_socket
blue_landed:
    ld a,(gate)
    or 2
    ld (gate),a
    call terrain_changed
land_socket:
    call swap_floor
    call sequence_floor
    call fixed_floor
    ld hl,params+19
    ld de,parts
    ld a,(params+5)
    ld b,a
actor_socket_loop:
    ld a,(ix+0)
    cp (hl)
    inc hl
    jr nz,actor_socket_next
    ld a,(ix+1)
    cp (hl)
    jr nz,actor_socket_next
    ld a,(de)
    or a
    jr z,actor_goal
    cp 3
    jp nc,actor_wait_chip
    cp 1
    ld a,(ix+4)
    jr nz,actor_left
    inc a
    jr actor_turn
actor_left:
    dec a
actor_turn:
    and 3
    ld (ix+4),a
    jr actor_goal
actor_socket_next:
    inc hl
    inc de
    djnz actor_socket_loop
actor_goal:
    ld hl,params+3
    ld a,(who)
    or a
    jr z,goal_pointer
    ld hl,params+443
goal_pointer:
    ld a,(ix+0)
    cp (hl)
    ret nz
    inc hl
    ld a,(ix+1)
    cp (hl)
    ret nz
    ld (ix+6),1
    ld a,95
    jp sound_start

advance_target:
    ld a,(ix+4)
    or a
    jr z,target_up
    cp 1
    jr z,target_right
    cp 2
    jr z,target_down
    ld hl,next_x
    dec (hl)
    ret
target_up:
    ld hl,next_y
    dec (hl)
    ret
target_right:
    ld hl,next_x
    inc (hl)
    ret
target_down:
    ld hl,next_y
    inc (hl)
    ret
target_index:
    ld a,(next_y)
    call row_to_index
    ld e,a
    ld a,(next_x)
    add a,e
    ld e,a
    ld d,0
    ret
inspect_target:
    ld a,(params+445)
    ld b,a
    ld a,(next_x)
    cp b
    jr nc,target_bad
    ld a,(next_y)
    cp 12
    jr nc,target_bad
    call target_index
    ld hl,params+236
    add hl,de
    ld c,(hl)
    ld a,(ix+4)
    xor 2
    ld b,a
    inc b
    ld a,080h
inspect_bit:
    rlca
    djnz inspect_bit
    and c
    jr z,target_bad
    ld hl,params+43
    add hl,de
    ld a,(hl)
    ld (next_code),a
    or a
    ret
target_bad:
    scf
    ret
occupied:
    ld a,(iy+6)
    or a
    jr nz,not_occupied
    ld a,(next_x)
    cp (iy+0)
    jr nz,check_reserved
    ld a,(next_y)
    cp (iy+1)
    jr z,target_bad
check_reserved:
    ld a,(iy+5)
    or a
    jr z,not_occupied
    ld a,(next_x)
    cp (iy+9)
    jr nz,not_occupied
    ld a,(next_y)
    cp (iy+10)
    jr z,target_bad
not_occupied:
    or a
    ret
push_box:
    ld a,(next_code)
    ld (box_old_code),a
    ld a,(next_x)
    ld (box_x),a
    ld a,(next_y)
    ld (box_y),a
    call advance_target
    call inspect_target
    jr c,box_blocked
    call occupied
    jr c,box_blocked
    ld a,(next_code)
    cp 18
    jr z,box_on_plate
    or a
    jr z,box_on_floor
    cp 9
    jr z,box_on_floor
    cp 2
    jr z,box_fill
    cp 6
    jr nz,box_blocked
box_fill:
    ld a,9
    jr box_write
box_on_floor:
    ld a,1
    jr box_write
box_on_plate:
    ld a,19
box_write:
    push af
    call target_index
    ld hl,params+43
    add hl,de
    pop af
    ld (hl),a
    call restore_box_target
    call target_index
    ld hl,params+43
    add hl,de
    xor a
    ld b,a
    ld a,(box_old_code)
    cp 19
    ld a,b
    jr nz,box_restore_floor
    ld a,18
box_restore_floor:
    ld (hl),a
    ld (next_code),a
    call terrain_changed
    or a
    ret
box_blocked:
    call restore_box_target
    scf
    ret
restore_box_target:
    ld a,(box_x)
    ld (next_x),a
    ld a,(box_y)
    ld (next_y),a
    ret

render:
    ld a,(map_mode)
    or a
    jp nz,map_render
    call camera_follow
    ld a,(dirty)
    or a
    call nz,refresh_board
    call sequence_hud
    ld hl,satbuf
    ld ix,cat_actor
    xor a
    call draw_actor
    ld ix,rabbit_actor
    ld a,128
    call draw_actor
render_sat:
    ld (hl),216
    ld a,1
    ld hl,03600h
    call vram_address
    ld hl,satbuf
    ld bc,36*256+VDP
    jp write_bytes
draw_actor:
    ld e,a
    ld a,(state)
    cp 3
    jr nz,actor_normal_pose
    ; Cleared stage: face the player and alternate the existing happy foot poses.
    ld a,e
    add a,64
    ld e,a
    ld a,(tick)
    and 8
    add a,a
    add a,e
    ld e,a
    jr actor_pose
actor_normal_pose:
    ld a,(ix+4)
    add a,a
    add a,a
    add a,a
    add a,a
    add a,a
    add a,e
    ld e,a
    ld a,(ix+5)
    ld b,a
    ld a,(ix+11)
    or b
    jr z,actor_pose
    ld a,(tick)
    and 8
    add a,a
    add a,e
    ld e,a
actor_pose:
    ld a,(map_mode)
    or a
    jp nz,map_actor_position
    ld b,(ix+2)
    ld a,(camera_y)
    call times28
    ld c,a
    ld b,(ix+2)
    ld a,(ix+3)
    sub c
    ld c,a
    ld a,(ix+8)
    or a
    jr z,actor_ground
    push hl
    push de
    ld a,(ix+5)
    ld e,a
    ld d,0
    ld hl,jump_heights
    add hl,de
    ld a,c
    sub (hl)
    ld c,a
    pop de
    pop hl
actor_ground:
    ld a,(state)
    cp 3
    jr nz,actor_clear_hop_done
    push hl
    push de
    ld a,(tick)
    and 63
    srl a
    ld l,a
    ld h,0
    ld de,clear_hop_heights
    add hl,de
    ld a,c
    add a,6
    sub (hl)
    ld c,a
    pop de
    pop hl
actor_clear_hop_done:
    ld a,(camera_y)
    ld b,a
    ld a,(ix+1)
    sub b
    cp 6
    jr c,actor_on_page
    ld c,221
actor_on_page:
    call actor_relative_x
    jr nc,actor_x_visible
    ld c,221
actor_x_visible:
    ld b,a
    dec c
    ld a,(ix+6)
    or a
    jr z,actor_visible
    ld a,(state)
    cp 3
    jr z,actor_visible
    ld c,220
actor_visible:
    ; Sprites must not obscure result-window text (sprite size 32x32).
    ld a,(state)
    cp 3
    jr z,actor_result_clip
    cp 5
    jr nz,actor_result_done
actor_result_clip:
    ld a,b
    cp 192
    jr nc,actor_result_done
    cp 33
    jr c,actor_result_done
    ld a,c
    cp 128
    jr nc,actor_result_done
    cp 32
    jr c,actor_result_done
    ld c,220
actor_result_done:
    ld a,e
    ld d,4
actor_planes:
    call sprite2_attr
    add a,4
    dec d
    jr nz,actor_planes
    ret
sprite2_attr:
    ld (hl),c
    inc hl
    ld (hl),b
    inc hl
    ld (hl),a
    inc hl
    ld (hl),0
    inc hl
    ret

; Bitmap edits happen only when a piece/selection/gate/state changes.
terrain_changed:
    ld a,1
    ld (terrain_refresh),a
    ld (dirty),a
    ret
refresh_board:
    ld a,(terrain_refresh)
    or a
    call nz,refresh_terrain
    xor a
    ld (dirty),a
    ld (render_index),a
refresh_tile:
    ld a,(render_index)
    call socket_xy
    ld a,c
    cp 255
    jr z,refresh_tile_next
    ld a,b
    ld (patch_x),a
    ld a,c
    ld (patch_y),a
    ld a,(render_index)
    ld e,a
    ld d,0
    ld hl,parts
    add hl,de
    ld a,(hl)
    ld c,a
    ld a,(state)
    or a
    jr nz,tile_not_selected
    ld a,(selected)
    cp e
    jr nz,tile_not_selected
    ld a,c
    add a,8
    ld c,a
tile_not_selected:
    call socket_badge_type
    ld hl,params+428
    add hl,de
    ld a,(hl)
    ld b,a
    ld a,(socket_badge)
    or a
    ld a,b
    jr nz,tile_special_bank
    add a,TILE_BANK
    jr tile_bank_ready
tile_special_bank:
    add a,SPECIAL_TILE_BANK
tile_bank_ready:
    call music_map_bank
    ld a,c
    and 15
    add a,a
    add a,060h
    ld h,a
    ld l,0
    call patch28
    call draw_socket_badge
refresh_tile_next:
    ld hl,render_index
    inc (hl)
    ld a,(params+5)
    cp (hl)
    jr nz,refresh_tile
    jp refresh_popup
refresh_popup:
    ld a,(state)
    cp 3
    jr z,result_popup
    cp 5
    jr z,result_popup
    cp 4
    ret nz
    ld a,POPUP_BANK
    call music_map_bank
    ld hl,06000h
    ld a,64
    ld (patch_x),a
    ld a,40
    ld (patch_y),a
    ld a,64
    ld (patch_bytes),a
    ld a,112
    ld (patch_rows),a
    jp patch_blit
result_popup:
    ld a,RESULT_BANK
    call music_map_bank
    ld hl,06000h
    ld a,(state)
    cp 5
    jr nz,result_popup_address
    ld hl,07000h
result_popup_address:
    ld a,64
    ld (patch_x),a
    ld (patch_y),a
    ld (patch_bytes),a
    ld (patch_rows),a
    jp patch_blit
patch28:
    ld a,14
    ld (patch_bytes),a
    ld a,28
    ld (patch_rows),a
patch_blit:
    ld (patch_source),hl
    ld a,(patch_y)
    ld l,a
    ld h,0
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ld a,(patch_x)
    srl a
    ld e,a
    ld d,0
    add hl,de
    ld (patch_dest),hl
patch_row:
    ld hl,(patch_dest)
    ld a,h
    rlca
    rlca
    and 3
    call vram_address
    ld hl,(patch_source)
    ld a,(patch_bytes)
    ld b,a
    ld c,VDP
    call write_bytes
    ld (patch_source),hl
    ld hl,(patch_dest)
    ld de,128
    add hl,de
    ld (patch_dest),hl
    ld hl,patch_rows
    dec (hl)
    jr nz,patch_row
    ret
restore_board:
    xor a
    ld e,1
    call reg_write
    xor a
    ld hl,0
    call vram_address
    call upload_stage
    call load_sprite_data
    ld a,(map_mode)
    or a
    ld a,043h
    jr z,restore_sprite_size
    dec a
restore_sprite_size:
    ld e,1
    call reg_write
    ret
load_sprite_data:
    ld a,1
    ld hl,03800h
    call vram_address
    ld hl,sprite_patterns
    ld d,8
    ld c,VDP
load_pattern_block:
    ld b,0
    call write_bytes
    dec d
    jr nz,load_pattern_block
    ld a,1
    ld hl,03400h
    call vram_address
    ld hl,sprite_colors
    ld bc,128*256+VDP
    jp write_bytes
write_bytes:
    outi
    nop
    nop
    jp nz,write_bytes
    ret
socket_xy:
    add a,a
    ld e,a
    ld d,0
    ld hl,params+19
    add hl,de
    ld a,(camera_x)
    ld b,a
    ld a,(hl)
    sub b
    cp 8
    jr nc,socket_off_page
    call times28
    add a,16
    ld (temp_x),a
    inc hl
    ld a,(camera_y)
    ld b,a
    ld a,(hl)
    sub b
    cp 6
    jr nc,socket_off_page
    call times28
    add a,12
    ld c,a
    ld a,(temp_x)
    ld b,a
    ret
socket_off_page:
    ld c,255
    ret
times28:
    ld b,a
    add a,a
    add a,a
    add a,a
    sub b
    add a,a
    add a,a
    ret

status_line:
    ld b,a
    ld a,(map_mode)
    or a
    ld a,b
    jp nz,map_status
    or a
    jr nz,status_chosen
    call part_pointer
    ld a,(hl)
    cp 3
    jr c,status_turn_label
    ld a,4
status_turn_label:
    add a,9
status_chosen:
    ld (status_id),a
    push af
    ld a,1
    ld (dirty),a
    pop af
    push af
    rrca
    and 7
    add a,STATUS_BANK
    call music_map_bank
    ld a,1
    ld hl,01A00h
    call vram_address
    pop af
    and 1
    rlca
    rlca
    rlca
    rlca
    add a,060h
    ld h,a
    ld l,0
    ld d,16
    ld c,VDP
status_block:
    ld b,0
    call write_bytes
    dec d
    jr nz,status_block
    ld a,(state)
    cp 3
    ret c
    cp 5
    ret nc
    jp password_show_clear
sound_start:
    di
    ld (sound_pitch),a
    ld a,16
    ld (sound_time),a
    ei
    ret
upload_banks:
    ld (banks_left),a
upload_bank:
    ld a,(bank_number)
    call music_map_bank
    ld hl,06000h
    ld d,32
    ld c,VDP
upload_block:
    ld b,0
    call write_bytes
    dec d
    jr nz,upload_block
    ld hl,bank_number
    inc (hl)
    ld hl,banks_left
    dec (hl)
    jr nz,upload_bank
    ret
reg_write:
    di
    push af
    ld a,e
    cp 1
    jr nz,reg_write_plain
    pop af
    or 020h
    jr reg_write_value
reg_write_plain:
    pop af
reg_write_value:
    out (VDP+1),a
    ld a,e
    or 080h
    out (VDP+1),a
    ei
    ret
vram_address:
    ld e,14
    call reg_write
    di
    ld a,l
    out (VDP+1),a
    ld a,h
    and 03Fh
    or 040h
    out (VDP+1),a
    ei
    ret
vblank:
    ld a,(music_vblanks)
vblank_wait:
    ld hl,music_vblanks
    cp (hl)
    jr z,vblank_wait
    ret
registers:
    db 0,06h,1,03h,2,1Fh,5,0EFh,6,0Fh,7,0,8,08h,9,80h
    db 11,0,18,0,19,0,23,0
registers_end:
stage: db 0
state: db 0
status_id: db 0
selected: db 0
direction: db 0
grid_x: db 0
grid_y: db 0
ball_x: db 0
ball_y: db 0
remaining: db 14
gate: db 0
steps: db 0
tick: db 0
last8: db 255
last7: db 255
keys8: db 0
keys7: db 0
bank_number: db 0
banks_left: db 0
render_index: db 0
temp_x: db 0
temp_pattern: db 0
sound_pitch: db 0
sound_time: db 0
dirty: db 1
patch_x: db 0
patch_y: db 0
patch_bytes: db 0
patch_rows: db 0
patch_source: dw 0
patch_dest: dw 0
    include "assets/levels.inc"
    include "assets/palettes.inc"

    include "assets/sprite2.inc"

; Goal-first stage bitmaps use PackBits-like byte runs, bounded at build time.
upload_compressed:
    ld a,(bank_number)
    call music_map_bank
    ld hl,(compressed_start)
    ld c,VDP
unpack_next:
    call rom_byte
    or a
    ret z
    bit 7,a
    jr nz,unpack_literal
    ld b,a
    call rom_byte
    ld d,a
unpack_repeat:
    ld a,d
    out (c),a
    nop
    nop
    djnz unpack_repeat
    jr unpack_next
unpack_literal:
    and 127
    inc a
    ld b,a
unpack_literal_loop:
    call rom_byte
    out (c),a
    nop
    nop
    djnz unpack_literal_loop
    jr unpack_next
rom_byte:
    ld a,(hl)
    inc hl
    push af
    ld a,h
    cp 080h
    jr nz,rom_byte_done
    ld a,(bank_number)
    inc a
    ld (bank_number),a
    call music_map_bank
    ld hl,06000h
rom_byte_done:
    pop af
    ret
apply_weight:
    ld a,(weight)
    ld hl,normal_colors
    or a
    jr z,weight_palette
    ld hl,light_colors
    cp 1
    jr z,weight_palette
    ld hl,heavy_colors
weight_palette:
    push hl
    ld a,1
    ld hl,03400h
    call vram_address
    pop hl
    ld bc,80*256+VDP
    call write_bytes
    ret
float_height:
    ld a,(air_steps)
    or a
    jr z,float_light
    ld b,a
    ld a,(remaining)
    dec b
    jr z,jump_lookup
    add a,14
jump_lookup:
    ld e,a
    ld d,0
    ld hl,jump_heights
    add hl,de
    ld a,(hl)
    ret
float_light:
    ld a,(weight)
    cp 1
    ld a,0
    ret nz
    ld a,(tick)
    and 16
    rrca
    rrca
    rrca
    rrca
    add a,3
    ret
refresh_terrain:
    xor a
    ld (terrain_refresh),a
    ld (terrain_index),a
terrain_draw_loop:
    ld a,(map_mode)
    or a
    jr nz,terrain_visible
    ld a,(terrain_index)
    ld b,a
    ld a,(params+445)
    dec a
    and b
    ld b,a
    ld a,(camera_x)
    ld c,a
    ld a,b
    sub c
    cp 8
    jp nc,terrain_draw_next
    ld a,(terrain_index)
    call index_to_row
    ld b,a
    ld a,(camera_y)
    ld c,a
    ld a,b
    sub c
    cp 6
    jp nc,terrain_draw_next
terrain_visible:
    ld a,(terrain_index)
    ld e,a
    ld d,0
    ld hl,params+43
    add hl,de
    ld a,(hl)
    cp 10
    jp z,terrain_draw_next
    cp 13
    jp z,terrain_draw_next
    or a
    jr nz,terrain_present
    ld hl,params+236
    add hl,de
    ld a,(hl)
    or a
    jp z,terrain_draw_next
    ld b,a
    ld a,FLOOR_BANK
    jr terrain_bank_chosen
terrain_present:
    call gate_visual_tile
    ld b,a
    cp 18
    jp nc,pressure_tile
    cp 14
    jr c,terrain_standard
    ld a,(gate)
    bit 2,a
    jr z,terrain_bank_default
    inc b
    inc b
    jr terrain_bank_default
terrain_standard:
    ld a,(gate)
    bit 0,a
    jr z,terrain_blue
    ld a,b
    cp 3
    jr z,terrain_red_open
    cp 4
    jr nz,terrain_blue
    ld b,11
    jr terrain_blue
terrain_red_open:
    ld b,9
terrain_blue:
    ld a,(gate)
    bit 1,a
    jr z,terrain_bank_default
    ld a,b
    cp 7
    jr z,terrain_blue_open
    cp 8
    jr nz,terrain_bank_default
    ld b,12
    jr terrain_bank_default
terrain_blue_open:
    ld b,9
terrain_bank_default:
    ld a,TERRAIN_BANK
terrain_bank_chosen:
    ld c,a
    ld a,b
terrain_bank_loop:
    cp 16
    jr c,terrain_bank_ready
    sub 16
    inc c
    jr terrain_bank_loop
terrain_bank_ready:
    ld b,a
    ld a,c
    ld (terrain_patch_bank),a
    ld a,b
    add a,a
    add a,060h
    ld (terrain_patch_hi),a
    call terrain_cache_changed
    jp z,terrain_draw_next
    ld a,(terrain_index)
    ld c,0
    ld b,a
    ld a,(params+445)
    ld d,a
    ld a,b
terrain_div8:
    cp d
    jr c,terrain_xy
    sub d
    inc c
    jr terrain_div8
terrain_xy:
    ld b,a
    ld a,(map_mode)
    or a
    jp nz,map_terrain_patch
    ld a,(camera_x)
    ld d,a
    ld a,b
    sub d
    push bc
    call times28
    add a,16
    ld (patch_x),a
    pop bc
    ld a,(camera_y)
    ld b,a
    ld a,c
    sub b
    call times28
    add a,12
    ld (patch_y),a
    ld a,(terrain_patch_bank)
    call music_map_bank
    ld a,(terrain_patch_hi)
    ld h,a
    ld l,0
    call patch28
terrain_draw_next:
    ld hl,terrain_index
    inc (hl)
    ld a,(hl)
    cp 192
    jp nz,terrain_draw_loop
    ret
normal_colors:
    defs 16,15
    defs 16,12
    defs 16,11
    defs 16,10
    defs 16,1
light_colors:
    defs 16,15
    defs 16,13
    defs 16,12
    defs 16,11
    defs 16,1
heavy_colors:
    defs 16,15
    defs 16,14
    defs 16,7
    defs 16,8
    defs 16,1
jump_heights:
    db 0,2,3,5,6,8,9,10,11,12,13,13,14,14,14,14,14,13,13,12,11,10,9,8,6,5,3,2,0
level_ptr: dw 0
level_bank: db 0
weight: db 0
air_steps: db 0
paused: db 0
terrain_refresh: db 1
terrain_index: db 0
terrain_patch_hi: db 0
terrain_code: db 0

terrain_patch_bank: db 56

help_mode: db 0
last6: db 255
launch_delay: db 0
saved_status: db 0
toggle_help:
    ld a,(help_mode)
    xor 1
    ld (help_mode),a
    or a
    jr z,close_help
    ld a,(status_id)
    ld (saved_status),a
    xor a
    ld e,1
    call reg_write
    ld a,0Ah
    ld e,8
    call reg_write
    xor a
    ld hl,0
    call vram_address
    ld hl,06000h
    ld (compressed_start),hl
    ld a,HELP_BANK
    ld (bank_number),a
    call upload_compressed
    call password_show_help
    ld a,043h
    ld e,1
    jp reg_write
close_help:
    call restore_board
    ld a,08h
    ld e,8
    call reg_write
    call terrain_changed
    ld a,(saved_status)
    jp status_line

compressed_start: dw 06000h
upload_stage:
    call invalidate_terrain_cache
    ld a,(stage)
    ld e,a
    add a,a
    add a,a
    add a,e
    ld e,a
    ld a,(map_mode)
    or a
    jr z,upload_camera_page
    inc e
    inc e
    inc e
    inc e
    jr upload_page_chosen
upload_camera_page:
    ld a,(camera_x)
    or a
    jr z,upload_camera_row
    inc e
upload_camera_row:
    ld a,(camera_y)
    or a
    jr z,upload_page_chosen
    inc e
    inc e
upload_page_chosen:
    ld d,0
    ld hl,board_table
    add hl,de
    add hl,de
    add hl,de
    ld a,(hl)
    ld (bank_number),a
    inc hl
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld (compressed_start),de
    jp upload_compressed
    include "assets/board_table.inc"

cat_actor equ 0E500h
rabbit_actor equ 0E510h
who: db 0
next_x: db 0
next_y: db 0
next_code: db 0
box_x: db 0
box_y: db 0

    include "src/password.asm"

    include "src/wide.asm"

; Definitive standstill, not a time limit. Check a second tick so a button
; pressed later in the first tick has a chance to release the waiting actor.
check_stuck:
    ld a,(cat_actor+11)
    ld b,a
    ld a,(rabbit_actor+11)
    or b
    jr nz,stuck_reset
    ld a,(cat_actor+5)
    ld b,a
    ld a,(rabbit_actor+5)
    or b
    jr nz,stuck_reset
    ld a,(cat_actor+6)
    ld b,a
    ld a,(cat_actor+7)
    or b
    jr z,stuck_reset
    ld a,(rabbit_actor+6)
    ld b,a
    ld a,(rabbit_actor+7)
    or b
    jr z,stuck_reset
    ld hl,stuck_frames
    inc (hl)
    ld a,(hl)
    cp 2
    ret c
    ld a,5
    ld (state),a
    ld a,12
    jp status_line
stuck_reset:
    xor a
    ld (stuck_frames),a
    ret
stuck_keys:
    ld a,(keys7)
    bit 7,a
    jp nz,edit_mode
    bit 2,a
    jp nz,password_open
    jp camera_cursor
stuck_frames: db 0

sequence_floor:
    call target_index
    ld hl,params+43
    add hl,de
    ld a,(hl)
    cp 14
    jr nz,sequence_arrow
    ld a,(who)
    or a
    ret nz
    ld a,(gate)
    xor 4
    ld (gate),a
    jp terrain_changed
sequence_arrow:
    cp 15
    ret nz
    ld a,(gate)
    bit 2,a
    ld a,1
    jr z,sequence_arrow_set
    inc a
sequence_arrow_set:
    ld (ix+4),a
    ret
actor_wait_chip:
    sub 2
    call times28
    ld (ix+11),a
    jp actor_goal

sequence_hud:
    ld a,(state)
    cp 1
    ret nz
    ld a,(cat_actor+11)
    call wait_beats
    ld c,a
    ld a,(wait_last_cat)
    cp c
    ld a,0
    jr z,wait_cat_same
    inc a
wait_cat_same:
    ld (wait_changed),a
    ld a,c
    ld (wait_last_cat),a
    add a,48
    ld (wait_text+9),a
    ld a,(rabbit_actor+11)
    call wait_beats
    ld c,a
    ld a,(wait_last_rabbit)
    cp c
    jr z,wait_rabbit_same
    ld a,1
    ld (wait_changed),a
wait_rabbit_same:
    ld a,c
    ld (wait_last_rabbit),a
    add a,48
    ld (wait_text+20),a
    ld a,(wait_changed)
    or a
    ret z
    ld a,(status_id)
    call status_line
    ld a,(wait_last_cat)
    ld b,a
    ld a,(wait_last_rabbit)
    or b
    ret z
    ld hl,wait_text
    ld de,06484h
    jp password_text
wait_beats:
    ld b,0
    or a
    ret z
wait_beat_loop:
    inc b
    sub 14
    jr c,wait_beat_done
    jr nz,wait_beat_loop
wait_beat_done:
    ld a,b
    ret
wait_text: db "WAIT CAT 0  RABBIT  0          ",0
wait_last_cat: db 255
wait_last_rabbit: db 255
wait_changed: db 0

    include "src/pressure.asm"
    include "src/advanced.asm"
    include "src/music.asm"

; v2 level width is 8 or 16. Preserve BC for callers holding a column there.
row_to_index:
    push bc
    ld b,a
    ld a,(params+445)
    cp 16
    ld a,b
    pop bc
    jr nz,row_index_eight
    add a,a
row_index_eight:
    add a,a
    add a,a
    add a,a
    ret
index_to_row:
    push bc
    ld b,a
    ld a,(params+445)
    cp 16
    ld a,b
    pop bc
    jr nz,index_row_eight
    srl a
index_row_eight:
    srl a
    srl a
    srl a
    ret

; Derive signed screen X from world tile and in-flight progress. Pixel bytes
; alone wrap at x=256 and cannot safely decide whether a sprite is on screen.
actor_relative_x:
    push bc
    push de
    push hl
    ld a,(camera_x)
    ld b,a
    ld a,(ix+0)
    sub b
    cp 8
    jr nc,relative_x_hidden
    call times28
    add a,14
    ld l,a
    ld h,0
    ld a,(ix+5)
    or a
    jr z,relative_x_done
    ld b,a
    ld a,(ix+8)
    or a
    ld a,14
    jr z,relative_x_duration
    ld a,28
relative_x_duration:
    sub b
    add a,a
    ld e,a
    ld d,0
    ld a,(ix+4)
    cp 1
    jr z,relative_x_right
    cp 3
    jr nz,relative_x_done
    or a
    sbc hl,de
    jr relative_x_done
relative_x_right:
    add hl,de
relative_x_done:
    ld a,h
    or a
    jr nz,relative_x_hidden
    ld a,l
    cp 240
    jr nc,relative_x_hidden
    or a
    jr relative_x_return
relative_x_hidden:
    xor a
    scf
relative_x_return:
    pop hl
    pop de
    pop bc
    ret

; Cache the final terrain bank/pattern, not logical gate state. Socket overlays
; remain on top; unrelated terrain refreshes must not erase them first.
invalidate_terrain_cache:
    push af
    push bc
    push de
    push hl
    ld hl,terrain_visual_cache
    ld de,terrain_visual_cache+1
    ld bc,383
    ld (hl),255
    ldir
    pop hl
    pop de
    pop bc
    pop af
    ret
terrain_cache_changed:
    ld a,(terrain_index)
    ld l,a
    ld h,0
    add hl,hl
    ld de,terrain_visual_cache
    add hl,de
    ld a,(terrain_patch_bank)
    cp (hl)
    jr nz,terrain_cache_update
    inc hl
    ld a,(terrain_patch_hi)
    cp (hl)
    ret z
    dec hl
terrain_cache_update:
    ld a,(terrain_patch_bank)
    ld (hl),a
    inc hl
    ld a,(terrain_patch_hi)
    ld (hl),a
    ld a,1
    or a
    ret
terrain_visual_cache: defs 384,255

clear_hop_heights:
    db 0,0,0,0,1,2,4,6,8,9,9,8,6,4,2,1
    db 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
