using backend.Dtos;

namespace backend.Utils;

using Microsoft.AspNetCore.SignalR;
using System.Threading.Tasks;

public class SimulationHub(SimulationService simulationService) : Hub
{
    public async Task SendParameters(SimulationParameters parameters)
    {
        await simulationService.SendParameters(parameters);
    }
}