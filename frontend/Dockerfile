# Base stage
FROM node:18-alpine as base
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Development stage
FROM base as dev
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

# Build stage
FROM base as build
ARG VITE_API_URL
ARG BUILD_TIME=0
ENV VITE_API_URL=$VITE_API_URL
RUN BUILD_TIME_VAL=${BUILD_TIME} && \
  if [ "$BUILD_TIME_VAL" = "0" ]; then BUILD_TIME_VAL=$(date +%s); fi && \
  echo "Building with timestamp: $BUILD_TIME_VAL" && \
  npm run build && \
  if [ -f /app/dist/index.html ]; then \
    sed -i "s/{{BUILD_TIME}}/$BUILD_TIME_VAL/g" /app/dist/index.html; \
  fi

# Production stage
FROM nginx:alpine as prod
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
