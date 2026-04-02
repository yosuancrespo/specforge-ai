const fs = require("fs");
const path = require("path");

const source = path.resolve(__dirname, "../../src/OrderEscrow.sol");
const targetDir = path.resolve(__dirname, "../contracts");
const target = path.join(targetDir, "OrderEscrow.sol");

fs.mkdirSync(targetDir, { recursive: true });
fs.copyFileSync(source, target);
console.log(`Synced Solidity source to ${target}`);