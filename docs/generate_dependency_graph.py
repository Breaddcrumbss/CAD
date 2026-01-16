#!/usr/bin/env python3
"""
Generate a dependency graph from the Makefile.
Parses the Makefile to extract stage dependencies and generates a DOT graph.
"""

import re
import subprocess
import sys

# Define the stages and their dependencies based on Makefile structure
# Format: (target_pattern, [dependency_patterns], stage_name)
STAGES = [
    {
        'name': 'parameter',
        'artifact': '{boat}.{config}.parameter.json',
        'depends_on': ['boat.json', 'configuration.json'],
        'color': '#a8e6cf'
    },
    {
        'name': 'design',
        'artifact': '{boat}.{config}.design.FCStd',
        'depends_on': ['parameter'],
        'color': '#dcedc1'
    },
    {
        'name': 'color',
        'artifact': '{boat}.{config}.color.FCStd',
        'depends_on': ['design', 'material.json'],
        'color': '#ffd3b6'
    },
    {
        'name': 'mass',
        'artifact': '{boat}.{config}.mass.json',
        'depends_on': ['design', 'material.json'],
        'color': '#ffaaa5'
    },
    {
        'name': 'render',
        'artifact': '{boat}.{config}.render.png',
        'depends_on': ['color'],
        'color': '#ff8b94'
    },
    {
        'name': 'step',
        'artifact': '{boat}.{config}.step.step',
        'depends_on': ['design'],
        'color': '#b5ead7'
    },
]

INPUTS = [
    {'name': 'boat.json', 'label': 'constant/boat/*.json', 'color': '#c7ceea'},
    {'name': 'configuration.json', 'label': 'constant/configuration/*.json', 'color': '#c7ceea'},
    {'name': 'material.json', 'label': 'constant/material/*.json', 'color': '#c7ceea'},
]

def generate_dot():
    """Generate DOT graph representation."""
    lines = [
        'digraph MakefileDependencies {',
        '    rankdir=LR;',
        '    node [shape=box, style="rounded,filled", fontname="Helvetica"];',
        '    edge [fontname="Helvetica", fontsize=10];',
        '',
        '    // Input files (constants)',
        '    subgraph cluster_inputs {',
        '        label="Constants";',
        '        style=dashed;',
        '        color=gray;',
    ]

    # Add input nodes
    for inp in INPUTS:
        lines.append(f'        {inp["name"].replace(".", "_")} [label="{inp["label"]}", fillcolor="{inp["color"]}"];')

    lines.extend([
        '    }',
        '',
        '    // Processing stages',
        '    subgraph cluster_stages {',
        '        label="Stages (src/*)";',
        '        style=dashed;',
        '        color=gray;',
    ])

    # Add stage nodes
    for stage in STAGES:
        label = f"{stage['name']}\\n{stage['artifact']}"
        lines.append(f'        {stage["name"]} [label="{label}", fillcolor="{stage["color"]}"];')

    lines.extend([
        '    }',
        '',
        '    // Dependencies',
    ])

    # Add edges
    for stage in STAGES:
        for dep in stage['depends_on']:
            dep_node = dep.replace('.', '_')
            lines.append(f'    {dep_node} -> {stage["name"]};')

    lines.extend([
        '',
        '    // Legend',
        '    subgraph cluster_legend {',
        '        label="Legend";',
        '        style=solid;',
        '        color=black;',
        '        legend_input [label="Input (JSON)", fillcolor="#c7ceea"];',
        '        legend_stage [label="Stage", fillcolor="#a8e6cf"];',
        '        legend_input -> legend_stage [style=invis];',
        '    }',
        '}',
    ])

    return '\n'.join(lines)


def main():
    dot_content = generate_dot()

    if len(sys.argv) > 1 and sys.argv[1] == '--dot':
        # Output DOT format only
        print(dot_content)
    else:
        # Try to generate PNG
        output_file = sys.argv[1] if len(sys.argv) > 1 else 'docs/dependency_graph.png'

        try:
            result = subprocess.run(
                ['dot', '-Tpng', '-o', output_file],
                input=dot_content,
                text=True,
                capture_output=True
            )
            if result.returncode == 0:
                print(f"✓ Generated {output_file}")
            else:
                print(f"Error running dot: {result.stderr}", file=sys.stderr)
                sys.exit(1)
        except FileNotFoundError:
            print("Error: 'dot' (graphviz) not found. Install with:", file=sys.stderr)
            print("  brew install graphviz  # macOS", file=sys.stderr)
            print("  apt install graphviz   # Linux", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
