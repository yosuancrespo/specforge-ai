// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "forge-std/Test.sol";
import "../src/OrderEscrow.sol";

contract OrderEscrowTest is Test {
    address internal buyer = address(0xB0B);
    address internal seller = address(0xA11CE);
    address internal arbiter = address(0xCAFE);
    OrderEscrow internal escrow;

    function setUp() public {
        vm.deal(buyer, 10 ether);
        vm.prank(buyer);
        escrow = new OrderEscrow(seller, arbiter, 1 ether);
    }

    function testBuyerCanFundDeliverAndRelease() public {
        vm.prank(buyer);
        escrow.fund{value: 1 ether}();

        vm.prank(buyer);
        escrow.markDelivered();

        vm.prank(buyer);
        escrow.approveRelease();

        assertEq(uint256(escrow.status()), uint256(OrderEscrow.Status.Released));
        assertEq(seller.balance, 1 ether);
    }

    function testNonBuyerCannotMarkDelivered() public {
        vm.prank(buyer);
        escrow.fund{value: 1 ether}();

        vm.expectRevert("buyer only");
        vm.prank(seller);
        escrow.markDelivered();
    }
}

