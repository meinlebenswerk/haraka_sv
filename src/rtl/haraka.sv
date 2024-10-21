// Implementation of Haraka v2 512 hash
// 512-bit input, 256-bit output

module HarakaV2_512
    import harakav2::*;
#(
    parameter M = 2, // # of AES rounds per Haraka round
    parameter T = 5, // # of Haraka rounds
    localparam int BITS_T_CTR = $clog2(T)
)
(
    input  wire         clk,
    input  wire         rst_n,
    input  wire         start,
    input  wire [511:0] msg,
    output wire [255:0] hash,
    output wire         done
);

// Internal state
haraka_state_t state, next_state;
logic [BITS_T_CTR-1:0] t_ctr;
logic [511:0] state_reg;

// State-transition process
always_comb begin
    next_state = state;
    unique case(state)
        HARAKA_IDLE: begin
            if (start) next_state = HARAKA_RUN;
        end
        HARAKA_RUN: begin
            if (t_ctr == T-1) next_state = HARAKA_IDLE;
        end
    endcase
end

// State-register update
always_ff @(posedge clk) begin
    if (!rst_n) begin
        state <= HARAKA_IDLE;
    end else begin
        state <= next_state;
    end
end

// Counter process
always_ff @(posedge clk) begin
    if (!rst_n) begin
        t_ctr <= 0;
    end else begin
        unique case(state)
            HARAKA_IDLE: begin
                t_ctr <= 0;
            end
            HARAKA_RUN: begin
                if (t_ctr == T-1) begin
                    t_ctr <= 0;
                end else begin
                    t_ctr <= t_ctr + 1;
                end
            end
        endcase
    end
end

// Done signal process
// done is asserted when this module processes the last round
assign done = state == HARAKA_RUN && t_ctr == T-1;

// Combinatorial process for state -> state update

// AES rounds
wire [511:0] state_aes_out_0;
wire [511:0] state_aes_out;
generate
    // Loop over the blocks
    for (genvar j = 0; j < 4; j = j + 1) begin
        // AES round I
        Haraka_AES_ROUND aes_inst0(
            .key(HARAKA512_RC[(t_ctr * 8) + 0*4 + j]),
            .msg(state_reg[j*128 +: 128]),
            .out(state_aes_out_0[j*128 +: 128])
        );

        Haraka_AES_ROUND aes_inst1(
            .key(HARAKA512_RC[(t_ctr * 8) + 1*4 + j]),
            .msg(state_aes_out_0[j*128 +: 128]),
            .out(state_aes_out[j*128 +: 128])
        );
    end
endgenerate

// State-permutation
wire [511:0] state_perm_out;
assign state_perm_out[ 0*32 +: 32] = state_aes_out[ 3*32 +: 32];
assign state_perm_out[ 1*32 +: 32] = state_aes_out[11*32 +: 32];
assign state_perm_out[ 2*32 +: 32] = state_aes_out[ 7*32 +: 32];
assign state_perm_out[ 3*32 +: 32] = state_aes_out[15*32 +: 32];
assign state_perm_out[ 4*32 +: 32] = state_aes_out[ 8*32 +: 32];
assign state_perm_out[ 5*32 +: 32] = state_aes_out[ 0*32 +: 32];
assign state_perm_out[ 6*32 +: 32] = state_aes_out[12*32 +: 32];
assign state_perm_out[ 7*32 +: 32] = state_aes_out[ 4*32 +: 32];
assign state_perm_out[ 8*32 +: 32] = state_aes_out[ 9*32 +: 32];
assign state_perm_out[ 9*32 +: 32] = state_aes_out[ 1*32 +: 32];
assign state_perm_out[10*32 +: 32] = state_aes_out[13*32 +: 32];
assign state_perm_out[11*32 +: 32] = state_aes_out[ 5*32 +: 32];
assign state_perm_out[12*32 +: 32] = state_aes_out[ 2*32 +: 32];
assign state_perm_out[13*32 +: 32] = state_aes_out[10*32 +: 32];
assign state_perm_out[14*32 +: 32] = state_aes_out[ 6*32 +: 32];
assign state_perm_out[15*32 +: 32] = state_aes_out[14*32 +: 32];


// state-register process
always_ff @(posedge clk) begin
    if (!rst_n) begin
        state_reg <= 512'h0;
    end else begin
        unique case(state)
            HARAKA_IDLE: begin
                if (start) state_reg <= msg; // Not sure if this actually helps
            end
            HARAKA_RUN: begin
                state_reg <= state_perm_out;
            end
        endcase
    end
end

// Feed-forward
wire [511:0] state_ff;
assign state_ff = state_reg ^ msg;

// Output Truncation
assign hash[0 +: 64] = state_ff[64 +: 64]; // x2, x3
assign hash[64 +: 128] = state_ff[192 +: 128]; // x6, x7, x8, x9
assign hash[192 +: 64] = state_ff[384 +: 64]; // x12, x13

endmodule