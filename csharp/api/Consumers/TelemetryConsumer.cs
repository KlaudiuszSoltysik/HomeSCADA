using MassTransit;
using backend.Contracts;

namespace backend.Consumers;

public class TelemetryConsumer : IConsumer<SimulationTelemetry>
{
    public Task Consume(ConsumeContext<SimulationTelemetry> context)
    {
        var msg = context.Message;

        Console.WriteLine($"[RabbitMQ] Otrzymano krok symulacji! Czas: {msg.Timestamp}, Temp: {msg.Weather.Temperature}°C, Pokoi: {msg.RoomTemperatures.Count}");

        return Task.CompletedTask;
    }
}