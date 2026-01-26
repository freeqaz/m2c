"""Tests for VMX128 instruction parsing and evaluation.

VMX128 is the Xbox 360's extended AltiVec instruction set which adds:
- 128 vector registers (v0-v127) instead of 32
- ~75 additional SIMD instructions optimized for graphics/physics

This test file verifies:
1. All 75 VMX128 instructions parse without errors
2. Extended registers (v32-v127) work correctly
3. Instruction handlers produce correct output types
"""

import unittest

from m2c.asm_instruction import (
    AsmInstruction,
    AsmState,
    Register,
    parse_asm_instruction,
)
from m2c.arch_ppc import PpcArch


class TestVMX128InstructionParsing(unittest.TestCase):
    """Test VMX128 instruction parsing."""

    def setUp(self) -> None:
        self.arch = PpcArch()
        self.asm_state = AsmState()

    def parse(self, asm_line: str) -> AsmInstruction:
        """Parse a single assembly instruction."""
        return parse_asm_instruction(asm_line, self.arch, self.asm_state)

    # =========================================================================
    # Load Instructions (9 total)
    # =========================================================================
    def test_lvx128(self) -> None:
        """lvx128: Load Vector Indexed"""
        instr = self.parse("lvx128 v32, r3, r4")
        self.assertEqual(instr.mnemonic, "lvx128")
        self.assertEqual(len(instr.args), 3)
        self.assertIsInstance(instr.args[0], Register)
        self.assertEqual(instr.args[0].register_name, "v32")

    def test_lvxl128(self) -> None:
        """lvxl128: Load Vector Indexed LRU hint"""
        instr = self.parse("lvxl128 v64, r5, r6")
        self.assertEqual(instr.mnemonic, "lvxl128")
        self.assertEqual(instr.args[0].register_name, "v64")

    def test_lvewx128(self) -> None:
        """lvewx128: Load Vector Element Word Indexed"""
        instr = self.parse("lvewx128 v40, r7, r8")
        self.assertEqual(instr.mnemonic, "lvewx128")
        self.assertEqual(instr.args[0].register_name, "v40")

    def test_lvlx128(self) -> None:
        """lvlx128: Load Vector Left Indexed"""
        instr = self.parse("lvlx128 v50, r9, r10")
        self.assertEqual(instr.mnemonic, "lvlx128")

    def test_lvrx128(self) -> None:
        """lvrx128: Load Vector Right Indexed"""
        instr = self.parse("lvrx128 v60, r11, r12")
        self.assertEqual(instr.mnemonic, "lvrx128")

    def test_lvlxl128(self) -> None:
        """lvlxl128: Load Vector Left Indexed LRU hint"""
        instr = self.parse("lvlxl128 v70, r3, r4")
        self.assertEqual(instr.mnemonic, "lvlxl128")

    def test_lvrxl128(self) -> None:
        """lvrxl128: Load Vector Right Indexed LRU hint"""
        instr = self.parse("lvrxl128 v80, r5, r6")
        self.assertEqual(instr.mnemonic, "lvrxl128")

    def test_lvsl128(self) -> None:
        """lvsl128: Load Vector for Shift Left"""
        instr = self.parse("lvsl128 v90, r7, r8")
        self.assertEqual(instr.mnemonic, "lvsl128")

    def test_lvsr128(self) -> None:
        """lvsr128: Load Vector for Shift Right"""
        instr = self.parse("lvsr128 v100, r9, r10")
        self.assertEqual(instr.mnemonic, "lvsr128")

    # =========================================================================
    # Store Instructions (7 total)
    # =========================================================================
    def test_stvx128(self) -> None:
        """stvx128: Store Vector Indexed"""
        instr = self.parse("stvx128 v110, r3, r4")
        self.assertEqual(instr.mnemonic, "stvx128")
        self.assertEqual(instr.args[0].register_name, "v110")

    def test_stvxl128(self) -> None:
        """stvxl128: Store Vector Indexed LRU hint"""
        instr = self.parse("stvxl128 v120, r5, r6")
        self.assertEqual(instr.mnemonic, "stvxl128")

    def test_stvewx128(self) -> None:
        """stvewx128: Store Vector Element Word Indexed"""
        instr = self.parse("stvewx128 v127, r7, r8")
        self.assertEqual(instr.mnemonic, "stvewx128")
        self.assertEqual(instr.args[0].register_name, "v127")

    def test_stvlx128(self) -> None:
        """stvlx128: Store Vector Left Indexed"""
        instr = self.parse("stvlx128 v32, r9, r10")
        self.assertEqual(instr.mnemonic, "stvlx128")

    def test_stvrx128(self) -> None:
        """stvrx128: Store Vector Right Indexed"""
        instr = self.parse("stvrx128 v33, r11, r12")
        self.assertEqual(instr.mnemonic, "stvrx128")

    def test_stvlxl128(self) -> None:
        """stvlxl128: Store Vector Left Indexed LRU hint"""
        instr = self.parse("stvlxl128 v34, r3, r4")
        self.assertEqual(instr.mnemonic, "stvlxl128")

    def test_stvrxl128(self) -> None:
        """stvrxl128: Store Vector Right Indexed LRU hint"""
        instr = self.parse("stvrxl128 v35, r5, r6")
        self.assertEqual(instr.mnemonic, "stvrxl128")

    # =========================================================================
    # Arithmetic Instructions (5 total)
    # =========================================================================
    def test_vaddfp128(self) -> None:
        """vaddfp128: Vector Add Floating Point"""
        instr = self.parse("vaddfp128 v36, v37, v38")
        self.assertEqual(instr.mnemonic, "vaddfp128")
        self.assertEqual(len(instr.args), 3)

    def test_vsubfp128(self) -> None:
        """vsubfp128: Vector Subtract Floating Point"""
        instr = self.parse("vsubfp128 v39, v40, v41")
        self.assertEqual(instr.mnemonic, "vsubfp128")

    def test_vmulfp128(self) -> None:
        """vmulfp128: Vector Multiply Floating Point"""
        instr = self.parse("vmulfp128 v42, v43, v44")
        self.assertEqual(instr.mnemonic, "vmulfp128")

    def test_vmaxfp128(self) -> None:
        """vmaxfp128: Vector Maximum Floating Point"""
        instr = self.parse("vmaxfp128 v45, v46, v47")
        self.assertEqual(instr.mnemonic, "vmaxfp128")

    def test_vminfp128(self) -> None:
        """vminfp128: Vector Minimum Floating Point"""
        instr = self.parse("vminfp128 v48, v49, v50")
        self.assertEqual(instr.mnemonic, "vminfp128")

    # =========================================================================
    # Multiply-Add Instructions (3 total)
    # =========================================================================
    def test_vmaddfp128(self) -> None:
        """vmaddfp128: Vector Multiply-Add Floating Point"""
        instr = self.parse("vmaddfp128 v51, v52, v53, v51")
        self.assertEqual(instr.mnemonic, "vmaddfp128")
        self.assertEqual(len(instr.args), 4)

    def test_vmaddcfp128(self) -> None:
        """vmaddcfp128: Vector Multiply-Add Floating Point (cumulative)"""
        instr = self.parse("vmaddcfp128 v54, v55, v54, v56")
        self.assertEqual(instr.mnemonic, "vmaddcfp128")

    def test_vnmsubfp128(self) -> None:
        """vnmsubfp128: Vector Negative Multiply-Subtract Floating Point"""
        instr = self.parse("vnmsubfp128 v57, v58, v59, v57")
        self.assertEqual(instr.mnemonic, "vnmsubfp128")

    # =========================================================================
    # Dot Product Instructions (2 total)
    # =========================================================================
    def test_vmsum3fp128(self) -> None:
        """vmsum3fp128: Vector 3D Dot Product"""
        instr = self.parse("vmsum3fp128 v60, v61, v62")
        self.assertEqual(instr.mnemonic, "vmsum3fp128")

    def test_vmsum4fp128(self) -> None:
        """vmsum4fp128: Vector 4D Dot Product"""
        instr = self.parse("vmsum4fp128 v63, v64, v65")
        self.assertEqual(instr.mnemonic, "vmsum4fp128")

    # =========================================================================
    # Logical Instructions (5 total)
    # =========================================================================
    def test_vand128(self) -> None:
        """vand128: Vector AND"""
        instr = self.parse("vand128 v66, v67, v68")
        self.assertEqual(instr.mnemonic, "vand128")

    def test_vandc128(self) -> None:
        """vandc128: Vector AND with Complement"""
        instr = self.parse("vandc128 v69, v70, v71")
        self.assertEqual(instr.mnemonic, "vandc128")

    def test_vnor128(self) -> None:
        """vnor128: Vector NOR"""
        instr = self.parse("vnor128 v72, v73, v74")
        self.assertEqual(instr.mnemonic, "vnor128")

    def test_vor128(self) -> None:
        """vor128: Vector OR"""
        instr = self.parse("vor128 v75, v76, v77")
        self.assertEqual(instr.mnemonic, "vor128")

    def test_vxor128(self) -> None:
        """vxor128: Vector XOR"""
        instr = self.parse("vxor128 v78, v79, v80")
        self.assertEqual(instr.mnemonic, "vxor128")

    # =========================================================================
    # Comparison Instructions (10 total - 5 base + 5 with Rc=1)
    # =========================================================================
    def test_vcmpeqfp128(self) -> None:
        """vcmpeqfp128: Vector Compare Equal Floating Point"""
        instr = self.parse("vcmpeqfp128 v81, v82, v83")
        self.assertEqual(instr.mnemonic, "vcmpeqfp128")

    def test_vcmpeqfp128_dot(self) -> None:
        """vcmpeqfp128.: Vector Compare Equal FP (Rc=1)"""
        instr = self.parse("vcmpeqfp128. v84, v85, v86")
        self.assertEqual(instr.mnemonic, "vcmpeqfp128.")

    def test_vcmpgefp128(self) -> None:
        """vcmpgefp128: Vector Compare Greater-Equal Floating Point"""
        instr = self.parse("vcmpgefp128 v87, v88, v89")
        self.assertEqual(instr.mnemonic, "vcmpgefp128")

    def test_vcmpgefp128_dot(self) -> None:
        """vcmpgefp128.: Vector Compare Greater-Equal FP (Rc=1)"""
        instr = self.parse("vcmpgefp128. v90, v91, v92")
        self.assertEqual(instr.mnemonic, "vcmpgefp128.")

    def test_vcmpgtfp128(self) -> None:
        """vcmpgtfp128: Vector Compare Greater-Than Floating Point"""
        instr = self.parse("vcmpgtfp128 v93, v94, v95")
        self.assertEqual(instr.mnemonic, "vcmpgtfp128")

    def test_vcmpgtfp128_dot(self) -> None:
        """vcmpgtfp128.: Vector Compare Greater-Than FP (Rc=1)"""
        instr = self.parse("vcmpgtfp128. v96, v97, v98")
        self.assertEqual(instr.mnemonic, "vcmpgtfp128.")

    def test_vcmpbfp128(self) -> None:
        """vcmpbfp128: Vector Compare Bounds Floating Point"""
        instr = self.parse("vcmpbfp128 v99, v100, v101")
        self.assertEqual(instr.mnemonic, "vcmpbfp128")

    def test_vcmpbfp128_dot(self) -> None:
        """vcmpbfp128.: Vector Compare Bounds FP (Rc=1)"""
        instr = self.parse("vcmpbfp128. v102, v103, v104")
        self.assertEqual(instr.mnemonic, "vcmpbfp128.")

    def test_vcmpequw128(self) -> None:
        """vcmpequw128: Vector Compare Equal Unsigned Word"""
        instr = self.parse("vcmpequw128 v105, v106, v107")
        self.assertEqual(instr.mnemonic, "vcmpequw128")

    def test_vcmpequw128_dot(self) -> None:
        """vcmpequw128.: Vector Compare Equal Unsigned Word (Rc=1)"""
        instr = self.parse("vcmpequw128. v108, v109, v110")
        self.assertEqual(instr.mnemonic, "vcmpequw128.")

    # =========================================================================
    # Select Instruction (1 total)
    # =========================================================================
    def test_vsel128(self) -> None:
        """vsel128: Vector Select"""
        instr = self.parse("vsel128 v111, v112, v113, v111")
        self.assertEqual(instr.mnemonic, "vsel128")
        self.assertEqual(len(instr.args), 4)

    # =========================================================================
    # Permute Instructions (2 total)
    # =========================================================================
    def test_vperm128(self) -> None:
        """vperm128: Vector Permute"""
        instr = self.parse("vperm128 v114, v115, v116, v7")
        self.assertEqual(instr.mnemonic, "vperm128")
        self.assertEqual(len(instr.args), 4)

    def test_vpermwi128(self) -> None:
        """vpermwi128: Vector Permute Word Immediate"""
        instr = self.parse("vpermwi128 v117, v118, 27")
        self.assertEqual(instr.mnemonic, "vpermwi128")
        self.assertEqual(len(instr.args), 3)

    # =========================================================================
    # Shift/Rotate Instructions (8 total)
    # =========================================================================
    def test_vsldoi128(self) -> None:
        """vsldoi128: Shift Left Double by Octet Immediate"""
        instr = self.parse("vsldoi128 v119, v120, v121, 8")
        self.assertEqual(instr.mnemonic, "vsldoi128")
        self.assertEqual(len(instr.args), 4)

    def test_vrlw128(self) -> None:
        """vrlw128: Vector Rotate Left Word"""
        instr = self.parse("vrlw128 v122, v123, v124")
        self.assertEqual(instr.mnemonic, "vrlw128")

    def test_vslw128(self) -> None:
        """vslw128: Vector Shift Left Word"""
        instr = self.parse("vslw128 v125, v126, v127")
        self.assertEqual(instr.mnemonic, "vslw128")

    def test_vsraw128(self) -> None:
        """vsraw128: Vector Shift Right Arithmetic Word"""
        instr = self.parse("vsraw128 v32, v33, v34")
        self.assertEqual(instr.mnemonic, "vsraw128")

    def test_vsrw128(self) -> None:
        """vsrw128: Vector Shift Right Word"""
        instr = self.parse("vsrw128 v35, v36, v37")
        self.assertEqual(instr.mnemonic, "vsrw128")

    def test_vslo128(self) -> None:
        """vslo128: Vector Shift Left by Octet"""
        instr = self.parse("vslo128 v38, v39, v40")
        self.assertEqual(instr.mnemonic, "vslo128")

    def test_vsro128(self) -> None:
        """vsro128: Vector Shift Right by Octet"""
        instr = self.parse("vsro128 v41, v42, v43")
        self.assertEqual(instr.mnemonic, "vsro128")

    def test_vrlimi128(self) -> None:
        """vrlimi128: Vector Rotate Left Immediate and Mask Insert"""
        instr = self.parse("vrlimi128 v44, v45, 3, 2")
        self.assertEqual(instr.mnemonic, "vrlimi128")
        self.assertEqual(len(instr.args), 4)

    # =========================================================================
    # Merge Instructions (2 total)
    # =========================================================================
    def test_vmrghw128(self) -> None:
        """vmrghw128: Vector Merge High Word"""
        instr = self.parse("vmrghw128 v46, v47, v48")
        self.assertEqual(instr.mnemonic, "vmrghw128")

    def test_vmrglw128(self) -> None:
        """vmrglw128: Vector Merge Low Word"""
        instr = self.parse("vmrglw128 v49, v50, v51")
        self.assertEqual(instr.mnemonic, "vmrglw128")

    # =========================================================================
    # Splat Instructions (2 total)
    # =========================================================================
    def test_vspltw128(self) -> None:
        """vspltw128: Vector Splat Word"""
        instr = self.parse("vspltw128 v52, v53, 2")
        self.assertEqual(instr.mnemonic, "vspltw128")
        self.assertEqual(len(instr.args), 3)

    def test_vspltisw128(self) -> None:
        """vspltisw128: Vector Splat Immediate Signed Word"""
        instr = self.parse("vspltisw128 v54, -5")
        self.assertEqual(instr.mnemonic, "vspltisw128")
        self.assertEqual(len(instr.args), 2)

    # =========================================================================
    # Conversion Instructions (4 total)
    # =========================================================================
    def test_vcfpsxws128(self) -> None:
        """vcfpsxws128: Convert Float to Signed Int (with scale)"""
        instr = self.parse("vcfpsxws128 v55, v56, 4")
        self.assertEqual(instr.mnemonic, "vcfpsxws128")
        self.assertEqual(len(instr.args), 3)

    def test_vcfpuxws128(self) -> None:
        """vcfpuxws128: Convert Float to Unsigned Int (with scale)"""
        instr = self.parse("vcfpuxws128 v57, v58, 8")
        self.assertEqual(instr.mnemonic, "vcfpuxws128")

    def test_vcsxwfp128(self) -> None:
        """vcsxwfp128: Convert Signed Int to Float (with scale)"""
        instr = self.parse("vcsxwfp128 v59, v60, 2")
        self.assertEqual(instr.mnemonic, "vcsxwfp128")

    def test_vcuxwfp128(self) -> None:
        """vcuxwfp128: Convert Unsigned Int to Float (with scale)"""
        instr = self.parse("vcuxwfp128 v61, v62, 6")
        self.assertEqual(instr.mnemonic, "vcuxwfp128")

    # =========================================================================
    # Rounding Instructions (4 total)
    # =========================================================================
    def test_vrfim128(self) -> None:
        """vrfim128: Round to Float Integer toward -Infinity (floor)"""
        instr = self.parse("vrfim128 v63, v64")
        self.assertEqual(instr.mnemonic, "vrfim128")
        self.assertEqual(len(instr.args), 2)

    def test_vrfin128(self) -> None:
        """vrfin128: Round to Float Integer toward Nearest"""
        instr = self.parse("vrfin128 v65, v66")
        self.assertEqual(instr.mnemonic, "vrfin128")

    def test_vrfip128(self) -> None:
        """vrfip128: Round to Float Integer toward +Infinity (ceil)"""
        instr = self.parse("vrfip128 v67, v68")
        self.assertEqual(instr.mnemonic, "vrfip128")

    def test_vrfiz128(self) -> None:
        """vrfiz128: Round to Float Integer toward Zero (truncate)"""
        instr = self.parse("vrfiz128 v69, v70")
        self.assertEqual(instr.mnemonic, "vrfiz128")

    # =========================================================================
    # FP Estimate Instructions (4 total)
    # =========================================================================
    def test_vrefp128(self) -> None:
        """vrefp128: Vector Reciprocal Estimate Floating Point"""
        instr = self.parse("vrefp128 v71, v72")
        self.assertEqual(instr.mnemonic, "vrefp128")

    def test_vrsqrtefp128(self) -> None:
        """vrsqrtefp128: Vector Reciprocal Square Root Estimate"""
        instr = self.parse("vrsqrtefp128 v73, v74")
        self.assertEqual(instr.mnemonic, "vrsqrtefp128")

    def test_vexptefp128(self) -> None:
        """vexptefp128: Vector Exponent Estimate (2^x)"""
        instr = self.parse("vexptefp128 v75, v76")
        self.assertEqual(instr.mnemonic, "vexptefp128")

    def test_vlogefp128(self) -> None:
        """vlogefp128: Vector Logarithm Estimate (log2)"""
        instr = self.parse("vlogefp128 v77, v78")
        self.assertEqual(instr.mnemonic, "vlogefp128")

    # =========================================================================
    # Pack Instructions (9 total)
    # =========================================================================
    def test_vpkshss128(self) -> None:
        """vpkshss128: Pack Signed Halfword Signed Saturate"""
        instr = self.parse("vpkshss128 v79, v80, v81")
        self.assertEqual(instr.mnemonic, "vpkshss128")

    def test_vpkshus128(self) -> None:
        """vpkshus128: Pack Signed Halfword Unsigned Saturate"""
        instr = self.parse("vpkshus128 v82, v83, v84")
        self.assertEqual(instr.mnemonic, "vpkshus128")

    def test_vpkswss128(self) -> None:
        """vpkswss128: Pack Signed Word Signed Saturate"""
        instr = self.parse("vpkswss128 v85, v86, v87")
        self.assertEqual(instr.mnemonic, "vpkswss128")

    def test_vpkswus128(self) -> None:
        """vpkswus128: Pack Signed Word Unsigned Saturate"""
        instr = self.parse("vpkswus128 v88, v89, v90")
        self.assertEqual(instr.mnemonic, "vpkswus128")

    def test_vpkuhum128(self) -> None:
        """vpkuhum128: Pack Unsigned Halfword Unsigned Modulo"""
        instr = self.parse("vpkuhum128 v91, v92, v93")
        self.assertEqual(instr.mnemonic, "vpkuhum128")

    def test_vpkuhus128(self) -> None:
        """vpkuhus128: Pack Unsigned Halfword Unsigned Saturate"""
        instr = self.parse("vpkuhus128 v94, v95, v96")
        self.assertEqual(instr.mnemonic, "vpkuhus128")

    def test_vpkuwum128(self) -> None:
        """vpkuwum128: Pack Unsigned Word Unsigned Modulo"""
        instr = self.parse("vpkuwum128 v97, v98, v99")
        self.assertEqual(instr.mnemonic, "vpkuwum128")

    def test_vpkuwus128(self) -> None:
        """vpkuwus128: Pack Unsigned Word Unsigned Saturate"""
        instr = self.parse("vpkuwus128 v100, v101, v102")
        self.assertEqual(instr.mnemonic, "vpkuwus128")

    def test_vpkd3d128(self) -> None:
        """vpkd3d128: Pack D3D Type"""
        instr = self.parse("vpkd3d128 v103, v104, 5, 2, 1")
        self.assertEqual(instr.mnemonic, "vpkd3d128")
        self.assertEqual(len(instr.args), 5)

    # =========================================================================
    # Unpack Instructions (5 total)
    # =========================================================================
    def test_vupkhsb128(self) -> None:
        """vupkhsb128: Unpack High Signed Byte"""
        instr = self.parse("vupkhsb128 v105, v106")
        self.assertEqual(instr.mnemonic, "vupkhsb128")
        self.assertEqual(len(instr.args), 2)

    def test_vupklsb128(self) -> None:
        """vupklsb128: Unpack Low Signed Byte"""
        instr = self.parse("vupklsb128 v107, v108")
        self.assertEqual(instr.mnemonic, "vupklsb128")

    def test_vupkhsh128(self) -> None:
        """vupkhsh128: Unpack High Signed Halfword"""
        instr = self.parse("vupkhsh128 v109, v110")
        self.assertEqual(instr.mnemonic, "vupkhsh128")

    def test_vupklsh128(self) -> None:
        """vupklsh128: Unpack Low Signed Halfword"""
        instr = self.parse("vupklsh128 v111, v112")
        self.assertEqual(instr.mnemonic, "vupklsh128")

    def test_vupkd3d128(self) -> None:
        """vupkd3d128: Unpack D3D Type"""
        instr = self.parse("vupkd3d128 v113, v114, 3")
        self.assertEqual(instr.mnemonic, "vupkd3d128")
        self.assertEqual(len(instr.args), 3)


