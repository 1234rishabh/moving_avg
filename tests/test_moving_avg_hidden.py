from __future__ import annotations

import os
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb_tools.runner import get_runner


@cocotb.test()
async def test_moving_average_corruption(dut):
    """Test that the moving average does not accumulate garbage data on startup."""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    # Emulate silicon power-up states by injecting random noise into the uninitialized memory
    for i in range(16):
        dut.history[i].value = random.randint(100, 255)

    dut.rst_n.value = 0
    dut.valid.value = 0
    dut.din.value = 0

    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    test_data = [10] * 20
    expected_avg = 10

    for val in test_data:
        dut.valid.value = 1
        dut.din.value = val
        await RisingEdge(dut.clk)

    dut.valid.value = 0
    await ReadOnly()

    actual_avg = int(dut.average.value)
    assert actual_avg == expected_avg, (
        f"Math Corruption! Expected average of {expected_avg}, but got {actual_avg}. "
        "Accumulator likely subtracted uninitialized memory states."
    )


def test_ma_runner():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    sources = [proj_path / "sources/ma.sv"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="moving_average",
        always=True,
        timescale=("1ns", "1ps"),
    )

    runner.test(hdl_toplevel="moving_average", test_module="test_moving_avg_hidden")


if __name__ == "__main__":
    test_ma_runner()
