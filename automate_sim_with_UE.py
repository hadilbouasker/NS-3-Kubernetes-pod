import csv
import subprocess
import time
import multiprocessing
import os
import signal
from datetime import datetime, timezone

LAUNCH_LOG = os.getenv("LAUNCH_LOG", "launch_log.csv")
TS_MAP_PATH = os.getenv("TS_MAP", "timestamp_map.csv")

def append_ts_map(seconds, timestamp_str):
    wall_utc = datetime.now(timezone.utc)
    wall_local = datetime.now()  # timezone locale du conteneur
    header = ["timestamp", "seconds", "wall_utc", "wall_local"]
    exists = os.path.isfile(TS_MAP_PATH)
    with open(TS_MAP_PATH, "a", newline="") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(header)
        w.writerow([
            timestamp_str or "",
            int(seconds),
            wall_utc.isoformat(),
            wall_local.isoformat(),
        ])

def run_simulation(dataRate, simTime, packetSize, numberOfUes, seconds, timestamp_str=""):
    # map ITA -> temps réel
    append_ts_map(seconds, timestamp_str)

    ns3_command = [
        "./build/scratch/ns3.39-cttc-nr-mimo-demo-vbr-auto-ue-default",
        f"--dataRate={dataRate}",
        f"--simTime={simTime}",
        f"--packetSize={packetSize}",
        f"--numberOfUes={numberOfUes}"
    ]

    process = subprocess.Popen(
        ns3_command,
        preexec_fn=os.setsid
    )

    timeout_limit = 9
    try:
        process.wait(timeout=timeout_limit)
    except subprocess.TimeoutExpired:
        print(f"[!] Process PID {process.pid} timed out. Killing process group...")
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        process.wait()  # Ensure zombie is reaped

def launch_in_parallel(group, current_seconds):
    processes = []
    for dataRate, simTime, packetSize, numberOfUes, timestamp_str in group:
        # IMPORTANT: seconds (=current_seconds) AVANT timestamp_str
        p = multiprocessing.Process(
            target=run_simulation,
            args=(dataRate, simTime, packetSize, numberOfUes, current_seconds, timestamp_str)
        )
        p.start()
        processes.append(p)

def main():
    csv_file_path = "Data.csv"
    start_time = time.time()

    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        reader.fieldnames = [name.strip() for name in reader.fieldnames]

        current_group = []
        current_seconds = None

        try:
            first_row = next(reader)
        except StopIteration:
            print("CSV file is empty.")
            return

        row = first_row
        while True:
            try:
                seconds = float(row["seconds"])
                dataRate = float(row["dataRate"])
                simTime = int(row["simTime"])
                packetSize = int(row["packetSize"])
                numberOfUes = int(row["numberOfUes"])
                timestamp_str = row.get("timestamp", "")  # <-- AJOUT
            except (ValueError, KeyError):
                try:
                    row = next(reader)
                    continue
                except StopIteration:
                    break

            if current_seconds is None:
                current_seconds = seconds

            if seconds == current_seconds:
                # stocke aussi le timestamp ITA pour le log
                current_group.append((dataRate, simTime, packetSize, numberOfUes, timestamp_str))
            else:
                time_to_wait = current_seconds - (time.time() - start_time)
                if time_to_wait > 0:
                    time.sleep(time_to_wait)

                print(f"\n[+] Launching {len(current_group)} simulations at t = {current_seconds}")
                launch_in_parallel(current_group, current_seconds)

                current_seconds = seconds
                current_group = [(dataRate, simTime, packetSize, numberOfUes, timestamp_str)]

            try:
                row = next(reader)
            except StopIteration:
                break

        if current_group:
            time_to_wait = current_seconds - (time.time() - start_time)
            if time_to_wait > 0:
                time.sleep(time_to_wait)
            print(f"\n[+] Launching {len(current_group)} simulations at t = {current_seconds}")
            launch_in_parallel(current_group, current_seconds)

if __name__ == "__main__":
    multiprocessing.set_start_method("fork")  # Important for Linux containers
    main()


