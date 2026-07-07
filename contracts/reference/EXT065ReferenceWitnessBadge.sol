// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title EXT065ReferenceWitnessBadge
/// @notice Reference ERC-1155 implementation conforming to EXT-064 production policy freeze.
/// @dev Witness-only completion badge. Non-transferable. No authority, no vote power, no truth claim.
contract EXT065ReferenceWitnessBadge is ERC1155, Ownable {
    string public constant ISSUE = "EXT-065";
    string public constant POLICY_SOURCE = "EXT-064";
    string public constant RUNTIME_MODE = "witness_only";
    string public constant RESOLUTION_SEMANTICS = "absent";
    string public constant MINT_REPRESENTS = "witness_action_completion";

    bool public constant AUTHORITY = false;
    bool public constant TRUTH_CLAIM = false;
    bool public constant GOVERNANCE_ACTION_ALLOWED = false;
    bool public constant PROMOTION_ALLOWED = false;
    bool public constant TRANSFER_GOVERNANCE_RIGHTS = false;
    bool public constant RECEIPT_HASH_REQUIRED = true;
    bool public constant ONE_BADGE_PER_RECEIPT = true;
    bool public constant NON_TRANSFERABLE = true;

    uint256 public constant BADGE_POWER = 0;
    uint256 public constant VOTE_POWER = 0;
    uint256 public constant BADGE_TOKEN_ID = 1;

    mapping(bytes32 => bool) public mintedReceipts;
    mapping(address => mapping(bytes32 => bool)) public holderReceiptBadge;

    event WitnessBadgeMinted(address indexed holder, bytes32 indexed receiptHash, uint256 indexed tokenId);

    error ReceiptHashRequired();
    error WitnessCompletionRequired();
    error DuplicateReceipt();
    error NonTransferable();
    error GovernanceDisabled();
    error TruthPromotionDisabled();

    constructor() ERC1155("") Ownable(msg.sender) {}

    function mintBadge(bytes32 receiptHash, bool witnessCompletion) external {
        if (receiptHash == bytes32(0)) revert ReceiptHashRequired();
        if (!witnessCompletion) revert WitnessCompletionRequired();
        if (mintedReceipts[receiptHash]) revert DuplicateReceipt();

        mintedReceipts[receiptHash] = true;
        holderReceiptBadge[msg.sender][receiptHash] = true;
        _mint(msg.sender, BADGE_TOKEN_ID, 1, "");

        emit WitnessBadgeMinted(msg.sender, receiptHash, BADGE_TOKEN_ID);
    }

    function hasReceiptBadge(address holder, bytes32 receiptHash) external view returns (bool) {
        return holderReceiptBadge[holder][receiptHash];
    }

    function safeTransferFrom(address, address, uint256, uint256, bytes memory) public pure override {
        revert NonTransferable();
    }

    function safeBatchTransferFrom(address, address, uint256[] memory, uint256[] memory, bytes memory) public pure override {
        revert NonTransferable();
    }

    function vote() external pure {
        revert GovernanceDisabled();
    }

    function resolve() external pure {
        revert GovernanceDisabled();
    }

    function grantAuthority() external pure {
        revert GovernanceDisabled();
    }

    function promoteTruth() external pure {
        revert TruthPromotionDisabled();
    }
}
