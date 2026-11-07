import os
import git
import networkx as nx
from typing import Dict, List, Any

class GitRepositoryAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)

    def extract_commit_history(self, max_commits: int = 50) -> List[Dict[str, Any]]:
        commits_data = []
        commits = list(self.repo.iter_commits('HEAD', max_count=max_commits))
        commits.reverse()  # Chronological order (Purano dekhi naya)

        for commit in commits:
            changed_files = list(commit.stats.files.keys())
            commits_data.append({
                "hash": commit.hexsha[:7],
                "full_hash": commit.hexsha,
                "author": commit.author.name,
                "message": commit.summary,
                "timestamp": commit.committed_datetime.isoformat(),
                "files_changed": changed_files,
                "additions": commit.stats.total['insertions'],
                "deletions": commit.stats.total['deletions']
            })
        return commits_data

    def generate_3d_spatial_nodes(self, max_commits: int = 50) -> Dict[str, Any]:
        """File relationships map garera 3D coordinates system tayar garchha"""
        graph = nx.Graph()
        commits = self.extract_commit_history(max_commits)
        
        file_metrics = {}

        for commit in commits:
            files = commit["files_changed"]
            for f in files:
                if f not in file_metrics:
                    file_metrics[f] = {"churn": 0, "size": 1}
                file_metrics[f]["churn"] += 1
            
            # File co-changes ke aadhar ma connections (edges) banaune
            for i in range(len(files)):
                for j in range(i + 1, len(files)):
                    f1, f2 = files[i], files[j]
                    if graph.has_edge(f1, f2):
                        graph[f1][f2]['weight'] += 1
                    else:
                        graph.add_edge(f1, f2, weight=1)

        # 3D layout coordinates calculate garne (Spring Layout)
        pos_3d = nx.spring_layout(graph, dim=3, seed=42)

        nodes = []
        for file_path, coords in pos_3d.items():
            churn = file_metrics.get(file_path, {}).get("churn", 1)
            nodes.append({
                "id": file_path,
                "x": float(coords[0] * 10),
                "y": float(coords[1] * 10),
                "z": float(coords[2] * 10),
                "churn": churn,
                "val": min(churn * 2, 8)  # Node size based on churn
            })

        links = []
        for u, v, data in graph.edges(data=True):
            links.append({
                "source": u,
                "target": v,
                "weight": data["weight"]
            })

        return {
            "nodes": nodes,
            "links": links,
            "timeline": commits
        }