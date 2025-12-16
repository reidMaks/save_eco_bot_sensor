# SaveEcoBot Sensor for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration) [![Validate](https://github.com/reidMaks/save_eco_bot_sensor/actions/workflows/validate.yaml/badge.svg)](https://github.com/reidMaks/save_eco_bot_sensor/actions/workflows/validate.yaml)


Custom component for Home Assistant to get air quality data from [SaveEcoBot](https://www.saveecobot.com/).

## Features
- **Config Flow**: Easy setup via Home Assistant UI.
- **Smart Discovery**: Automatically find nearest stations based on your Home Assistant location.
- **Efficient Data Fetching**: Fetches data for all sensors in a single API call to avoid overloading the service.
- **Multilingual**: Supports English and Ukrainian.
- **Sensors**:
  - PM2.5
  - PM10
  - Temperature
  - Humidity
  - Atmospheric Pressure
  - Air Quality Index (AQI)

## Installation

### Method 1: HACS (Recommended)
Click the button below to open the repository in HACS directly:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=reidMaks&repository=save_eco_bot_sensor&category=integration)

Alternatively:
1. Open HACS.
2. Go to "Integrations".
3. Click the 3 dots in the top right corner and select "Custom repositories".
4. Add the URL of this repository: `https://github.com/reidMaks/save_eco_bot_sensor`
5. Select **Integration** as the category.
6. Click **Add**.
7. Close the modal and find "Save Eco Bot Sensor" in the list.
8. Click **Download**.
9. Restart Home Assistant.

### Method 2: Manual
1. Download the `save_eco_bot` folder from the `custom_components` directory in this repository.
2. Copy the `save_eco_bot` folder to your Home Assistant `custom_components` directory.
3. Restart Home Assistant.

## Configuration

1. Go to **Settings** -> **Devices & Services**.
2. Click **Add Integration** in the bottom right corner.
3. Search for **SaveEcoBot**.
4. Follow the on-screen instructions:
   - **Use home location coordinates?**: If selected, it will find the 10 nearest stations to your HA location.
   - **Select City**: Alternatively, you can select a city from the list.
   - **Select Sensors**: Choose which sensors (stations/pollutants) you want to monitor.

## Updates
The integration fetches fresh data every 60 seconds.

## License
MIT