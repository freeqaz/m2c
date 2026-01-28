"""Tests for Xbox 360 comma-separated load/store syntax normalization.

Xbox 360 assembly uses a different syntax for load/store instructions than
standard PPC assembly:

Xbox 360 format:  std r30, -0x18, r1  (3 args: reg, offset, base_reg)
Standard PPC:     std r30, -0x18(r1)  (2 args: reg, address_mode)

The normalize_instruction() function in arch_ppc.py converts the Xbox 360
comma-separated format to the standard AsmAddressMode format.
"""

import unittest

from m2c.asm_instruction import (
    AsmAddressMode,
    AsmInstruction,
    AsmLiteral,
    AsmState,
    Register,
    parse_asm_instruction,
)
from m2c.arch_ppc import PpcArch


class TestCommaLoadStoreSyntaxNormalization(unittest.TestCase):
    """Test Xbox 360 comma-separated load/store syntax normalization."""

    def setUp(self) -> None:
        self.arch = PpcArch()
        self.asm_state = AsmState()

    def parse_and_normalize(self, asm_line: str) -> AsmInstruction:
        """Parse and normalize a single assembly instruction."""
        raw_instr = parse_asm_instruction(asm_line, self.arch, self.asm_state)
        return self.arch.normalize_instruction(raw_instr, self.asm_state)

    # =========================================================================
    # Store Instructions - Comma Syntax Normalization
    # =========================================================================
    def test_std_comma_syntax(self) -> None:
        """std with comma-separated syntax should normalize to AsmAddressMode."""
        instr = self.parse_and_normalize("std r30, -0x18, r1")
        self.assertEqual(instr.mnemonic, "std")
        self.assertEqual(len(instr.args), 2)
        self.assertIsInstance(instr.args[0], Register)
        self.assertEqual(instr.args[0].register_name, "r30")
        self.assertIsInstance(instr.args[1], AsmAddressMode)
        self.assertEqual(instr.args[1].base.register_name, "r1")
        # The addend should be -0x18 = -24
        self.assertIsInstance(instr.args[1].addend, AsmLiteral)
        self.assertEqual(instr.args[1].addend.value, -0x18)

    def test_stw_comma_syntax(self) -> None:
        """stw with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("stw r5, 0x10, r3")
        self.assertEqual(instr.mnemonic, "stw")
        self.assertEqual(len(instr.args), 2)
        self.assertIsInstance(instr.args[1], AsmAddressMode)
        self.assertEqual(instr.args[1].base.register_name, "r3")
        self.assertEqual(instr.args[1].addend.value, 0x10)

    def test_stb_comma_syntax(self) -> None:
        """stb with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("stb r7, 0x0, r4")
        self.assertEqual(instr.mnemonic, "stb")
        self.assertEqual(len(instr.args), 2)
        self.assertIsInstance(instr.args[1], AsmAddressMode)
        self.assertEqual(instr.args[1].addend.value, 0x0)

    def test_sth_comma_syntax(self) -> None:
        """sth with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("sth r8, 0x4, r5")
        self.assertEqual(instr.mnemonic, "sth")
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    def test_stfs_comma_syntax(self) -> None:
        """stfs with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("stfs f1, 0x8, r6")
        self.assertEqual(instr.mnemonic, "stfs")
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    def test_stfd_comma_syntax(self) -> None:
        """stfd with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("stfd f2, 0xc, r7")
        self.assertEqual(instr.mnemonic, "stfd")
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    # =========================================================================
    # Store with Update Instructions - Comma Syntax Normalization
    # =========================================================================
    def test_stdu_comma_syntax(self) -> None:
        """stdu with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("stdu r3, -0x20, r1")
        self.assertEqual(instr.mnemonic, "stdu")
        self.assertEqual(len(instr.args), 2)
        self.assertIsInstance(instr.args[1], AsmAddressMode)
        self.assertEqual(instr.args[1].base.register_name, "r1")

    def test_stwu_comma_syntax(self) -> None:
        """stwu with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("stwu r4, -0x10, r1")
        self.assertEqual(instr.mnemonic, "stwu")
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    # =========================================================================
    # Load Instructions - Comma Syntax Normalization
    # =========================================================================
    def test_ld_comma_syntax(self) -> None:
        """ld with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("ld r3, 0x10, r4")
        self.assertEqual(instr.mnemonic, "ld")
        self.assertEqual(len(instr.args), 2)
        self.assertIsInstance(instr.args[0], Register)
        self.assertIsInstance(instr.args[1], AsmAddressMode)
        self.assertEqual(instr.args[1].base.register_name, "r4")
        self.assertEqual(instr.args[1].addend.value, 0x10)

    def test_lwz_comma_syntax(self) -> None:
        """lwz with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("lwz r5, 0x0, r6")
        self.assertEqual(instr.mnemonic, "lwz")
        self.assertEqual(len(instr.args), 2)
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    def test_lbz_comma_syntax(self) -> None:
        """lbz with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("lbz r7, 0x4, r8")
        self.assertEqual(instr.mnemonic, "lbz")
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    def test_lhz_comma_syntax(self) -> None:
        """lhz with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("lhz r9, 0x2, r10")
        self.assertEqual(instr.mnemonic, "lhz")
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    def test_lha_comma_syntax(self) -> None:
        """lha with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("lha r11, 0x6, r12")
        self.assertEqual(instr.mnemonic, "lha")
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    def test_lfs_comma_syntax(self) -> None:
        """lfs with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("lfs f3, 0x14, r13")
        self.assertEqual(instr.mnemonic, "lfs")
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    def test_lfd_comma_syntax(self) -> None:
        """lfd with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("lfd f4, 0x18, r14")
        self.assertEqual(instr.mnemonic, "lfd")
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    def test_lwa_comma_syntax(self) -> None:
        """lwa (load word algebraic) with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("lwa r15, 0x1c, r16")
        self.assertEqual(instr.mnemonic, "lwa")
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    # =========================================================================
    # Load with Update Instructions - Comma Syntax Normalization
    # =========================================================================
    def test_ldu_comma_syntax(self) -> None:
        """ldu with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("ldu r17, 0x20, r18")
        self.assertEqual(instr.mnemonic, "ldu")
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    def test_lwzu_comma_syntax(self) -> None:
        """lwzu with comma-separated syntax should normalize."""
        instr = self.parse_and_normalize("lwzu r19, 0x24, r20")
        self.assertEqual(instr.mnemonic, "lwzu")
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    # =========================================================================
    # Indexed Instructions - Should NOT be normalized (already use 3 args)
    # =========================================================================
    def test_stdx_unchanged(self) -> None:
        """stdx is indexed and should keep 3 register args."""
        instr = self.parse_and_normalize("stdx r3, r4, r5")
        self.assertEqual(instr.mnemonic, "stdx")
        self.assertEqual(len(instr.args), 3)
        self.assertIsInstance(instr.args[0], Register)
        self.assertIsInstance(instr.args[1], Register)
        self.assertIsInstance(instr.args[2], Register)

    def test_lwzx_unchanged(self) -> None:
        """lwzx is indexed and should keep 3 register args."""
        instr = self.parse_and_normalize("lwzx r6, r7, r8")
        self.assertEqual(instr.mnemonic, "lwzx")
        self.assertEqual(len(instr.args), 3)

    def test_stwx_unchanged(self) -> None:
        """stwx is indexed and should keep 3 register args."""
        instr = self.parse_and_normalize("stwx r9, r10, r11")
        self.assertEqual(instr.mnemonic, "stwx")
        self.assertEqual(len(instr.args), 3)

    # =========================================================================
    # VMX128 Indexed Instructions - Should NOT be normalized
    # =========================================================================
    def test_stvx128_unchanged(self) -> None:
        """stvx128 is indexed VMX128 and should keep 3 args."""
        instr = self.parse_and_normalize("stvx128 v32, r3, r4")
        self.assertEqual(instr.mnemonic, "stvx128")
        self.assertEqual(len(instr.args), 3)

    def test_lvx128_unchanged(self) -> None:
        """lvx128 is indexed VMX128 and should keep 3 args."""
        instr = self.parse_and_normalize("lvx128 v64, r5, r6")
        self.assertEqual(instr.mnemonic, "lvx128")
        self.assertEqual(len(instr.args), 3)

    # =========================================================================
    # Standard PPC Syntax - Should Work Unchanged
    # =========================================================================
    def test_std_standard_syntax(self) -> None:
        """std with standard PPC syntax should work unchanged."""
        instr = self.parse_and_normalize("std r30, -0x18(r1)")
        self.assertEqual(instr.mnemonic, "std")
        self.assertEqual(len(instr.args), 2)
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    def test_lwz_standard_syntax(self) -> None:
        """lwz with standard PPC syntax should work unchanged."""
        instr = self.parse_and_normalize("lwz r3, 0x10(r4)")
        self.assertEqual(instr.mnemonic, "lwz")
        self.assertEqual(len(instr.args), 2)
        self.assertIsInstance(instr.args[1], AsmAddressMode)

    # =========================================================================
    # Edge Cases
    # =========================================================================
    def test_zero_offset(self) -> None:
        """Zero offset should work correctly."""
        instr = self.parse_and_normalize("stw r3, 0, r4")
        self.assertEqual(instr.mnemonic, "stw")
        self.assertIsInstance(instr.args[1], AsmAddressMode)
        self.assertEqual(instr.args[1].addend.value, 0)

    def test_negative_offset(self) -> None:
        """Negative offset should be preserved."""
        instr = self.parse_and_normalize("std r5, -0x100, r1")
        self.assertIsInstance(instr.args[1], AsmAddressMode)
        self.assertEqual(instr.args[1].addend.value, -0x100)

    def test_large_positive_offset(self) -> None:
        """Large positive offset should work."""
        instr = self.parse_and_normalize("lwz r6, 0x7FFF, r7")
        self.assertIsInstance(instr.args[1], AsmAddressMode)
        self.assertEqual(instr.args[1].addend.value, 0x7FFF)


if __name__ == "__main__":
    unittest.main()
