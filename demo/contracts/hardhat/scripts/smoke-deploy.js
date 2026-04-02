const hre = require("hardhat");

async function main() {
  const [buyer, seller, arbiter] = await hre.ethers.getSigners();
  const Factory = await hre.ethers.getContractFactory("OrderEscrow", buyer);
  const contract = await Factory.deploy(seller.address, arbiter.address, hre.ethers.parseEther("1"));
  await contract.waitForDeployment();
  console.log(
    JSON.stringify(
      {
        contract: "OrderEscrow",
        address: await contract.getAddress(),
        buyer: buyer.address,
        seller: seller.address,
        arbiter: arbiter.address
      },
      null,
      2
    )
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

