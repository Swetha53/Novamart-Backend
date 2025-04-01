package com.novamart.user_service;

import io.restassured.RestAssured;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.testcontainers.containers.MongoDBContainer;
import org.testcontainers.junit.jupiter.Testcontainers;

@Testcontainers
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class UserServiceApplicationTests {

	@ServiceConnection
	static MongoDBContainer mongoDBContainer = new MongoDBContainer("mongo:7.0.5");
	@LocalServerPort
	private int port;

	@BeforeEach
	void setUp() {
		RestAssured.baseURI = "https://localhost";
		RestAssured.port = port;
	}

	static {
		mongoDBContainer.start();
	}

	@Test
	void testRegisterUser() {
		String requestBody = """
				{
				    "email": "johndoe99@gmail.com",
				    "password": "Strong_pa55word",
				    "firstName": "John",
				    "lastName": "Doe",
				    "age": 26,
				    "gender": "M",
				    "phone": "1234567890",
				    "address": "2nd floor, Ravenclaw Common Room, Hogwarts, Scotland",
				    "avatar": "",
				    "accountType": "CUSTOMER",
				    "preferences": []
				}
				""";
		RestAssured.given()
				.header("Content-Type", "application/json")
				.body(requestBody)
				.relaxedHTTPSValidation()
				.when()
				.post("/api/users/register")
				.then()
				.statusCode(201)
				.log().all();
	}

	@Test
	void testLoginUser() {
		String requestBody = """
				{
				    "email": "johndoe99@gmail.com",
				    "password": "Strong_pa55word"
				}
				""";
		RestAssured.given()
				.header("Content-Type", "application/json")
				.body(requestBody)
				.relaxedHTTPSValidation()
				.when()
				.post("/api/users/login")
				.then()
				.statusCode(200)
				.log().all();
	}

	@Test
	void getUser() {
		RestAssured.given()
				.header("Content-Type", "application/json")
				.relaxedHTTPSValidation()
				.when()
				.get("/api/users?userId=1234567890")
				.then()
				.statusCode(200)
				.log().all();
	}

	@Test
	void updateUser() {
		String requestBody = """
				{
				    "email": "johndoe99@gmail.com",
				    "password": "Strong_pa55word",
				    "firstName": "John",
				    "lastName": "Doe",
				    "age": 26,
				    "gender": "M",
				    "phone": "1234567890",
				    "address": "2nd floor, Ravenclaw Common Room, Hogwarts, Scotland",
				    "avatar": "",
				    "accountType": "CUSTOMER",
				    "preferences": []
				}
				""";
		RestAssured.given()
				.header("Content-Type", "application/json")
				.body(requestBody)
				.relaxedHTTPSValidation()
				.when()
				.put("/api/users/update")
				.then()
				.statusCode(200)
				.log().all();
	}

	@Test
	void resetPassword() {
		String requestBody = """
				{
				    "email": "johndoe99@gmail.com",
				    "password": "Strong_pa55word"
				}
				""";
		RestAssured.given()
				.header("Content-Type", "application/json")
				.body(requestBody)
				.relaxedHTTPSValidation()
				.when()
				.put("/api/users/reset-password")
				.then()
				.statusCode(200)
				.log().all();
	}

	@Test
	void deleteUser() {
		RestAssured.given()
				.header("Content-Type", "application/json")
				.relaxedHTTPSValidation()
				.when()
				.delete("/api/users/delete?userId=1234567890")
				.then()
				.statusCode(200)
				.log().all();
	}

	@Test
	void authenticateUser() {
		RestAssured.given()
				.header("Content-Type", "application/json")
				.relaxedHTTPSValidation()
				.when()
				.get("/api/users/authenticate?userId=1234567890&checkField=role&value=ADMIN")
				.then()
				.statusCode(200)
				.log().all();
	}

	@Test
	void deleteAllUsers() {
		RestAssured.given()
				.header("Content-Type", "application/json")
				.relaxedHTTPSValidation()
				.when()
				.delete("/api/users/delete-all")
				.then()
				.statusCode(200)
				.log().all();
	}

	@Test
	void getAllUsers() {
		RestAssured.given()
				.header("Content-Type", "application/json")
				.relaxedHTTPSValidation()
				.when()
				.get("/api/users/all")
				.then()
				.statusCode(200)
				.log().all();
	}
}
