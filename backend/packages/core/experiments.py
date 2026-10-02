import hashlib

class ExperimentAssignment:
    def __init__(self, salt: str = "swarn_experiment"):
        self.salt = salt

    def assign_user(self, user_id: str, experiment_id: str, split: int = 50) -> str:
        """
        Deterministically assign a user to a control or variant bucket.
        split: percentage of users that go to the variant (0-100)
        """
        key = f"{self.salt}:{experiment_id}:{user_id}".encode("utf-8")
        hash_val = int(hashlib.sha256(key).hexdigest()[:8], 16)
        
        # Determine bucket based on hash
        if (hash_val % 100) < split:
            return "variant"
        return "control"
