"""
VMX128 Instruction Disassembly for Xbox 360 PowerPC

This module provides custom disassembly for VMX128 SIMD instructions used by the
Xbox 360 Xenon CPU. Capstone does not support VMX128, so this fills that gap.

VMX128 extends AltiVec with:
- 128 vector registers (v0-v127) instead of 32
- ~80 additional instructions optimized for Xbox 360 graphics/physics

References:
- ~/code/milohax/vmx128-research/PPC-Altivec-IDA/plugin.cpp (IDA Pro plugin)
- ~/code/milohax/vmx128-research/powerpc-rs/isa.yaml (ISA definitions)
- ~/code/milohax/dc3-decomp/docs/vmx128/REGISTER_ENCODING.md
- ~/code/milohax/dc3-decomp/docs/vmx128/ISA_REFERENCE.md
"""

from typing import Optional, Tuple, List


# =============================================================================
# Register Extraction Functions
# =============================================================================

def extract_vd128(inst: int) -> int:
    """Extract VD128 (destination/source) register number (7 bits).

    Bit positions: bits 21-25 (low 5 bits), bits 2-3 (high 2 bits)
    """
    return ((inst >> 21) & 0x1F) | ((inst & 0x0C) << 3)


def extract_va128(inst: int) -> int:
    """Extract VA128 (source A) register number (7 bits).

    Bit positions: bits 16-20 (low 5 bits), bit 5, bit 10 << 6
    """
    return ((inst >> 16) & 0x1F) | (inst & 0x20) | ((inst >> 4) & 0x40)


def extract_vb128(inst: int) -> int:
    """Extract VB128 (source B) register number (7 bits).

    Bit positions: bits 11-15 (low 5 bits), bits 0-1 (high 2 bits)
    """
    return ((inst << 5) & 0x60) | ((inst >> 11) & 0x1F)


def extract_vc128(inst: int) -> int:
    """Extract VC128 (source C) register number (3 bits, v0-v7 only).

    Bit positions: bits 6-8
    """
    return (inst >> 6) & 0x7


def extract_ra(inst: int) -> int:
    """Extract rA (GPR source A) register number."""
    return (inst >> 16) & 0x1F


def extract_rb(inst: int) -> int:
    """Extract rB (GPR source B) register number."""
    return (inst >> 11) & 0x1F


def extract_simm(inst: int) -> int:
    """Extract signed immediate from bits 16-20 (5 bits, sign-extended)."""
    val = (inst >> 16) & 0x1F
    if val & 0x10:  # Sign extend
        val -= 0x20
    return val


def extract_uimm(inst: int) -> int:
    """Extract unsigned immediate from bits 16-20 (5 bits)."""
    return (inst >> 16) & 0x1F


def extract_shb(inst: int) -> int:
    """Extract shift amount for vsldoi128 (4 bits, bits 6-9)."""
    return (inst >> 6) & 0xF


def extract_vperm128(inst: int) -> int:
    """Extract permutation immediate for vpermwi128 (7 bits split).

    PERMh (bits 8-9), PERMl (bits 16-20)
    """
    return ((inst >> 3) & 0x60) | ((inst >> 16) & 0x1F)


def extract_vd3d0(inst: int) -> int:
    """Extract VD3D0 (D3D type selector) - 3 bits from bits 18-20."""
    return (inst >> 18) & 0x7


def extract_vd3d1(inst: int) -> int:
    """Extract VD3D1 (vector mask) - 2 bits from bits 16-17."""
    return (inst >> 16) & 0x3


def extract_vd3d2(inst: int) -> int:
    """Extract VD3D2 (zero immediate) - 2 bits from bits 6-7."""
    return (inst >> 6) & 0x3


# =============================================================================
# Instruction Encoding Helpers
# =============================================================================

def get_primary_opcode(inst: int) -> int:
    """Extract primary opcode (bits 26-31)."""
    return (inst >> 26) & 0x3F


def match_pattern(inst: int, mask: int, pattern: int) -> bool:
    """Check if instruction matches the given pattern after applying mask."""
    return (inst & mask) == pattern


# =============================================================================
# Instruction Format Masks and Patterns
# =============================================================================

# Primary opcode shifted left by 26
def OP(op: int) -> int:
    return op << 26


# VX128 format: Primary opcode 5 or 6, XOP in bits 4-9 (masked)
def VX128(op: int, xop: int) -> int:
    return OP(op) | (xop & 0x3D0)

VX128_MASK = 0xFC0003D0


# VX128_1 format: Load/store instructions
def VX128_1(op: int, xop: int) -> int:
    return OP(op) | (xop & 0x7F3)

