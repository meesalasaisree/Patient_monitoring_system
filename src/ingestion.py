import pandas as pd
import random
import time
import os

def generate_patient_data(num_records=100):
    data = []
    for i in range(num_records):
        patient_id = random.randint(1000, 9999)
        heart_rate = random.randint(50, 120)  # Normal 60-100
        oxygen_sat = random.randint(85, 100)  # Normal 95-100
        temperature = round(random.uniform(96.0, 104.0), 1) # Normal 98.6
        # Label: 1 if vitals are critical, 0 if normal
        is_critical = 1 if (heart_rate > 100 or heart_rate < 60 or oxygen_sat < 90) else 0
        
        data.append([patient_id, heart_rate, oxygen_sat, temperature, is_critical])
    
    df = pd.DataFrame(data, columns=['patient_id', 'heart_rate', 'oxygen_sat', 'temperature', 'label'])
    
    # Save to the data folder we created
    output_path = os.path.join('data', 'patient_vitals.csv')
    df.to_csv(output_path, index=False)
    print(f"Generated {num_records} records at {output_path}")

if __name__ == "__main__":
    generate_patient_data()