using backend;
using backend.Utils;
using Microsoft.EntityFrameworkCore;
using Scalar.AspNetCore;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddOpenApi();

builder.Services.AddSignalR();
builder.Services.AddSingleton<SimulationService>();

if (builder.Environment.EnvironmentName != "Testing")
{
    builder.Services.AddDbContext<PostgresContext>(options =>
        options.UseNpgsql(builder.Configuration.GetConnectionString("PostgresConnection")));
}

builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy
            .AllowAnyOrigin()
            .AllowAnyMethod()
            .AllowAnyHeader();
    });
});

var app = builder.Build();

app.MapHub<SimulationHub>("/simulation-hub");
app.UseWebSockets();
app.Use(async (context, next) =>
{
    if (context.Request.Path == "/ws" && context.WebSockets.IsWebSocketRequest)
    {
        using var webSocket = await context.WebSockets.AcceptWebSocketAsync();
        var service = context.RequestServices.GetRequiredService<SimulationService>();
        await service.StartListening(webSocket);
    }
    else
    {
        await next();
    }
});

if (app.Environment.IsDevelopment() || app.Environment.IsEnvironment("Testing"))
{
    app.MapOpenApi();
    app.MapScalarApiReference();
}

app.UseCors();

app.UseAuthorization();

app.MapControllers();

app.Run();

public partial class Program
{
}