VX128_1_MASK = 0xFC0007F3


# VX128_2 format: vperm128
def VX128_2(op: int, xop: int) -> int:
    return OP(op) | (xop & 0x210)

VX128_2_MASK = 0xFC000210


# VX128_3 format: Conversion, rounding, estimates
def VX128_3(op: int, xop: int) -> int:
    return OP(op) | (xop & 0x7F0)

VX128_3_MASK = 0xFC0007F0


# VX128_4 format: D3D pack/unpack, vrlimi128
def VX128_4(op: int, xop: int) -> int:
    return OP(op) | (xop & 0x730)

VX128_4_MASK = 0xFC000730


# VX128_5 format: vsldoi128
def VX128_5(op: int, xop: int) -> int:
    return OP(op) | (xop & 0x10)

VX128_5_MASK = 0xFC000010


# VX128_P format: vpermwi128
def VX128_P(op: int, xop: int) -> int:
    return OP(op) | (xop & 0x630)

VX128_P_MASK = 0xFC000630


# =============================================================================
# Instruction Definitions
# =============================================================================

# Each instruction is: (pattern, mask, mnemonic, operand_format)
# Operand formats:
#   "VD,VA,VB"   - Three vector registers
#   "VD,VB"      - Two vector registers
#   "VD,RA,RB"   - Vector dest, two GPR sources
#   "VD,VB,UIMM" - Vector dest, vector source, unsigned immediate
#   "VD,VB,SIMM" - Vector dest, vector source, signed immediate
#   "VD,VA,VB,VC"- Four vector registers (vperm128)
#   "VD,VA,VB,VS"- Three vectors, VD also used as implicit source (vmaddfp128)
#   "VD,VA,VB,SHB" - vsldoi128
#   "VD,VB,PERM" - vpermwi128
#   "VD,VB,D3D0,D3D1,D3D2" - vpkd3d128
#   "VD,VB,UIMM,D3D2" - vrlimi128

