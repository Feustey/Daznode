import { supabase } from "@/utils/supabase";
import { sendOrderConfirmationEmail, sendOrderShippedEmail } from "./email";
import { generateId } from "@/utils/id";

export interface CreateOrderData {
  userId: string;
  customerName: string;
  customerEmail: string;
  productType: "dazenode" | "daz-ia";
  plan?: string;
  billingCycle?: string;
  items: {
    productId: string;
    quantity: number;
    price: number;
  }[];
  totalAmount: number;
  deliveryAddress: {
    name: string;
    street: string;
    city: string;
    country: string;
  };
  metadata?: {
    nodeType?: string;
    subscriptionId?: string;
    features?: string[];
  };
}

export interface Order {
  id: string;
  userId: string;
  customerName: string;
  customerEmail: string;
  productType: "dazenode" | "daz-ia";
  plan?: string;
  billingCycle?: string;
  items: {
    productId: string;
    quantity: number;
    price: number;
  }[];
  totalAmount: number;
  status: "pending" | "processing" | "shipped" | "delivered" | "cancelled";
  createdAt: string;
  updatedAt: string;
  deliveryAddress: {
    name: string;
    street: string;
    city: string;
    country: string;
  };
  trackingNumber?: string;
  trackingUrl?: string;
  metadata?: {
    nodeType?: string;
    subscriptionId?: string;
    features?: string[];
  };
}

export async function createOrder(data: CreateOrderData): Promise<Order> {
  try {
    const id = generateId();
    const now = new Date().toISOString();

    const order: Order = {
      id,
      ...data,
      status: "pending",
      createdAt: now,
      updatedAt: now,
    };

    const { data: insertedOrder, error } = await supabase
      .from("orders")
      .insert({
        user_id: data.userId,
        product_type: data.productType,
        plan: data.plan,
        billing_cycle: data.billingCycle,
        amount: data.totalAmount,
        payment_method: "lightning",
        payment_status: "pending",
        metadata: data.metadata,
        created_at: now,
        updated_at: now,
      })
      .select()
      .single();

    if (error) throw error;

    await sendOrderConfirmationEmail({
      id,
      customerName: data.customerName,
      deliveryAddress: {
        ...data.deliveryAddress,
        email: data.customerEmail,
      },
      deliveryOption: {
        name: "Standard",
        estimatedDays: "5-7 days",
        price: data.totalAmount,
      },
      total: data.totalAmount,
    });

    return insertedOrder;
  } catch (error) {
    console.error("Error creating order:", error);
    throw error;
  }
}

export async function updateOrderStatus(
  id: string,
  status: Order["status"],
  trackingNumber?: string,
  trackingUrl?: string
): Promise<Order> {
  try {
    const { data: order, error } = await supabase
      .from("orders")
      .update({
        status,
        updatedAt: new Date().toISOString(),
        trackingNumber,
        trackingUrl,
      })
      .eq("id", id)
      .select()
      .single();

    if (error) throw error;

    if (status === "shipped") {
      await sendOrderShippedEmail({
        id,
        customerName: order.customerName,
        email: order.customerEmail,
        trackingNumber: order.trackingNumber || "",
        trackingUrl: order.trackingUrl || "",
      });
    }

    return order;
  } catch (error) {
    console.error("Error updating order status:", error);
    throw error;
  }
}

export async function getOrder(id: string): Promise<Order | null> {
  try {
    const { data: order, error } = await supabase
      .from("orders")
      .select()
      .eq("id", id)
      .single();

    if (error) {
      if (error.code === "PGRST116") return null;
      throw error;
    }

    return order;
  } catch (error) {
    console.error("Error getting order:", error);
    throw error;
  }
}
