import os
import json
from backend.dataset.resplan_evaluation import evaluate_resplan_vs_generator

def test_evaluation_runs():
    dataset_dir = r"D:\2D AND 3D house Text-to-3D\datasets\resplan"
    report_out = r"D:\2D AND 3D house Text-to-3D\project\AI-Text-to-3D-House\docs\resplan_evaluation_report.json"
    
    # Run evaluation on just 2 samples to keep test fast
    report = evaluate_resplan_vs_generator(dataset_dir, report_out, sample_size=2)
    
    assert report is not None
    assert report["resplan_samples_evaluated"] <= 2
    assert report["generator_samples_evaluated"] == 5
    assert "metrics" in report
    
    assert os.path.exists(report_out)
    
    with open(report_out, 'r') as f:
        loaded = json.load(f)
        assert "limitations" in loaded