VMX128_INSTRUCTIONS: List[Tuple[int, int, str, str]] = [
    # =========================================================================
    # Load Instructions (Primary Opcode 4, VX128_1 format)
    # =========================================================================
    (VX128_1(4, 0x003), VX128_1_MASK, "lvsl128", "VD,RA,RB"),
    (VX128_1(4, 0x043), VX128_1_MASK, "lvsr128", "VD,RA,RB"),
    (VX128_1(4, 0x083), VX128_1_MASK, "lvewx128", "VD,RA,RB"),
    (VX128_1(4, 0x0C3), VX128_1_MASK, "lvx128", "VD,RA,RB"),
    (VX128_1(4, 0x2C3), VX128_1_MASK, "lvxl128", "VD,RA,RB"),
    (VX128_1(4, 0x403), VX128_1_MASK, "lvlx128", "VD,RA,RB"),
    (VX128_1(4, 0x443), VX128_1_MASK, "lvrx128", "VD,RA,RB"),
    (VX128_1(4, 0x603), VX128_1_MASK, "lvlxl128", "VD,RA,RB"),
    (VX128_1(4, 0x643), VX128_1_MASK, "lvrxl128", "VD,RA,RB"),

    # =========================================================================
    # Store Instructions (Primary Opcode 4, VX128_1 format)
    # =========================================================================
    (VX128_1(4, 0x183), VX128_1_MASK, "stvewx128", "VD,RA,RB"),
    (VX128_1(4, 0x1C3), VX128_1_MASK, "stvx128", "VD,RA,RB"),
    (VX128_1(4, 0x3C3), VX128_1_MASK, "stvxl128", "VD,RA,RB"),
    (VX128_1(4, 0x503), VX128_1_MASK, "stvlx128", "VD,RA,RB"),
    (VX128_1(4, 0x543), VX128_1_MASK, "stvrx128", "VD,RA,RB"),
    (VX128_1(4, 0x703), VX128_1_MASK, "stvlxl128", "VD,RA,RB"),
    (VX128_1(4, 0x743), VX128_1_MASK, "stvrxl128", "VD,RA,RB"),

    # =========================================================================
    # Shift Left Double by Octet Immediate (Primary Opcode 4, VX128_5 format)
    # =========================================================================
    (VX128_5(4, 0x10), VX128_5_MASK, "vsldoi128", "VD,VA,VB,SHB"),

    # =========================================================================
    # Floating-Point Arithmetic (Primary Opcode 5, VX128 format)
    # =========================================================================
    (VX128(5, 0x010), VX128_MASK, "vaddfp128", "VD,VA,VB"),
    (VX128(5, 0x050), VX128_MASK, "vsubfp128", "VD,VA,VB"),
    (VX128(5, 0x090), VX128_MASK, "vmulfp128", "VD,VA,VB"),
    (VX128(5, 0x0D0), VX128_MASK, "vmaddfp128", "VD,VA,VB,VS"),
    (VX128(5, 0x110), VX128_MASK, "vmaddcfp128", "VD,VA,VS,VB"),  # Note: VD=VA*VD+VB
    (VX128(5, 0x150), VX128_MASK, "vnmsubfp128", "VD,VA,VB,VS"),
    (VX128(5, 0x190), VX128_MASK, "vmsum3fp128", "VD,VA,VB"),  # 3D dot product
    (VX128(5, 0x1D0), VX128_MASK, "vmsum4fp128", "VD,VA,VB"),  # 4D dot product

    # =========================================================================
    # Logical Operations (Primary Opcode 5, VX128 format)
    # =========================================================================
    (VX128(5, 0x210), VX128_MASK, "vand128", "VD,VA,VB"),
    (VX128(5, 0x250), VX128_MASK, "vandc128", "VD,VA,VB"),
    (VX128(5, 0x290), VX128_MASK, "vnor128", "VD,VA,VB"),
    (VX128(5, 0x2D0), VX128_MASK, "vor128", "VD,VA,VB"),
    (VX128(5, 0x310), VX128_MASK, "vxor128", "VD,VA,VB"),
    (VX128(5, 0x350), VX128_MASK, "vsel128", "VD,VA,VB,VS"),

    # =========================================================================
    # Pack Operations (Primary Opcode 5, VX128 format)
    # =========================================================================
    (VX128(5, 0x200), VX128_MASK, "vpkshss128", "VD,VA,VB"),
    (VX128(5, 0x240), VX128_MASK, "vpkshus128", "VD,VA,VB"),
    (VX128(5, 0x280), VX128_MASK, "vpkswss128", "VD,VA,VB"),
    (VX128(5, 0x2C0), VX128_MASK, "vpkswus128", "VD,VA,VB"),
    (VX128(5, 0x300), VX128_MASK, "vpkuhum128", "VD,VA,VB"),
    (VX128(5, 0x340), VX128_MASK, "vpkuhus128", "VD,VA,VB"),
    (VX128(5, 0x380), VX128_MASK, "vpkuwum128", "VD,VA,VB"),
    (VX128(5, 0x3C0), VX128_MASK, "vpkuwus128", "VD,VA,VB"),

    # =========================================================================
    # Shift Operations (Primary Opcode 5, VX128 format)
    # =========================================================================
    (VX128(5, 0x390), VX128_MASK, "vslo128", "VD,VA,VB"),
    (VX128(5, 0x3D0), VX128_MASK, "vsro128", "VD,VA,VB"),

    # =========================================================================
    # Permutation (Primary Opcode 5, VX128_2 format)
    # =========================================================================
    (VX128_2(5, 0x000), VX128_2_MASK, "vperm128", "VD,VA,VB,VC"),

    # =========================================================================
    # Comparison Operations (Primary Opcode 6, VX128 format)
    # =========================================================================
    (VX128(6, 0x000), VX128_MASK, "vcmpeqfp128", "VD,VA,VB"),
    (VX128(6, 0x040), VX128_MASK, "vcmpeqfp128.", "VD,VA,VB"),  # Rc=1
    (VX128(6, 0x080), VX128_MASK, "vcmpgefp128", "VD,VA,VB"),
    (VX128(6, 0x0C0), VX128_MASK, "vcmpgefp128.", "VD,VA,VB"),  # Rc=1
    (VX128(6, 0x100), VX128_MASK, "vcmpgtfp128", "VD,VA,VB"),
    (VX128(6, 0x140), VX128_MASK, "vcmpgtfp128.", "VD,VA,VB"),  # Rc=1
    (VX128(6, 0x180), VX128_MASK, "vcmpbfp128", "VD,VA,VB"),
    (VX128(6, 0x1C0), VX128_MASK, "vcmpbfp128.", "VD,VA,VB"),  # Rc=1
    (VX128(6, 0x200), VX128_MASK, "vcmpequw128", "VD,VA,VB"),
    (VX128(6, 0x240), VX128_MASK, "vcmpequw128.", "VD,VA,VB"),  # Rc=1

    # =========================================================================
    # Shift/Rotate Operations (Primary Opcode 6, VX128 format)
    # =========================================================================
    (VX128(6, 0x050), VX128_MASK, "vrlw128", "VD,VA,VB"),
    (VX128(6, 0x0D0), VX128_MASK, "vslw128", "VD,VA,VB"),
    (VX128(6, 0x150), VX128_MASK, "vsraw128", "VD,VA,VB"),
    (VX128(6, 0x1D0), VX128_MASK, "vsrw128", "VD,VA,VB"),

    # =========================================================================
    # Min/Max Operations (Primary Opcode 6, VX128 format)
    # =========================================================================
    (VX128(6, 0x280), VX128_MASK, "vmaxfp128", "VD,VA,VB"),
    (VX128(6, 0x2C0), VX128_MASK, "vminfp128", "VD,VA,VB"),

    # =========================================================================
    # Merge Operations (Primary Opcode 6, VX128 format)
    # =========================================================================
    (VX128(6, 0x300), VX128_MASK, "vmrghw128", "VD,VA,VB"),
    (VX128(6, 0x340), VX128_MASK, "vmrglw128", "VD,VA,VB"),

    # =========================================================================
    # Unpack Operations (Primary Opcode 6, VX128 format - VB only)
    # =========================================================================
    (VX128(6, 0x380), VX128_MASK, "vupkhsb128", "VD,VB"),
    (VX128(6, 0x3C0), VX128_MASK, "vupklsb128", "VD,VB"),

    # =========================================================================
    # Conversion Operations (Primary Opcode 6, VX128_3 format)
    # =========================================================================
    (VX128_3(6, 0x230), VX128_3_MASK, "vcfpsxws128", "VD,VB,SIMM"),  # vctsxs128 alias
    (VX128_3(6, 0x270), VX128_3_MASK, "vcfpuxws128", "VD,VB,UIMM"),  # vctuxs128 alias
    (VX128_3(6, 0x2B0), VX128_3_MASK, "vcsxwfp128", "VD,VB,SIMM"),   # vcfsx128 alias
    (VX128_3(6, 0x2F0), VX128_3_MASK, "vcuxwfp128", "VD,VB,UIMM"),   # vcfux128 alias

    # =========================================================================
    # Rounding Operations (Primary Opcode 6, VX128_3 format)
    # =========================================================================
    (VX128_3(6, 0x330), VX128_3_MASK, "vrfim128", "VD,VB"),
    (VX128_3(6, 0x370), VX128_3_MASK, "vrfin128", "VD,VB"),
    (VX128_3(6, 0x3B0), VX128_3_MASK, "vrfip128", "VD,VB"),
    (VX128_3(6, 0x3F0), VX128_3_MASK, "vrfiz128", "VD,VB"),

    # =========================================================================
    # Estimate Operations (Primary Opcode 6, VX128_3 format)
    # =========================================================================
    (VX128_3(6, 0x630), VX128_3_MASK, "vrefp128", "VD,VB"),
    (VX128_3(6, 0x670), VX128_3_MASK, "vrsqrtefp128", "VD,VB"),
    (VX128_3(6, 0x6B0), VX128_3_MASK, "vexptefp128", "VD,VB"),
    (VX128_3(6, 0x6F0), VX128_3_MASK, "vlogefp128", "VD,VB"),

    # =========================================================================
    # D3D Pack/Unpack (Primary Opcode 6, VX128_4 format)
    # =========================================================================
    (VX128_4(6, 0x610), VX128_4_MASK, "vpkd3d128", "VD,VB,D3D0,D3D1,D3D2"),

    # =========================================================================
    # Rotate Left Immediate and Mask Insert (Primary Opcode 6, VX128_4 format)
    # =========================================================================
    (VX128_4(6, 0x710), VX128_4_MASK, "vrlimi128", "VD,VB,UIMM,D3D2"),

    # =========================================================================
    # Splat Operations (Primary Opcode 6, VX128_3 format)
    # =========================================================================
    (VX128_3(6, 0x730), VX128_3_MASK, "vspltw128", "VD,VB,UIMM"),
    (VX128_3(6, 0x770), VX128_3_MASK, "vspltisw128", "VD,VB,SIMM"),

    # =========================================================================
    # Unpack D3D (Primary Opcode 6, VX128_3 format)
    # =========================================================================
    (VX128_3(6, 0x7F0), VX128_3_MASK, "vupkd3d128", "VD,VB,UIMM"),

    # =========================================================================
    # Permute Word Immediate (Primary Opcode 6, VX128_P format)
    # =========================================================================
    (VX128_P(6, 0x210), VX128_P_MASK, "vpermwi128", "VD,VB,PERM"),

    # =========================================================================
    # Additional Unpack Operations (Primary Opcode 6, VX128_3 format)
    # =========================================================================
    (VX128_3(6, 0x7A0), VX128_3_MASK, "vupkhsh128", "VD,VB"),
    (VX128_3(6, 0x7E0), VX128_3_MASK, "vupklsh128", "VD,VB"),
]


