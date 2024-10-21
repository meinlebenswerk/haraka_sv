from cocotb_test.simulator import run  # type: ignore


verilog_sources = [
    "src/rtl/haraka_types.sv",
    "src/rtl/tiny_sbox.sv",
    "src/rtl/aes.sv",
    "src/rtl/haraka.sv",
]

def test_aes_round():
    run(
        simulator='verilator',
        verilog_sources=verilog_sources,
        testcase="haraka_round_test",
        module="src.cocotb.haraka_round",
        toplevel="HarakaV2_512",
        compile_args=[
            # *(["-Wall"] if enable_all_warnings else []),  # Enable all warnings
            "-Wno-UNUSED",
            "-Wno-GENUNNAMED",
            "-Wno-PKGNODECL",
            "-Wno-UNOPTFLAT", # Not the greatest thing
            "-Werror-CASEINCOMPLETE",
            "-Werror-CASEOVERLAP",
        ],
        extra_args=[
            "--trace-max-width",
            "2048",
            "--trace-max-array",
            "2048",
            "--trace",
            "--trace-structs",
        ],
        sim_args=[
            "--trace-max-width",
            "2048",
            "--trace-max-array",
            "2048",
            "--trace",
            "--trace-structs",
            "-v",
            "dump.vcd",
        ],
    )