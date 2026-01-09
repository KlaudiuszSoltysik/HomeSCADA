# District Digital Twin (during development)

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

### 🔙 Backend (.NET 10 & PostgreSQL)

- Central Orchestrator: Manages room schedules, user setpoints, and historical data.
- Real-time Communication: High-speed data exchange via WebSockets between the Simulation Engine and the UI.
- Data Persistence: PostgreSQL handles time-series data for long-term efficiency analysis.

### 📲 Frontend (.NET 10 & Blazor)

- Interactive Dashboard: Real-time visualization of room temperatures and device states.
- 3D Digital Twin: Integration with a 3D model (Blender) for spatial temperature mapping.
- Schedule Manager: Intuitive UI for setting weekly temperature targets.

### 🐍 Data Engineering (Python)

- Simulation Core: Pure Python implementation of thermodynamic laws.
- Numerical Stability: Advanced handling of simulation "explosions" through adaptive internal stepping.
- Optimization Algorithms: Implementation of lookahead logic and greedy search for optimal energy scheduling.

### 🛠️ DevOps & Infrastructure

- Languages: C#, Python 3.x, HTML/CSS.
- Frameworks: .NET 10 (ASP.NET Core, Blazor WebAssembly).
- Libraries (Python): Pandas (Weather data), NumPy (Interpolation/Math), WebSockets.
- Visualization: Blender (3D Modeling).
- Database: PostgreSQL.

## 💻 Tech Stack

## 🚀 Project Roadmap

### 🔴 Mandatory (MVP Core)

### 🟡 High Impact

### 🟢 Nice to Have

To jest doskonałe podsumowanie. Przechodzimy z "hobbystycznego projektu" na "profesjonalny system klasy Enterprise".

Przygotowałem dla Ciebie Dokumentację Koncepcyjną (Project Vision Statement). Jest sformatowana tak, żebyś mógł ją wrzucić do README.md w repozytorium albo wydrukować i powiesić nad biurkiem. Zawiera wszystkie nasze ustalenia, architekturę i cele biznesowe.

🏙️ ResiFlow: Community Energy Management System (CEMS)
Koncepcja: Zaawansowana platforma IoT/SaaS do zarządzania energią i komfortem w budownictwie wielorodzinnym. System wykorzystuje technologię Digital Twin do symulacji fizyki budynku oraz algorytmy predykcyjne do optymalizacji kosztów ogrzewania i bilansowania mocy przyłączeniowej.

🎯 Główny Cel
Stworzenie skalowalnego systemu backendowego, który zarządza "wirtualnym blokiem" (a docelowo całym osiedlem), rozwiązując realne problemy współczesnej energetyki:

Dynamiczne Bilansowanie Mocy (DLM): Zapobieganie awariom sieci przy ładowaniu aut elektrycznych (EV).

Optymalizacja Hybrydowa: Automatyczny wybór źródła ciepła (Gaz vs Pompa Ciepła) w zależności od pogody i cen prądu.

Sprawiedliwe Rozliczanie: Precyzyjny billing dla mieszkańców na podstawie wirtualnych liczników ciepła.

🏢 Model Obiektu (The Digital Twin)
Symulowany obiekt to nowoczesny, 3-kondygnacyjny blok mieszkalny ("Sześciopak").

Struktura: 6 mieszkań (układ 3 piętra x 2 lokale) + Garaż podziemny.

Fizyka (Thermal Coupling): Zaimplementowane przenikanie ciepła między sąsiadami (macierz sąsiedztwa). Mieszkanie środkowe traci mniej ciepła niż narożne.

Infrastruktura:

Źródło ciepła: Hybrydowy węzeł cieplny (Kocioł Gazowy + Pompa Ciepła + Bufor).

Źródło prądu: Instalacja PV na dachu + Przyłącze sieciowe (z limitem mocy).

Obciążenie: 6x AGD/Bytowe + 2x Ładowarka EV w garażu.

