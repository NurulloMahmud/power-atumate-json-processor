import json
from datetime import datetime, timedelta
import random
from onedrive import upload_file


def generate_weather_data(num_records: int = 10) -> dict:
    """
    Generate sample weather data records.
    
    Returns a dict with metadata and a list of weather readings.
    """
    base_time = datetime.now()
    
    cities = ["New York", "London", "Tokyo", "Paris", "Sydney"]
    
    records = []
    for i in range(num_records):
        record_time = base_time - timedelta(hours=i)
        records.append({
            "timestamp": record_time.isoformat(),
            "city": random.choice(cities),
            "temperature_celsius": round(random.uniform(-5, 35), 1),
            "humidity_percent": random.randint(30, 90),
            "wind_speed_kmh": round(random.uniform(0, 50), 1),
            "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Windy", "Snowy"]),
        })
    
    return {
        "report_generated_at": base_time.isoformat(),
        "total_records": num_records,
        "data": records,
    }


def main():
    print("Generating weather data...")
    weather_data = generate_weather_data(num_records=10)
    
    json_content = json.dumps(weather_data, indent=2)
    print(f"Generated {weather_data['total_records']} records")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"weather_report_{timestamp}.json"
    
    print(f"Uploading {filename} to OneDrive...")
    result = upload_file(json_content.encode("utf-8"), filename)
    
    print(f"\nSuccess! File available at: {result.get('webUrl')}")
    print("\nSample of uploaded data:")
    print(json.dumps(weather_data["data"][:3], indent=2))


if __name__ == "__main__":
    main()