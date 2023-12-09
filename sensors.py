import subprocess
import re
import sounddevice as sd
import numpy as np
import psutil
import matplotlib.pyplot as plt

class SensorValue:
    def get_value(self):
        raise NotImplementedError("Subclasses must implement get_value method")

class TemperatureSensor(SensorValue):
    def get_value(self):
        try:
            result = subprocess.run(['osx-cpu-temp'], capture_output=True, text=True)
            output = result.stdout.strip()

            temperature_matches = re.findall(r'\d+\.\d+', output)

            if temperature_matches:
                temperature = float(temperature_matches[0])
                return temperature
            else:
                print("Error retrieving temperature.")
                return None
        except Exception as e:
            print(f"Error retrieving temperature: {e}")
            return None

class BatterySensor(SensorValue):
    def get_value(self):
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_level = battery.percent
                return battery_level
            else:
                print("Battery information not available.")
                return None
        except Exception as e:
            print(f"Error retrieving battery level: {e}")
            return None

class MicrophoneNoiseSensor(SensorValue):
    def get_value(self):
        try:
            audio_data = sd.rec(int(2 * 44100), samplerate=44100, channels=1, dtype='int16')
            sd.wait()
            rms = np.sqrt(np.mean(audio_data ** 2))
            rms_rounded = round(rms, 2)

            frequencies, power = plt.psd(audio_data[:, 0], Fs=44100)
            plt.xlabel('Frequency')
            plt.ylabel('Power, dB')
            plt.title('Sound Spectrum')
            plt.show()

            return rms_rounded
        except Exception as e:
            print(f"Error retrieving microphone noise level: {e}")
            return None

class CPUUsageSensor(SensorValue):
    def get_value(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_usage_with_units = f"{cpu_usage}"
            return cpu_usage_with_units
        except Exception as e:
            print(f"Error retrieving CPU usage: {e}")
            return None

class Sensor:
    def __init__(self, sensor_value, name):
        self.sensor_value = sensor_value
        self.name = name

    def get_value(self):
        return self.sensor_value.get_value()

if __name__ == '__main__':
    sensors = [
        Sensor(TemperatureSensor(), "CPU Temperature"),
        Sensor(BatterySensor(), "Battery Level"),
        Sensor(CPUUsageSensor(), "CPU Usage"),
        Sensor(MicrophoneNoiseSensor(), "Microphone Noise Level")
    ]

    for sensor in sensors:
        result = sensor.get_value()
        if result is not None:
            print(f"{sensor.name}: {result}")
