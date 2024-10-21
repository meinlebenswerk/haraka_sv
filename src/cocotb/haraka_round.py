
import cocotb
from cocotb.handle import SimHandleBase  # type: ignore
from cocotb.triggers import Timer, RisingEdge  # type: ignore
from cocotb.clock import Clock  # type: ignore

from src.lib.haraka import haraka512


# Helper functions
def _pack_bytes(data: bytes | list[int]) -> int:
    value = 0
    for i, byte in enumerate(reversed(data)):
        value = value << 8 | byte
    return value

def _unpack_bytes(value: int) -> bytes:
    data = []
    for i in range(32):
        data.append(value & 0xff)
        value = value >> 8
    return bytes(data)

@cocotb.test()
async def haraka_round_test(dut: SimHandleBase):
    """
    Test the AES round over a few input values
    Not exhaustive, but verifies if we're roughly on the right track
    """
    for offset in range(16):
        print(f'Testing Haraka round with {offset=}')
        msg = [(i + offset) & 0xff for i in range(64)]
        ref_out = haraka512(bytes(msg))

        # Initialize and start the clock
        dut.clk.value = 0
        dut.rst_n.value = 1
        dut.start.value = 0
        cocotb.start_soon(Clock(dut.clk, 10, "ns").start())

        # Reset the DUT
        await RisingEdge(dut.clk)
        dut.rst_n.value = 0
        await RisingEdge(dut.clk)
        dut.rst_n.value = 1
        await RisingEdge(dut.clk)

        # Set the inputs to the DUT
        dut.msg.value = _pack_bytes(msg)
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0

        # wait until the dut signals that it's done
        await RisingEdge(dut.done)
        await RisingEdge(dut.clk) # wait for the current cycle to finish
        await Timer(1, 'step') # step through the current transition

        # Read the output from the DUT
        out = _unpack_bytes(dut.hash.value)
        dut._log.info(f"out: {out.hex()} | {ref_out.hex()}")

        # Check the output
        assert out == ref_out, f"Expected {ref_out.hex()}, got {out.hex()}"