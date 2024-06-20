const Web3 = require('web3');

// Connect to the Base network using Alchemy
const web3 = new Web3('https://base-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_BASE_API_KEY');

// Proxy contract address (BaseJump contract address)
const proxyContractAddress = '0x31C0282Fa6D0A82aD22ab63BbaCd87F62B2a9bfD';

// Function to get the implementation address from the proxy contract
async function getImplementationAddress(proxyAddress) {
  // EIP-1967 storage slot for the implementation address
  const storageSlot = web3.utils.keccak256('eip1967.proxy.implementation').substring(0, 66);

  // Fetch the implementation address from the storage slot
  const implementationAddress = await web3.eth.getStorageAt(proxyAddress, storageSlot);
  return web3.utils.toChecksumAddress('0x' + implementationAddress.substring(26));
}

// Example usage
(async () => {
  try {
    const implementationAddress = await getImplementationAddress(proxyContractAddress);
    console.log(`Implementation Contract Address: ${implementationAddress}`);
  } catch (error) {
    console.error('Error fetching implementation address:', error);
  }
})();
