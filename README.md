# HarakaV2
For an explanation of the rationale behind Haraka v2, see the [paper](https://eprint.iacr.org/2016/098.pdf).

An implementation of the Haraka v2 512-bit hash function in SystemVerilog, validated using cocotb.
There's not much to this project, except a bit of experimentation and an example setup for using cocotb and verilator to test a SystemVerilog module.
Initially developed as part of an exploration into the VerusHash 2.2 algorithm, which uses Haraka v2 internally, both in it's 512 and 256 bit variants, but the project was later abandoned, because the internals of VerusHash 2.2 are, well, *weird*, and largely undocumented, except in some highly obscure C++ code.

## The hash function
Haraka v2 is meant to be a really simple and fast hash function, that's internally based on multiple parallel rounds of the AES round function, keyed with publicly known constants, and a simple permutation function after that.
This function is run 5 times for each input, and the resulting state is then mixed with the input (feed-forward and XOR), truncated (only in the 512-bit variant), and then output.
For a more details, look into the paper, or the python implementation under `src/lib/haraka.py`.

## The Hardware implementation
Is not much more complicated than the outline above.
It's split into two modules, the haraka function itself, and a sub-module that implements a single AES round function, living in `src/rtl/haraka.sv` and `src/rtl/aes.sv`, respectively.
I experimented a bit with different implementations of the sbox - using a simple LUT, or an optimized design, but in the end, Vivado seems to prefer the LUT approach, with the other one being much larger in synthesis.
Apart from these, there's also the `src/rtl/haraka_types.sv` file, that defines the s-box LUT and Haraka's round-constants, as well as an enum of the Haraka module's internal states.

The implementation is a bit quirky:
- While the module requires multiple cycles to complete a single hash (5 to be exact), it requires the input-data to stay constant during that time, otherwise it'd need to save it internally, which was intentionally omitted, because, as mentioned, this was meant to be part of a larger project, with the VerusHash wrapper around it.

## Testing
Testing is handled via cocotb, the entrypoints, which compile the `verilator` testbenches are in the `tests` directory, and call into their respective testbenches, which are in the `cocotb` directory.
Nothing fancy here, either, just running the python implementation against the hardware and checking the results.
For AES, we also check the intermediate states, which would be possible for Haraka as well, but I didn't bother to implement that.

## Installing and running the tests
Dependency management is handled via `poetry`, so you'll need to install that first.
Then, you can install the dependencies via `poetry install`, and run the tests via `poetry run pytest -rA`.
Note that the simulations require `verilator` to be installed on your machine and accessible in your current `PATH`.