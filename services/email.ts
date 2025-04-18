import { Resend } from "resend";
import OrderConfirmationEmail from "../components/emails/OrderConfirmationEmail";
import OrderShippedEmail from "../components/emails/OrderShippedEmail";

interface OrderConfirmationEmailData {
  id: string;
  customerName: string;
  deliveryAddress: {
    name: string;
    street: string;
    city: string;
    country: string;
    email: string;
  };
  deliveryOption: {
    name: string;
    estimatedDays: string;
    price: number;
  };
  total: number;
}

export async function sendOrderConfirmationEmail(
  data: OrderConfirmationEmailData
) {
  const resend = new Resend(process.env.RESEND_API_KEY);

  const { id, customerName, deliveryAddress, deliveryOption, total } = data;

  await resend.emails.send({
    from: "DazNode <no-reply@daznode.com>",
    to: [deliveryAddress.email],
    subject: `Confirmation de commande #${id}`,
    react: OrderConfirmationEmail({
      id,
      customerName,
      deliveryAddress,
      deliveryOption,
      total,
    }),
  });
}

interface OrderShippedEmailData {
  id: string;
  customerName: string;
  email: string;
  trackingNumber: string;
  trackingUrl: string;
}

export async function sendOrderShippedEmail(data: OrderShippedEmailData) {
  const resend = new Resend(process.env.RESEND_API_KEY);

  const { id, customerName, email, trackingNumber, trackingUrl } = data;

  await resend.emails.send({
    from: "DazNode <no-reply@daznode.com>",
    to: [email],
    subject: `Votre commande #${id} a été expédiée`,
    react: OrderShippedEmail({
      id,
      customerName,
      trackingNumber,
      trackingUrl,
    }),
  });
}
