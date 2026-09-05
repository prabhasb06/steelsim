# 13. Auto Setup

Auto Setup is an atomic orchestration workflow that transforms a set of unlinked equipment nodes into a fully wired, validated, and optimized steel manufacturing facility.

## Execution workflow

When an operator triggers **Auto Setup**, the system executes a three-phase pipeline:

<pre class="mermaid">
flowchart TD
    Step1["1. Process Auto-Wiring<br/>Connects material ports linearly from Raw Yard through Cooling Bed"]
    Step2["2. Utility Auto-Wiring<br/>Wires Substation and Water Station to all rated thermal and power consumers"]
    Step3["3. Hierarchical Auto-Layout<br/>Arranges nodes into collision-free process and infrastructure lanes"]

    Step1 --> Step2 --> Step3
</pre>

## Atomic server proposal

Auto Setup can be executed on the client or requested from the backend API:

```http
POST /api/plant/auto-setup HTTP/1.1
Content-Type: application/json

{
  "nodes": [ ... ],
  "edges": [ ... ]
}
```

### Response schema (`AutoSetupProposal`)
```json
{
  "proposed_graph": {
    "nodes": [ ... ],
    "edges": [ ... ]
  },
  "added_connections": 22,
  "layout_applied": true,
  "validation": {
    "is_valid": true,
    "issues": []
  }
}
```

If successful, the client replaces the current canvas state with the proposed graph in a single atomic transaction, saving the result to browser LocalStorage and updating the Topology Issues panel.
