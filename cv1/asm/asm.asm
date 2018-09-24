%define BUFF_SIZE 128000

section .data
  trajectory: db `ABCDEFGHIJKLMNOPQRSTUVWXYZ`
  c: times 20 db 0 
  out: times BUFF_SIZE db 0
  out_pos: dq 0
  err_args: db `Vstupni chyba\n\0`
  err_args_end:


section .text

print:
  mov ax, ds               ; setup segments
  mov es, ax               ; setup segments

  mov rdi, out             ; destination
  add rdi, [out_pos]
  mov rsi, trajectory      ; source

  mov rcx, r9              ; number of cities to copy
  inc rcx                  ; add newline
  add [out_pos], rcx        ; update size of out buffer
  rep movsb

  cmp [out_pos], dword BUFF_SIZE - 1000
  jge flush
  ret

flush:
  mov rax, 1
  mov rdi, 1
  mov rsi, out
  mov rdx, [out_pos]
  syscall

  mov [out_pos], dword 0

  ret

swap:
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

  mov [trajectory + r9], byte `\n`


  call print
  push r12


  mov r12, 0 ; i

.start:
  cmp r12, r9
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
  mov rdi, 0
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

  call flush

  mov rax, 60
  mov rdi, 0 
  syscall

