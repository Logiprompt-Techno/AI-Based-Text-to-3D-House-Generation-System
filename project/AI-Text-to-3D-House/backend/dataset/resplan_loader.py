import json
import pickle
import os
import networkx as nx
from shapely.geometry import Polygon, MultiPolygon
from typing import List, Dict, Any, Tuple

class ResPlanLoader:
    def __init__(self, dataset_dir: str):
        self.dataset_dir = dataset_dir
        self.pkl_path = os.path.join(dataset_dir, 'ResPlan.pkl')
        self.split_path = os.path.join(dataset_dir, 'split.json')
        self.data: List[Dict[str, Any]] = []
        self.splits: Dict[str, List[int]] = {}

    def load_splits(self):
        with open(self.split_path, 'r') as f:
            self.splits = json.load(f)

    def load_data(self):
        with open(self.pkl_path, 'rb') as f:
            self.data = pickle.load(f)
            
    @property
    def sample_count(self) -> int:
        return len(self.data)
        
    @property
    def train_ids(self) -> List[int]:
        return self.splits.get('train', [])

    @property
    def val_ids(self) -> List[int]:
        return self.splits.get('val', [])

    @property
    def test_ids(self) -> List[int]:
        return self.splits.get('test', [])

    def inspect_sample(self, index: int) -> Dict[str, Any]:
        """Safely inspects and converts a single sample into JSON-serializable format."""
        if not self.data:
            self.load_data()
            
        sample = self.data[index]
        return self._convert_sample_to_json_safe(sample)
        
    def _convert_geometry(self, geom: Any) -> Any:
        if isinstance(geom, Polygon):
            return {"type": "Polygon", "coordinates": [list(geom.exterior.coords)]}
        elif isinstance(geom, MultiPolygon):
            coords = []
            for poly in geom.geoms:
                coords.append([list(poly.exterior.coords)])
            return {"type": "MultiPolygon", "coordinates": coords}
        return None

    def _convert_graph(self, graph: Any) -> Dict[str, Any]:
        if not isinstance(graph, nx.Graph):
            return {}
        
        nodes = []
        for n, data in graph.nodes(data=True):
            safe_data = {}
            for k, v in data.items():
                if isinstance(v, (Polygon, MultiPolygon)):
                    safe_data[k] = self._convert_geometry(v)
                else:
                    safe_data[k] = v
            nodes.append((n, safe_data))
            
        edges = []
        for u, v, data in graph.edges(data=True):
            safe_data = {}
            for k, val in data.items():
                if isinstance(val, (Polygon, MultiPolygon)):
                    safe_data[k] = self._convert_geometry(val)
                else:
                    safe_data[k] = val
            edges.append((u, v, safe_data))
            
        return {"nodes": nodes, "edges": edges}

    def _convert_sample_to_json_safe(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        json_safe = {}
        
        # Room types and structural features
        geo_keys = [
            'balcony', 'bathroom', 'bedroom', 'door', 'garden', 
            'inner', 'parking', 'pool', 'wall', 'window', 
            'front_door', 'kitchen', 'land', 'living'
        ]
        
        for key in geo_keys:
            if key in sample:
                json_safe[key] = self._convert_geometry(sample[key])
                
        # Graph
        if 'graph' in sample:
            json_safe['graph'] = self._convert_graph(sample['graph'])
            
        # Metadata
        if 'id' in sample:
            json_safe['id'] = int(sample['id'])
        if 'area' in sample:
            json_safe['area'] = float(sample['area'])
        if 'net_area' in sample:
            json_safe['net_area'] = float(sample['net_area'])
        if 'wall_depth' in sample:
            json_safe['wall_depth'] = float(sample['wall_depth'])
        if 'neighbor' in sample:
            json_safe['neighbor'] = [
                self._convert_geometry(n) if isinstance(n, (Polygon, MultiPolygon)) else n 
                for n in sample['neighbor']
            ]

        return json_safe
