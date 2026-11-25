# Memory Management Simulator

A beginner-friendly MCA Operating Systems mini project that demonstrates **contiguous memory allocation**.

## Features
- Configure total memory size (KB) and choose empty or 12-block fragmented demo layout
- Allocate processes using First Fit, Best Fit and Worst Fit
- Deallocate processes
- Visual memory map with block sizes and starting addresses
- Memory utilization, free memory and external fragmentation statistics
- SQLite action history

## Requirements
- macOS
- Python 3.9 or newer
- Internet connection for the first-time Flask installation

## Run on Mac using VS Code

1. Extract `MemoryManagementSimulator.zip`.
2. Open the extracted `MemoryManagementSimulator` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Run:

   ```bash
   chmod +x run_mac.command
   ./run_mac.command
   ```

5. Wait for Flask to start, then open this address in your browser:

   `http://127.0.0.1:5000`

Keep the VS Code terminal running while using the simulator. Press `Control + C` in the terminal to stop it.

### Manual setup (alternative)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Then visit `http://127.0.0.1:5000`.

## How to demonstrate

1. Select Empty memory, set total memory to 1024 KB and click **Apply**.
2. Allocate P1 = 200 KB using First Fit.
3. Allocate P2 = 300 KB using Best Fit.
4. Allocate P3 = 100 KB using Worst Fit.
5. Deallocate P2 and observe the free block.
6. Allocate another process and compare the strategies.
7. Use Reset to start again.

To compare algorithms, choose the 12-block fragmented demo at 1024 KB. Allocate a process of 70 KB using First Fit, reset, repeat using Best Fit, reset, and repeat using Worst Fit. Demo processes are ordinary allocated processes and can be released.

## Concepts covered
- Contiguous memory allocation
- First Fit, Best Fit and Worst Fit
- Memory utilization
- Free-space tracking
- External fragmentation
- Coalescing adjacent free blocks

## Notes
- This is an educational simulator, not a real operating-system memory manager.
- Blocks are split when a process is allocated and adjacent free blocks are merged after deallocation.
- External fragmentation is displayed as the percentage of free memory that is not part of the largest free block.
- SQLite stores a short history of actions in `simulation_history.db`, created automatically.
