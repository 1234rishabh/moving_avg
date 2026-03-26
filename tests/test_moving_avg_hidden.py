from __future__ import annotations

import os
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb_tools.runner import get_runner

@cocotb.test()
async def test_simultaneous_flush_and_load(dut):
    """Test that a simultaneous flush and valid pulse correctly restarts the math."""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start(start_high=False))

    dut.rst_n.value = 0
    dut.flush.value = 0
    dut.valid.value = 0
    dut.din.value = 0

    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Phase 1: Fill the accumulator with high values
    for _ in range(16):
        dut.valid.value = 1
        dut.din.value = 100
        await RisingEdge(dut.clk)

    # Allow average to settle
    dut.valid.value = 0
    await RisingEdge(dut.clk)
    
    await ReadOnly()
    assert int(dut.average.value) == 100, "Initial pipeline fill failed."

    # Phase 2: The Edge Case. 
    # Assert flush AND valid simultaneously with a small number (16).
    # The expected new sum is exactly 16. The expected average is 16 >> 4 = 1.
    dut.flush.value = 1
    dut.valid.value = 1
    dut.din.value = 16
    await RisingEdge(dut.clk)

    # Remove signals
    dut.flush.value = 0
    dut.valid.value = 0
    await ReadOnly()

    actual_avg = int(dut.average.value)
    
    # If the bug is present, the Verilog scheduler allowed the valid block to 
    # overwrite the flush block using the old sum of 1600. 
    # 1600 + 16 = 1616. 1616 >> 4 = 101.
    assert actual_avg == 1, \
        f"Scheduling Failure! Expected average of 1 after simultaneous flush/load, but got {actual_avg}. " \
        "The flush command was likely swallowed by non-blocking assignment overwrites."

def test_ma_runner():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    
    # Ensure this points to the right path for your setup
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
