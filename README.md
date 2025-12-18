# HomeSCADA (during development)

![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)
![Tech Stack](https://img.shields.io/badge/Stack-%20.NET%20|%20Python-blue)

Platform to simulate energy consumption and optimization of single family house with heat pump, PV panels, ventilation, 3D blender model, complex simulation of temperature losses and changes etc.

## 📖 About

HomeSCADA is a high-fidelity energy simulation and management platform. Unlike simple thermostat models, it uses a custom physics engine and Model Predictive Control (MPC) to simulate thermodynamic processes in a building. The project aims to find the "sweet spot" between thermal comfort and energy efficiency by predicting weather impacts and building inertia.

## 📸 Screenshots

screenshots

## ⚙️ Core Mechanics

- Custom Simulation Engine: A Python-based engine using the Euler method for solving heat transfer equations. It operates with a high-frequency internal timestep (1s) to ensure numerical stability while reporting hourly states.
- Complex Building Physics: Models heat flow through multi-layered walls, floors (ground temperature), and roofs, accounting for solar radiation (Azimuth & Altitude), wind speed, and external temperature.
- Inverter Heat Pump Model: A non-linear model where COP (Efficiency) and Max Power are dynamic functions of external temperature and current load percentage.
- Predictive Control Logic: A "Smart Brain" that runs parallel "what-if" simulations to minimize a Cost Function (Discomfort Penalty + Energy Consumption).

## 🚀 Technical Highlights

### 🔙 Backend (.NET 9.0 & PostgreSQL)

- Central Orchestrator: Manages room schedules, user setpoints, and historical data.
- Real-time Communication: High-speed data exchange via WebSockets between the Simulation Engine and the UI.
- Data Persistence: PostgreSQL handles time-series data for long-term efficiency analysis.

### 📲 Frontend (.NET 9.0 & Blazor)

- Interactive Dashboard: Real-time visualization of room temperatures and device states.
- 3D Digital Twin: Integration with a 3D model (Blender) for spatial temperature mapping.
- Schedule Manager: Intuitive UI for setting weekly temperature targets.

### 🐍 Data Engineering (Python)

- Simulation Core: Pure Python implementation of thermodynamic laws.
- Numerical Stability: Advanced handling of simulation "explosions" through adaptive internal stepping.
- Optimization Algorithms: Implementation of lookahead logic and greedy search for optimal energy scheduling.

### 🛠️ DevOps & Infrastructure

- Languages: C#, Python 3.x, HTML/CSS.
- Frameworks: .NET 9.0 (ASP.NET Core, Blazor WebAssembly).
- Libraries (Python): Pandas (Weather data), NumPy (Interpolation/Math), WebSockets.
- Visualization: Blender (3D Modeling).
- Database: PostgreSQL.

## 💻 Tech Stack

## 🚀 Project Roadmap

### 🔴 Mandatory (MVP Core)

### 🟡 High Impact

### 🟢 Nice to Have
