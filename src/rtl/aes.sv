// Implementation of a single keyed AES round, operating over 16 bytes (128 bits)
// AES state is column-major!

// Helper functions
// GF(2^8) multiplication
function bit [7:0] gf256_mul_2 (input bit [7:0] a);
    if (a < 8'h80) begin
        gf256_mul_2 = a << 1;
    end else begin
        gf256_mul_2 = (a << 1) ^ 8'h1B;
    end
endfunction

function bit [7:0] gf256_mul_3 (input bit [7:0] a);
    gf256_mul_3 = gf256_mul_2(a) ^ a;
endfunction

module Haraka_AES_ROUND
    import harakav2::AES_SBOX;
(
    input  wire [127:0] key,
    input  wire [127:0] msg,
    output wire [127:0] out
);
// SubBytes
// Two options here: use a 256*8-bit LUT, or implement the S-Box as a function
// Likely comes out to the same thing in the end, depending on how Vivado optimizes this
wire [127:0] sbox_out;
generate
    // Iterate over each byte of the input
    for (genvar i = 0; i < 16; i = i + 1) begin
        assign sbox_out[i*8 +: 8] = AES_SBOX[msg[i*8 +: 8]];
        // tiny_sbox sbox_inst(
        //     .in(msg[i*8 +: 8]),
        //     .out(sbox_out[i*8 +: 8])
        // );
    end
endgenerate

// ShiftRows
wire [127:0] shift_out;
generate
    for(genvar i = 0; i < 4; i = i + 1) begin
        // Column 0 (no shift)
        assign shift_out[i*32 +: 8] = sbox_out[i*32 +: 8];
        // Column 1 (shift left by 1)
        if(i < 3) begin
            assign shift_out[8 + i*32 +: 8] = sbox_out[8 + (i+1)*32 +: 8];
        end else begin
            assign shift_out[8 + i*32 +: 8] = sbox_out[8 + 0*32 +: 8];
        end
        // Column 2 (shift left by 2)
        if(i < 2) begin
            assign shift_out[16 + i*32 +: 8] = sbox_out[16 + (i+2)*32 +: 8];
        end else begin
            assign shift_out[16 + i*32 +: 8] = sbox_out[16 + (i-2)*32 +: 8];
        end
        // Column 3 (shift left by 3)
        if(i < 1) begin
            assign shift_out[24 + i*32 +: 8] = sbox_out[24 + (i+3)*32 +: 8];
        end else begin
            assign shift_out[24 + i*32 +: 8] = sbox_out[24 + (i-1)*32 +: 8];
        end
    end
endgenerate

// MixColumns
wire [127:0] mix_out;
generate
    // Iterate over the columns
    for (genvar i = 0; i < 4; i = i + 1) begin
        // Compute single column
        assign mix_out[ 0 + i*32 +: 8] = gf256_mul_2(shift_out[0 + i*32 +: 8]) ^ gf256_mul_3(shift_out[8 + i*32 +: 8]) ^ shift_out[16 + i*32 +: 8] ^ shift_out[24 + i*32 +: 8];
        assign mix_out[ 8 + i*32 +: 8] = shift_out[0 + i*32 +: 8] ^ gf256_mul_2(shift_out[8 + i*32 +: 8]) ^ gf256_mul_3(shift_out[16 + i*32 +: 8]) ^ shift_out[24 + i*32 +: 8];
        assign mix_out[16 + i*32 +: 8] = shift_out[0 + i*32 +: 8] ^ shift_out[8 + i*32 +: 8] ^ gf256_mul_2(shift_out[16 + i*32 +: 8]) ^ gf256_mul_3(shift_out[24 + i*32 +: 8]);
        assign mix_out[24 + i*32 +: 8] = gf256_mul_3(shift_out[0 + i*32 +: 8]) ^ shift_out[8 + i*32 +: 8] ^ shift_out[16 + i*32 +: 8] ^ gf256_mul_2(shift_out[24 + i*32 +: 8]);
    end
endgenerate

// AddRoundKey(key)
assign out = mix_out ^ key;

endmodule