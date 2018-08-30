# Global variables for LMC components
memory = [0] * 100
pc = 0
accum = 0
inbox = []
outbox = []
running = True  # Set to False when HLT is executed
dic1 = {} # For using labels
dic2 = {} # For using labels

# Instruction numbers $ A little different from the actual number
HLT = 0
ADD = 1
SUB = 2
STA = 3
LDA = 4
BRA = 5
BRZ = 6
INP = 7
OUT = 8

# ---------------- LMC Component Interfaces ------------------

def readMem(addr):
    """Returns value at address `addr` in memory, or 0 if `addr` is out of range"""
    if 0 <= addr < len(memory):
        return memory[addr]
    else:
        return 0

def writeMem(addr, val):
    """Writes `val` to memory cell at address `addr`"""
    if 0 <= addr < len(memory) and 0 <= val <= 999:
        memory[addr] = val

def readAccum():
    """Returns value of accumulator"""
    return accum

def writeAccum(val: int):
    """Writes `val` to accumulator, if 0 <= `val` <= 999"""
    global accum
    if 0 <= val <= 999:
        accum = val

def readPC():
    """Returns current program counter value"""
    return pc

def writePC(val):
    """Writes `val` to program counter, if 0 <= `val` <= 999"""
    global pc
    if 0 <= val < len(memory):
        pc = val

def writeInbox(val):
    """Writes `val` to inbox"""
    global inbox
    inbox = val

def readInbox():
    """Removes and returns first number from inbox. If inbox is empty, returns 0."""
    if len(inbox) == 0:
        return 0
    else:
        return inbox.pop(0)

def writeOutbox(val):
    """Places `val` at end of outbox"""
    outbox.append(val)

# ------------ Fetch / Decode / Execute Functions ------------

def fetch():
    """Fetches and returns next instruction indicated by PC. Increments PC."""
    pcval = readPC()
    instr = readMem(pcval)
    writePC(pcval + 1)
    return instr

