const axios = require('axios');

const apiKey = 'ihpdGrQG_xK19f1Bz89nR3uc6jjHmW_d'; // Replace with your Alchemy API key
const url = `https://base-mainnet.g.alchemy.com/v2/${apiKey}`;

// Proxy contract address (BaseJump contract address)
const proxyContractAddress = '0x31C0282Fa6D0A82aD22ab63BbaCd87F62B2a9bfD';

// Storage slot for the implementation address (EIP-1967)
const storageSlot = '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc';

// JSON-RPC payload to fetch storage at specific slot
const payload = {
  jsonrpc: '2.0',
  id: 1,
  method: 'eth_getStorageAt',
  params: [proxyContractAddress, storageSlot, 'latest']
};

axios.post(url, payload)
  .then(response => {
    const implementationAddress = response.data.result;
    const formattedAddress = '0x' + implementationAddress.slice(-40); // Extract and format address
    console.log(`Implementation Contract Address: ${formattedAddress}`);
  })
  .catch(error => {
    console.error(error);
  });
