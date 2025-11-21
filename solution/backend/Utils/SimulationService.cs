using backend.Dtos;

namespace backend.Utils;

using Microsoft.AspNetCore.SignalR;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;

public class SimulationService(IHubContext<SimulationHub> hubContext)
{
    private WebSocket? _pythonWebSocket;

    public async Task StartListening(WebSocket webSocket)
    {
        _pythonWebSocket = webSocket;

        var buffer = new byte[1024 * 4];
        var segment = new ArraySegment<byte>(buffer);

        if (webSocket.State == WebSocketState.Open)
        {
            Console.WriteLine("WebSocket connected.");
        }

        while (webSocket.State == WebSocketState.Open)
        {
            WebSocketReceiveResult result;
            try
            {
                result = await webSocket.ReceiveAsync(segment, CancellationToken.None);
            }
            catch (WebSocketException)
            {
                break;
            }

            if (result.MessageType == WebSocketMessageType.Close)
            {
                break;
            }

            var message = Encoding.UTF8.GetString(buffer, 0, result.Count);

            using var document = JsonDocument.Parse(message);
            var root = document.RootElement;

            if (root.TryGetProperty("Type", out var typeElement))
            {
                var messageType = typeElement.GetString() ?? string.Empty;

                switch (messageType)
                {
                    case "SimulationData":
                    {
                        var data = JsonSerializer.Deserialize<SimulationData>(message);
                        if (data != null)
                        {
                            await hubContext.Clients.All.SendAsync("UpdateSimulationData", data);
                        }

                        break;
                    }
                    default:
                        Console.WriteLine($"Received unexpected message type: {messageType}");
                        break;
                }
            }
        }

        await webSocket.CloseOutputAsync(WebSocketCloseStatus.NormalClosure,
            "Closing", CancellationToken.None);
        Console.WriteLine("WebSocket disconnected.");
    }

    public async Task SendParameters(SimulationParameters parameters)
    {
        if (_pythonWebSocket is not { State: WebSocketState.Open })
        {
            Console.WriteLine("WebSocket error.");
            return;
        }

        var commandJson = JsonSerializer.Serialize(parameters);
        var bytes = Encoding.UTF8.GetBytes(commandJson);

        await _pythonWebSocket.SendAsync(
            new ArraySegment<byte>(bytes),
            WebSocketMessageType.Text,
            true,
            CancellationToken.None);
    }
}