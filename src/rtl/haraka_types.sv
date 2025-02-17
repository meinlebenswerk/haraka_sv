package harakav2;


    // AES S-Box
    localparam bit [7:0] AES_SBOX [256] = {
        8'h63, 8'h7C, 8'h77, 8'h7B, 8'hF2, 8'h6B, 8'h6F, 8'hC5, 8'h30, 8'h01, 8'h67, 8'h2B, 8'hFE, 8'hD7, 8'hAB, 8'h76, 
        8'hCA, 8'h82, 8'hC9, 8'h7D, 8'hFA, 8'h59, 8'h47, 8'hF0, 8'hAD, 8'hD4, 8'hA2, 8'hAF, 8'h9C, 8'hA4, 8'h72, 8'hC0, 
        8'hB7, 8'hFD, 8'h93, 8'h26, 8'h36, 8'h3F, 8'hF7, 8'hCC, 8'h34, 8'hA5, 8'hE5, 8'hF1, 8'h71, 8'hD8, 8'h31, 8'h15, 
        8'h04, 8'hC7, 8'h23, 8'hC3, 8'h18, 8'h96, 8'h05, 8'h9A, 8'h07, 8'h12, 8'h80, 8'hE2, 8'hEB, 8'h27, 8'hB2, 8'h75, 
        8'h09, 8'h83, 8'h2C, 8'h1A, 8'h1B, 8'h6E, 8'h5A, 8'hA0, 8'h52, 8'h3B, 8'hD6, 8'hB3, 8'h29, 8'hE3, 8'h2F, 8'h84, 
        8'h53, 8'hD1, 8'h00, 8'hED, 8'h20, 8'hFC, 8'hB1, 8'h5B, 8'h6A, 8'hCB, 8'hBE, 8'h39, 8'h4A, 8'h4C, 8'h58, 8'hCF, 
        8'hD0, 8'hEF, 8'hAA, 8'hFB, 8'h43, 8'h4D, 8'h33, 8'h85, 8'h45, 8'hF9, 8'h02, 8'h7F, 8'h50, 8'h3C, 8'h9F, 8'hA8, 
        8'h51, 8'hA3, 8'h40, 8'h8F, 8'h92, 8'h9D, 8'h38, 8'hF5, 8'hBC, 8'hB6, 8'hDA, 8'h21, 8'h10, 8'hFF, 8'hF3, 8'hD2, 
        8'hCD, 8'h0C, 8'h13, 8'hEC, 8'h5F, 8'h97, 8'h44, 8'h17, 8'hC4, 8'hA7, 8'h7E, 8'h3D, 8'h64, 8'h5D, 8'h19, 8'h73, 
        8'h60, 8'h81, 8'h4F, 8'hDC, 8'h22, 8'h2A, 8'h90, 8'h88, 8'h46, 8'hEE, 8'hB8, 8'h14, 8'hDE, 8'h5E, 8'h0B, 8'hDB, 
        8'hE0, 8'h32, 8'h3A, 8'h0A, 8'h49, 8'h06, 8'h24, 8'h5C, 8'hC2, 8'hD3, 8'hAC, 8'h62, 8'h91, 8'h95, 8'hE4, 8'h79, 
        8'hE7, 8'hC8, 8'h37, 8'h6D, 8'h8D, 8'hD5, 8'h4E, 8'hA9, 8'h6C, 8'h56, 8'hF4, 8'hEA, 8'h65, 8'h7A, 8'hAE, 8'h08, 
        8'hBA, 8'h78, 8'h25, 8'h2E, 8'h1C, 8'hA6, 8'hB4, 8'hC6, 8'hE8, 8'hDD, 8'h74, 8'h1F, 8'h4B, 8'hBD, 8'h8B, 8'h8A, 
        8'h70, 8'h3E, 8'hB5, 8'h66, 8'h48, 8'h03, 8'hF6, 8'h0E, 8'h61, 8'h35, 8'h57, 8'hB9, 8'h86, 8'hC1, 8'h1D, 8'h9E, 
        8'hE1, 8'hF8, 8'h98, 8'h11, 8'h69, 8'hD9, 8'h8E, 8'h94, 8'h9B, 8'h1E, 8'h87, 8'hE9, 8'hCE, 8'h55, 8'h28, 8'hDF, 
        8'h8C, 8'hA1, 8'h89, 8'h0D, 8'hBF, 8'hE6, 8'h42, 8'h68, 8'h41, 8'h99, 8'h2D, 8'h0F, 8'hB0, 8'h54, 8'hBB, 8'h16
    };

    // Haraka round-constants
    localparam bit [127:0] HARAKA512_RC [40] = {
        128'h0684704ce620c00ab2c5fef075817b9d,
        128'h8b66b4e188f3a06b640f6ba42f08f717,
        128'h3402de2d53f28498cf029d609f029114,
        128'h0ed6eae62e7b4f08bbf3bcaffd5b4f79,
        128'hcbcfb0cb4872448b79eecd1cbe397044,
        128'h7eeacdee6e9032b78d5335ed2b8a057b,
        128'h67c28f435e2e7cd0e2412761da4fef1b,
        128'h2924d9b0afcacc07675ffde21fc70b3b,
        128'hab4d63f1e6867fe9ecdb8fcab9d465ee,
        128'h1c30bf84d4b7cd645b2a404fad037e33,
        128'hb2cc0bb9941723bf69028b2e8df69800,
        128'hfa0478a6de6f55724aaa9ec85c9d2d8a,
        128'hdfb49f2b6b772a120efa4f2e29129fd4,
        128'h1ea10344f449a23632d611aebb6a12ee,
        128'haf0449884b0500845f9600c99ca8eca6,
        128'h21025ed89d199c4f78a2c7e327e593ec,
        128'hbf3aaaf8a759c9b7b9282ecd82d40173,
        128'h6260700d6186b01737f2efd910307d6b,
        128'h5aca45c22130044381c29153f6fc9ac6,
        128'h9223973c226b68bb2caf92e836d1943a,
        128'hd3bf9238225886eb6cbab958e51071b4,
        128'hdb863ce5aef0c677933dfddd24e1128d,
        128'hbb606268ffeba09c83e48de3cb2212b1,
        128'h734bd3dce2e4d19c2db91a4ec72bf77d,
        128'h43bb47c361301b434b1415c42cb3924e,
        128'hdba775a8e707eff603b231dd16eb6899,
        128'h6df3614b3c7559778e5e23027eca472c,
        128'hcda75a17d6de7d776d1be5b9b88617f9,
        128'hec6b43f06ba8e9aa9d6c069da946ee5d,
        128'hcb1e6950f957332ba25311593bf327c1,
        128'h2cee0c7500da619ce4ed0353600ed0d9,
        128'hf0b1a5a196e90cab80bbbabc63a4a350,
        128'hae3db1025e962988ab0dde30938dca39,
        128'h17bb8f38d554a40b8814f3a82e75b442,
        128'h34bb8a5b5f427fd7aeb6b779360a16f6,
        128'h26f65241cbe5543843ce5918ffbaafde,
        128'h4ce99a54b9f3026aa2ca9cf7839ec978,
        128'hae51a51a1bdff7be40c06e2822901235,
        128'ha0c1613cba7ed22bc173bc0f48a659cf,
        128'h756acc03022882884ad6bdfde9c59da1
    };

    // Haraka module state-machine
    typedef enum logic [1:0] {
        HARAKA_IDLE,
        HARAKA_RUN
    } haraka_state_t;

endpackage