FROM node:18-slim

WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev

COPY ./app ./app
COPY ./scripts ./scripts
COPY server.js ./

EXPOSE 3000

CMD ["node", "server.js"]
