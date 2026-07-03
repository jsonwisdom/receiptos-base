const pngBase64 =
  "iVBORw0KGgoAAAANSUhEUgAAASwAAACWAQMAAAAU1PscAAAABlBMVEURGCb///9yqW5EAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAKUlEQVRIie3BMQEAAADCoPVPbQ0PoAAAAAAAAAAAAAAAAAAAAAB8GRvWAAGqUD+tAAAAAElFTkSuQmCC";

export async function GET() {
  const bytes = Uint8Array.from(Buffer.from(pngBase64, "base64"));

  return new Response(bytes, {
    headers: {
      "Content-Type": "image/png",
      "Cache-Control": "public, max-age=31536000, immutable",
    },
  });
}
