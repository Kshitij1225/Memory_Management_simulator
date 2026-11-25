class MemoryManager:
    """Contiguous memory allocation using First Fit, Best Fit and Worst Fit."""

    def __init__(self, total_memory=1024):
        self.configure(total_memory, "demo" if total_memory >= 12 else "empty")

    def configure(self, total_memory, layout="empty"):
        total_memory = int(total_memory)
        if total_memory < 1 or total_memory > 1000000:
            raise ValueError("Total memory must be between 1 and 1,000,000 KB.")
        if layout not in ("empty", "demo"):
            raise ValueError("Choose a valid memory layout.")
        if layout == "demo" and total_memory < 12:
            raise ValueError("Demo layout requires at least 12 KB.")
        self.total_memory = total_memory
        self.layout = layout
        self.blocks = [{"start": 0, "size": total_memory, "process": None}]
        if layout == "demo":
            weights = [12, 4, 20, 5, 8, 4, 16, 5, 10, 4, 8, 4]
            sizes = [1 + (total_memory - 12) * w // sum(weights) for w in weights]
            sizes[0] += total_memory - sum(sizes)
            self.blocks = []
            start = 0
            for i, size in enumerate(sizes):
                self.blocks.append({"start": start, "size": size,
                                    "process": None if i % 2 == 0 else f"Demo{i // 2 + 1}"})
                start += size

    def allocate(self, name, size, strategy="first"):
        name = str(name).strip()
        size = int(size)
        if not name:
            raise ValueError("Enter a process name.")
        if size <= 0:
            raise ValueError("Process size must be greater than zero.")
        if any(b["process"] == name for b in self.blocks):
            raise ValueError(f"Process {name} is already allocated.")
        if strategy not in ("first", "best", "worst"):
            raise ValueError("Choose First Fit, Best Fit or Worst Fit.")

        free_indexes = [
            i for i, block in enumerate(self.blocks)
            if block["process"] is None and block["size"] >= size
        ]
        if not free_indexes:
            largest = max((b["size"] for b in self.blocks if b["process"] is None), default=0)
            raise ValueError(
                f"Allocation failed. Largest free block is {largest} KB; "
                f"requested {size} KB. Total free memory may be fragmented."
            )

        if strategy == "first":
            chosen = free_indexes[0]
        elif strategy == "best":
            chosen = min(free_indexes, key=lambda i: self.blocks[i]["size"])
        else:
            chosen = max(free_indexes, key=lambda i: self.blocks[i]["size"])

        block = self.blocks[chosen]
        allocated = {"start": block["start"], "size": size, "process": name}
        remainder = block["size"] - size
        replacement = [allocated]
        if remainder:
            replacement.append({
                "start": block["start"] + size,
                "size": remainder,
                "process": None
            })
        self.blocks[chosen:chosen + 1] = replacement
        self._merge_free_blocks()
        return f"{name} allocated {size} KB using {strategy.title()} Fit."

    def deallocate(self, name):
        name = str(name).strip()
        if not name:
            raise ValueError("Enter a process name.")
        for block in self.blocks:
            if block["process"] == name:
                block["process"] = None
                self._merge_free_blocks()
                return f"{name} deallocated successfully."
        raise ValueError(f"Process {name} was not found.")

    def _merge_free_blocks(self):
        merged = []
        for block in self.blocks:
            if merged and merged[-1]["process"] is None and block["process"] is None:
                merged[-1]["size"] += block["size"]
            else:
                merged.append(block.copy())
        self.blocks = merged
        # Recalculate starts to maintain a continuous memory map.
        position = 0
        for block in self.blocks:
            block["start"] = position
            position += block["size"]

    def snapshot(self):
        allocated = sum(b["size"] for b in self.blocks if b["process"] is not None)
        free_blocks = [b["size"] for b in self.blocks if b["process"] is None]
        free = sum(free_blocks)
        return {
            "total_memory": self.total_memory,
            "layout": self.layout,
            "allocated_memory": allocated,
            "free_memory": free,
            "utilization": round((allocated / self.total_memory) * 100, 1),
            "fragment_count": len(free_blocks),
            "largest_free_block": max(free_blocks, default=0),
            "external_fragmentation": round(((free - max(free_blocks, default=0)) / free) * 100, 1) if free else 0,
            "blocks": [
                {**b, "status": "Allocated" if b["process"] is not None else "Free"}
                for b in self.blocks
            ],
            "processes": [
                {"name": b["process"], "size": b["size"], "start": b["start"]}
                for b in self.blocks if b["process"] is not None
            ]
        }
