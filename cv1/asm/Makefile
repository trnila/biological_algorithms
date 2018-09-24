CXXFLAGS=-g


main: asm.o
	ld $^


%.o: %.asm
	nasm -g -f elf64 -F dwarf $^



clean:
	rm -f *.o main
