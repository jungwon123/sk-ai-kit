import { summary } from "@/lib/data";

export const dynamic = "force-dynamic";

export function GET() {
  return Response.json({ ok: true, files: summary() });
}
