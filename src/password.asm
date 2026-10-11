; Eight letters displayed as two four-letter words. No security dependency.
password_open:
    ld a,(help_mode)
    or a
    call nz,toggle_help
    ld a,1
    ld (password_mode),a
    xor a
    ld (password_cursor),a
    ld hl,password_buffer
    ld b,8
password_blank:
    ld (hl),32
    inc hl
    djnz password_blank
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
    ld a,PASSWORD_BANK
    ld (bank_number),a
    call upload_compressed
    call password_draw
    ld a,043h
    ld e,1
    jp reg_write
password_keys:
    ld a,(keys7)
    bit 2,a
    jp nz,password_close
    bit 7,a
    jp nz,password_submit
    ld a,(keys8)
    bit 7,a
    jr nz,password_right
    bit 0,a
    jr nz,password_right
    bit 4,a
    jr nz,password_left
    ld hl,password_buffer
    ld a,(password_cursor)
    ld e,a
    ld d,0
    add hl,de
    ld a,(keys8)
    bit 5,a
    jr nz,password_up
    bit 6,a
    ret z
    ld a,(hl)
    cp 32
    jr z,password_z
    cp 65
    jr nz,password_down
    ld a,33
password_down:
    dec a
    jr password_set
password_z:
    ld a,90
    jr password_set
password_up:
    ld a,(hl)
    cp 32
    jr nz,password_increment
    ld a,64
password_increment:
    inc a
    cp 91
    jr nz,password_set
    ld a,32
password_set:
    ld (hl),a
    jp password_draw
password_right:
    ld a,(password_cursor)
    inc a
    and 7
    ld (password_cursor),a
    jp password_draw
password_left:
    ld a,(password_cursor)
    dec a
    and 7
    ld (password_cursor),a
    jp password_draw
password_submit:
    ld hl,password_buffer
    ld b,8
password_empty_check:
    ld a,(hl)
    cp 32
    jr nz,password_lookup
    inc hl
    djnz password_empty_check
    xor a
    jr password_accept
password_lookup:
    ld ix,password_table
    ld c,0
password_candidate:
    ld hl,password_buffer
    ld b,8
    ld d,0
password_compare:
    ld a,(ix+0)
    cp (hl)
    jr z,password_equal
    inc d
password_equal:
    inc ix
    inc hl
    djnz password_compare
    ld a,d
    or a
    jr z,password_found
    inc c
    ld a,c
    cp LEVEL_COUNT
    jr c,password_candidate
    ld hl,password_invalid
    ld de,03220h
    jp password_text
password_found:
    ld a,c
password_accept:
    ld (stage),a
    xor a
    ld (password_mode),a
    ld a,08h
    ld e,8
    call reg_write
    jp load_stage
password_close:
    xor a
    ld (password_mode),a
    call restore_board
    ld a,08h
    ld e,8
    call reg_write
    call terrain_changed
    ld a,(status_id)
    jp status_line
password_draw:
    ld hl,password_buffer
    ld de,03C2Eh
    call password_words
    ld hl,password_spaces
    ld de,0442Eh
    call password_text
    ld a,(password_cursor)
    cp 4
    jr c,password_cursor_first
    inc a
password_cursor_first:
    add a,a
    add a,a
    add a,02Eh
    ld e,a
    ld d,044h
    ld hl,password_mark
    jp password_text
password_show_help:
    ld a,(stage)
    inc a
    ld b,48
password_help_tens:
    cp 10
    jr c,password_help_digits
    sub 10
    inc b
    jr password_help_tens
password_help_digits:
    add a,48
    ld (password_help_label+7),a
    ld a,b
    ld (password_help_label+6),a
    ld hl,password_help_label
    ld de,06584h
    call password_text
    ld a,(stage)
    ld l,a
    ld h,0
    add hl,hl
    add hl,hl
    add hl,hl
    ld de,password_table
    add hl,de
    ld de,065D4h
    jp password_words
password_help_label: db "STAGE 00 PASSWORD",0
password_show_clear:
    ld hl,password_label
    ld de,05F04h
    call password_text
    ld a,(stage)
    ld l,a
    ld h,0
    add hl,hl
    add hl,hl
    add hl,hl
    ld de,password_table
    add hl,de
    ld de,05F30h
    jp password_words
password_words:
    ld (password_source),hl
    ld (password_dest),de
    ld b,9
    ld c,0
password_word_loop:
    push bc
    ld a,c
    cp 4
    ld a,32
    jr z,password_word_space
    ld hl,(password_source)
    ld a,(hl)
    inc hl
    ld (password_source),hl
password_word_space:
    call password_glyph
    pop bc
    inc c
    djnz password_word_loop
    ret
; A=ASCII; password_dest is the linear SCREEN 5 byte address.
password_glyph:
    cp 48
    jr c,password_glyph_alpha
    cp 58
    jr nc,password_glyph_alpha
    sub 20
    jr password_glyph_valid
password_glyph_alpha:
    sub 64
    jr nc,password_glyph_letter
    xor a
password_glyph_letter:
    cp 27
    jr c,password_glyph_valid
    ld a,27
password_glyph_valid:
    ld l,a
    ld h,0
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ld de,password_font
    add hl,de
    ld (password_pixels),hl
    ld hl,(password_dest)
    ld b,8
password_glyph_row:
    push bc
    push hl
    ld a,h
    rlca
    rlca
    and 3
    call vram_address
    ld hl,(password_pixels)
    ld bc,4*256+VDP
    call write_bytes
    ld (password_pixels),hl
    pop hl
    ld de,128
    add hl,de
    pop bc
    djnz password_glyph_row
    ld hl,(password_dest)
    ld de,4
    add hl,de
    ld (password_dest),hl
    ret
password_text:
    ld (password_dest),de
password_text_loop:
    ld a,(hl)
    or a
    ret z
    push hl
    call password_glyph
    pop hl
    inc hl
    jr password_text_loop
password_mode: db 0
password_cursor: db 0
password_buffer: defs 8,32
password_source: dw 0
password_dest: dw 0
password_pixels: dw 0
password_label: db "PASSWORD",0
password_invalid: db "INVALID PASSWORD",0
password_spaces: db "         ",0
password_mark: db "_",0
    include "assets/passwords.inc"
