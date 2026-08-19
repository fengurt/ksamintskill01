// Hybrid encryption for the provider-key store.
//   provider keys (JSON)  --AES-256-GCM-->  ciphertext
//   random AES key        --RSA-OAEP(pub)-> wrapped key
// The server decrypts only with the LOCAL PRIVATE PEM. The encrypted file
// (keys.enc) is safe at rest; without the PEM it is useless.
import { readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { publicEncrypt, privateDecrypt, randomBytes, createCipheriv, createDecipheriv, constants } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const APP_DIR = dirname(__dirname);

export const ENC_FILE = () => process.env.SECRETS_ENC || join(APP_DIR, "secrets", "keys.enc");
export const PRIV_PEM = () => process.env.LLMHUB_PEM || join(APP_DIR, "secrets", "llmhub_private.pem");
const PASSPHRASE = () => process.env.LLMHUB_PEM_PASSPHRASE || undefined;

const RSA_OPTS = (key, passphrase) => ({ key, passphrase, padding: constants.RSA_PKCS1_OAEP_PADDING, oaepHash: "sha256" });

export function encryptToFile(obj, publicPem, outPath) {
  const aesKey = randomBytes(32);
  const iv = randomBytes(12);
  const cipher = createCipheriv("aes-256-gcm", aesKey, iv);
  const data = Buffer.concat([cipher.update(JSON.stringify(obj), "utf8"), cipher.final()]);
  const tag = cipher.getAuthTag();
  const wrapped = publicEncrypt(RSA_OPTS(publicPem), aesKey);
  const payload = {
    v: 1, alg: "rsa-oaep-sha256+aes-256-gcm",
    key: wrapped.toString("base64"), iv: iv.toString("base64"),
    tag: tag.toString("base64"), data: data.toString("base64"),
    created: new Date().toISOString(),
  };
  return writeFile(outPath, JSON.stringify(payload, null, 2), { mode: 0o600 });
}

let cached = null;
export async function decryptSecrets() {
  if (cached) return cached;
  const encPath = ENC_FILE();
  const pemPath = PRIV_PEM();
  if (!existsSync(encPath) || !existsSync(pemPath)) return {};
  const payload = JSON.parse(await readFile(encPath, "utf8"));
  const pem = await readFile(pemPath, "utf8");
  const aesKey = privateDecrypt(RSA_OPTS(pem, PASSPHRASE()), Buffer.from(payload.key, "base64"));
  const decipher = createDecipheriv("aes-256-gcm", aesKey, Buffer.from(payload.iv, "base64"));
  decipher.setAuthTag(Buffer.from(payload.tag, "base64"));
  const json = Buffer.concat([decipher.update(Buffer.from(payload.data, "base64")), decipher.final()]).toString("utf8");
  cached = JSON.parse(json);
  return cached;
}

export function clearSecretsCache() { cached = null; }
