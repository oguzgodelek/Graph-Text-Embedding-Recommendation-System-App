FROM node:20

# Update and install security patches
RUN apt-get update && apt-get upgrade -y && apt-get clean

WORKDIR /app

COPY package.json /app
RUN npm install

COPY ./public /app/public
COPY ./src /app/src
COPY . /app/
EXPOSE 8080

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
