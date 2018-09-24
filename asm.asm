section .data
  trajectory: db `ABCD\n\0XXX`
  c: times 20 db 0 
  out: times 200 db 0
  err_args: db `Vstupni chyba\n\0`
  err_args_end:


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
  ; argc == 2
  cmp [rsp], dword 2
  je .args_ok

  ; write(2, err_args, len(err_args)
  mov rax, 1                    ; SYS_WRITE
  mov rdi, 2                    ; stderr
  mov rsi, err_args
  mov rdx, err_args_end - err_args
  syscall

  ; exit(1)
  mov rax, 60                   ; SYS_EXIT
  mov rdi, 1
  syscall

  .args_ok:
  
  ; parse argument
  mov rdi, [rsp + 16]           ; argv[1]
  mov rsi, 10                   ; base
  mov rax, 0                    ; converted number

  .loop:
    cmp byte [rdi], 0           ; is \0
    je .endloop

    mul rsi                     ; multiply by base 10
    add al, [rdi]               ; += ascii number
    sub al, '0'                 ; substract '0' from ascii number
    
    inc rdi                     ; move to the next character 
    jmp .loop
  .endloop:

  mov r9, rax                   ; r9 = number of cities


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