🛠️ Architektura Techniczna
System podzielony na dwie główne domeny zgodnie z zasadą Separation of Concerns:

1. The Physics Engine (Python) 🐍
   Mikroserwis odpowiedzialny za "Prawdę Fizyczną". Stateless Compute.

Rola: Symuluje termodynamikę budynku krok po kroku (np. co 1s).

Technologia: Python + NumPy (macierze cieplne).

Komunikacja: gRPC (wysoka wydajność).

Kluczowe Klasy:

BuildingMatrix: Reprezentacja siatki mieszkań i przepływów ciepła.

SensorMock: Generuje odczyty z szumem (Noise) i awariami.

ActuatorMock: Symuluje bezwładność zaworów i urządzeń.

2. The Orchestrator (.NET 9) 🧠
   Mózg systemu, Sterownik PLC/SCADA i Logika Biznesowa.

Rola: Podejmuje decyzje, zarządza użytkownikami, liczy pieniądze.

Technologia: .NET 9, Aspire, MassTransit (RabbitMQ).

Baza Danych: PostgreSQL (Dane relacyjne/Konfiguracja) + TimescaleDB (Time-series/History).

Kluczowe Moduły:

Control Loop: Pętla sterowania (odczyt sensorów -> decyzja -> sterowanie).

Billing Engine: Agregacja zużycia energii i wyliczanie kosztów w PLN.

Load Balancer (EV): Algorytm obcinający moc ładowarek, gdy mieszkańcy gotują obiady.

3. Frontend (Blazor / Web) 🖥️
   Panel Mieszkańca: Ustawianie temperatury, podgląd rachunku, wykresy zużycia.

Panel Zarządcy: Heatmapa budynku (2D), status węzła cieplnego, alerty awarii.

🚀 Kluczowe Algorytmy (Backend Challenges)
A. Algorytm "Load Shedding" (Garaż)
Problem: Przyłącze ma 40kW. 6 mieszkań zużywa 20kW. Dwie Tesle chcą po 11kW (razem 42kW). Wywali bezpiecznik.

Rozwiązanie: Backend wykrywa wzrost zużycia w mieszkaniach i dynamicznie dławi ładowarki EV (np. do 2kW), a w nocy je odkręca.

B. Algorytm "Economic Broker" (Kotłownia)
Problem: Czym grzać?

Rozwiązanie:

Scenario 1: Świeci słońce (darmowy prąd z PV) -> Grzejemy Pompą Ciepła na maxa (magazynujemy ciepło w buforze).

Scenario 2: Noc, mróz -15°C (Pompa ma słabe COP, prąd płatny) -> Wyłączamy Pompę, odpalamy Gaz.

C. Multi-tenancy & Security
Izolacja danych: Sąsiad A nie widzi rachunków Sąsiada B.

RBAC: Tylko Zarządca może zmienić krzywą grzewczą pieca głównego.

📅 Plan Implementacji (Roadmap)
Faza 1: Python Core (Grid 2x3)

Stworzenie macierzy wymiany ciepła dla 6 mieszkań w numpy.

Wystawienie prostego interfejsu (gRPC) do pobierania temperatur.

Faza 2: .NET Foundation

Postawienie projektu Aspire.

Implementacja pętli sterowania (Control Loop), która "popycha" czas w Pythonie.

Baza danych TimescaleDB.

Faza 3: Logika "Sześciopaka"

Dodanie węzła cieplnego i logiki rozdzielania ciepła na mieszkania.

Pierwszy Dashboard (Heatmapa).

Faza 4: Advanced Features (To co "sprzedaje" w CV)

Dodanie Garażu i algorytmu ładowania EV.

Billing i konta użytkowników.

Skalowanie (architektura pod obsługę wielu bloków jednocześnie - "Rój").

własny autoscaling (zasymulowanie aws)

porządnie zrobiona grafana
