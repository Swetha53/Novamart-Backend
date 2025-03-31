# Use an official Java runtime as a parent image
FROM openjdk:21-jdk-slim

RUN apt-get update && apt-get install -y curl

# Set the working directory
WORKDIR /app

# Copy the compiled .jar file from the target folder (you can adjust the path if necessary)
COPY target/search-service-0.0.1-SNAPSHOT.jar /app/search-service-0.0.1-SNAPSHOT.jar

# Expose the port that the application will run on
EXPOSE 8086

# Run the application
ENTRYPOINT ["java", "-jar", "search-service-0.0.1-SNAPSHOT.jar"]