# =============================================================================
# Disassembly Function
# =============================================================================

def format_operands(inst: int, fmt: str) -> str:
    """Format operands according to the operand format string."""
    parts = []

    for operand in fmt.split(","):
        if operand == "VD":
            parts.append(f"v{extract_vd128(inst)}")
        elif operand == "VA":
            parts.append(f"v{extract_va128(inst)}")
        elif operand == "VB":
            parts.append(f"v{extract_vb128(inst)}")
        elif operand == "VC":
            parts.append(f"v{extract_vc128(inst)}")
        elif operand == "VS":
            # VS uses same encoding as VD - implicit operand
            parts.append(f"v{extract_vd128(inst)}")
        elif operand == "RA":
            ra = extract_ra(inst)
            parts.append(f"r{ra}" if ra != 0 else "0")
        elif operand == "RB":
            parts.append(f"r{extract_rb(inst)}")
        elif operand == "UIMM":
            parts.append(f"{extract_uimm(inst)}")
        elif operand == "SIMM":
            parts.append(f"{extract_simm(inst)}")
        elif operand == "SHB":
            parts.append(f"{extract_shb(inst)}")
        elif operand == "PERM":
            parts.append(f"{extract_vperm128(inst)}")
        elif operand == "D3D0":
            parts.append(f"{extract_vd3d0(inst)}")
        elif operand == "D3D1":
            parts.append(f"{extract_vd3d1(inst)}")
        elif operand == "D3D2":
            parts.append(f"{extract_vd3d2(inst)}")
        else:
            parts.append(f"?{operand}?")

    return ", ".join(parts)


