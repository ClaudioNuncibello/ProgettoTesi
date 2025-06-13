# --- BUILD STAGE ---
FROM node:18-alpine AS builder
WORKDIR /app

# Installazione pnpm
RUN npm install -g pnpm

# Copia lockfile + package.json e installa
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Copia il sorgente (senza node_modules grazie a .dockerignore)
COPY . .

# Build Next.js
RUN pnpm build

# --- RUNTIME STAGE ---
FROM node:18-alpine AS runner
WORKDIR /app

# Installazione pnpm
RUN npm install -g pnpm

# Installa solo dipendenze di produzione
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --production --frozen-lockfile

# Copia la build e le risorse
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.mjs ./

EXPOSE 3000
CMD ["pnpm", "start"]
