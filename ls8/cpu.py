"""CPU functionality."""

import sys
# import instructions
from instruction import *

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.ir = 0
        self.fl = 0
        self.IM = self.reg[5]
        self.IS = self.reg[6]
        self.sp = self.reg[7] = 0xF4

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("usage: simple.py filename")
            sys.exit(1)

        filename = sys.argv[1]

        address = 0

        try:
            with open(filename) as f:
                for line in f:

                    # ignore comments
                    comment_split = line.split("#")

                    # strip whitespace
                    num = comment_split[0].strip()

                    # ignore blank lines
                    if num == '':
                        continue

                    val = int(num,2)
                    self.ram[address] = val
                    print(self.ram[address])
                    address += 1

        except FileNotFoundError:
            print("File not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b=None):
        # STRETCH: ALU operations ***
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            self.reg[reg_a] = self.reg[reg_a] & 255
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
            self.reg[reg_a] = self.reg[reg_a] & 255
        elif op == "CMP":
            val_a = self.reg[reg_a] 
            val_b = self.reg[reg_b]
            if val_a < val_b:
                self.fl = 4
            elif val_a > val_b:
                self.fl = 2
            else:
                self.fl = 1
        
        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]   

        elif op == "NOT":
            n = self.reg[reg_a]
            self.reg[reg_a] = self.reg[reg_a] ^ 255

        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]

        elif op == "SHL":
            self.reg[reg_a] = (self.reg[reg_a] * 2 ** self.reg[reg_b]) & 255

        elif op == "MOD":
            self.reg[reg_a] = self.reg[reg_a] % self.reg[reg_b]

        elif op == "SHR":
            self.reg[reg_a] = int(self.reg[reg_a] / 2 ** self.reg[reg_b])

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        """read the value from the given address"""
        return self.ram[address]

    def ram_write(self, address, value):
        """update the given address with the new value provided"""
        self.ram[address] = value
        return

    def stack_push(self, value):
        self.sp -= 1
        self.ram_write(self.sp, value)        

    def stack_pop(self):
        if self.sp < 0xF4:
            self.sp += 1
            return self.ram_read(self.sp - 1)
        else:
            halted = False
            self.trace()
            print("error: stack is empty")


    def run(self):
        """Run the CPU."""
        halted = True
        self.pc = 0

        while halted:
            self.ir = self.ram_read(self.pc)
            print(self.ir)

            if alu_1_param.get(self.ir) is not None:
                self.alu(
                    alu_1_param[self.ir],
                    self.ram_read(self.pc + 1),
                )
                self.pc += 2

            elif alu_2_param.get(self.ir) is not None:
                self.alu(
                    alu_2_param[self.ir],
                    self.ram_read(self.pc + 1),
                    self.ram_read(self.pc + 2)
                )
                self.pc += 3

            elif self.ir == HLT:
                """Halt CPU (and exit the emulator)."""
                halted = True

            elif self.ir == LDI:
                """Set the value of a register to an integer."""
                self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.pc + 2)
                self.pc += 3

            elif self.ir == PRN:
                """ Print numeric value stored in the given register."""
                print(self.reg[self.ram_read(self.pc + 1)])
                self.pc += 2

            elif self.ir == PUSH:
                """Push the value in the given register on the stack."""
                self.stack_push(self.reg[self.ram_read(self.pc + 1)])
                self.pc += 2

            elif self.ir == POP:
                """Pop the value at the top of the stack into the given register."""
                self.reg[self.ram_read(self.pc + 1)] = self.stack_pop()
                self.pc += 2

            elif self.ir == CALL:
                """Calls a subroutine (function) at the address stored in the register."""
                self.stack_push(self.pc + 2)
                self.pc = self.reg[self.ram_read(self.pc + 1)]

            elif self.ir == RET:
                """Return from subroutine."""
                self.pc = self.stack_pop()

            elif self.ir == JMP:
                self.pc = self.reg[self.ram_read(self.pc + 1)]

            elif self.ir == JEQ:
                if self.fl == 1:
                    self.pc = self.reg[self.ram_read(self.pc + 1)]
                else:
                    self.pc += 2
                
            elif self.ir == JNE:
                if self.fl != 1:
                    self.pc = self.reg[self.ram_read(self.pc + 1)]
                else:
                    self.pc += 2

            elif self.ir == ST:
                reg_a = reg[self.ram_read(self.pc + 1)]
                reg_b = reg[self.ram_read(self.pc+ 2)]

                self.ram_write(reg_a, reg_b)

            elif self.ir == LD:
                reg_a = reg[self.ram_read(self.pc + 1)]
                reg_b = reg[self.ram_read(self.pc+ 2)]

                reg_a = self.ram_read(reg_b)

            else:
                # this should not activate unless PC has landed on invalid instruction
                self.trace()
                halted = True