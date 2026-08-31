import os

file_path = "src/App.tsx"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Fix handleCommand
old_handle_cmd = """    if (res.ok) {
        const state = await res.json();
        setSimState(state);
    }"""
new_handle_cmd = """    if (res.ok) {
        const state = await res.json();
        setSimState(state);
        setSnapshot(null);
    }"""
text = text.replace(old_handle_cmd, new_handle_cmd)

# Fix handleSpeed
old_handle_speed = """    await fetch(`/api/simulations/${activeSimId}/speed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ speed })
    });"""
new_handle_speed = """    const res = await fetch(`/api/simulations/${activeSimId}/speed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ speed })
    });
    if (res.ok) {
        const state = await res.json();
        setSimState(state);
        setSnapshot(null);
    }"""
text = text.replace(old_handle_speed, new_handle_speed)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
