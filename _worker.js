const DOCS_URL = "refineai.mintlify.dev";
const CUSTOM_URL = "refinehq.ai";

export default {
  async fetch(request, env) {
    try {
      const incomingUrl = new URL(request.url);

      if (incomingUrl.pathname.startsWith("/docs")) {
        const proxyUrl = new URL(request.url);
        proxyUrl.hostname = DOCS_URL;
        proxyUrl.protocol = "https:";

        const headers = new Headers(request.headers);
        headers.set("Host", DOCS_URL);
        headers.set("X-Forwarded-Host", CUSTOM_URL);
        headers.set("X-Forwarded-Proto", "https");

        const proxyInit = {
          method: request.method,
          headers,
          redirect: "manual",
        };

        if (request.method !== "GET" && request.method !== "HEAD") {
          proxyInit.body = request.body;
        }

        return await fetch(new Request(proxyUrl.toString(), proxyInit));
      }
    } catch {
      // Fall through to the regular Pages asset pipeline.
    }

    return env.ASSETS.fetch(request);
  },
};
