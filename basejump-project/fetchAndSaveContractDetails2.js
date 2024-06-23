const axios = require('axios');
const fs = require('fs');

const apiKey = 'ihpdGrQG_xK19f1Bz89nR3uc6jjHmW_d'; // Replace with your Alchemy API key
const url = `https://base-mainnet.g.alchemy.com/v2/${apiKey}`;

// Replace with the actual address fetched previously
const implementationContractAddress = '0x6e9e8d9664b0a8af3d8ca4f7f9c14ed6443766d0';

// Function to fetch and save contract details
async function fetchAndSaveContractDetails(contractAddress) {
  try {
    // JSON-RPC payload to fetch contract bytecode
    const payload = {
      jsonrpc: '2.0',
      id: 1,
      method: 'eth_getCode',
      params: [contractAddress, 'latest']
    };

    // Make the request to fetch bytecode
    const response = await axios.post(url, payload);
    const contractBytecode = response.data.result;

    // Save contract details to a file
    const contractDetails = {
      address: contractAddress,
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
