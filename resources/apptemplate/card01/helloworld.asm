INCLUDE "libcarde.asm"

org 100h
.main:
	ld hl,.palette
	ld de,00F0h
	ld c,2h
	API 7Eh ;SetBackgroundPalette
	ld hl,010Fh
	ld de,0101h
	ld bc,1004h
	API 90h ;CreateRegion
	ld (.region),a
	ld de,0100h
	API 98h ;SetTextColor
	ld a,14h
	API 0h ;FadeIn
.loop:
	ld a,(.region)
	ld bc,.string
	ld de,0000h
	API 99h ;DrawText
	WAIT 1h
	ld hl,(9F02h)
	ld a,2h
	and l
	jp z, .loop
	ld a,14h
	API 1h ;FadeOut
	ld a,2
	APIEXT 0h ;Exit
.palette:
	dw 0000h,7FFFh
.region:
	db 0
.string:
	db "Hello World!",0