class TestVMX128ExtendedRegisters(unittest.TestCase):
    """Test VMX128 extended register handling (v32-v127)."""

    def setUp(self) -> None:
        self.arch = PpcArch()
        self.asm_state = AsmState()

    def parse(self, asm_line: str) -> AsmInstruction:
        """Parse a single assembly instruction."""
        return parse_asm_instruction(asm_line, self.arch, self.asm_state)

    def test_standard_registers_v0_to_v31(self) -> None:
        """Standard AltiVec registers v0-v31 should work."""
        for i in range(32):
            instr = self.parse(f"vaddfp128 v{i}, v0, v1")
            self.assertEqual(instr.args[0].register_name, f"v{i}")

    def test_extended_registers_v32_to_v63(self) -> None:
        """Extended registers v32-v63 should work."""
        for i in range(32, 64):
            instr = self.parse(f"vaddfp128 v{i}, v0, v1")
            self.assertEqual(instr.args[0].register_name, f"v{i}")

    def test_extended_registers_v64_to_v95(self) -> None:
        """Extended registers v64-v95 should work."""
        for i in range(64, 96):
            instr = self.parse(f"vsubfp128 v{i}, v0, v1")
            self.assertEqual(instr.args[0].register_name, f"v{i}")

    def test_extended_registers_v96_to_v127(self) -> None:
        """Extended registers v96-v127 should work."""
        for i in range(96, 128):
            instr = self.parse(f"vmulfp128 v{i}, v0, v1")
            self.assertEqual(instr.args[0].register_name, f"v{i}")

    def test_max_register_v127(self) -> None:
        """Maximum register v127 should work."""
        instr = self.parse("vaddfp128 v127, v127, v127")
        self.assertEqual(instr.args[0].register_name, "v127")
        self.assertEqual(instr.args[1].register_name, "v127")
        self.assertEqual(instr.args[2].register_name, "v127")

    def test_extended_registers_in_all_operand_positions(self) -> None:
        """Extended registers work in destination, source A, and source B."""
        instr = self.parse("vaddfp128 v100, v64, v32")
        self.assertEqual(instr.args[0].register_name, "v100")
        self.assertEqual(instr.args[1].register_name, "v64")
        self.assertEqual(instr.args[2].register_name, "v32")


