# Stage 1: Build the frontend
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm ci

COPY . .

RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built assets from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
