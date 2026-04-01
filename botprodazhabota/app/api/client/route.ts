import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';

function checkAdmin(req: NextRequest) {
  const secret = req.headers.get('x-admin-secret');
  return secret === process.env.ADMIN_SECRET;
}

// GET /api/client — list all clients (admin only)
export async function GET(req: NextRequest) {
  if (!checkAdmin(req)) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const clients = await prisma.client.findMany({
    orderBy: { createdAt: 'desc' },
    select: { id: true, apiKey: true, businessName: true, businessType: true,
               systemPrompt: true, isActive: true, createdAt: true },
  });
  return Response.json(clients);
}

// POST /api/client — create new client (admin only)
export async function POST(req: NextRequest) {
  if (!checkAdmin(req)) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const { businessName, businessType, systemPrompt } = await req.json();
  if (!businessName || !systemPrompt) {
    return Response.json({ error: 'businessName and systemPrompt are required' }, { status: 400 });
  }

  const client = await prisma.client.create({
    data: { businessName, businessType, systemPrompt },
  });
  return Response.json(client, { status: 201 });
}
