import { createPublicClient, http, isAddress } from "viem";
import { base } from "viem/chains";

const JAYWISDOM_TOKEN = "0x694cE46C64D9D1a5e9376A9feBcF85Ec05D72e9F" as const;

const erc20BalanceOfAbi = [
  {
    type: "function",
    name: "balanceOf",
    stateMutability: "view",
    inputs: [{ name: "account", type: "address" }],
    outputs: [{ name: "balance", type: "uint256" }],
  },
] as const;

const client = createPublicClient({
  chain: base,
  transport: http(process.env.BASE_RPC_URL || "https://mainnet.base.org"),
});

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const wallet = searchParams.get("address");

  if (!wallet || !isAddress(wallet)) {
    return Response.json(
      {
        error: "INVALID_ADDRESS",
        expected: "/api/jaywisdom-utility?address=0x...",
        authority_created: false,
      },
      { status: 400 },
    );
  }

  try {
    const balance = await client.readContract({
      address: JAYWISDOM_TOKEN,
      abi: erc20BalanceOfAbi,
      functionName: "balanceOf",
      args: [wallet],
    });

    return Response.json({
      utility_version: "0.1",
      network: "Base",
      chain_id: 8453,
      token_contract: JAYWISDOM_TOKEN,
      wallet,
      balance_atomic: balance.toString(),
      eligible_to_submit_replay: balance > 0n,
      token_transfer_required: false,
      public_verification_permissionless: true,
      scoring_weight: 0,
      semantic_validation_weight: 0,
      authority_weight: 0,
      authority_created: false,
    });
  } catch {
    return Response.json(
      {
        error: "CHAIN_READ_FAILED",
        eligible_to_submit_replay: false,
        authority_created: false,
      },
      { status: 503 },
    );
  }
}
