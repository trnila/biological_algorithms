section .data
  trajectory db `ABCD\n\0XXX`
  c times 20 db 0 



section .text

print:
  mov rax, 1
  mov rdi, 1
  mov rsi, trajectory
  mov rdx, 5
  syscall
  ret

swap:
  mov rsi, 0
  mov rdx, 0

  mov sil, [trajectory + r12] ; a[i]
  mov dl, [trajectory + rdi] ; 
  mov [trajectory + r12], dl
  mov [trajectory + rdi], sil
  ret


global _start
_start:
  call print
  push r12


  mov r12, 0 ; i

.start:
  cmp r12, 4
  jge .end

  ; c[i] < i
  cmp byte [c + r12], r12b
  jge .else

  ; is i even?
  bt r12, 0 ; copy 0 bit to CF
  jc .odd
  ; is even!
  mov rdi, 0
  call swap
  jmp .cont
  .odd:
  mov dil, byte [c + r12]
  call swap
  .cont:
  
  call print

  inc byte [c + r12]
  mov r12, 0
  jmp .start

  .else:
  mov [c + r12], byte 0
  inc r12
  jmp .start

  .end:
  pop r12

  mov rax, 60
  syscall

