import { inferAsyncReturnType } from "@trpc/server";
import { CreateNextContextOptions } from "@trpc/server/adapters/next";
import { auth } from "@/lib/auth";
import { Session } from "next-auth";
import { initTRPC, TRPCError } from "@trpc/server";

export async function createContext(opts: CreateNextContextOptions) {
  const session = await auth();
  return {
    session,
  };
}

export type Context = inferAsyncReturnType<typeof createContext>;

const t = initTRPC.context<Context>().create();

export const router = t.router;
export const publicProcedure = t.procedure;
export const protectedProcedure = t.procedure.use(
  t.middleware(({ ctx, next }) => {
    if (!ctx.session?.user) {
      throw new TRPCError({ code: "UNAUTHORIZED" });
    }
    return next({
      ctx: {
        ...ctx,
        session: ctx.session,
      },
    });
  })
);