def decode(instr: int) -> (int, int):
    """Decodes instruction `instr`, returning its (opcode, operand)"""
    return (instr // 100, instr % 100)

def execute(opcode: int, operand: int):
    """Executes instruction corresponding to `opcode`, using `operand` if needed"""
    global running
    if opcode == HLT:
        running = False
    elif opcode == ADD:
        writeAccum(readAccum() + readMem(operand))
    elif opcode == SUB:
        writeAccum(readAccum() - readMem(operand))
    elif opcode == STA:
        writeMem(operand, readAccum())
    elif opcode == LDA:
        writeAccum(readMem(operand))
    elif opcode == BRA:
        writePC(operand)
    elif opcode == BRZ:
        if readAccum() == 0:
            writePC(operand)
    elif opcode == INP:
        writeAccum(readInbox())
    elif opcode == OUT:
        writeOutbox(readAccum())

def step():
    """Performs one fetch-decode-execute step"""
    instr = fetch()
    (opcode, operand) = decode(instr)
    execute(opcode, operand)

def run():
    """Performs fetch-decode-execute steps until `running` is False"""
    while running:
        step()

# ------------ Encode / Assemble / Labels / Change Functions ------------

def encode(asm: str) -> (int):
    """Converts a single assembly instruction to machine language. If not valid returns -1

    Preconditions: None
    Postconditions:
      * Assume that the instruction is syntactically valid, but the instruction may contain an
        invalid instruction name, and should return -1 else return a correct machine language.
      * If valid, and 'DAT' is contained simply loads the value into the next available mailbox.
        If there is only 'DAT', then the default value is zero
    """
    mnemonic = ['HLT', 'ADD', 'SUB', 'STA', 'LDA', 'BRA', 'BRZ', 'INP', 'OUT']
    try:
        if asm.find('DAT') != -1:
            return int(asm[3:])
        if asm[:3] in mnemonic:
            opcode = mnemonic.index(asm[:3])
            if len(asm) > 3:
                operand = int(asm[3:])
                return opcode * 100 + operand
            return opcode * 100
        else:
            return -1
    except:
        return -1

def assemble(program: str) -> (list, list):
    """
    Takes a complete assembly program, with instructions separated by newline characters
    (‘\n’) and comments indicated by // marks, and returns two lists. The first list should
    be the list of translated machine language instructions. The second list should be a list
    of assembly instructions that failed to translate. + Labeling
    """
    list1 = []
    list2 = []
    array = []
    instr = program.split('\n')
    del instr[0], instr[len(instr) - 1]
    for cut in range(len(instr)):
        if instr[cut].find('//') != -1:
            instr[cut] = instr[cut][:instr[cut].find('//')]
    while instr.count('') > 0:
        instr.remove('')
    for stp in range(len(instr)):
        instr[stp] = instr[stp].strip()
    for idx in range(len(instr)):
        array.append(labels(instr[idx], idx))
    instr = change(array)
    for asm in range(len(instr)):
        if encode(instr[asm]) != -1:
            list1.append(instr[asm])
        else:
            list2.append(instr[asm])
    return list1, list2

def labels(asm: str, idx: int):
    """Make dictionary for labeling"""
    global dic2
    mnemonic = ['HLT', 'ADD', 'SUB', 'STA', 'LDA', 'BRA', 'BRZ', 'INP', 'OUT']
    instr = asm.split(' ')
    while instr.count('') > 0:
        instr.remove('')
    if len(instr) == 1:
        if instr[0] == 'DAT' or instr[0] in mnemonic:
            instr.insert(0, 0)
            instr.insert(2, 0)
        else:
            instr.insert(0, 1)
            instr.insert(2, 0)
            idx = idx - 1
    elif len(instr) == 2:
        if instr[0] == 'DAT' or instr[0] in mnemonic:
            instr.insert(0, 0)
        elif instr[1] == 'DAT' or instr[1] in mnemonic:
            instr.insert(2, 0)
            dic2[instr[0]] = idx
        else:
            instr.insert(0, 1)
    elif len(instr) == 3:
        if instr[1] == 'DAT' or instr[1] in mnemonic:
            dic2[instr[0]] = idx
    return instr

def change(array: list) -> (list):
    """By using dictionary this fuction change variable name to value, then make string"""
    global dic1, dic2
    instr = []
    for idx in range(len(array)):
        if str(array[idx][0]).isalpha():
            dic1[array[idx][0]] = array[idx][2]
    for key1 in dic1.keys():
        for key2 in dic1.keys():
            if dic1[key1] == key2:
                dic1[key1] = dic1[key2]
    for dk2 in dic2.keys():
        for dk1 in dic1.keys():
            if dk2 == dk1:
                dic1[dk2] = dic2[dk2]
    for chg in range(len(array)):
        for trd in range(3):
            for key in dic1.keys():
                if array[chg][trd] == key:
                    array[chg][trd] = dic1[key]
        if array[chg][2] == 0:
            instr.append(str(array[chg][1]))
        else:
            instr.append(str(array[chg][1]) + ' ' + str(array[chg][2]))
    return instr

# ----------------- Simulator setup ----------------

def reset():
    """Resets all computer components to their initial state"""
    global pc, memory, accum, inbox, outbox, running
    pc = 0
    memory = [0] * 100
    accum = 0
    inbox = []
    outbox = []
    running = True

def load(program: list, indata: list):
    """Resets computer, loads memory with `program`, and sets inbox to `indata`"""
    global inbox
    reset()
    for i in range(len(program)):
        writeMem(i, program[i])
    inbox = indata
    writeInbox(indata)

def loadAssembly(program: str, indata: str):
    """
    Takes a complete, syntactically valid assembly program, and a string containing a
    comma-delimited list of numbers. It should assemble the program using assemble(),and if there
    are no errors, use load() to load it into memory, and load the data in indata into the inbox.
    """
    if len(assemble(program)[1]) == 0:
        program = assemble(program)[0]
        indata = indata.split(',')
        for pro in range(len(program)):
            program[pro] = encode(program[pro])
        for dat in range(len(indata)):
            indata[dat] = int(indata[dat])
        load(program, indata)
    elif len(assemble(program)[1]) > 0:
        print("\nThe following instructions failed to assemble:")
        print(", ".join(assemble(program)[1]))

# ---------------- Simulator "display" ----------------------

def dump():
    """Displays the state of memory/CPU"""
    print(end='\n')
    for row in range(10):
        for col in range(10):
            address = str(row * 10 + col).rjust(2)
            numeric = '[' + str(readMem(int(address))).ljust(3) + ']'
            print(address + numeric, end=" ")
        print(end='\n')
    pc_str = 'PC['+ str(readPC()).ljust(2) +']'
    acc_str = 'ACC[' + str(readAccum()).ljust(3) + ']'
    instr_str = toAssembly(readMem(readPC()))
    print(' ' * 31, pc_str, acc_str, instr_str, end='\n\n')
    print('In box:', str(inbox))
    print('Out box:', str(outbox))

def dumpWeb():
    """Make dump string for web"""
    html = ''''''
    for row in range(10):
        for col in range(10):
            address = str(row * 10 + col).rjust(2)
            numeric = '[' + str(readMem(int(address))).ljust(3) + ']'
            html += address + numeric + ' '
        html += '\n'
    pc_str = 'PC['+ str(readPC()).ljust(2) +']'
    acc_str = 'ACC[' + str(readAccum()).ljust(3) + ']'
    instr_str = toAssembly(readMem(readPC()))
    html += ' ' * 31 + ' ' + pc_str + ' ' + acc_str + ' ' + instr_str + '\n\n'
    html += 'In box:' + str(inbox) + '\n'
    html += 'Out box:' + str(outbox) + '\n'
    return html

def toAssembly(instr: int) -> (str):
    """Returns assembly language translation of machine language instruction `instr`"""
    mnemonic = ['HLT', 'ADD', 'SUB', 'STA', 'LDA', 'BRA', 'BRZ', 'INP', 'OUT']
    opcode = instr // 100
    operand = instr % 100
    if operand == 0 or opcode == 0:
        address = ''
    else:
        address = ' ' + str(operand)
    return mnemonic[opcode] + address

def disassemble(start: int, end: int):
    """Displays assembly language listing of memory contents `start` to `end`"""
    for addr in range(start, end + 1):
        print(str(addr).rjust(2) + ": " + toAssembly(readMem(addr)))

# ----------- Define shortcut names for interactive use

def sd():
    """Shortcut step and dump"""
    step()
    dump()
    
s = step
d = dump
r = run

# ----------------- Unit Tests ------------------------

def test_toAssembly():
    """For testing toAssembly function"""
    assert toAssembly(000) == 'HLT'
    assert toAssembly(101) == 'ADD 1'
    assert toAssembly(202) == 'SUB 2'
    assert toAssembly(303) == 'STA 3'
    assert toAssembly(404) == 'LDA 4'
    assert toAssembly(505) == 'BRA 5'
    assert toAssembly(606) == 'BRZ 6'
    assert toAssembly(700) == 'INP'
    assert toAssembly(800) == 'OUT'

def test_encode():
    """For testing encode function"""
    assert encode("HLT") == 000 # 000 = 0
    assert encode("ADD 7") == 107
    assert encode("SUB 13") == 213
    assert encode("STA 8") == 308
    assert encode("LDA 22") == 422
    assert encode("BRA 52") == 552
    assert encode("BRZ 3") == 603
    assert encode("INP") == 700
    assert encode("OUT") == 800

def test_readInbox():
    """For testing readInbox function"""
    reset()
    writeInbox([4, 2])
    assert readInbox() == 4

def test_mem():
    """For testing mem"""
    reset()
    assert memory == [0] * 100
    writeMem(1, 5)
    assert readMem(1) == 5

    reset()
    writeMem(-1, 5)
    assert memory == [0] * 100

    writeMem(1, 1000)
    assert memory == [0] * 100

def test_HLT():
    """For testing HLT"""
    reset()
    execute(HLT, 0)
    assert running == False

def test_ADD():
    """For testing ADD"""
    reset()
    writeAccum(5)
    writeMem(6, 3)
    execute(ADD, 6)
    assert readAccum() == 8

def test_SUB():
    """For testing SUB"""
    reset()
    writeAccum(5)
    writeMem(6, 3)
    execute(SUB, 6)
    assert readAccum() == 2

def test_STA():
    """For testing STA"""
    reset()
    writeAccum(10)
    execute(STA, 8)
    assert readMem(8) == 10

def test_LDA():
    """For testing LDA"""
    reset()
    writeMem(3, 50)
    execute(LDA, 3)
    assert readAccum() == 50

def test_BRA():
    """For testing BRA"""
    reset()
    writePC(2)
    execute(BRA, 8)
    assert readPC() == 8

def test_BRZ():
    """For testing BRZ"""
    reset()
    writePC(0)
    writeAccum(0)
    execute(BRZ, 4)
    assert readPC() == 4

def test_INP():
    """For testing INP"""
    reset()
    writeAccum(3)
    writeInbox([7, 2])
    execute(INP, 0)
    assert readAccum() == 7

def test_OUT():
    """For testing OUT"""
    reset()
    writeAccum(3)
    execute(OUT, 0)
    assert outbox == [3]

if __name__ == '__main__':
    reset()