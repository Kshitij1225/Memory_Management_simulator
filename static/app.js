const $ = (id) => document.getElementById(id);
let toastTimer;
function showToast(message, error=false) {
  const toast = $("toast");
  toast.textContent = message;
  toast.className = "toast show" + (error ? " error" : "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.className = "toast", 3200);
}
async function api(url, data) {
  const options = data === undefined ? {} : {
    method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(data)
  };
  const response = await fetch(url, options);
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "Something went wrong.");
  return result;
}
function number(value) { return Number(value).toLocaleString("en-IN"); }

function render(state) {
  $("totalStat").innerHTML = `${number(state.total_memory)} <small>KB</small>`;
  $("allocatedStat").innerHTML = `${number(state.allocated_memory)} <small>KB</small>`;
  $("freeStat").innerHTML = `${number(state.free_memory)} <small>KB</small>`;
  $("utilStat").innerHTML = `${state.utilization}<small>%</small>`;
  $("utilBar").style.width = `${state.utilization}%`;
  $("highAddress").textContent = `HIGH ADDRESS · ${number(state.total_memory)} KB`;
  $("fragmentCount").textContent = state.fragment_count;
  $("largestFree").textContent = `${number(state.largest_free_block)} KB`;
  $("externalFrag").textContent = `${state.external_fragmentation}%`;

  $("layout").value = state.layout;
  $("totalMemory").value = state.total_memory;
  const map = $("memoryMap");
  map.innerHTML = "";
  state.blocks.forEach(block => {
    const item = document.createElement("div");
    item.className = "memory-block " + (block.process ? "used-block" : "free-block");
    item.style.flex = `0 0 ${Math.max(44, block.size / state.total_memory * 480)}px`;
    const title = document.createElement("strong");
    title.textContent = block.process || "FREE";
    const detail = document.createElement("span");
    detail.textContent = `${number(block.size)} KB · Start ${number(block.start)}`;
    item.append(title, detail);
    map.appendChild(item);
  });

  const tbody = $("processTable");
  tbody.innerHTML = "";
  $("processCount").textContent = `${state.processes.length} process${state.processes.length === 1 ? "" : "es"}`;
  if (!state.processes.length) {
    const row = tbody.insertRow();
    const cell = row.insertCell();
    cell.colSpan = 4;
    cell.className = "empty-state";
    cell.textContent = "No processes allocated yet. Add a process to begin.";
  } else {
    state.processes.forEach(process => {
      const row = tbody.insertRow();
      [process.name, `${number(process.start)} KB`, `${number(process.size)} KB`].forEach((value, i) => {
        const cell = row.insertCell();
        cell.textContent = value;
        if (i === 0) cell.className = "process-name";
      });
      const status = row.insertCell();
      const tag = document.createElement("span");
      tag.className = "status-tag";
      tag.textContent = "Allocated";
      status.appendChild(tag);
    });
  }

  const select = $("releaseName");
  const previous = select.value;
  select.innerHTML = "";
  if (!state.processes.length) {
    select.add(new Option("No allocated processes", ""));
  } else {
    select.add(new Option("Select process", ""));
    state.processes.forEach(p => select.add(new Option(`${p.name} · ${p.size} KB`, p.name)));
    if (state.processes.some(p => p.name === previous)) select.value = previous;
  }
}
async function refresh() {
  render(await api("/api/state"));
  const history = await api("/api/history");
  const list = $("historyList");
  list.innerHTML = "";
  if (!history.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "Your simulation actions will appear here.";
    list.appendChild(empty);
  } else {
    history.forEach(entry => {
      const item = document.createElement("div");
      item.className = "history-item";
      const title = document.createElement("strong");
      title.textContent = entry.action;
      const detail = document.createElement("p");
      detail.textContent = entry.details;
      const time = document.createElement("time");
      time.textContent = entry.created_at;
      item.append(title, detail, time);
      list.appendChild(item);
    });
  }
}
$("configForm").addEventListener("submit", async e => {
  e.preventDefault();
  try {
    const state = await api("/api/configure", {total_memory: $("totalMemory").value, layout: $("layout").value});
    render(state); await refresh(); showToast("Memory configuration updated.");
  } catch (err) { showToast(err.message, true); }
});
$("allocateForm").addEventListener("submit", async e => {
  e.preventDefault();
  try {
    const result = await api("/api/allocate", {
      process_name: $("processName").value,
      size: $("processSize").value,
      strategy: $("strategy").value
    });
    render(result); await refresh(); showToast(result.message);
    $("processName").value = ""; $("processSize").value = "";
  } catch (err) { showToast(err.message, true); }
});
$("deallocateForm").addEventListener("submit", async e => {
  e.preventDefault();
  try {
    if (!$("releaseName").value) throw new Error("Select a process to release.");
    const result = await api("/api/deallocate", {process_name: $("releaseName").value});
    render(result); await refresh(); showToast(result.message);
  } catch (err) { showToast(err.message, true); }
});
$("resetButton").addEventListener("click", async () => {
  try {
    const result = await api("/api/reset", {total_memory: $("totalMemory").value || 1024, layout: $("layout").value});
    render(result); await refresh(); showToast("Simulation reset.");
  } catch (err) { showToast(err.message, true); }
});
refresh().catch(err => showToast(err.message, true));
