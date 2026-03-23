import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Proposal:
    id: str
    title: str 
    description: str
    proposer: str
    timestamp: datetime
    votes: Dict[str, bool]
    status: str
    reputation_threshold: float

@dataclass 
class Agent:
    id: str
    reputation: float
    voting_history: List[str]

class SwarmGovernance:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.proposals: Dict[str, Proposal] = {}
        self.min_reputation = 0.1
        
    def register_agent(self, agent_id: str) -> None:
        """Register a new agent in the swarm with initial reputation"""
        if agent_id not in self.agents:
            self.agents[agent_id] = Agent(
                id=agent_id,
                reputation=self.min_reputation,
                voting_history=[]
            )
    
    def create_proposal(self, title: str, description: str, proposer: str,
                        reputation_threshold: float) -> Optional[str]:
        """Create a new governance proposal"""
        if proposer not in self.agents:
            return None
            
        proposal_id = hashlib.sha256(
            f"{title}{description}{proposer}{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        self.proposals[proposal_id] = Proposal(
            id=proposal_id,
            title=title,
            description=description, 
            proposer=proposer,
            timestamp=datetime.now(),
            votes={},
            status='active',
            reputation_threshold=reputation_threshold
        )
        
        return proposal_id
    
    def cast_vote(self, agent_id: str, proposal_id: str, vote: bool) -> bool:
        """Cast a vote on a proposal"""
        if agent_id not in self.agents or proposal_id not in self.proposals:
            return False
            
        proposal = self.proposals[proposal_id]
        agent = self.agents[agent_id]
        
        if proposal.status != 'active':
            return False
            
        if agent.reputation < proposal.reputation_threshold:
            return False
            
        proposal.votes[agent_id] = vote
        agent.voting_history.append(proposal_id)
        
        self._check_proposal_status(proposal_id)
        return True
        
    def _check_proposal_status(self, proposal_id: str) -> None:
        """Check if proposal has reached consensus"""
        proposal = self.proposals[proposal_id]
        
        if not proposal.votes:
            return
            
        total_reputation = sum(
            self.agents[voter].reputation 
            for voter in proposal.votes.keys()
        )
        
        approve_reputation = sum(
            self.agents[voter].reputation
            for voter, vote in proposal.votes.items()
            if vote is True
        )
        
        if approve_reputation > total_reputation * 0.66:
            proposal.status = 'approved'
            self._update_reputations(proposal_id)
        elif total_reputation - approve_reputation > total_reputation * 0.66:
            proposal.status = 'rejected'
            self._update_reputations(proposal_id)
            
    def _update_reputations(self, proposal_id: str) -> None:
        """Update agent reputations based on voting alignment with outcome"""
        proposal = self.proposals[proposal_id]
        outcome = proposal.status == 'approved'
        
        for agent_id, vote in proposal.votes.items():
            agent = self.agents[agent_id]
            if vote == outcome:
                agent.reputation *= 1.1  # Reward alignment
            else:
                agent.reputation *= 0.9  # Penalize misalignment
                
    def get_agent_reputation(self, agent_id: str) -> Optional[float]:
        """Get the current reputation score for an agent"""
        if agent_id in self.agents:
            return self.agents[agent_id].reputation
        return None

    def get_proposal_status(self, proposal_id: str) -> Optional[str]:
        """Get the current status of a proposal"""
        if proposal_id in self.proposals:
            return self.proposals[proposal_id].status
        return None