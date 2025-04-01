package com.novamart.product_service;

import static com.github.tomakehurst.wiremock.core.WireMockConfiguration.wireMockConfig;
import static org.hamcrest.Matchers.*;

import com.github.tomakehurst.wiremock.WireMockServer;
import com.github.tomakehurst.wiremock.junit.WireMockRule;
import com.novamart.product_service.client.UserClient;
import org.junit.Rule;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnitRunner;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.cloud.contract.wiremock.AutoConfigureWireMock;
import org.springframework.context.annotation.Import;
import org.testcontainers.containers.MongoDBContainer;
import io.restassured.RestAssured;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.shaded.org.hamcrest.Matchers;

import static com.github.tomakehurst.wiremock.client.WireMock.*;

@Testcontainers
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ProductServiceApplicationTests {

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
	void getAllProducts() {
		RestAssured.given()
				.relaxedHTTPSValidation()
				.when()
				.get("/api/products/all")
				.then()
				.statusCode(200)
				.log().all();
	}
	@Test
	void getProductsByMerchantId() {
		RestAssured.given()
				.relaxedHTTPSValidation()
				.when()
				.get("/api/products?merchantId=12345")
				.then()
				.statusCode(200)
				.log().all();
	}
	@Test
	void searchProducts() {
		RestAssured.given()
				.relaxedHTTPSValidation()
				.when()
				.get("/api/products/search?name=12345")
				.then()
				.statusCode(200)
				.log().all();
	}
	@Test
	void getReviews() {
		RestAssured.given()
				.relaxedHTTPSValidation()
				.when()
				.get("/api/reviews?productId=12345")
				.then()
				.statusCode(200)
				.log().all();
	}
	@Test
	void getReviewsByUserId() {
		RestAssured.given()
				.relaxedHTTPSValidation()
				.when()
				.get("/api/reviews?userId=12345")
				.then()
				.statusCode(200)
				.log().all();
	}
	@Test
	void getReviewsByMerchantId() {
		RestAssured.given()
				.relaxedHTTPSValidation()
				.when()
				.get("/api/reviews?merchantId=12345")
				.then()
				.statusCode(200)
				.log().all();
	}
}
