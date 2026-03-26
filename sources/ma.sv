`timescale 1ns/1ps
module moving_average (
    input wire clk,
    input wire rst_n,
    input wire valid,
    input wire [7:0] din,
    output reg valid_out,
    output reg [11:0] average
);

    reg [7:0] history [0:15];
    reg [15:0] sum;
    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sum <= 16'd0;
            valid_out <= 1'b0;
            average <= 12'd0;
        end else begin
            valid_out <= valid;
            
            if (valid) begin
                history[0] <= din;
                for (i = 1; i < 16; i = i + 1) begin
                    history[i] <= history[i-1];
                end

                sum <= sum + din - history[15];
                
                average <= (sum + din - history[15]) >> 4; 
            end
        end
    end
endmodule
