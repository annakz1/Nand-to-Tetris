// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
    // n = num of screen words + 1
    @8192
    D=A
    @n
    M=D
(LOOP)
    // i = 0
    @i
    M =0
    // if no key is pressed: KBD =0 - goto WHITE
    @KBD
    D=M
    @WHITE
    D;JEQ
    // if key was pressed: KBD >0 - goto BLACK
    @BLACK
    D;JGT
    // goto LOOP
    @LOOP
    0;JMP
(BLACK)
    // if (i == n) goto LOOP
    @i
    D=M
    @n
    D=D-M
    @LOOP
    D;JEQ
    // RAM[SCREEN + i] = -1
    @SCREEN
    D=A
    @i
    A=D+M
    M= -1
    // i = i + 1
    @i
    M=M+1
    // goto BLACK
    @BLACK
    0;JMP
(WHITE)
    // if (i == n) goto LOOP
    @i
    D=M
    @n
    D=D-M
    @LOOP
    D;JEQ
    // RAM[SCREEN + i] = 0
    @SCREEN
    D=A
    @i
    A=D+M
    M= 0
    // i = i + 1
    @i
    M=M+1
    // goto WHITE
    @WHITE
    0;JMP
