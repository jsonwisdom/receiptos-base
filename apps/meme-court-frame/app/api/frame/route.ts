import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  // MVP Frame handler for Meme Court
  return new Response(JSON.stringify({
    message: 'Meme Court Frame Active - PENDING_SIGNATURE',
    status: 'PENDING_SIGNATURE'
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  });
}

export async function GET() {
  return new Response('Meme Court Frame');
}