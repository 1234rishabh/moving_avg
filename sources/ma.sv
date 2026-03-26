`timescale 1ns/1ps
module moving_average (
    input wire clk,
    input wire rst_n,
    input wire flush,
    input wire valid,
    input wire [7:0] din,
    output reg valid_out,
    output reg [11:0] average
);

    reg [7:0] history [0:15];
    reg [15:0] sum;
    reg [4:0] fill_count;
    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sum <= 16'd0;
            valid_out <= 1'b0;
            average <= 12'd0;
            fill_count <= 5'd0;
        end else begin
            valid_out <= valid;
            if (flush) begin
                sum <= 16'd0;
                fill_count <= 5'd0;
                average <= 12'd0;
            end
            
            if (valid) begin
                history[0] <= din;
                for (i = 1; i < 16; i = i + 1) begin
                    history[i] <= history[i-1];
                end

                if (fill_count < 5'd16) begin
                    fill_count <= fill_count + 1'b1;
                end

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
//new
