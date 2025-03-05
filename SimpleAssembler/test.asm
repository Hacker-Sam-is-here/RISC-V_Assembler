main:
    addi x1, x0, 42
    sw x1, 0(x2)
    lw x3, 0(x2)
loop:
    beq x3, x1, exit
    addi x3, x3, -1
    jal x0, loop
exit:
    halt