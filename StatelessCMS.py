from fastapi import FastAPI, HTTPException
from typing import List, Dict
from pydantic import BaseModel

app = FastAPI()

# In-memory storage
db_policyholders: Dict[int, dict] = {}
db_policies: Dict[int, dict] = {}
db_claims: Dict[int, dict] = {}

# Entity Models
class Policyholder(BaseModel):
    id: int
    name: str
    age: int

class Policy(BaseModel):
    id: int
    policyholder_id: int
    type: str  # e.g., Health, Auto, Life
    coverage_amount: float

class Claim(BaseModel):
    id: int
    policy_id: int
    amount_claimed: float
    status: str  # e.g., Pending, Approved, Rejected

# CRUD Operations
@app.post("/policyholder/")
def create_policyholder(holder: Policyholder):
    if holder.id in db_policyholders:
        raise HTTPException(status_code=400, detail="Policyholder already exists")
    db_policyholders[holder.id] = holder.dict()
    return holder

@app.get("/policyholders/")
def get_policyholders():
    return list(db_policyholders.values())

@app.put("/policyholder/{holder_id}")
def update_policyholder(holder_id: int, holder: Policyholder):
    if holder_id not in db_policyholders:
        raise HTTPException(status_code=404, detail="Policyholder not found")
    db_policyholders[holder_id] = holder.dict()
    return holder

@app.delete("/policyholder/{holder_id}")
def delete_policyholder(holder_id: int):
    if holder_id not in db_policyholders:
        raise HTTPException(status_code=404, detail="Policyholder not found")
    del db_policyholders[holder_id]
    return {"message": "Policyholder deleted successfully"}

@app.post("/policy/")
def create_policy(policy: Policy):
    if policy.id in db_policies:
        raise HTTPException(status_code=400, detail="Policy already exists")
    if policy.policyholder_id not in db_policyholders:
        raise HTTPException(status_code=400, detail="Policyholder does not exist")
    db_policies[policy.id] = policy.dict()
    return policy

@app.get("/policies/")
def get_policies():
    return list(db_policies.values())

@app.put("/policy/{policy_id}")
def update_policy(policy_id: int, policy: Policy):
    if policy_id not in db_policies:
        raise HTTPException(status_code=404, detail="Policy not found")
    db_policies[policy_id] = policy.dict()
    return policy

@app.delete("/policy/{policy_id}")
def delete_policy(policy_id: int):
    if policy_id not in db_policies:
        raise HTTPException(status_code=404, detail="Policy not found")
    del db_policies[policy_id]
    return {"message": "Policy deleted successfully"}

@app.post("/claim/")
def create_claim(claim: Claim):
    if claim.id in db_claims:
        raise HTTPException(status_code=400, detail="Claim already exists")
    if claim.policy_id not in db_policies:
        raise HTTPException(status_code=400, detail="Policy does not exist")
    if claim.amount_claimed > db_policies[claim.policy_id]["coverage_amount"]:
        raise HTTPException(status_code=400, detail="Claim amount exceeds policy coverage")
    db_claims[claim.id] = claim.dict()
    return claim

@app.get("/claims/")
def get_claims():
    return list(db_claims.values())

@app.put("/claim/{claim_id}")
def update_claim(claim_id: int, claim: Claim):
    if claim_id not in db_claims:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim.policy_id not in db_policies:
        raise HTTPException(status_code=400, detail="Policy does not exist")
    if claim.amount_claimed > db_policies[claim.policy_id]["coverage_amount"]:
        raise HTTPException(status_code=400, detail="Claim amount exceeds policy coverage")
    db_claims[claim_id] = claim.dict()
    return claim

@app.delete("/claim/{claim_id}")
def delete_claim(claim_id: int):
    if claim_id not in db_claims:
        raise HTTPException(status_code=404, detail="Claim not found")
    del db_claims[claim_id]
    return {"message": "Claim deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
