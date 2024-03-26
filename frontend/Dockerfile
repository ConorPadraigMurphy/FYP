# Use an official Node.js runtime as the base image
FROM node:14 AS builder


# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install the application dependencies
RUN npm ci

# Copy the frontend application code to the working directory
COPY . .

# Change directory to the frontend
WORKDIR /frontend

# Build the frontend application
RUN npm run build

# Node.js runtime
FROM node:14-alpine

# Install serve to serve the built application
RUN npm install -g serve

# Copy the built frontend application from the previous stage
COPY --from=0 /frontend

# Copy the server.js file from the frontend folder
COPY --from=0 /frontend/server.js

# Expose port 3000 for the application
EXPOSE 3000

# Define the command to run the application
CMD ["sh", "-c", "npm start --prefix frontend & node frontend/server.js"]
