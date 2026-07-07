export const runtime = "nodejs";
export const dynamic = "force-static";

const pngBase64 =
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=";

export async function GET() {
  const image = Buffer.from(pngBase64, "base64");

  return new Response(image, {
    status: 200,
    headers: {
      "Content-Type": "image/png",
      "Content-Length": String(image.length),
      "Cache-Control": "public, max-age=31536000, immutable",
    },
  });
}
