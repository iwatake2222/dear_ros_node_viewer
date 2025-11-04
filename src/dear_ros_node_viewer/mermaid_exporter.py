# Copyright 2023 iwatake2222
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module to export NetworkX graph to Mermaid format"""
from __future__ import annotations
from datetime import datetime
import networkx as nx
try:
    import networkx_mermaid as nxm
    MERMAID_AVAILABLE = True
except ImportError:
    MERMAID_AVAILABLE = False
from .logger_factory import LoggerFactory

logger = LoggerFactory.create(__name__)


def export_to_mermaid_html(graph: nx.DiGraph, output_path: str, title: str = "ROS Node Graph") -> bool:
    """
    Export a NetworkX graph to Mermaid HTML format
    
    Args:
        graph: NetworkX DiGraph to export
        output_path: Path to save the HTML file
        title: Title for the diagram
    
    Returns:
        bool: True if export was successful, False otherwise
    """
    if not MERMAID_AVAILABLE:
        logger.error("networkx-mermaid is not installed. Please install it with: pip install networkx-mermaid")
        return False
    
    try:
        # Create a Mermaid Diagram Builder
        builder = nxm.builders.DiagramBuilder(
            orientation=nxm.DiagramOrientation.TOP_DOWN,
            node_shape=nxm.DiagramNodeShape.ROUND_RECTANGLE,
        )
        
        # Prepare graph for Mermaid export
        graph_copy = _prepare_graph_for_mermaid(graph)
        
        # Build the Mermaid Diagram
        mermaid_diagram: nxm.typing.MermaidDiagram = builder.build(graph_copy)
        
        # Format as HTML
        html_diagram: str = nxm.formatters.html(mermaid_diagram, title=title)
            
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_diagram)
        
        logger.info(f"Successfully exported Mermaid HTML to: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to export to Mermaid HTML: {e}")
        return False


def _prepare_graph_for_mermaid(graph: nx.DiGraph) -> nx.DiGraph:
    """
    Prepare graph for Mermaid export by ensuring proper node and edge attributes
    
    Args:
        graph: Original NetworkX DiGraph (or MultiDiGraph)
    
    Returns:
        nx.DiGraph: Copy of graph with proper attributes for Mermaid
    """
    # Create a simple DiGraph copy (not MultiDiGraph) for Mermaid
    # Mermaid doesn't support multiple edges between same nodes well
    graph_copy = nx.DiGraph()
    
    # Copy nodes with their attributes
    for node in graph.nodes():
        node_data = dict(graph.nodes[node])
        
        # Clean node name (remove quotes if present)
        clean_name = str(node).strip('"')
        
        # Set label if not present
        if 'label' not in node_data:
            node_data['label'] = clean_name
        
        # Set color if present in original graph
        if 'color' in node_data:
            color = node_data['color']
            # Convert color format if needed
            if isinstance(color, list) and len(color) >= 3:
                # Convert RGB list to hex color
                hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                node_data['color'] = hex_color
        
        graph_copy.add_node(node, **node_data)
    
    # Process edges: handle both DiGraph and MultiDiGraph
    # For MultiDiGraph, we'll consolidate multiple edges into one
    edge_labels = {}  # Store (u, v) -> [labels]
    
    if isinstance(graph, nx.MultiDiGraph):
        # MultiDiGraph: iterate with keys
        for u, v, key, edge_data in graph.edges(keys=True, data=True):
            edge_key = (u, v)
            if edge_key not in edge_labels:
                edge_labels[edge_key] = []
            
            # Collect labels from multiple edges
            if 'label' in edge_data:
                label = str(edge_data['label']).strip('"')
                if label not in edge_labels[edge_key]:
                    edge_labels[edge_key].append(label)
    else:
        # Simple DiGraph
        for u, v, edge_data in graph.edges(data=True):
            edge_key = (u, v)
            if 'label' in edge_data:
                label = str(edge_data['label']).strip('"')
                edge_labels[edge_key] = [label]
    
    # Add edges to the new graph
    for (u, v), labels in edge_labels.items():
        # Combine multiple labels with commas if there are multiple edges
        combined_label = ', '.join(labels) if labels else ''
        if combined_label:
            graph_copy.add_edge(u, v, label=combined_label)
        else:
            graph_copy.add_edge(u, v)
    
    return graph_copy


def save_graph_to_mermaid(graph: nx.DiGraph, base_dir: str = './') -> str:
    """
    Save graph to Mermaid HTML file with timestamp
    
    Args:
        graph: NetworkX DiGraph to export
        base_dir: Base directory to save files
    
    Returns:
        str: Path to saved HTML file
    """
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate filename
    html_path = f"{base_dir}ros_graph_{timestamp}.mermaid.html"
    
    # Export to HTML format
    title = "ROS Node Graph"
    export_to_mermaid_html(graph, html_path, title)
    
    return html_path