def disasm_vmx128(inst: int) -> Optional[str]:
    """
    Disassemble a VMX128 instruction.

    Args:
        inst: 32-bit instruction word (big-endian)

    Returns:
        Disassembled instruction string, or None if not a VMX128 instruction.
    """
    primary_op = get_primary_opcode(inst)

    # VMX128 instructions use primary opcodes 4, 5, or 6
    if primary_op not in (4, 5, 6):
        return None

    # Try to match against all known VMX128 instructions
    for pattern, mask, mnemonic, operand_fmt in VMX128_INSTRUCTIONS:
        if match_pattern(inst, mask, pattern):
            operands = format_operands(inst, operand_fmt)
            return f"{mnemonic} {operands}"

    return None


def is_vmx128_opcode(primary_op: int) -> bool:
    """Check if the primary opcode could be a VMX128 instruction."""
    return primary_op in (4, 5, 6)


# =============================================================================
# Test Function
# =============================================================================

def _test_disasm():
    """Test disassembly of some known instruction encodings."""
    # Test cases: (encoded_instruction, expected_output)
    test_cases = [
        # vaddfp128 v3, v1, v2  (example encoding)
        # Pattern: VX128(5, 0x10) = OP(5) | 0x10 = 0x14000010
        # With VD=3, VA=1, VB=2:
        # - VD bits 21-25 = 3 (0b00011), bits 2-3 = 0
        # - VA bits 16-20 = 1 (0b00001), bit 5 = 0, bit 10 = 0
        # - VB bits 11-15 = 2 (0b00010), bits 0-1 = 0
        # Full: 0x14 61 10 10 (approximately)
        # Let's verify manually:
        # Primary op 5 = 0x14000000
        # XOP 0x10 in bits 4-9 area
        # VD=3: bits 21-25 = 3 << 21 = 0x00600000
        # VA=1: bits 16-20 = 1 << 16 = 0x00010000
        # VB=2: bits 11-15 = 2 << 11 = 0x00001000
        (0x14611010, "vaddfp128 v3, v1, v2"),
    ]

    print("VMX128 Disassembler Tests")
    print("=" * 50)

    for encoded, expected_substr in test_cases:
        result = disasm_vmx128(encoded)
        if result:
            # Just check if mnemonic is correct
            if expected_substr.split()[0] in result:
                print(f"PASS: 0x{encoded:08X} -> {result}")
            else:
                print(f"FAIL: 0x{encoded:08X} -> {result} (expected {expected_substr})")
        else:
            print(f"FAIL: 0x{encoded:08X} -> None (expected {expected_substr})")


if __name__ == "__main__":
    _test_disasm()
