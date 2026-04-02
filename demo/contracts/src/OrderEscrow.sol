// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract OrderEscrow {
    enum Status {
        Created,
        Funded,
        Delivered,
        Released,
        Refunded
    }

    address public immutable buyer;
    address public immutable seller;
    address public immutable arbiter;
    uint256 public immutable amount;
    Status public status;

    event Funded(address indexed buyer, uint256 amount);
    event Delivered(address indexed buyer);
    event ReleaseApproved(address indexed seller, uint256 amount);

    modifier onlyBuyer() {
        require(msg.sender == buyer, "buyer only");
        _;
    }

    modifier atStatus(Status expected) {
        require(status == expected, "invalid status");
        _;
    }

    constructor(address seller_, address arbiter_, uint256 amount_) {
        buyer = msg.sender;
        seller = seller_;
        arbiter = arbiter_;
        amount = amount_;
        status = Status.Created;
    }

    function fund() external payable onlyBuyer atStatus(Status.Created) {
        require(msg.value == amount, "incorrect amount");
        status = Status.Funded;
        emit Funded(msg.sender, msg.value);
    }

    function markDelivered() external onlyBuyer atStatus(Status.Funded) {
        status = Status.Delivered;
        emit Delivered(msg.sender);
    }

    function approveRelease() external onlyBuyer atStatus(Status.Delivered) {
        status = Status.Released;
        payable(seller).transfer(address(this).balance);
        emit ReleaseApproved(seller, amount);
    }
}

