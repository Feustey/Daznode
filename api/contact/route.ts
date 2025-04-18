import { NextResponse } from "next/server";
import { Resend } from "resend";
import { ContactEmailTemplate } from "../../components/emails/ContactEmailTemplate";

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request: Request) {
  try {
    const {
      firstName,
      lastName,
      email,
      companyName,
      jobTitle,
      companyPhone,
      companyWebsite,
      interest,
      message,
    } = await request.json();

    const emailContent = `
      Nouveau message de contact:
      
      Nom: ${firstName} ${lastName}
      Email: ${email}
      Entreprise: ${companyName || "Non renseigné"}
      Fonction: ${jobTitle || "Non renseigné"}
      Téléphone: ${companyPhone || "Non renseigné"}
      Site web: ${companyWebsite || "Non renseigné"}
      Sujet: ${interest}
      
      Message:
      ${message}
    `;

    await resend.emails.send({
      from: "DazNode <onboarding@resend.dev>",
      to: "contact@dazno.de",
      subject: `Nouveau message de contact - ${interest}`,
      text: emailContent,
      replyTo: email,
    });

    // Envoyer l'email de contact à l'admin
    await resend.emails.send({
      from: "DazNode <onboarding@resend.dev>",
      to: "contact@dazno.de",
      subject: `[Contact DazNode] ${interest} - ${firstName} ${lastName}`,
      react: ContactEmailTemplate({
        type: "admin",
        firstName,
        lastName,
        email,
        interest,
        message,
      }),
    });

    // Envoyer un email de confirmation à l'utilisateur
    await resend.emails.send({
      from: "DazNode <onboarding@resend.dev>",
      to: email,
      subject: "Confirmation de votre message - DazNode",
      react: ContactEmailTemplate({
        type: "user",
        firstName,
        lastName,
        email,
        interest,
      }),
    });

    return NextResponse.json(
      { message: "Message envoyé avec succès" },
      { status: 200 }
    );
  } catch (error) {
    console.error("Erreur lors de l'envoi de l'email:", error);
    return NextResponse.json(
      { error: "Erreur lors de l'envoi du message" },
      { status: 500 }
    );
  }
}
