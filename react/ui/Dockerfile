FROM node:22-alpine

WORKDIR /app

# We don't copy the whole folder here because we want to mount it
# and install dependencies dynamically for the dev environment.
# This acts as a pure dev container environment.

CMD ["sh", "-c", "npm install && npm run dev -- --host 0.0.0.0 --port 5175"]