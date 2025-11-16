const std = @import("std");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const address = try std.net.Address.parseIp("127.0.0.1", 8080);
    var server = try address.listen(.{
        .reuse_address = true,
    });
    defer server.deinit();

    std.debug.print("Server is running on port 8080...\n", .{});

    while (true) {
        const connection = try server.accept();
        const thread = try std.Thread.spawn(.{}, handleConnection, .{ allocator, connection });
        thread.detach();
    }
}

fn handleConnection(allocator: std.mem.Allocator, connection: std.net.Server.Connection) void {
    defer connection.stream.close();

    var buffer: [4096]u8 = undefined;
    _ = connection.stream.read(&buffer) catch |err| {
        std.debug.print("Error reading request: {}\n", .{err});
        return;
    };

    const response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 13\r\nConnection: close\r\n\r\nHello, World!";

    _ = connection.stream.writeAll(response) catch |err| {
        std.debug.print("Error writing response: {}\n", .{err});
        return;
    };

    _ = allocator;
}
