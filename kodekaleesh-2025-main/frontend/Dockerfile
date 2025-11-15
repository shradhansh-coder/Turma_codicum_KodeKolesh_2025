### Stage 1: Build
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Build with passed build-time env (Compose can use args)
ARG REACT_APP_API_BASE
ARG REACT_APP_ETH_CHAIN_ID
ARG REACT_APP_ETH_CONTRACT
ENV REACT_APP_API_BASE=${REACT_APP_API_BASE} \
	REACT_APP_ETH_CHAIN_ID=${REACT_APP_ETH_CHAIN_ID} \
	REACT_APP_ETH_CONTRACT=${REACT_APP_ETH_CONTRACT}
RUN npm run build

### Stage 2: Serve
FROM nginx:1.27-alpine AS runtime
WORKDIR /usr/share/nginx/html
COPY --from=build /app/build .
EXPOSE 80
# Provide minimal health info route via nginx default (index.html)
CMD ["nginx", "-g", "daemon off;"]
