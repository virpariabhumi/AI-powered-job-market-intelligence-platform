import itertools
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import networkx as nx
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
JOB_SKILLS_PATH = PROJECT_ROOT / "data" / "processed" / "job_skills.csv"
GRAPH_OUTPUT_PATH = PROJECT_ROOT / "data" / "skills" / "skill_graph.json"


class DemandWeightedSkillGraph:
    """
    Constructs and queries a demand-weighted graph where:
      - Nodes = Skills (weighted by total market demand count and category)
      - Edges = Co-occurrence in identical job postings (weighted by pair frequency)
    """

    def __init__(self, job_skills_path: Path = JOB_SKILLS_PATH):
        self.df = pd.read_csv(job_skills_path)
        self.graph = nx.Graph()
        self._build_graph()

    def _build_graph(self) -> None:
        """
        Builds the NetworkX graph with node demand weights and edge co-occurrence weights.
        """
        # 1. Compute node weights (total postings per skill) & metadata
        skill_metadata = {}
        for _, row in self.df.iterrows():
            skill = row["skill"]
            category = row["category"]
            if skill not in skill_metadata:
                skill_metadata[skill] = {"demand": 0, "category": category}
            skill_metadata[skill]["demand"] += 1

        # Add nodes with attributes
        for skill, meta in skill_metadata.items():
            self.graph.add_node(
                skill,
                demand=meta["demand"],
                category=meta["category"]
            )

        # 2. Compute edge weights (co-occurrences within identical jobs)
        pair_counts = Counter()
        job_groups = self.df.groupby("job_id")["skill"].unique()

        for skills in job_groups:
            if len(skills) > 1:
                # Generate all unique pairs within this job posting
                for u, v in itertools.combinations(sorted(skills), 2):
                    pair_counts[(u, v)] += 1

        # Add edges with co-occurrence weights
        for (u, v), weight in pair_counts.items():
            self.graph.add_edge(u, v, weight=weight)

    def get_related_skills(self, skill: str, top_n: int = 5) -> List[Dict[str, any]]:
        """
        Queries the graph for the strongest co-occurring companion skills.
        """
        skill_clean = skill.strip()
        # Find exact case-insensitive match in graph nodes
        matched_node = None
        for node in self.graph.nodes():
            if node.lower() == skill_clean.lower():
                matched_node = node
                break

        if not matched_node or matched_node not in self.graph:
            return []

        neighbors = []
        for neighbor in self.graph.neighbors(matched_node):
            weight = self.graph[matched_node][neighbor]["weight"]
            category = self.graph.nodes[neighbor]["category"]
            demand = self.graph.nodes[neighbor]["demand"]
            neighbors.append({
                "skill": neighbor,
                "category": category,
                "co_occurrence": int(weight),
                "demand": int(demand)
            })

        # Rank by co-occurrence strength descending
        neighbors.sort(key=lambda x: x["co_occurrence"], reverse=True)
        return neighbors[:top_n]

    def export_graph_for_visualization(
        self,
        output_path: Path = GRAPH_OUTPUT_PATH,
        min_edge_weight: int = 3
    ) -> Dict:
        """
        Exports the graph topology into standard Nodes and Links JSON
        for Member 2's D3.js or React-Force-Graph interactive component.
        Filters out very weak edges (< min_edge_weight) to keep rendering clean.
        """
        nodes = []
        # Track connected nodes with meaningful edges
        connected_nodes = set()

        links = []
        for u, v, data in self.graph.edges(data=True):
            weight = data["weight"]
            if weight >= min_edge_weight:
                links.append({
                    "source": u,
                    "target": v,
                    "weight": int(weight)
                })
                connected_nodes.add(u)
                connected_nodes.add(v)

        for node in connected_nodes:
            nodes.append({
                "id": node,
                "demand": int(self.graph.nodes[node]["demand"]),
                "category": self.graph.nodes[node]["category"]
            })

        graph_json = {
            "metadata": {
                "total_nodes": len(nodes),
                "total_links": len(links),
                "min_edge_weight_threshold": min_edge_weight
            },
            "nodes": sorted(nodes, key=lambda x: x["demand"], reverse=True),
            "links": links
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(graph_json, f, indent=2)

        print(f"Graph JSON exported for frontend: {output_path}")
        return graph_json


_skill_graph = None

def get_graph() -> DemandWeightedSkillGraph:
    global _skill_graph
    if _skill_graph is None:
        _skill_graph = DemandWeightedSkillGraph()
    return _skill_graph


def get_companion_skills(skill: str, top_n: int = 5) -> List[Dict[str, any]]:
    """
    Public API helper for Member 2's FastAPI route.
    """
    return get_graph().get_related_skills(skill, top_n)


if __name__ == "__main__":
    print("Building Demand-Weighted Skill Graph with NetworkX...")
    sg = get_graph()
    g = sg.graph

    print("\n=== DEMAND-WEIGHTED SKILL GRAPH SUMMARY ===")
    print(f"Total Skill Nodes: {g.number_of_nodes()}")
    print(f"Total Skill Edges (Co-occurrences): {g.number_of_edges()}")

    print("\n=== SAMPLE COMPANION SKILLS QUERIES ===")
    sample_queries = ["Python", "SQL", "React", "Machine Learning"]
    for q in sample_queries:
        print(f"\nTop companion skills for '{q}':")
        companions = sg.get_related_skills(q, top_n=5)
        for c in companions:
            print(f"  -> {c['skill']:<20} | Co-occurrences: {c['co_occurrence']:>3} | Category: {c['category']}")

    print("\nExporting graph for Member 2 frontend visualization...")
    sg.export_graph_for_visualization(min_edge_weight=3)
