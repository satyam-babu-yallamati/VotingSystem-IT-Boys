// SPDX-License-Identifier: MIT 
pragma solidity ^0.8.19;

contract Voting {
    struct Candidate {
        uint id;
        string name;
        string party; 
        uint voteCount;
    }

    mapping (uint => Candidate) public candidates;
    mapping (address => bool) public voters;

    uint public countCandidates;
    uint256 public votingEnd;
    uint256 public votingStart;

    function addCandidate(string memory name, string memory party) public returns(uint) {
        countCandidates++;
        candidates[countCandidates] = Candidate(countCandidates, name, party, 0);
        return countCandidates;
    }
   
    function vote(uint candidateId) public {
        require(!voters[msg.sender], "You have already voted."); // Corrected variable name
        require(candidateId > 0 && candidateId <= countCandidates, "Invalid candidate ID."); // Corrected variable name
        require(block.timestamp >= votingStart && block.timestamp <= votingEnd, "Voting is not active.");
        
        voters[msg.sender] = true; // Corrected variable name
        candidates[candidateId].voteCount += 1;
    }
      
    function checkVote() public view returns(bool){
        return voters[msg.sender];
    }
       
    function getCountCandidates() public view returns(uint) {
        return countCandidates;
    }

    function getCandidate(uint candidateID) public view returns (uint, string memory, string memory, uint) {
        return (candidateID, candidates[candidateID].name, candidates[candidateID].party, candidates[candidateID].voteCount);
    }

    function setDates(uint256 _startDate, uint256 _endDate) public {
        require(votingEnd == 0 && votingStart == 0, "Voting dates have already been set."); // Prevent resetting
        require(_startDate + 1000000 > block.timestamp, "Start date must be in the future.");
        require(_endDate > _startDate, "End date must be after start date.");
        
        votingStart = _startDate;
        votingEnd = _endDate;
    }

    function getDates() public view returns (uint256, uint256) {
        return (votingStart, votingEnd);
    }
}
