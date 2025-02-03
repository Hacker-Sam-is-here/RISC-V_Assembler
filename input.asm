main:
    addi sp, sp, -16
    addi s0, zero, 10
    addi s1, zero, 5
    add s2, s0, s1
    sub s3, s0, s1
    sw s2, -4(sp)
    lw t0, -4(sp)
loop:
    addi s1, s1, -1
    bne s1, zero, loop
    jal ra, function
    beq zero, zero, end
function:
    addi sp, sp, -4
    sw ra, 0(sp)
    addi t1, zero, 1
    lw ra, 0(sp)
    addi sp, sp, 4
    jalr zero, ra, 0
end:
    addi zero, zero, 0