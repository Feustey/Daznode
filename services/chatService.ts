import { router, publicProcedure } from "../lib/trpc/trpc";
import { z } from "zod";

export const chatRouter = router({
  sendMessage: publicProcedure
    .input(
      z.object({
        message: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      // Implémentation du chat à venir
      return {
        success: true,
        message: `Message reçu: ${input.message}`,
      };
    }),
});

export async function processChatMessage(_input: string) {
  // ... existing code ...
}
