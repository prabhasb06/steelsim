import os

file_path = "src/App.tsx"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Fix Sim Time fallback
old_time = "{snapshot?.simulation_time ? snapshot.simulation_time.replace('T', ' ').substring(0, 19) : '0000-00-00 00:00:00'}"
new_time = "{(snapshot?.simulation_time || simState?.current_time) ? (snapshot?.simulation_time || simState?.current_time)?.replace('T', ' ').substring(0, 19) : '0000-00-00 00:00:00'}"
text = text.replace(old_time, new_time)

# Fix Tick fallback
old_tick = "{snapshot?.tick ?? 0}"
new_tick = "{snapshot?.tick ?? simState?.tick ?? 0}"
text = text.replace(old_tick, new_tick)

# Fix Seed fallback
old_seed = "{snapshot?.seed || '---'}"
new_seed = "{snapshot?.seed || simState?.seed || '---'}"
text = text.replace(old_seed, new_seed)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
