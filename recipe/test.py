import unittest


class TestUnicornAndroidWheel(unittest.TestCase):
    def test_aarch64_executes(self):
        from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
        from unicorn.arm64_const import UC_ARM64_REG_X0

        emulator = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        emulator.mem_map(0x1000, 0x1000)
        # mov x0, #42
        emulator.mem_write(0x1000, b"\x40\x05\x80\xd2")
        emulator.emu_start(0x1000, 0x1004)
        self.assertEqual(42, emulator.reg_read(UC_ARM64_REG_X0))
