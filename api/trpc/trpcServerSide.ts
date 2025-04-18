import { createTRPCProxyClient, httpBatchLink } from "@trpc/client";
import type { AppRouter } from "./router";

export const trpc = createTRPCProxyClient<AppRouter>({
  links: [
    httpBatchLink({
      url: "/api/trpc",
    }),
  ],
});
