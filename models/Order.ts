import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.SUPABASE_URL || "",
  process.env.SUPABASE_ANON_KEY || ""
);

interface Order {
  id: string;
  status: "pending" | "paid" | "cancelled";
  amount: number;
  currency: string;
  paymentHash?: string;
  paidAt?: Date;
  createdAt: Date;
  updatedAt: Date;
  paymentDetails?: {
    amount: number;
    currency: string;
    paymentHash: string;
    settledAt: string;
  };
}

const Order = {
  async findOneAndUpdate(query: { paymentHash: string }, update: any) {
    const { data, error } = await supabase
      .from("orders")
      .update(update.$set)
      .match(query)
      .single();

    if (error) throw error;
    return data;
  },
};

export default Order;
