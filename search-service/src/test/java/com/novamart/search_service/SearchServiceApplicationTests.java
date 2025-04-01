package com.novamart.search_service;

import io.restassured.RestAssured;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.testcontainers.junit.jupiter.Testcontainers;

@Testcontainers
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class SearchServiceApplicationTests {

	@LocalServerPort
	private int port;

	@BeforeEach
	void setUp() {
		RestAssured.baseURI = "https://localhost";
		RestAssured.port = port;
	}

	@Test
	void getUser() {
		String requestBody = """
				{
				    "name": "Laptop"
				}
				""";
		RestAssured.given()
				.header("Content-Type", "application/json")
				.body(requestBody)
				.relaxedHTTPSValidation()
				.when()
				.get("/api/search")
				.then()
				.statusCode(200)
				.log().all();
	}

}
