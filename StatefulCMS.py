from fastapi import FastAPI, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database setup
# DATABASE_URL = "postgresql://postgres:postgres@localhost/claims_management"
DATABASE_URL="postgresql://claims_management_v687_user:EISKLXFO56eMDftFcT9DDZ2XfgKfYXLR@dpg-culf33lsvqrc73ccr0o0-a/claims_management_v687"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class PolicyholderDB(Base):
    __tablename__ = "policyholders"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)

class PolicyDB(Base):
    __tablename__ = "policies"
    id = Column(Integer, primary_key=True, index=True)
    policyholder_id = Column(Integer, ForeignKey("policyholders.id"))
    type = Column(String)
    coverage_amount = Column(Float)

class ClaimDB(Base):
    __tablename__ = "claims"
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"))
    amount_claimed = Column(Float)
    status = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Entity Models
class Policyholder(BaseModel):
    id: int
    name: str
    age: int

class Policy(BaseModel):
    id: int
    policyholder_id: int
    type: str
    coverage_amount: float

class Claim(BaseModel):
    id: int
    policy_id: int
    amount_claimed: float
    status: str

# CRUD Operations
@app.post("/policyholder/")
def create_policyholder(holder: Policyholder, db: Session = Depends(get_db)):
    db_holder = PolicyholderDB(**holder.dict())
    db.add(db_holder)
    db.commit()
    db.refresh(db_holder)
    return db_holder

@app.get("/policyholders/")
def get_policyholders(db: Session = Depends(get_db)):
    return db.query(PolicyholderDB).all()

@app.put("/policyholder/{holder_id}")
def update_policyholder(holder_id: int, holder: Policyholder, db: Session = Depends(get_db)):
    db_holder = db.query(PolicyholderDB).filter(PolicyholderDB.id == holder_id).first()
    if not db_holder:
        raise HTTPException(status_code=404, detail="Policyholder not found")
    for key, value in holder.dict().items():
        setattr(db_holder, key, value)
    db.commit()
    return db_holder

@app.delete("/policyholder/{holder_id}")
def delete_policyholder(holder_id: int, db: Session = Depends(get_db)):
    db_holder = db.query(PolicyholderDB).filter(PolicyholderDB.id == holder_id).first()
    if not db_holder:
        raise HTTPException(status_code=404, detail="Policyholder not found")
    db.delete(db_holder)
    db.commit()
    return {"message": "Policyholder deleted"}

@app.post("/policy/")
def create_policy(policy: Policy, db: Session = Depends(get_db)):
    db_policy = PolicyDB(**policy.dict())
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy

@app.get("/policies/")
def get_policies(db: Session = Depends(get_db)):
    return db.query(PolicyDB).all()

@app.put("/policy/{policy_id}")
def update_policy(policy_id: int, policy: Policy, db: Session = Depends(get_db)):
    db_policy = db.query(PolicyDB).filter(PolicyDB.id == policy_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    for key, value in policy.dict().items():
        setattr(db_policy, key, value)
    db.commit()
    return db_policy

@app.delete("/policy/{policy_id}")
def delete_policy(policy_id: int, db: Session = Depends(get_db)):
    db_policy = db.query(PolicyDB).filter(PolicyDB.id == policy_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    db.delete(db_policy)
    db.commit()
    return {"message": "Policy deleted"}

@app.post("/claim/")
def create_claim(claim: Claim, db: Session = Depends(get_db)):
    policy = db.query(PolicyDB).filter(PolicyDB.id == claim.policy_id).first()
    if not policy:
        raise HTTPException(status_code=400, detail="Policy does not exist")
    if claim.amount_claimed > policy.coverage_amount:
        raise HTTPException(status_code=400, detail="Claim amount exceeds policy coverage")
    db_claim = ClaimDB(**claim.dict())
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    return db_claim

@app.get("/claims/")
def get_claims(db: Session = Depends(get_db)):
    return db.query(ClaimDB).all()

@app.put("/claim/{claim_id}")
def update_claim(claim_id: int, claim: Claim, db: Session = Depends(get_db)):
    db_claim = db.query(ClaimDB).filter(ClaimDB.id == claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    for key, value in claim.dict().items():
        setattr(db_claim, key, value)
    db.commit()
    return db_claim

@app.delete("/claim/{claim_id}")
def delete_claim(claim_id: int, db: Session = Depends(get_db)):
    db_claim = db.query(ClaimDB).filter(ClaimDB.id == claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    db.delete(db_claim)
    db.commit()
    return {"message": "Claim deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)