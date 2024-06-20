const Web3 = require('web3');
const fs = require('fs');

// Connect to the Base network using Alchemy
const web3 = new Web3('https://base-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_BASE_API_KEY');

// Replace with the actual address fetched previously
const implementationContractAddress = '0xYourImplementationAddressHere';

// Function to fetch and save contract details
async function fetchAndSaveContractDetails(contractAddress) {
  try {
    // Fetch contract ABI and bytecode
    const contractABI = await web3.eth.getCode(contractAddress);
    const contractBytecode = await web3.eth.getCode(contractAddress);

    // Save contract details to a file
    const contractDetails = {
      address: contractAddress,
      abi: contractABI,
      bytecode: contractBytecode,
    };

    fs.writeFileSync('ImplementationContract.json', JSON.stringify(contractDetails, null, 2));
    console.log('Contract details saved to ImplementationContract.json');
  } catch (error) {
    console.error('Error fetching contract details:', error);
  }
}

// Fetch and save contract details
fetchAndSaveContractDetails(implementationContractAddress);
