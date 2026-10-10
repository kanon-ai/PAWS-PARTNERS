; Fixed VBlank PSG playback. Main renderer can map ROM independently.
; E600:E700 IM2 vectors, E7E7 trampoline; no BIOS ISR/VDP command use.
music_init:
    ld a,1
    ld (password_mode),a
    ld hl,0E600h
    ld de,0E601h
    ld bc,256
    ld (hl),0E7h
    ldir
    ld a,0C3h
    ld (0E7E7h),a
    ld hl,music_irq
    ld (0E7E8h),hl
    ld a,0E6h
    ld i,a
    im 2
    xor a
    out (VDP+1),a
    ld a,08Fh
    out (VDP+1),a
    ld a,7
    out (0A0h),a
    in a,(0A2h)
    and 0C0h
    ld (music_io),a
    ret

music_map_bank:
    di
    ld (06800h),a
    ld (music_bank),a
    ei
    ret

music_irq:
    push af
    push bc
    push de
    push hl
    in a,(VDP+1)
    bit 7,a
    jp z,music_irq_done
    ld hl,music_vblanks
    inc (hl)
    ld a,(password_mode)
    or a
    jp nz,music_silence
    ld a,(state)
    cp 5
    jp z,music_silence
    ld a,MUSIC_BANK
    ld (06800h),a
    ld a,(music_running)
    or a
    jp nz,music_continue
    inc a
    ld (music_running),a
    ld hl,06000h
    ld a,(hl)
    inc hl
    ld (music_position),hl
    ld (music_delay),a
music_continue:
    ld a,(music_delay)
    or a
    jp z,music_packet
    dec a
    ld (music_delay),a
    jp nz,music_output
music_packet:
    ld hl,(music_position)
    ld b,(hl)
    inc hl
music_write_next:
    ld a,b
    or a
    jp z,music_next_packet
    ld e,(hl)
    inc hl
    ld d,0
    push hl
    ld hl,music_shadow
    add hl,de
    ex de,hl
    pop hl
    ld a,(hl)
    ld (de),a
    inc hl
    ; Envelope register is a trigger, so only write when present in stream.
    ld a,e
    cp (music_shadow+13) & 255
    jp nz,music_not_envelope
    ld a,13
    out (0A0h),a
    dec hl
    ld a,(hl)
    out (0A1h),a
    inc hl
music_not_envelope:
    djnz music_write_next
music_next_packet:
    ld a,(hl)
    inc hl
    cp 255
    jp nz,music_store_next
    ld hl,06001h
    xor a
    ld de,(music_loops)
    inc de
    ld (music_loops),de
music_store_next:
    ld (music_position),hl
    ld (music_delay),a
    or a
    jp z,music_packet
music_output:
    ld a,(music_bank)
    ld (06800h),a
    ld hl,music_shadow
    ld c,0
music_output_loop:
    ld a,c
    out (0A0h),a
    ld a,(hl)
    ld b,a
    ld a,c
    cp 7
    ld a,b
    jp nz,music_output_value
    and 03Fh
    ld b,a
    ld a,(music_io)
    or b
music_output_value:
    out (0A1h),a
    inc hl
    inc c
    ld a,c
    cp 13
    jp nz,music_output_loop
    ; Brief C-channel SFX borrow percussion, never either melodic channel.
    ld a,(sound_time)
    or a
    jp z,music_irq_done
    dec a
    ld (sound_time),a
    jp z,music_irq_done
    ld a,4
    out (0A0h),a
    ld a,(sound_pitch)
    out (0A1h),a
    ld a,5
    out (0A0h),a
    xor a
    out (0A1h),a
    ld a,7
    out (0A0h),a
    ld a,(music_shadow+7)
    and 03Bh
    or 020h
    ld b,a
    ld a,(music_io)
    or b
    out (0A1h),a
    ld a,10
    out (0A0h),a
    ld a,7
    out (0A1h),a
    jp music_irq_done
music_silence:
    xor a
    ld (music_running),a
    ld (sound_time),a
    ld a,8
    ld b,3
music_mute_loop:
    out (0A0h),a
    ld c,a
    xor a
    out (0A1h),a
    ld a,c
    inc a
    djnz music_mute_loop
music_irq_done:
    pop hl
    pop de
    pop bc
    pop af
    ei
    reti
music_shadow: defs 14,0
music_position: dw 06001h
music_delay: db 0
music_running: db 0
music_vblanks: db 0
music_bank: db 3
music_io: db 080h
music_loops: dw 0
