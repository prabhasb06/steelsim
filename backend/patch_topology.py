import os

with open('app/engine/topology_validator.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_check = '''                if src_tp and tgt_tp and src_tp.value > tgt_tp.value:
                    diff = src_tp.value - tgt_tp.value
                    issues.append(ValidationIssue(level="WARNING", issue_code="CAPACITY_BOTTLENECK", node_id=tgt.id, edge_id=edge.id,
                        message=f"Capacity mismatch: Upstream is {src_tp.value} {src_tp.unit}, Downstream is {tgt_tp.value} {tgt_tp.unit}.",
                        engineering_reason=f"Potential configured restriction of {diff} {tgt_tp.unit}.",
                        blocks_simulation=False))'''

new_check = '''                if src_tp and tgt_tp and src_tp.value > tgt_tp.value:
                    diff = src_tp.value - tgt_tp.value
                    # 5% tolerance threshold
                    if diff > (src_tp.value * 0.05):
                        issues.append(ValidationIssue(level="WARNING", issue_code="CAPACITY_BOTTLENECK", node_id=tgt.id, edge_id=edge.id,
                            message=f"Capacity mismatch: Upstream is {src_tp.value} {src_tp.unit}, Downstream is {tgt_tp.value} {tgt_tp.unit}.",
                            engineering_reason=f"Potential configured restriction of {round(diff, 2)} {tgt_tp.unit} (>{round(diff/src_tp.value*100, 1)}% deficit).",
                            blocks_simulation=False))'''

text = text.replace(old_check, new_check)

with open('app/engine/topology_validator.py', 'w', encoding='utf-8') as f:
    f.write(text)
