import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';

function checkAdmin(req: NextRequest) {
  return req.headers.get('x-admin-secret') === process.env.ADMIN_SECRET;
}

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ apiKey: string }> }
) {
  const { apiKey } = await params;
  const client = await prisma.client.findUnique({
    where: { apiKey },
    select: { businessName: true, businessType: true, systemPrompt: true,
              isActive: true, vkGroupId: true },
  });
  if (!client) return Response.json({ error: 'Not found' }, { status: 404 });
  return Response.json(client);
}

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ apiKey: string }> }
) {
  if (!checkAdmin(req)) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const { apiKey } = await params;
  const data = await req.json();
  const allowed = [
    'businessName', 'businessType', 'systemPrompt', 'isActive',
    'vkGroupId', 'vkAccessToken', 'vkConfirmCode', 'vkSecretKey',
  ] as const;
  const update = Object.fromEntries(
    Object.entries(data).filter(([k]) => allowed.includes(k as typeof allowed[number]))
  );

  const client = await prisma.client.update({ where: { apiKey }, data: update });
  return Response.json(client);
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ apiKey: string }> }
) {
  if (!checkAdmin(req)) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  const { apiKey } = await params;
  await prisma.client.update({ where: { apiKey }, data: { isActive: false } });
  return Response.json({ ok: true });
}
