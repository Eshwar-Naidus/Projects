# Multi-stage production build for Hermes WebUI
FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=8787
ENV TRUST_PROXY=true

# Create non-root runner user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 hermes

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/public ./public

USER hermes

EXPOSE 8787

CMD ["node", "dist/server.js"]
