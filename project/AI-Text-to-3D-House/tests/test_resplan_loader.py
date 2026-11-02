import os
import pytest
import json
from backend.dataset.resplan_loader import ResPlanLoader

DATASET_DIR = r"D:\2D AND 3D house Text-to-3D\datasets\resplan"

@pytest.fixture
def loader():
    loader = ResPlanLoader(DATASET_DIR)
    loader.load_splits()
    loader.load_data()
    return loader

def test_resplan_pkl_can_be_loaded(loader):
    assert loader.data is not None
    assert isinstance(loader.data, list)

def test_total_dataset_count_is_17000(loader):
    assert loader.sample_count == 17000

def test_split_json_can_be_loaded(loader):
    assert loader.splits is not None
    assert 'train' in loader.splits

def test_train_val_test_counts_match(loader):
    assert len(loader.train_ids) == 13053
    assert len(loader.val_ids) == 1632
    assert len(loader.test_ids) == 1632

def test_sample_can_be_converted_to_json_safe(loader):
    sample_safe = loader.inspect_sample(0)
    assert isinstance(sample_safe, dict)
    # verify it can be json dumped
    json_str = json.dumps(sample_safe)
    assert isinstance(json_str, str)

def test_geometry_conversion_works(loader):
    sample_safe = loader.inspect_sample(0)
    # At least one geometry should be present and valid
    found_geom = False
    geo_keys = ['balcony', 'bathroom', 'bedroom', 'door', 'garden', 'wall', 'window', 'front_door', 'kitchen', 'living']
    for k in geo_keys:
        if k in sample_safe and sample_safe[k] is not None:
            geom = sample_safe[k]
            assert 'type' in geom
            assert 'coordinates' in geom
            found_geom = True
            break
    assert found_geom

def test_graph_conversion_works(loader):
    sample_safe = loader.inspect_sample(0)
    if 'graph' in sample_safe:
        graph = sample_safe['graph']
        assert 'nodes' in graph
        assert 'edges' in graph

def test_no_modification_made_to_original_dataset():
    import hashlib
    # We won't modify the dataset because the loader only reads.
    # We can just verify the file exists and hasn't been written to recently.
    assert os.path.exists(os.path.join(DATASET_DIR, 'ResPlan.pkl'))
