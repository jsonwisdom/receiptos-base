// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title EXT060MockWitnessBadge
/// @notice Mock-only ERC-1155-style badge skeleton for witness completion receipts.
/// @dev This file is a non-deploy semantic skeleton. It grants no authority, no vote power, and no truth claim.
contract EXT060MockWitnessBadge {
    string public constant ISSUE = "EXT-060";
    string public constant CONTRACT_MODE = "mock_skeleton_only";
    string public constant MINT_REPRESENTS = "witness_action_completion";

    bool public constant DEPLOY_ALLOWED = false;
    bool public constant AUTHORITY = false;
    bool public constant TRUTH_CLAIM = false;
    bool public constant GOVERNANCE_ACTION_ALLOWED = false;
    bool public constant TRANSFER_GOVERNANCE_RIGHTS = false;
    bool public constant PROMOTION_ALLOWED = false;

    uint256 public constant BADGE_POWER = 0;
    uint256 public constant VOTE_POWER = 0;

    mapping(bytes32 => bool) public receiptMinted;
    mapping(address => mapping(bytes32 => bool)) public holderReceiptBadge;
    mapping(address => bytes32[]) private holderReceiptHashes;

    event CompletionBadgeMinted(address indexed to, bytes32 indexed receiptHash, string action);

    error MockOnlyNoDeployAuthority();
    error ReceiptHashRequired();
    error WitnessCompletionRequired();
    error DuplicateReceiptBadge();
    error TransferDisabled();
    error GovernanceDisabled();
    error TruthPromotionDisabled();

    constructor() {
        revert MockOnlyNoDeployAuthority();
    }

    function mintCompletionBadge(
        address to,
        bytes32 receiptHash,
        string calldata action,
        bool witnessCompletion
    ) external returns (bool) {
        if (receiptHash == bytes32(0)) revert ReceiptHashRequired();
        if (!witnessCompletion) revert WitnessCompletionRequired();
        if (receiptMinted[receiptHash]) revert DuplicateReceiptBadge();

        receiptMinted[receiptHash] = true;
        holderReceiptBadge[to][receiptHash] = true;
        holderReceiptHashes[to].push(receiptHash);

        emit CompletionBadgeMinted(to, receiptHash, action);
        return true;
    }

    function hasReceiptBadge(address holder, bytes32 receiptHash) external view returns (bool) {
        return holderReceiptBadge[holder][receiptHash];
    }

    function receiptHashOf(address holder, uint256 index) external view returns (bytes32) {
        return holderReceiptHashes[holder][index];
    }

    function badgeMetadata(bytes32 receiptHash) external pure returns (string memory) {
        if (receiptHash == bytes32(0)) revert ReceiptHashRequired();
        return "EXT-060 mock witness completion badge; authority=false; truth_claim=false; vote_power=0";
    }

    function safeTransferFrom(address, address, uint256, uint256, bytes calldata) external pure {
        revert TransferDisabled();
    }

    function safeBatchTransferFrom(address, address, uint256[] calldata, uint256[] calldata, bytes calldata) external pure {
        revert TransferDisabled();
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

    function executeGovernance() external pure {
        revert GovernanceDisabled();
    }
}
