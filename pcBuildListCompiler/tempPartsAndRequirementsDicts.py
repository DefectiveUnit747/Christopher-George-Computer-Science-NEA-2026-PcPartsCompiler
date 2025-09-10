partsDb = {
    "CPU": [
        {
            "id": "cpu1",
            "name": "Intel Core i5-12400F",
            "socket": "LGA1700",
            "tdp": 65,
            "score": 17800,
            "price": 160
        },
        {
            "id": "cpu2",
            "name": "Intel Core i7-12700K",
            "socket": "LGA1700",
            "tdp": 125,
            "score": 28000,
            "price": 350
        },
        {
            "id": "cpu3",
            "name": "AMD Ryzen 5 5600",
            "socket": "AM4",
            "tdp": 65,
            "score": 22000,
            "price": 170
        },
        {
            "id": "cpu4",
            "name": "AMD Ryzen 7 5800X",
            "socket": "AM4",
            "tdp": 105,
            "score": 28500,
            "price": 320
        },
        {
            "id": "cpu5",
            "name": "Intel Pentium Gold G6400",
            "socket": "LGA1200",
            "tdp": 58,
            "score": 4200,
            "price": 60
        }
    ],
    "GPU": [
        {
            "id": "gpu1",
            "name": "NVIDIA RTX 3060",
            "length_mm": 242,
            "tdp": 170,
            "score": 12500,
            "price": 300
        },
        {
            "id": "gpu2",
            "name": "NVIDIA RTX 3070",
            "length_mm": 267,
            "tdp": 220,
            "score": 17000,
            "price": 480
        },
        {
            "id": "gpu3",
            "name": "AMD RX 6600 XT",
            "length_mm": 240,
            "tdp": 160,
            "score": 11500,
            "price": 280
        },
        {
            "id": "gpu4",
            "name": "NVIDIA GTX 1650",
            "length_mm": 229,
            "tdp": 75,
            "score": 6500,
            "price": 150
        },
        {
            "id": "gpu5",
            "name": "NVIDIA RTX 4090",
            "length_mm": 304,
            "tdp": 450,
            "score": 38000,
            "price": 1600
        }
    ],
    "Motherboard": [
        {
            "id": "mb1",
            "name": "ASUS Prime B660-PLUS",
            "socket": "LGA1700",
            "chipset": "B660",
            "form_factor": "ATX",
            "ram_type": "DDR4",
            "max_ram": 128,
            "price": 120
        },
        {
            "id": "mb2",
            "name": "MSI MAG B550 TOMAHAWK",
            "socket": "AM4",
            "chipset": "B550",
            "form_factor": "ATX",
            "ram_type": "DDR4",
            "max_ram": 128,
            "price": 140
        },
        {
            "id": "mb3",
            "name": "Gigabyte B450M DS3H",
            "socket": "AM4",
            "chipset": "B450",
            "form_factor": "Micro-ATX",
            "ram_type": "DDR4",
            "max_ram": 64,
            "price": 80
        },
        {
            "id": "mb4",
            "name": "ASRock H510M-HDV",
            "socket": "LGA1200",
            "chipset": "H510",
            "form_factor": "Micro-ATX",
            "ram_type": "DDR4",
            "max_ram": 64,
            "price": 65
        }
    ],
    "RAM": [
        {
            "id": "ram1",
            "name": "Corsair Vengeance LPX 16GB (2x8GB) DDR4-3200 CL16",
            "capacity_gb": 16,
            "speed_mhz": 3200,
            "cas_latency": 16,
            "type": "DDR4",
            "price": 60
        },
        {
            "id": "ram2",
            "name": "G.Skill Ripjaws V 32GB (2x16GB) DDR4-3600 CL18",
            "capacity_gb": 32,
            "speed_mhz": 3600,
            "cas_latency": 18,
            "type": "DDR4",
            "price": 120
        },
        {
            "id": "ram3",
            "name": "Kingston Fury Beast 8GB DDR4-2666 CL16",
            "capacity_gb": 8,
            "speed_mhz": 2666,
            "cas_latency": 16,
            "type": "DDR4",
            "price": 30
        }
    ],
    "Storage": [
        {
            "id": "sto1",
            "name": "Samsung 970 EVO Plus 1TB NVMe SSD",
            "capacity_gb": 1000,
            "type": "NVMe",
            "price": 90
        },
        {
            "id": "sto2",
            "name": "Crucial MX500 500GB SATA SSD",
            "capacity_gb": 500,
            "type": "SATA",
            "price": 45
        },
        {
            "id": "sto3",
            "name": "Seagate Barracuda 2TB HDD",
            "capacity_gb": 2000,
            "type": "HDD",
            "price": 55
        }
    ],
    "Case": [
        {
            "id": "case1",
            "name": "NZXT H510",
            "form_factor_support": ["ATX", "Micro-ATX"],
            "gpu_max_length_mm": 381,
            "price": 70
        },
        {
            "id": "case2",
            "name": "Cooler Master Q300L",
            "form_factor_support": ["Micro-ATX"],
            "gpu_max_length_mm": 360,
            "price": 50
        },
        {
            "id": "case3",
            "name": "Fractal Design Meshify 2 Compact",
            "form_factor_support": ["ATX", "Micro-ATX"],
            "gpu_max_length_mm": 341,
            "price": 110
        }
    ],
    "PSU": [
        {
            "id": "psu1",
            "name": "Corsair CX550M 550W 80+ Bronze",
            "wattage": 550,
            "price": 60
        },
        {
            "id": "psu2",
            "name": "Seasonic Focus GX-650 650W 80+ Gold",
            "wattage": 650,
            "price": 90
        },
        {
            "id": "psu3",
            "name": "EVGA SuperNOVA 850 G5 850W 80+ Gold",
            "wattage": 850,
            "price": 130
        }
    ]
}

eldenRingMinimum = {
    "OS": "Windows 10",
    "CPU": {
        "name": ["Intel Core i5-8400", "AMD Ryzen 3 3300X"],
        "score": 9500  # Approximate PassMark score
    },
    "RAM": {
        "required_gb": 12
    },
    "GPU": {
        "name": ["NVIDIA GeForce GTX 1060 3GB", "AMD Radeon RX 580 4GB"],
        "score": 9500  # Approximate 3DMark score
    },
    "Storage": {
        "required_gb": 60
    }
}

""""
def get_game_requirements(gameName):
    search_url = f"{BASE_URL}/games"
    params = {
        "key": API_KEY,
        "search": gameName,
        "search_exact": True  # helps avoid wrong matches
    }
    search_resp = requests.get(search_url, params=params)
    search_resp.raise_for_status()
    results = search_resp.json().get("results", [])

    if not results:
        return None  # No game found

    game_id = results[0]["id"]  # Take the first match

    # Step 2: Get game details
    details_url = f"{BASE_URL}/games/{game_id}"
    details_resp = requests.get(details_url, params={"key": API_KEY})
    details_resp.raise_for_status()
    game_data = details_resp.json()

    # Step 3: Extract PC requirements
    for platform in game_data.get("platforms", []):
        if platform["platform"]["id"] == 4:  # PC platform ID
            reqs = platform.get("requirements", {})
            return {
                "minimum": reqs.get("minimum"),
            }

    return None  # No PC requirements found

if __name__ == "__main__":
    game = "Elden Ring"
    requirements = get_game_requirements(game)
    print(requirements)
    print(f"\n{requirements['minimum']}\n")
"""""