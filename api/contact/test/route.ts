import { NextResponse } from "next/server";
import { Resend } from "resend";
import { ContactEmailTemplate } from "../../../components/emails/ContactEmailTemplate";

const resend = new Resend(process.env.RESEND_API_KEY);

// Adresses email de test
const TEST_SENDER = "onboarding@resend.dev";
const TEST_ADMIN = "feustey@pm.me";
const TEST_USER = "feustey@pm.me";

export async function GET() {
  try {
    console.log("Démarrage du test d'envoi d'emails...");
    console.log(
      "Clé Resend:",
      process.env.RESEND_API_KEY ? "Présente" : "Manquante"
    );

    const testData = {
      firstName: "Test",
      lastName: "Utilisateur",
      email: TEST_USER,
      companyName: "DazNode Test",
      jobTitle: "Testeur",
      companyPhone: "+33 123456789",
      companyWebsite: "https://dazno.de",
      interest: "Test Email",
      message: "Ceci est un test du système d'envoi d'email.",
    };

    console.log("Données de test:", testData);

    const emailContent = `
      Nouveau message de contact (TEST):
      
      Nom: ${testData.firstName} ${testData.lastName}
      Email: ${testData.email}
      Entreprise: ${testData.companyName}
      Fonction: ${testData.jobTitle}
      Téléphone: ${testData.companyPhone}
      Site web: ${testData.companyWebsite}
      Sujet: ${testData.interest}
      
      Message:
      ${testData.message}
    `;

    console.log("Envoi de l'email texte brut...");
    // Email texte brut pour l'admin
    const plainEmailResult = await resend.emails.send({
      from: TEST_SENDER,
      to: TEST_ADMIN,
      subject: `[TEST] Nouveau message de contact - ${testData.interest}`,
      text: emailContent,
      replyTo: testData.email,
    });
    console.log("Résultat email texte:", plainEmailResult);

    console.log("Envoi de l'email template admin...");
    // Email avec template pour l'admin
    const adminEmailResult = await resend.emails.send({
      from: TEST_SENDER,
      to: TEST_ADMIN,
      subject: `[TEST] [Contact DazNode] ${testData.interest} - ${testData.firstName} ${testData.lastName}`,
      react: ContactEmailTemplate({
        type: "admin",
        firstName: testData.firstName,
        lastName: testData.lastName,
        email: testData.email,
        interest: testData.interest,
        message: testData.message,
      }),
    });
    console.log("Résultat email admin:", adminEmailResult);

    console.log("Envoi de l'email utilisateur...");
    // Email de confirmation pour l'utilisateur
    const userEmailResult = await resend.emails.send({
      from: TEST_SENDER,
      to: testData.email,
      subject: "[TEST] Confirmation de votre message - DazNode",
      react: ContactEmailTemplate({
        type: "user",
        firstName: testData.firstName,
        lastName: testData.lastName,
        email: testData.email,
        interest: testData.interest,
      }),
    });
    console.log("Résultat email utilisateur:", userEmailResult);

    return NextResponse.json(
      {
        message: "Emails de test envoyés avec succès",
        details: {
          from: TEST_SENDER,
          admin: TEST_ADMIN,
          user: TEST_USER,
        },
        results: {
          plainEmail: plainEmailResult,
          adminEmail: adminEmailResult,
          userEmail: userEmailResult,
        },
      },
      { status: 200 }
    );
  } catch (error) {
    console.error(
      "Erreur détaillée lors de l'envoi des emails de test:",
      error
    );
    return NextResponse.json(
      {
        error: "Erreur lors de l'envoi des emails de test",
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}
