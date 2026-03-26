`timescale 1ns/1ps
module moving_average (
    input wire clk,
    input wire rst_n,
    input wire valid,
    input wire [7:0] din,
    output reg valid_out,
    output reg [11:0] average
);

    // 16-deep delay line
    reg [7:0] history [0:15];
    reg [15:0] sum;
    reg [4:0] fill_count; // Tracks how many valid items are in the pipeline
    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sum <= 16'd0;
            valid_out <= 1'b0;
            average <= 12'd0;
            fill_count <= 5'd0;
            // NOTE: 'history' array intentionally left uninitialized to save reset routing.
        end else begin
            valid_out <= valid;
            
            if (valid) begin
                // Shift pipeline
                history[0] <= din;
                for (i = 1; i < 16; i = i + 1) begin
                    history[i] <= history[i-1];
                end

                // CORRECT: Only increment count up to 16.
                if (fill_count < 5'd16) begin
                    fill_count <= fill_count + 1'b1;
                end

                // CORRECT: Only subtract the history if the pipeline is actually full.
                // This prevents the uninitialized 'X' states or random silicon garbage 
                // from corrupting the math during the first 16 cycles.
                if (fill_count == 5'd16) begin
                    sum <= sum + din - history[15];
                    average <= (sum + din - history[15]) >> 4;
                end else begin
                    sum <= sum + din;
                    average <= (sum + din) >> 4; 
                end
            end
        end
    end
endmodule
