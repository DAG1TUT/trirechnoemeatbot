import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';

function checkAdmin(req: NextRequest) {
  const secret = req.headers.get('x-admin-secret');
  return secret === process.env.ADMIN_SECRET;
}

// GET /api/client/[apiKey] — get client by apiKey
export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ apiKey: string }> }
) {
  const { apiKey } = await params;
  const client = await prisma.client.findUnique({
    where: { apiKey },
    select: { businessName: true, businessType: true, systemPrompt: true, isActive: true },
  });
  if (!client) return Response.json({ error: 'Not found' }, { status: 404 });
  return Response.json(client);
}

// PATCH /api/client/[apiKey] — update client (admin only)
export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ apiKey: string }> }
) {
  if (!checkAdmin(req)) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const { apiKey } = await params;
  const data = await req.json();
  const allowed = ['businessName', 'businessType', 'systemPrompt', 'isActive'] as const;
  const update = Object.fromEntries(
    Object.entries(data).filter(([k]) => allowed.includes(k as typeof allowed[number]))
  );

  const client = await prisma.client.update({ where: { apiKey }, data: update });
  return Response.json(client);
}

// DELETE /api/client/[apiKey] — deactivate client (admin only)
export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ apiKey: string }> }
) {
  if (!checkAdmin(req)) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const { apiKey } = await params;
  await prisma.client.update({ where: { apiKey }, data: { isActive: false } });
  return Response.json({ ok: true });
}
