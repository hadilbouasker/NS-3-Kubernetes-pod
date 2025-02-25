import csv
import subprocess
import time

def run_simulation(dataRate, simTime, packetSize, start_time, numberOfUes):
    ns3_command = [
        "./ns3",  
        "run",  
        f'scratch/cttc-nr-mimo-demo-vbr-auto-ue --dataRate={dataRate} --simTime={simTime} --packetSize={packetSize} --numberOfUes={numberOfUes}'
    ]
    
    print(f"Running simulation with: dataRate={dataRate}, simTime={simTime}, packetSize={packetSize}, start_time={start_time}, numberOfUes={numberOfUes}")
    subprocess.Popen(ns3_command)

def main():
    csv_file_path = "output_with_UE.csv"  
    
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        start_time = 0  # This will hold the cumulative sum of time intervals
        initial_time = time.time()  
        previous_seconds = None  # To track the previous 'seconds' value

        for row in reader:
            # skipping empty rows by checking all the required fields
            if not row["seconds"] or not row["dataRate"] or not row["simTime"] or not row["packetSize"]:
                continue

            try:
                seconds = float(row["seconds"])
                dataRate = float(row["dataRate"])
                simTime = int(row["simTime"])
                packetSize = int(row["packetSize"])
                numberOfUes = int(row["numberOfUes"])

                # Check if the current 'seconds' value is the same as the previous one
                if previous_seconds is not None and seconds != previous_seconds:
                    # Add the 'seconds' value to the start_time only when the seconds differ
                    start_time += seconds

                    # Calculate the time difference between now and when the simulation should start
                    time_to_wait = start_time - (time.time() - initial_time)

                    # Wait until the calculated start time
                    if time_to_wait > 0:
                        time.sleep(time_to_wait)

                run_simulation(dataRate, simTime, packetSize, start_time, numberOfUes)

                time.sleep(simTime)

                previous_seconds = seconds

            except ValueError as e:
                print(f"Error parsing row: {row}, Error: {e}")
                continue

if __name__ == "__main__":
    main()


