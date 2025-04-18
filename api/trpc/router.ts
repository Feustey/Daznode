import { initTRPC } from "@trpc/server";
import { Context } from "./context";
import { chatRouter } from "../../services/chatService";

const t = initTRPC.context<Context>().create();

export const router = t.router;
export const publicProcedure = t.procedure;

export const appRouter = router({
  chat: chatRouter,
});

export type AppRouter = typeof appRouter;
