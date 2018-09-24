CXXFLAGS=-g

all: asm cpp

asm: asm.o
	ld $^ -o $@


%.o: %.asm
	nasm -g -f elf64 -F dwarf $^


clean:
	rm -f *.o asm cpp 
