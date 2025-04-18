import { NextResponse } from "next/server";
import nodemailer from "nodemailer";

interface ShippingInfo {
  name: string;
  address: string;
  city: string;
  zipCode: string;
  country: string;
  phone: string;
  email: string;
  recipientEmail: string;
}

export async function POST(req: Request) {
  try {
    const data: ShippingInfo = await req.json();

    // Configuration du transporteur d'email
    const transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: Number(process.env.SMTP_PORT),
      secure: true,
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
      },
    });

    // Template HTML pour l'email
    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <style>
            body {
              font-family: Arial, sans-serif;
              line-height: 1.6;
              color: #333;
            }
            .container {
              max-width: 600px;
              margin: 0 auto;
              padding: 20px;
            }
            .header {
              background-color: #ff6b00;
              color: white;
              padding: 20px;
              text-align: center;
              border-radius: 5px 5px 0 0;
            }
            .content {
              background-color: #f9f9f9;
              padding: 20px;
              border-radius: 0 0 5px 5px;
            }
            .section {
              margin-bottom: 20px;
              padding: 15px;
              background-color: white;
              border-radius: 5px;
            }
            .footer {
              text-align: center;
              margin-top: 20px;
              font-size: 12px;
              color: #666;
            }
            .price {
              font-size: 24px;
              color: #ff6b00;
              font-weight: bold;
            }
            .check {
              color: #22c55e;
              margin-right: 5px;
            }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>🎉 Nouvelle commande Daznode !</h1>
            </div>
            <div class="content">
              <div class="section">
                <h2>Détails de la commande</h2>
                <p class="price">400,000 sats</p>
                <p><strong>Date :</strong> ${new Date().toLocaleDateString("fr-FR")}</p>
                <p><strong>Référence :</strong> DN${Date.now().toString().slice(-6)}</p>
              </div>
              
              <div class="section">
                <h2>Informations de livraison</h2>
                <p><strong>Nom :</strong> ${data.name}</p>
                <p><strong>Adresse :</strong> ${data.address}</p>
                <p><strong>Ville :</strong> ${data.city}</p>
                <p><strong>Code postal :</strong> ${data.zipCode}</p>
                <p><strong>Pays :</strong> ${data.country}</p>
                <p><strong>Téléphone :</strong> ${data.phone}</p>
                <p><strong>Email :</strong> ${data.email}</p>
              </div>

              <div class="section">
                <h2>Contenu de la commande</h2>
                <p><span class="check">✓</span> Nœud Raspberry Pi 5 (8GB RAM) pré-configuré</p>
                <p><span class="check">✓</span> SSD 1To avec UmbrelOS installé</p>
                <p><span class="check">✓</span> 50,000 sats pré-chargés pour vos premiers canaux</p>
                <p><span class="check">✓</span> 2 semaines de support dédié</p>
                <p><span class="check">✓</span> 1 an d'abonnement DazIA Premium offert</p>
                <p><span class="check">✓</span> Livraison gratuite en France</p>
              </div>

              <div class="section">
                <h2>Prochaines étapes</h2>
                <p>1. Confirmation de paiement en cours de traitement</p>
                <p>2. Préparation et configuration de votre Daznode</p>
                <p>3. Expédition sous 48-72h après confirmation du paiement</p>
                <p>4. Email de suivi avec numéro de tracking</p>
              </div>

              <div class="footer">
                <p>Pour toute question, contactez-nous à support@daznode.com</p>
                <p>© ${new Date().getFullYear()} DazNode - Tous droits réservés</p>
              </div>
            </div>
          </div>
        </body>
      </html>
    `;

    // Version texte simple pour les clients qui ne supportent pas l'HTML
    const textContent = `
      Nouvelle commande Daznode !
      
      Détails de la commande :
      ----------------------
      Prix : 400,000 sats
      Date : ${new Date().toLocaleDateString("fr-FR")}
      Référence : DN${Date.now().toString().slice(-6)}

      Informations de livraison :
      -------------------------
      Nom : ${data.name}
      Adresse : ${data.address}
      Ville : ${data.city}
      Code postal : ${data.zipCode}
      Pays : ${data.country}
      Téléphone : ${data.phone}
      Email : ${data.email}
      
      Contenu de la commande :
      ----------------------
      ✓ Nœud Raspberry Pi 5 (8GB RAM) pré-configuré
      ✓ SSD 1To avec UmbrelOS installé
      ✓ 50,000 sats pré-chargés pour vos premiers canaux
      ✓ 2 semaines de support dédié
      ✓ 1 an d'abonnement DazIA Premium offert
      ✓ Livraison gratuite en France

      Prochaines étapes :
      -----------------
      1. Confirmation de paiement en cours de traitement
      2. Préparation et configuration de votre Daznode
      3. Expédition sous 48-72h après confirmation du paiement
      4. Email de suivi avec numéro de tracking

      Pour toute question, contactez-nous à support@daznode.com
      © ${new Date().getFullYear()} DazNode - Tous droits réservés
    `;

    // Envoi de l'email
    await transporter.sendMail({
      from: process.env.SMTP_FROM,
      to: [data.recipientEmail, data.email], // Envoi à l'admin et au client
      subject:
        "🚀 Nouvelle commande Daznode #DN" + Date.now().toString().slice(-6),
      text: textContent,
      html: htmlContent,
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Erreur lors de l'envoi de l'email:", error);
    return NextResponse.json(
      { error: "Erreur lors de l'envoi de l'email" },
      { status: 500 }
    );
  }
}
