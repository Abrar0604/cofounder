import hashlib
import json
from typing import Dict, List, Optional
from pydantic import BaseModel

class ExperimentVariant(BaseModel):
    id: str
    name: str
    weight: float

class Experiment(BaseModel):
    id: str
    name: str
    variants: List[ExperimentVariant]

class ExperimentService:
    def __init__(self):
        # In a real scenario, this would come from a DB or LaunchDarkly
        self.experiments: Dict[str, Experiment] = {
            "ui_redesign_q4": Experiment(
                id="exp_01",
                name="UI Redesign Q4",
                variants=[
                    ExperimentVariant(id="control", name="Control", weight=0.5),
                    ExperimentVariant(id="variant_a", name="Variant A (New Sidebar)", weight=0.5)
                ]
            ),
            "swarn_decision_model": Experiment(
                id="exp_02",
                name="Swarn Decision Engine",
                variants=[
                    ExperimentVariant(id="jev_flash", name="Gemini 2.5 Flash", weight=0.8),
                    ExperimentVariant(id="jev_pro", name="Gemini 2.5 Pro", weight=0.2)
                ]
            )
        }
        
    def get_assignment(self, experiment_id: str, user_id: str) -> Optional[str]:
        if experiment_id not in self.experiments:
            return None
            
        experiment = self.experiments[experiment_id]
        
        # Deterministic assignment based on user_id and experiment_id hash
        hash_input = f"{user_id}_{experiment_id}".encode("utf-8")
        hash_val = int(hashlib.md5(hash_input).hexdigest(), 16)
        normalized = hash_val / (2**128 - 1)  # 0.0 to 1.0
        
        cumulative_weight = 0.0
        for variant in experiment.variants:
            cumulative_weight += variant.weight
            if normalized <= cumulative_weight:
                return variant.id
                
        # Fallback
        return experiment.variants[0].id

    def get_all_assignments_for_user(self, user_id: str) -> Dict[str, str]:
        return {
            exp_id: self.get_assignment(exp_id, user_id)
            for exp_id in self.experiments.keys()
        }
