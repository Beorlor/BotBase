const { ethers } = require("ethers");
const axios = require("axios");

const provider = new ethers.providers.JsonRpcProvider("https://eth-mainnet.alchemyapi.io/v2/ihpdGrQG_xK19f1Bz89nR3uc6jjHmW_d"); // Replace with your Alchemy API URL
const contractAddress = "0x6E9E8d9664b0a8aF3d8Ca4F7F9C14eD6443766d0"; // Replace with your contract address
const contractABI = [
    // Add your contract ABI here
];

const contract = new ethers.Contract(contractAddress, contractABI, provider);

async function main() {
    try {
        const presaleMaxAmount = await contract.presaleMaxAmount();
        console.log("Presale Max Amount:", presaleMaxAmount.toString());

        const weth = await contract.weth();
        console.log("WETH Address:", weth);

        const presaleMinAmount = await contract.presaleMinAmount();
        console.log("Presale Min Amount:", presaleMinAmount.toString());

        const nftPositionManager = await contract.nftPositionManager();
        console.log("NFT Position Manager:", nftPositionManager);

        const getPresalesLength = await contract.getPresalesLength();
        console.log("Total Presales Length:", getPresalesLength.toString());

        for (let i = 0; i < getPresalesLength; i++) {
            const presale = await contract.presales(i);
            console.log(`Presale ${i}:`, presale);
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

main();