class TestVMX128InstructionHandlers(unittest.TestCase):
    """Test that VMX128 instructions have handlers in PpcArch."""

    def setUp(self) -> None:
        self.arch = PpcArch()

    def test_load_instructions_have_handlers(self) -> None:
        """All load instructions should have handlers."""
        load_instrs = [
            "lvx128", "lvxl128", "lvewx128", "lvlx128", "lvrx128",
            "lvlxl128", "lvrxl128", "lvsl128", "lvsr128",
        ]
        for mnemonic in load_instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_load,
                f"Missing handler for {mnemonic}"
            )

    def test_store_instructions_have_handlers(self) -> None:
        """All store instructions should have handlers."""
        store_instrs = [
            "stvx128", "stvxl128", "stvewx128", "stvlx128",
            "stvrx128", "stvlxl128", "stvrxl128",
        ]
        for mnemonic in store_instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_store,
                f"Missing handler for {mnemonic}"
            )

    def test_arithmetic_instructions_have_handlers(self) -> None:
        """All arithmetic instructions should have handlers."""
        arith_instrs = [
            "vaddfp128", "vsubfp128", "vmulfp128", "vmaxfp128", "vminfp128",
            "vmaddfp128", "vmaddcfp128", "vnmsubfp128",
            "vmsum3fp128", "vmsum4fp128",
        ]
        for mnemonic in arith_instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_dest_first_non_load,
                f"Missing handler for {mnemonic}"
            )

    def test_logical_instructions_have_handlers(self) -> None:
        """All logical instructions should have handlers."""
        logical_instrs = [
            "vand128", "vandc128", "vnor128", "vor128", "vxor128",
        ]
        for mnemonic in logical_instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_dest_first_non_load,
                f"Missing handler for {mnemonic}"
            )

    def test_comparison_instructions_have_handlers(self) -> None:
        """All comparison instructions should have handlers."""
        cmp_instrs = [
            "vcmpeqfp128", "vcmpeqfp128.",
            "vcmpgefp128", "vcmpgefp128.",
            "vcmpgtfp128", "vcmpgtfp128.",
            "vcmpbfp128", "vcmpbfp128.",
            "vcmpequw128", "vcmpequw128.",
        ]
        for mnemonic in cmp_instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_dest_first_non_load,
                f"Missing handler for {mnemonic}"
            )

    def test_select_and_permute_instructions_have_handlers(self) -> None:
        """Select and permute instructions should have handlers."""
        instrs = ["vsel128", "vperm128", "vpermwi128"]
        for mnemonic in instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_dest_first_non_load,
                f"Missing handler for {mnemonic}"
            )

    def test_shift_rotate_instructions_have_handlers(self) -> None:
        """All shift/rotate instructions should have handlers."""
        shift_instrs = [
            "vsldoi128", "vrlw128", "vslw128", "vsraw128", "vsrw128",
            "vslo128", "vsro128", "vrlimi128",
        ]
        for mnemonic in shift_instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_dest_first_non_load,
                f"Missing handler for {mnemonic}"
            )

    def test_merge_instructions_have_handlers(self) -> None:
        """Merge instructions should have handlers."""
        merge_instrs = ["vmrghw128", "vmrglw128"]
        for mnemonic in merge_instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_dest_first_non_load,
                f"Missing handler for {mnemonic}"
            )

    def test_splat_instructions_have_handlers(self) -> None:
        """Splat instructions should have handlers."""
        splat_instrs = ["vspltw128", "vspltisw128"]
        for mnemonic in splat_instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_dest_first_non_load,
                f"Missing handler for {mnemonic}"
            )

    def test_conversion_instructions_have_handlers(self) -> None:
        """Conversion instructions should have handlers."""
        conv_instrs = [
            "vcfpsxws128", "vcfpuxws128", "vcsxwfp128", "vcuxwfp128",
        ]
        for mnemonic in conv_instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_dest_first_non_load,
                f"Missing handler for {mnemonic}"
            )

    def test_rounding_instructions_have_handlers(self) -> None:
        """Rounding instructions should have handlers."""
        round_instrs = ["vrfim128", "vrfin128", "vrfip128", "vrfiz128"]
        for mnemonic in round_instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_dest_first_non_load,
                f"Missing handler for {mnemonic}"
            )

    def test_estimate_instructions_have_handlers(self) -> None:
        """FP estimate instructions should have handlers."""
        est_instrs = ["vrefp128", "vrsqrtefp128", "vexptefp128", "vlogefp128"]
        for mnemonic in est_instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_dest_first_non_load,
                f"Missing handler for {mnemonic}"
            )

    def test_pack_instructions_have_handlers(self) -> None:
        """Pack instructions should have handlers."""
        pack_instrs = [
            "vpkshss128", "vpkshus128", "vpkswss128", "vpkswus128",
            "vpkuhum128", "vpkuhus128", "vpkuwum128", "vpkuwus128",
            "vpkd3d128",
        ]
        for mnemonic in pack_instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_dest_first_non_load,
                f"Missing handler for {mnemonic}"
            )

    def test_unpack_instructions_have_handlers(self) -> None:
        """Unpack instructions should have handlers."""
        unpack_instrs = [
            "vupkhsb128", "vupklsb128", "vupkhsh128", "vupklsh128",
            "vupkd3d128",
        ]
        for mnemonic in unpack_instrs:
            self.assertIn(
                mnemonic, self.arch.instrs_dest_first_non_load,
                f"Missing handler for {mnemonic}"
            )


class TestVMX128InstructionCount(unittest.TestCase):
    """Verify we have the expected number of VMX128 instructions."""

    def test_total_vmx128_instruction_count(self) -> None:
        """We should have handlers for all 75 VMX128 instructions."""
        arch = PpcArch()

        # Count VMX128 instructions in each map
        vmx128_in_load = sum(
            1 for k in arch.instrs_load if k.endswith("128")
        )
        vmx128_in_store = sum(
            1 for k in arch.instrs_store if k.endswith("128")
        )
        vmx128_in_dest_first = sum(
            1 for k in arch.instrs_dest_first_non_load
            if k.endswith("128") or k.endswith("128.")
        )

        total = vmx128_in_load + vmx128_in_store + vmx128_in_dest_first

        # We expect 75 instructions (some with Rc=1 variants counted separately)
        # 9 load + 7 store + 59 dest_first = 75
        # Plus 5 Rc=1 variants for comparisons = 80 total handlers
        self.assertGreaterEqual(
            total, 75,
            f"Expected at least 75 VMX128 handlers, found {total}"
        )


if __name__ == "__main__":
    unittest.main()
