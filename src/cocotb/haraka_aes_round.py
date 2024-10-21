
import cocotb
from cocotb.handle import SimHandleBase  # type: ignore
from cocotb.triggers import Timer  # type: ignore

from src.lib.haraka import haraka_aes_round_verbose


# Helper functions
def _pack_bytes(data: bytes | list[int]) -> int:
    value = 0
    for i, byte in enumerate(reversed(data)):
        value = value << 8 | byte
    return value

def _unpack_bytes(value: int) -> bytes:
    data = []
    for i in range(16):
        data.append(value & 0xff)
        value = value >> 8
    return bytes(data)

@cocotb.test()
async def haraka_aes_round_test(dut: SimHandleBase):
    """
    Test the AES round over a few input values
    Not exhaustive, but verifies if we're roughly on the right track
    """
    for msg_idx in range(16):
        for key_idx in range(16):
            print(f'Testing AES round with msg_idx={msg_idx} and key_idx={key_idx}')
            msg = [(i + msg_idx) & 0xff for i in range(16)]
            key = [(i + key_idx + 16) & 0xff for i in range(16)]

            ref_sub_out, ref_shift_out, ref_mix_out, ref_out = haraka_aes_round_verbose(bytes(msg), bytes(key))

            # Set the inputs to the DUT
            dut.msg.value = _pack_bytes(msg)
            dut.key.value = _pack_bytes(key)

            # Step the module (make Verilator execute a transition step)
            await Timer(10, "ns")  # type: ignore

            dut._log.info(f"msg: {bytes(msg).hex()}")
            dut._log.info(f"key: {bytes(key).hex()}")
            # Check the intermediate values
            assert _unpack_bytes(dut.sbox_out.value) == ref_sub_out, f"sbox_out mismatch, expected {ref_sub_out.hex()}, got {_unpack_bytes(dut.sbox_out.value).hex()}"
            assert _unpack_bytes(dut.shift_out.value) == ref_shift_out, f"shift_out mismatch, expected {ref_shift_out.hex()}, got {_unpack_bytes(dut.shift_out.value).hex()}"
            assert _unpack_bytes(dut.mix_out.value) == ref_mix_out, f"mix_out mismatch, expected {ref_mix_out.hex()}, got {_unpack_bytes(dut.mix_out.value).hex()}"

            # Read the output from the DUT
            out = _unpack_bytes(dut.out.value)
            dut._log.info(f"out: {out.hex()} | {ref_out.hex()}")    

            # Check the output
            assert out == ref_out, f"Output mismatch: {out.hex()} != {ref_out.hex()}"