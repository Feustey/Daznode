import { supabase } from "@/app/lib/supabase";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import nodemailer from "nodemailer";

export interface User {
  id: string;
  email: string;
  name: string;
  password: string;
  created_at: Date;
  updated_at: Date;
  email_verified: boolean;
}

export interface Session {
  id: string;
  user_id: string;
  expires: Date;
  created_at: Date;
}

export interface VerificationCode {
  id: string;
  user_id: string;
  code: string;
  expires: Date;
  created_at: Date;
}

export class AuthService {
  private transporter: nodemailer.Transporter;

  constructor() {
    this.transporter = nodemailer.createTransport({
      host: process.env.EMAIL_SERVER_HOST,
      port: Number(process.env.EMAIL_SERVER_PORT),
      secure: Number(process.env.EMAIL_SERVER_PORT) === 465,
      auth: {
        user: process.env.EMAIL_SERVER_USER,
        pass: process.env.EMAIL_SERVER_PASSWORD,
      },
    });
  }

  async createUser(
    email: string,
    name: string,
    password: string
  ): Promise<User> {
    try {
      // Vérifier si l'utilisateur existe déjà
      const { data: existingUser } = await supabase
        .from("users")
        .select("*")
        .eq("email", email)
        .single();

      if (existingUser) {
        throw new Error("User already exists");
      }

      // Hasher le mot de passe
      const hashedPassword = await bcrypt.hash(password, 10);

      // Créer un nouvel utilisateur
      const { data: user, error } = await supabase
        .from("users")
        .insert({
          email,
          name,
          password: hashedPassword,
          email_verified: false,
        })
        .select()
        .single();

      if (error) throw error;

      return {
        id: user.id,
        email: user.email,
        name: user.name,
        password: user.password,
        created_at: new Date(user.created_at),
        updated_at: new Date(user.updated_at),
        email_verified: user.email_verified,
      };
    } catch (error) {
      console.error("Error creating user:", error);
      throw error;
    }
  }

  async verifyUser(email: string, code: string): Promise<boolean> {
    try {
      // Trouver l'utilisateur
      const { data: user } = await supabase
        .from("users")
        .select("*")
        .eq("email", email)
        .single();

      if (!user) {
        throw new Error("User not found");
      }

      // Trouver le code de vérification
      const { data: verificationCode } = await supabase
        .from("verification_codes")
        .select("*")
        .eq("user_id", user.id)
        .eq("code", code)
        .single();

      if (!verificationCode) {
        throw new Error("Invalid verification code");
      }

      // Vérifier si le code est expiré
      if (new Date(verificationCode.expires) < new Date()) {
        throw new Error("Verification code expired");
      }

      // Marquer l'utilisateur comme vérifié
      const { error } = await supabase
        .from("users")
        .update({ email_verified: true })
        .eq("id", user.id);

      if (error) throw error;

      // Supprimer le code de vérification
      await supabase
        .from("verification_codes")
        .delete()
        .eq("id", verificationCode.id);

      return true;
    } catch (error) {
      console.error("Error verifying user:", error);
      throw error;
    }
  }

  async createSession(userId: string): Promise<Session> {
    try {
      // Vérifier si l'utilisateur existe
      const { data: user } = await supabase
        .from("users")
        .select("*")
        .eq("id", userId)
        .single();

      if (!user) {
        throw new Error("User not found");
      }

      // Créer une nouvelle session
      const { data: session, error } = await supabase
        .from("sessions")
        .insert({
          user_id: userId,
          expires: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        })
        .select()
        .single();

      if (error) throw error;

      return {
        id: session.id,
        user_id: session.user_id,
        expires: new Date(session.expires),
        created_at: new Date(session.created_at),
      };
    } catch (error) {
      console.error("Error creating session:", error);
      throw error;
    }
  }

  async getSession(sessionId: string): Promise<Session | null> {
    try {
      const { data: session } = await supabase
        .from("sessions")
        .select("*")
        .eq("id", sessionId)
        .single();

      if (!session) {
        return null;
      }

      // Vérifier si la session est expirée
      if (new Date(session.expires) < new Date()) {
        await supabase.from("sessions").delete().eq("id", sessionId);
        return null;
      }

      return {
        id: session.id,
        user_id: session.user_id,
        expires: new Date(session.expires),
        created_at: new Date(session.created_at),
      };
    } catch (error) {
      console.error("Error getting session:", error);
      throw error;
    }
  }

  async deleteSession(sessionId: string): Promise<boolean> {
    try {
      const { error } = await supabase
        .from("sessions")
        .delete()
        .eq("id", sessionId);

      if (error) throw error;
      return true;
    } catch (error) {
      console.error("Error deleting session:", error);
      throw error;
    }
  }

  async createVerificationCode(userId: string): Promise<VerificationCode> {
    try {
      // Vérifier si l'utilisateur existe
      const { data: user } = await supabase
        .from("users")
        .select("*")
        .eq("id", userId)
        .single();

      if (!user) {
        throw new Error("User not found");
      }

      // Générer un code de vérification
      const code = Math.floor(100000 + Math.random() * 900000).toString();

      // Créer un nouveau code de vérification
      const { data: verificationCode, error } = await supabase
        .from("verification_codes")
        .insert({
          user_id: userId,
          code,
          expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
        })
        .select()
        .single();

      if (error) throw error;

      // Envoyer l'email de vérification
      await this.transporter.sendMail({
        from: process.env.EMAIL_FROM,
        to: user.email,
        subject: "Vérification de votre compte",
        text: `Votre code de vérification est: ${code}`,
        html: `<p>Votre code de vérification est: <strong>${code}</strong></p>`,
      });

      return {
        id: verificationCode.id,
        user_id: verificationCode.user_id,
        code: verificationCode.code,
        expires: new Date(verificationCode.expires),
        created_at: new Date(verificationCode.created_at),
      };
    } catch (error) {
      console.error("Error creating verification code:", error);
      throw error;
    }
  }

  async getUser(userId: string): Promise<User | null> {
    try {
      const { data: user } = await supabase
        .from("users")
        .select("*")
        .eq("id", userId)
        .single();

      if (!user) {
        return null;
      }

      return {
        id: user.id,
        email: user.email,
        name: user.name,
        password: user.password,
        created_at: new Date(user.created_at),
        updated_at: new Date(user.updated_at),
        email_verified: user.email_verified,
      };
    } catch (error) {
      console.error("Error getting user:", error);
      throw error;
    }
  }

  generateToken(user: User): string {
    return jwt.sign(
      { id: user.id, email: user.email },
      process.env.JWT_SECRET || "secret",
      { expiresIn: "7d" }
    );
  }

  verifyToken(token: string): any {
    return jwt.verify(token, process.env.JWT_SECRET || "secret");
  }
}

export const authService = new AuthService();
