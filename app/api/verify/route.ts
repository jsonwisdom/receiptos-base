import { verifyL1 } from '../../../packages/receiptos-core/verifier.ts';

export async function POST(request: Request) {
  const body = await request.json();
  const result = await verifyL1({ payload: body });
  return Response.json(result);
}