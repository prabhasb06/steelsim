# 7. Engineering canvas

The Plant Builder canvas is implemented using React Flow (`@xyflow/react`), providing an interactive 2D industrial engineering surface.

## Canvas interactions

### 1. Navigation and viewport control
- **Pan and zoom:** Middle-click drag or spacebar drag pans across the plant floor. Mouse scroll wheels adjust magnification.
- **Fit to plant:** The `Fit View` button calculates the bounding box of all placed equipment and centers the viewport with optimal padding.
- **Focus mode:** Toggles full-screen canvas editing by collapsing the global application header and navigation sidebars.

### 2. Selection and multi-selection
- Single-clicking an equipment card selects it, opening its properties in the right-side Inspector drawer.
- Shift-drag draws a selection marquee to select multiple equipment nodes for bulk movement or deletion.

### 3. Edge creation and reconnection
- Dragging from an output port handle to a compatible input port handle creates a typed industrial connection edge.
- Existing edges can be reconnected by dragging their endpoints to different compatible ports.

### 4. History management (Undo and Redo)
- The canvas tracks state changes in an internal history stack, allowing full multi-level undo and redo via toolbar buttons or keyboard shortcuts (`Ctrl+Z`, `Ctrl+Y`).

## DOM preservation across views

A common flaw in single-page applications is unmounting canvas components during navigation, resulting in loss of zoom level, viewport coordinates, and unsaved changes.

In SteelSim, the Plant Builder remains mounted in the DOM regardless of the active view mode (`OVERVIEW`, `BUILDER`, `SIMULATION`, or `OPTIMIZATION`). When navigating away from the Builder:
- The canvas container receives `opacity: 0` and `pointer-events: none`.
- All React Flow nodes and edges remain intact in memory.
- When returning to the Builder, the user's workspace is preserved instantly without re-rendering or resetting.
