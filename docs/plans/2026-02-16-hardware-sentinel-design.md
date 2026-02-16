# Hardware Sentinel Design

## Overview
The "Hardware Sentinel" is a comprehensive monitoring and control module for the Jetson Orin Nano dashboard. It bridges the gap between passive telemetry and active hardware management, focusing on thermals, performance, and system safety.

## Architecture
- **Backend Expansion**: `web_monitor/app.py` and `scripts/get_stats.py` will be updated to expose full `jtop` thermal and system metrics.
- **New API Endpoints**:
  - `GET /api/hardware_sentinel`: Aggregates thermal zones, fan status, and swap pressure.
  - `POST /api/hardware_sentinel/turbo`: Toggles `jetson_clocks` (Turbo Mode).
  - `POST /api/hardware_sentinel/fan`: Sets fan profiles (Quiet, Cool, Manual).
- **Frontend Integration**: A new `HardwareSentinelCard` component in React, leveraging Shadcn UI.

## Features

### 1. Detailed Thermal Monitoring
- **Thermal Grid**: Live tracking of CPU (all clusters), GPU, AO (Ambient), and SOC zones.
- **Color Coding**: 
  - Blue: < 45°C (Idle)
  - Orange: 45°C - 75°C (Working)
  - Red: > 75°C (Caution)

### 2. Active Performance Controls
- **Turbo Mode Toggle**: Manual switch for `jetson.clocks`. Persists until manually disabled.
- **Fan Profile Selector**: 
  - **Quiet**: Low RPM.
  - **Cool**: Max RPM for heavy loads.
  - **Manual**: Slider for specific 0-100% control.
- **Optimistic UI Updates**: Instant toggle feedback with background server verification.

### 3. Safety Guardrails (Hardware Interlock)
- **Auto-Throttle**: If any zone > 82°C, Turbo Mode is automatically disabled and Fan is forced to "Cool".
- **Visual Alert**: Prominent warning banner and toggle lockout until < 75°C.
- **Superuser Override**: Hidden setting to bypass safety if absolutely necessary.

### 4. Swap & Memory Pressure
- **Memory Pressure Gauge**: Tracks Physical RAM vs. 16GB NVMe Swap usage.
- **Thrashing Detection**: Monitors Swap In/Out rates to identify performance bottlenecks.
- **Endurance Monitoring**: Basic health check for the NVMe boot/swap drive.

## Implementation Steps
1. Update `scripts/get_stats.py` to return full `jtop` stats.
2. Add `HardwareSentinel` endpoints to `web_monitor/app.py`.
3. Create `HardwareSentinelCard.tsx` and its associated hook.
4. Integrate into `App.tsx` layout.
5. Implement safety logic in the frontend and backend.
